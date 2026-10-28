-- PREPARED ONLY. One protected review table; no existing table/function/policy/grant is changed.
BEGIN;
CREATE TABLE gk_private.attendance_import_staging (
 id uuid PRIMARY KEY,
 source_record_id uuid NOT NULL REFERENCES gk_private.source_records(id) ON DELETE RESTRICT,
 header_source_record_id uuid REFERENCES gk_private.source_records(id) ON DELETE RESTRICT,
 artifact_id uuid NOT NULL REFERENCES gk_private.source_artifacts(id) ON DELETE RESTRICT,
 source_file text NOT NULL,
 source_sheet text NOT NULL,
 native_sheet_key text NOT NULL,
 source_row integer NOT NULL CHECK (source_row > 0),
 source_column text NOT NULL CHECK (source_column ~ '^([A-Z]{1,3}|__ROW__)$'),
 source_reference text NOT NULL,
 observation_kind text NOT NULL CHECK (observation_kind IN ('MARK','FORMULA','SUMMARY_VALUE','AUXILIARY_VALUE','SOURCE_CONTEXT')),
 recorded_child_identifier jsonb NOT NULL DEFAULT 'null',
 recorded_child_name jsonb NOT NULL DEFAULT 'null',
 original_mark jsonb NOT NULL,
 original_header jsonb NOT NULL DEFAULT 'null',
 header_label text,
 program_reported jsonb NOT NULL DEFAULT 'null',
 parsed_date date,
 verified_child_id uuid REFERENCES public.children(id) ON DELETE RESTRICT,
 candidate_child_ids uuid[] NOT NULL DEFAULT '{}',
 identity_status text NOT NULL CHECK (identity_status IN ('VERIFIED','PROVISIONAL_MATCH','AMBIGUOUS','UNMATCHED')),
 date_status text NOT NULL CHECK (date_status IN ('VERIFIED','MISSING','FORMULA_UNRESOLVED','SANITIZED_UNTRUSTED','UNPARSED')),
 code_status text NOT NULL CHECK (code_status IN ('VERIFIED','PENDING')),
 review_status text NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','reviewed','excluded')),
 flags text[] NOT NULL,
 provenance jsonb NOT NULL CHECK (jsonb_typeof(provenance)='object'),
 review_notes text NOT NULL DEFAULT '',
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE (source_record_id, source_column),
 CHECK ((identity_status='VERIFIED') = (verified_child_id IS NOT NULL)),
 CHECK ((date_status='VERIFIED') = (parsed_date IS NOT NULL)),
 CHECK (identity_status <> 'PROVISIONAL_MATCH' OR cardinality(candidate_child_ids)=1),
 CHECK (identity_status <> 'AMBIGUOUS' OR cardinality(candidate_child_ids)>1),
 CHECK (identity_status <> 'UNMATCHED' OR cardinality(candidate_child_ids)=0),
 CHECK ((observation_kind='SOURCE_CONTEXT')=(source_column='__ROW__'))
);
ALTER TABLE gk_private.attendance_import_staging ENABLE ROW LEVEL SECURITY;
ALTER TABLE gk_private.attendance_import_staging FORCE ROW LEVEL SECURITY;
REVOKE ALL ON gk_private.attendance_import_staging FROM PUBLIC, anon, authenticated, service_role;
-- No policies or application grants: even eligible Workspace members cannot read private staging.
CREATE INDEX attendance_staging_review_idx ON gk_private.attendance_import_staging(review_status,identity_status);
CREATE INDEX attendance_staging_child_date_idx ON gk_private.attendance_import_staging(verified_child_id,parsed_date) WHERE verified_child_id IS NOT NULL;
CREATE INDEX attendance_staging_header_idx ON gk_private.attendance_import_staging(header_source_record_id);
CREATE INDEX attendance_staging_artifact_idx ON gk_private.attendance_import_staging(artifact_id);

CREATE FUNCTION gk_private.guard_attendance_import_staging() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog AS $$
DECLARE sr gk_private.source_records%ROWTYPE; hr gk_private.source_records%ROWTYPE;
BEGIN
 IF TG_OP IN ('DELETE','TRUNCATE') THEN RAISE EXCEPTION 'ATTENDANCE_EVIDENCE_DELETION_DENIED'; END IF;
 IF TG_OP='UPDATE' THEN
  IF (to_jsonb(NEW)-ARRAY['updated_at','review_notes','review_status']) IS DISTINCT FROM
     (to_jsonb(OLD)-ARRAY['updated_at','review_notes','review_status']) THEN
    RAISE EXCEPTION 'ATTENDANCE_SOURCE_EVIDENCE_IMMUTABLE';
  END IF;
  NEW.created_at:=OLD.created_at; NEW.updated_at:=now(); RETURN NEW;
 END IF;
 SELECT * INTO STRICT sr FROM gk_private.source_records WHERE id=NEW.source_record_id;
 IF sr.artifact_id<>NEW.artifact_id OR sr.native_sheet_key<>NEW.native_sheet_key OR sr.source_row<>NEW.source_row THEN
  RAISE EXCEPTION 'ATTENDANCE_SOURCE_COORDINATE_MISMATCH';
 END IF;
 IF NOT EXISTS(SELECT 1 FROM gk_private.source_artifacts WHERE id=NEW.artifact_id AND file_code=NEW.source_file AND worksheet_manifest->NEW.source_sheet->>'native_sheet_key'=NEW.native_sheet_key) THEN
  RAISE EXCEPTION 'ATTENDANCE_SOURCE_FILE_MISMATCH';
 END IF;
 IF NEW.source_reference<>NEW.source_file||'/'||NEW.source_sheet||'/R'||NEW.source_row::text THEN RAISE EXCEPTION 'ATTENDANCE_SOURCE_REFERENCE_MISMATCH'; END IF;
 IF NEW.provenance->>'roster_row'='true' AND (NEW.recorded_child_name IS DISTINCT FROM COALESCE(sr.cell_payload->(NEW.provenance->>'name_column'),'null'::jsonb) OR NEW.recorded_child_identifier IS DISTINCT FROM COALESCE(sr.cell_payload->(NEW.provenance->>'identifier_column'),'null'::jsonb)) THEN RAISE EXCEPTION 'ATTENDANCE_RECORDED_IDENTITY_MISMATCH'; END IF;
 IF NEW.source_column<>'__ROW__' AND NEW.original_mark IS DISTINCT FROM COALESCE(sr.cell_payload->NEW.source_column,'null'::jsonb) THEN
  RAISE EXCEPTION 'ATTENDANCE_SOURCE_MARK_MISMATCH';
 END IF;
 IF NEW.header_source_record_id IS NOT NULL THEN
  SELECT * INTO STRICT hr FROM gk_private.source_records WHERE id=NEW.header_source_record_id;
  IF hr.artifact_id<>NEW.artifact_id OR hr.native_sheet_key<>NEW.native_sheet_key OR
     NEW.original_header IS DISTINCT FROM COALESCE(hr.cell_payload->NEW.source_column,'null'::jsonb) THEN
   RAISE EXCEPTION 'ATTENDANCE_HEADER_MISMATCH';
  END IF;
 END IF;
 IF EXISTS(SELECT 1 FROM unnest(NEW.candidate_child_ids) x(id) WHERE id IS NULL OR NOT EXISTS(SELECT 1 FROM public.children c WHERE c.id=x.id)) OR
    cardinality(NEW.candidate_child_ids)<>(SELECT count(DISTINCT x) FROM unnest(NEW.candidate_child_ids) x) THEN
  RAISE EXCEPTION 'ATTENDANCE_INVALID_CANDIDATE';
 END IF;
 -- No name-only verification or trusting syntactically valid sanitized dates.
 IF NEW.identity_status='VERIFIED' AND NOT EXISTS(SELECT 1 FROM public.children c WHERE c.id=NEW.verified_child_id AND to_jsonb(c.child_business_id)=NEW.recorded_child_identifier) THEN
  RAISE EXCEPTION 'ATTENDANCE_EXACT_ID_REQUIRED';
 END IF;
 IF NEW.date_status='VERIFIED' AND NEW.provenance->'date_fidelity_approved' IS DISTINCT FROM 'true'::jsonb THEN
  RAISE EXCEPTION 'ATTENDANCE_DATE_FIDELITY_REQUIRED';
 END IF;
 IF NEW.code_status='VERIFIED' AND NEW.provenance->'attendance_codes_approved' IS DISTINCT FROM 'true'::jsonb THEN RAISE EXCEPTION 'ATTENDANCE_CODE_APPROVAL_REQUIRED'; END IF;
 NEW.created_at:=now(); NEW.updated_at:=NEW.created_at; RETURN NEW;
END $$;
REVOKE ALL ON FUNCTION gk_private.guard_attendance_import_staging() FROM PUBLIC, anon, authenticated, service_role;
CREATE TRIGGER attendance_staging_guard BEFORE INSERT OR UPDATE OR DELETE ON gk_private.attendance_import_staging
 FOR EACH ROW EXECUTE FUNCTION gk_private.guard_attendance_import_staging();
CREATE TRIGGER attendance_staging_no_truncate BEFORE TRUNCATE ON gk_private.attendance_import_staging
 FOR EACH STATEMENT EXECUTE FUNCTION gk_private.guard_attendance_import_staging();
COMMENT ON TABLE gk_private.attendance_import_staging IS 'Restricted sanitized source-cell evidence; pending review is not verified/approved operational attendance. No application access activated.';
COMMIT;
