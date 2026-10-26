-- PREPARED ONLY. No migration has been executed.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';
CREATE FUNCTION gk_private.reject_evidence_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
 IF TG_OP='DELETE' OR TG_TABLE_NAME <> 'source_records' THEN RAISE EXCEPTION 'Evidence is append-only'; END IF;
 IF NEW.artifact_id IS DISTINCT FROM OLD.artifact_id OR NEW.native_sheet_key IS DISTINCT FROM OLD.native_sheet_key
  OR NEW.source_row IS DISTINCT FROM OLD.source_row OR NEW.cell_payload IS DISTINCT FROM OLD.cell_payload THEN RAISE EXCEPTION 'Original source payload and coordinates are immutable'; END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION gk_private.reject_evidence_mutation() FROM PUBLIC,anon,authenticated;

CREATE FUNCTION gk_private.reject_identity_change()
RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog AS $$
DECLARE key_name text;
BEGIN
 FOREACH key_name IN ARRAY TG_ARGV LOOP
  IF to_jsonb(NEW) -> key_name IS DISTINCT FROM to_jsonb(OLD) -> key_name THEN RAISE EXCEPTION 'Identity/definition change requires an explicit correction workflow'; END IF;
 END LOOP;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION gk_private.reject_identity_change() FROM PUBLIC,anon,authenticated;

CREATE FUNCTION gk_private.capture_row_change()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE old_doc jsonb; new_doc jsonb; chosen jsonb; keys jsonb := '{}'::jsonb; k text;
BEGIN
 IF TG_OP <> 'INSERT' THEN old_doc := to_jsonb(OLD); END IF;
 IF TG_OP <> 'DELETE' THEN new_doc := to_jsonb(NEW); END IF;
 chosen := COALESCE(new_doc,old_doc);
 FOREACH k IN ARRAY TG_ARGV LOOP keys := keys || jsonb_build_object(k,chosen -> k); END LOOP;
 IF TG_TABLE_NAME='source_records' THEN old_doc := old_doc - 'cell_payload'; new_doc := new_doc - 'cell_payload'; END IF;
 INSERT INTO gk_private.record_audit_events(schema_name,table_name,record_key,operation,before_value,after_value,created_by,updated_by,actor_ref)
 VALUES(TG_TABLE_SCHEMA,TG_TABLE_NAME,keys,TG_OP,old_doc,new_doc,auth.uid(),auth.uid(),COALESCE(chosen ->> 'actor_ref','db:'||session_user));
 RETURN COALESCE(NEW,OLD);
END;
$$;
REVOKE ALL ON FUNCTION gk_private.capture_row_change() FROM PUBLIC,anon,authenticated;

CREATE FUNCTION gk_private.require_import_provenance()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE ok boolean; pointer text := TG_ARGV[0]; target uuid;
BEGIN
 IF NEW.origin_kind <> 'import' THEN RETURN NEW; END IF;
 IF TG_TABLE_NAME='reference_values' THEN
  SELECT EXISTS(SELECT 1 FROM gk_private.source_provenance p WHERE p.reference_vocabulary=NEW.vocabulary AND p.reference_code=NEW.code) INTO ok;
 ELSE
  IF pointer <> ALL(ARRAY['child_id','private_profile_child_id','caregiver_id','child_caregiver_id','program_change_id','response_id','item_id','answer_id','attendance_id','support_id','adl_id']) THEN RAISE EXCEPTION 'Invalid typed provenance pointer'; END IF;
  target := (to_jsonb(NEW) ->> TG_ARGV[1])::uuid;
  EXECUTE format('SELECT EXISTS (SELECT 1 FROM gk_private.source_provenance WHERE %I = $1)',pointer) INTO ok USING target;
 END IF;
 IF NOT COALESCE(ok,false) THEN RAISE EXCEPTION 'Imported target requires source provenance in the same transaction'; END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION gk_private.require_import_provenance() FROM PUBLIC,anon,authenticated;

CREATE FUNCTION gk_private.check_answer_kind()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE kind text;
BEGIN
 SELECT value_kind INTO STRICT kind FROM public.questionnaire_items WHERE id=NEW.item_id;
 IF kind='numeric' AND NEW.text_value IS NOT NULL THEN RAISE EXCEPTION 'Numeric item cannot contain text'; END IF;
 IF kind IN ('text','recommendation') AND NEW.numeric_value IS NOT NULL THEN RAISE EXCEPTION 'Text item cannot contain a numeric score'; END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION gk_private.check_answer_kind() FROM PUBLIC,anon,authenticated;
CREATE TRIGGER check_answer_kind BEFORE INSERT OR UPDATE ON gk_private.questionnaire_answers FOR EACH ROW EXECUTE FUNCTION gk_private.check_answer_kind();

CREATE FUNCTION gk_private.check_child_chronology()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE child uuid; joined date; born date; kind text; state text;
BEGIN
 child := (to_jsonb(NEW) ->> CASE WHEN TG_TABLE_NAME='children' THEN 'id' ELSE 'child_id' END)::uuid;
 SELECT joining_date INTO joined FROM public.children WHERE id=child FOR UPDATE;
 SELECT birth_date,origin_kind,review_state INTO born,kind,state FROM gk_private.child_private_profiles WHERE child_id=child;
 IF born > joined AND (kind='manual' OR state='accepted') THEN RAISE EXCEPTION 'Birth/joining chronology conflict requires source review'; END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION gk_private.check_child_chronology() FROM PUBLIC,anon,authenticated;
CREATE CONSTRAINT TRIGGER check_child_dates AFTER INSERT OR UPDATE ON public.children DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.check_child_chronology();
CREATE CONSTRAINT TRIGGER check_profile_dates AFTER INSERT OR UPDATE ON gk_private.child_private_profiles DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.check_child_chronology();
-- Manual and accepted facts must reference approved active controlled values.
CREATE FUNCTION gk_private.check_reference_state()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE doc jsonb := to_jsonb(NEW); col text; f text; vocab text; code text;
BEGIN
 IF doc ->> 'origin_kind' = 'import' AND doc ->> 'review_state' <> 'accepted' THEN RETURN NEW; END IF;
 FOREACH col IN ARRAY TG_ARGV LOOP
  f := split_part(col,':',2); vocab := doc ->> split_part(col,':',1); code := doc ->> f;
  IF code IS NOT NULL THEN
   PERFORM 1 FROM public.reference_values r WHERE r.vocabulary=vocab AND r.code=code
    AND r.active AND r.review_state='accepted' AND r.archived_at IS NULL FOR SHARE;
   IF NOT FOUND THEN RAISE EXCEPTION 'Selected controlled value is not approved and active'; END IF;
  END IF;
 END LOOP;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION gk_private.check_reference_state() FROM PUBLIC,anon,authenticated;

-- GENERATED TRIGGER BINDINGS
CREATE TRIGGER history_reference_values AFTER INSERT OR UPDATE OR DELETE ON public.reference_values FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('vocabulary','code');
CREATE CONSTRAINT TRIGGER lineage_reference_values AFTER INSERT OR UPDATE ON public.reference_values DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('reference_vocabulary','vocabulary');
CREATE TRIGGER identity_reference_values BEFORE UPDATE ON public.reference_values FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('vocabulary','code');
CREATE TRIGGER history_children AFTER INSERT OR UPDATE OR DELETE ON public.children FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_children AFTER INSERT OR UPDATE ON public.children FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('program_vocabulary:current_program_code','program_vocabulary:admitted_program_code','status_vocabulary:child_status_code');
CREATE CONSTRAINT TRIGGER lineage_children AFTER INSERT OR UPDATE ON public.children DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('child_id','id');
CREATE TRIGGER identity_children BEFORE UPDATE ON public.children FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','child_business_id');
CREATE TRIGGER history_child_private_profiles AFTER INSERT OR UPDATE OR DELETE ON gk_private.child_private_profiles FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('child_id');
CREATE CONSTRAINT TRIGGER lineage_child_private_profiles AFTER INSERT OR UPDATE ON gk_private.child_private_profiles DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('private_profile_child_id','child_id');
CREATE TRIGGER identity_child_private_profiles BEFORE UPDATE ON gk_private.child_private_profiles FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('child_id');
CREATE TRIGGER history_caregivers AFTER INSERT OR UPDATE OR DELETE ON gk_private.caregivers FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE CONSTRAINT TRIGGER lineage_caregivers AFTER INSERT OR UPDATE ON gk_private.caregivers DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('caregiver_id','id');
CREATE TRIGGER identity_caregivers BEFORE UPDATE ON gk_private.caregivers FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','caregiver_business_id');
CREATE TRIGGER history_child_caregivers AFTER INSERT OR UPDATE OR DELETE ON public.child_caregivers FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_child_caregivers AFTER INSERT OR UPDATE ON public.child_caregivers FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('role_vocabulary:role_code');
CREATE CONSTRAINT TRIGGER lineage_child_caregivers AFTER INSERT OR UPDATE ON public.child_caregivers DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('child_caregiver_id','id');
CREATE TRIGGER identity_child_caregivers BEFORE UPDATE ON public.child_caregivers FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','child_id','caregiver_id');
CREATE TRIGGER history_program_changes AFTER INSERT OR UPDATE OR DELETE ON public.program_changes FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_program_changes AFTER INSERT OR UPDATE ON public.program_changes FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('program_vocabulary:program_code');
CREATE CONSTRAINT TRIGGER lineage_program_changes AFTER INSERT OR UPDATE ON public.program_changes DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('program_change_id','id');
CREATE TRIGGER identity_program_changes BEFORE UPDATE ON public.program_changes FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','child_id');
CREATE TRIGGER history_questionnaire_responses AFTER INSERT OR UPDATE OR DELETE ON public.questionnaire_responses FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_questionnaire_responses AFTER INSERT OR UPDATE ON public.questionnaire_responses FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('definition_vocabulary:definition_key','program_vocabulary:program_code','centre_vocabulary:centre_code');
CREATE CONSTRAINT TRIGGER lineage_questionnaire_responses AFTER INSERT OR UPDATE ON public.questionnaire_responses DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('response_id','id');
CREATE TRIGGER identity_questionnaire_responses BEFORE UPDATE ON public.questionnaire_responses FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','child_caregiver_id','definition_key');
CREATE TRIGGER history_questionnaire_items AFTER INSERT OR UPDATE OR DELETE ON public.questionnaire_items FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_questionnaire_items AFTER INSERT OR UPDATE ON public.questionnaire_items FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('definition_vocabulary:definition_key');
CREATE CONSTRAINT TRIGGER lineage_questionnaire_items AFTER INSERT OR UPDATE ON public.questionnaire_items DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('item_id','id');
CREATE TRIGGER identity_questionnaire_items BEFORE UPDATE ON public.questionnaire_items FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','definition_key','item_key','prompt','value_kind');
CREATE TRIGGER history_questionnaire_answers AFTER INSERT OR UPDATE OR DELETE ON gk_private.questionnaire_answers FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE CONSTRAINT TRIGGER lineage_questionnaire_answers AFTER INSERT OR UPDATE ON gk_private.questionnaire_answers DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('answer_id','id');
CREATE TRIGGER identity_questionnaire_answers BEFORE UPDATE ON gk_private.questionnaire_answers FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','response_id','item_id','definition_key');
CREATE TRIGGER history_attendance_observations AFTER INSERT OR UPDATE OR DELETE ON public.attendance_observations FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_attendance_observations AFTER INSERT OR UPDATE ON public.attendance_observations FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('service_vocabulary:service_code','mark_vocabulary:mark_code','program_vocabulary:program_code');
CREATE CONSTRAINT TRIGGER lineage_attendance_observations AFTER INSERT OR UPDATE ON public.attendance_observations DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('attendance_id','id');
CREATE TRIGGER identity_attendance_observations BEFORE UPDATE ON public.attendance_observations FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','child_id');
CREATE TRIGGER history_support_observations AFTER INSERT OR UPDATE OR DELETE ON public.support_observations FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_support_observations AFTER INSERT OR UPDATE ON public.support_observations FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('program_vocabulary:program_code');
CREATE CONSTRAINT TRIGGER lineage_support_observations AFTER INSERT OR UPDATE ON public.support_observations DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('support_id','id');
CREATE TRIGGER identity_support_observations BEFORE UPDATE ON public.support_observations FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','child_id');
CREATE TRIGGER history_adl_visits AFTER INSERT OR UPDATE OR DELETE ON public.adl_visits FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER values_adl_visits AFTER INSERT OR UPDATE ON public.adl_visits FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('program_vocabulary:program_code');
CREATE CONSTRAINT TRIGGER lineage_adl_visits AFTER INSERT OR UPDATE ON public.adl_visits DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('adl_id','id');
CREATE TRIGGER identity_adl_visits BEFORE UPDATE ON public.adl_visits FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id','child_id');
CREATE TRIGGER protect_source_artifacts BEFORE UPDATE OR DELETE ON gk_private.source_artifacts FOR EACH ROW EXECUTE FUNCTION gk_private.reject_evidence_mutation();
CREATE TRIGGER protect_source_records BEFORE UPDATE OR DELETE ON gk_private.source_records FOR EACH ROW EXECUTE FUNCTION gk_private.reject_evidence_mutation();
CREATE TRIGGER history_source_records AFTER UPDATE ON gk_private.source_records FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER protect_source_provenance BEFORE UPDATE OR DELETE ON gk_private.source_provenance FOR EACH ROW EXECUTE FUNCTION gk_private.reject_evidence_mutation();
CREATE TRIGGER history_access_memberships AFTER INSERT OR UPDATE OR DELETE ON gk_private.access_memberships FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('user_id');
CREATE TRIGGER values_access_memberships AFTER INSERT OR UPDATE ON gk_private.access_memberships FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state('role_vocabulary:role_code');
CREATE TRIGGER identity_access_memberships BEFORE UPDATE ON gk_private.access_memberships FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('user_id');
CREATE TRIGGER history_identity_candidates AFTER INSERT OR UPDATE OR DELETE ON gk_private.identity_candidates FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change('id');
CREATE TRIGGER identity_identity_candidates BEFORE UPDATE ON gk_private.identity_candidates FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change('id');
CREATE TRIGGER protect_recovery_actions BEFORE UPDATE OR DELETE ON gk_private.recovery_actions FOR EACH ROW EXECUTE FUNCTION gk_private.reject_evidence_mutation();
CREATE TRIGGER protect_record_audit_events BEFORE UPDATE OR DELETE ON gk_private.record_audit_events FOR EACH ROW EXECUTE FUNCTION gk_private.reject_evidence_mutation();
COMMIT;
