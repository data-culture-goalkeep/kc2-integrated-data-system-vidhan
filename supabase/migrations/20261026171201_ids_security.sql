-- PREPARED ONLY. Role matrix is DRAFT. No roles or memberships are seeded/activated.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';
GRANT USAGE ON SCHEMA gk_private TO authenticated, service_role;

CREATE FUNCTION gk_private.valid_permissions(p jsonb)
RETURNS boolean LANGUAGE sql IMMUTABLE SET search_path = pg_catalog AS $$
 SELECT CASE WHEN jsonb_typeof(p) IS DISTINCT FROM 'object' THEN false ELSE
 p - ARRAY['read','write','soft_delete','manage_access','review_data'] = '{}'::jsonb
 AND NOT EXISTS (SELECT 1 FROM jsonb_each(p) e WHERE jsonb_typeof(e.value) <> 'boolean') END;
$$;
REVOKE ALL ON FUNCTION gk_private.valid_permissions(jsonb) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION gk_private.valid_permissions(jsonb) TO service_role;
ALTER TABLE public.reference_values ADD CONSTRAINT ck_valid_role_permissions
 CHECK (gk_private.valid_permissions(permissions));

CREATE FUNCTION gk_private.is_goalkeep_identity(p_user uuid)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog AS $$
 SELECT EXISTS (
  SELECT 1 FROM auth.users u JOIN auth.identities i ON i.user_id = u.id
  WHERE u.id = p_user AND u.email_confirmed_at IS NOT NULL
   AND split_part(lower(u.email),'@',2) = 'goalkeep.net'
   AND i.provider = 'google'
   AND lower(i.identity_data ->> 'email') = lower(u.email)
   AND i.identity_data -> 'email_verified' = 'true'::jsonb
   AND lower(COALESCE(i.identity_data ->> 'hd', i.identity_data -> 'custom_claims' ->> 'hd')) = 'goalkeep.net'
 );
$$;
REVOKE ALL ON FUNCTION gk_private.is_goalkeep_identity(uuid) FROM PUBLIC, anon, authenticated;

CREATE FUNCTION gk_private.is_goalkeep_session()
RETURNS boolean LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE claims jsonb := auth.jwt();
BEGIN
 IF auth.uid() IS NULL OR claims ->> 'role' IS DISTINCT FROM 'authenticated' THEN RETURN false; END IF;
 IF claims -> 'app_metadata' ->> 'provider' IS DISTINCT FROM 'google' THEN RETURN false; END IF;
 IF split_part(lower(COALESCE(claims ->> 'email','')),'@',2) <> 'goalkeep.net' THEN RETURN false; END IF;
 IF jsonb_typeof(claims -> 'amr') IS DISTINCT FROM 'array' THEN RETURN false; END IF;
 IF NOT EXISTS (SELECT 1 FROM jsonb_array_elements(claims -> 'amr') a WHERE a ->> 'method' = 'oauth') THEN RETURN false; END IF;
 RETURN gk_private.is_goalkeep_identity(auth.uid());
END;
$$;
REVOKE ALL ON FUNCTION gk_private.is_goalkeep_session() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION gk_private.is_goalkeep_session() TO authenticated;

CREATE FUNCTION gk_private.has_capability(p_capability text)
RETURNS boolean LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE permitted boolean;
BEGIN
 IF NOT gk_private.is_goalkeep_session() THEN RETURN false; END IF;
 SELECT CASE p_capability
  WHEN 'read_private' THEN m.private_read AND r.permissions -> 'read' = 'true'::jsonb
  WHEN 'write_private' THEN m.private_read AND m.private_write AND r.permissions -> 'write' = 'true'::jsonb
  ELSE r.permissions -> p_capability = 'true'::jsonb END
 INTO permitted
 FROM gk_private.access_memberships m JOIN public.reference_values r
  ON r.vocabulary = m.role_vocabulary AND r.code = m.role_code
 WHERE m.user_id = auth.uid() AND m.approved_email_domain = 'goalkeep.net'
  AND m.active AND m.archived_at IS NULL AND m.approval_reference IS NOT NULL
  AND r.active AND r.archived_at IS NULL AND r.review_state = 'accepted' AND r.approval_reference IS NOT NULL;
 RETURN COALESCE(permitted,false);
END;
$$;
REVOKE ALL ON FUNCTION gk_private.has_capability(text) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION gk_private.has_capability(text) TO authenticated;

CREATE FUNCTION public.gk_register_member()
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE approved_ref text;
BEGIN
 IF NOT gk_private.is_goalkeep_session() THEN RAISE EXCEPTION 'Verified Goalkeep Workspace OAuth session required'; END IF;
 SELECT r.approval_reference INTO approved_ref FROM public.reference_values r
  WHERE r.vocabulary = 'access_role' AND r.code = 'member' AND r.active
   AND r.review_state = 'accepted' AND r.archived_at IS NULL AND r.approval_reference IS NOT NULL;
 IF approved_ref IS NULL THEN RAISE EXCEPTION 'Pilot role matrix not activated by project owner'; END IF;
 INSERT INTO gk_private.access_memberships(user_id,approved_email_domain,role_code,active,private_read,private_write,approval_reference)
 VALUES(auth.uid(),'goalkeep.net','member',true,false,false,approved_ref)
 ON CONFLICT(user_id) DO NOTHING;
 RETURN EXISTS(SELECT 1 FROM gk_private.access_memberships WHERE user_id = auth.uid() AND active AND archived_at IS NULL);
END;
$$;
REVOKE ALL ON FUNCTION public.gk_register_member() FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.gk_register_member() TO authenticated;

CREATE FUNCTION public.gk_manage_membership(p_user uuid,p_role text,p_active boolean,p_private_read boolean,p_private_write boolean,p_approval_reference text)
RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
BEGIN
 IF NOT gk_private.has_capability('manage_access') THEN RAISE EXCEPTION 'Access administration not authorized'; END IF;
 IF p_user = auth.uid() THEN RAISE EXCEPTION 'Self-role or private-access escalation is forbidden'; END IF;
 IF COALESCE(btrim(p_approval_reference),'') = '' THEN RAISE EXCEPTION 'Approval reference required'; END IF;
 -- Revocation must remain possible after identity or role eligibility is lost.
 IF p_active IS FALSE THEN
  UPDATE gk_private.access_memberships SET active=false,private_read=false,private_write=false,
   approval_reference=p_approval_reference WHERE user_id=p_user;
  RETURN;
 END IF;
 IF NOT gk_private.is_goalkeep_identity(p_user) THEN RAISE EXCEPTION 'Target identity is not verified Goalkeep Workspace'; END IF;
 IF p_private_write AND NOT p_private_read THEN RAISE EXCEPTION 'Private write requires private read authorization'; END IF;
 IF (p_private_read OR p_private_write) AND NOT gk_private.has_capability('write_private') THEN RAISE EXCEPTION 'Private authorization exceeds administrator scope'; END IF;
 IF NOT EXISTS(SELECT 1 FROM public.reference_values WHERE vocabulary='access_role' AND code=p_role AND active AND review_state='accepted' AND approval_reference IS NOT NULL AND archived_at IS NULL) THEN RAISE EXCEPTION 'Role not approved'; END IF;
 INSERT INTO gk_private.access_memberships(user_id,approved_email_domain,role_code,active,private_read,private_write,approval_reference)
 VALUES(p_user,'goalkeep.net',p_role,p_active,p_private_read,p_private_write,p_approval_reference)
 ON CONFLICT(user_id) DO UPDATE SET role_code=EXCLUDED.role_code,active=EXCLUDED.active,
  private_read=EXCLUDED.private_read,private_write=EXCLUDED.private_write,approval_reference=EXCLUDED.approval_reference;
END;
$$;
REVOKE ALL ON FUNCTION public.gk_manage_membership(uuid,text,boolean,boolean,boolean,text) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.gk_manage_membership(uuid,text,boolean,boolean,boolean,text) TO authenticated;

CREATE FUNCTION gk_private.stamp_audit()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog AS $$
DECLARE uid uuid := auth.uid(); is_domain boolean := TG_ARGV[0] = 'domain';
BEGIN
 IF TG_OP = 'INSERT' THEN
  NEW.created_at := now(); NEW.created_by := uid;
 ELSE
  NEW.created_at := OLD.created_at; NEW.created_by := OLD.created_by;
 END IF;
 NEW.updated_at := now(); NEW.updated_by := uid;
 IF auth.jwt() ->> 'role' = 'authenticated' THEN
  IF NOT gk_private.is_goalkeep_session() THEN RAISE EXCEPTION 'Workspace session required'; END IF;
  NEW.actor_ref := 'user:' || uid::text;
  IF is_domain THEN
   IF TG_OP = 'INSERT' AND NEW.origin_kind <> 'manual' THEN RAISE EXCEPTION 'Users cannot impersonate an import job'; END IF;
   IF TG_OP = 'UPDATE' THEN NEW.origin_kind := OLD.origin_kind; END IF;
   IF ((TG_OP = 'INSERT' AND NEW.review_state <> 'pending') OR (TG_OP = 'UPDATE' AND NEW.review_state IS DISTINCT FROM OLD.review_state)) AND NOT gk_private.has_capability('review_data') THEN RAISE EXCEPTION 'Review authorization required'; END IF;
  END IF;
 ELSE
  IF auth.jwt() ->> 'role' IS DISTINCT FROM 'service_role' AND session_user NOT IN ('postgres','supabase_admin') THEN RAISE EXCEPTION 'Unidentified database actor'; END IF;
  NEW.actor_ref := 'db:' || session_user || '/role:' || COALESCE(auth.jwt() ->> 'role','database_owner');
 END IF;
 IF TG_ARGV[1] = 'archive' THEN
  IF TG_OP = 'UPDATE' AND NEW.archived_at IS DISTINCT FROM OLD.archived_at THEN
   IF auth.jwt() ->> 'role'='authenticated' AND NOT gk_private.has_capability('soft_delete') THEN RAISE EXCEPTION 'Soft deletion not authorized'; END IF;
   IF NEW.archived_at IS NULL THEN NEW.archived_by := NULL;
   ELSE
    IF uid IS NULL THEN RAISE EXCEPTION 'Soft deletion requires an authenticated accountable user'; END IF;
    NEW.archived_at := now(); NEW.archived_by := uid;
   END IF;
  ELSIF TG_OP='INSERT' AND NEW.archived_at IS NOT NULL THEN RAISE EXCEPTION 'Cannot create an already archived record';
  ELSIF TG_OP='UPDATE' THEN NEW.archived_by := OLD.archived_by;
  END IF;
 END IF;
 RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION gk_private.stamp_audit() FROM PUBLIC, anon, authenticated;
-- GENERATED TABLE POLICIES
CREATE TRIGGER audit_reference_values BEFORE INSERT OR UPDATE ON public.reference_values FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.reference_values TO service_role;
GRANT SELECT ON public.reference_values TO authenticated;
CREATE POLICY read_reference_values ON public.reference_values FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND archived_at IS NULL AND (active OR gk_private.has_capability('review_data')) AND (review_state='accepted' OR gk_private.has_capability('review_data')) AND (vocabulary <> 'access_role' OR gk_private.has_capability('manage_access')));
CREATE TRIGGER audit_children BEFORE INSERT OR UPDATE ON public.children FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.children TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.children TO authenticated;
CREATE POLICY select_children ON public.children FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_children ON public.children FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_children ON public.children FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_child_private_profiles BEFORE INSERT OR UPDATE ON gk_private.child_private_profiles FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE gk_private.child_private_profiles TO service_role;
GRANT SELECT, INSERT, UPDATE ON gk_private.child_private_profiles TO authenticated;
CREATE POLICY select_child_private_profiles ON gk_private.child_private_profiles FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_child_private_profiles ON gk_private.child_private_profiles FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write_private') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_child_private_profiles ON gk_private.child_private_profiles FOR UPDATE TO authenticated USING (gk_private.has_capability('write_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_caregivers BEFORE INSERT OR UPDATE ON gk_private.caregivers FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE gk_private.caregivers TO service_role;
GRANT SELECT, INSERT, UPDATE ON gk_private.caregivers TO authenticated;
CREATE POLICY select_caregivers ON gk_private.caregivers FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_caregivers ON gk_private.caregivers FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write_private') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_caregivers ON gk_private.caregivers FOR UPDATE TO authenticated USING (gk_private.has_capability('write_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_child_caregivers BEFORE INSERT OR UPDATE ON public.child_caregivers FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.child_caregivers TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.child_caregivers TO authenticated;
CREATE POLICY select_child_caregivers ON public.child_caregivers FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_child_caregivers ON public.child_caregivers FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_child_caregivers ON public.child_caregivers FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_program_changes BEFORE INSERT OR UPDATE ON public.program_changes FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.program_changes TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.program_changes TO authenticated;
CREATE POLICY select_program_changes ON public.program_changes FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_program_changes ON public.program_changes FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_program_changes ON public.program_changes FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_questionnaire_responses BEFORE INSERT OR UPDATE ON public.questionnaire_responses FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.questionnaire_responses TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.questionnaire_responses TO authenticated;
CREATE POLICY select_questionnaire_responses ON public.questionnaire_responses FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_questionnaire_responses ON public.questionnaire_responses FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_questionnaire_responses ON public.questionnaire_responses FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_questionnaire_items BEFORE INSERT OR UPDATE ON public.questionnaire_items FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.questionnaire_items TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.questionnaire_items TO authenticated;
CREATE POLICY select_questionnaire_items ON public.questionnaire_items FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_questionnaire_items ON public.questionnaire_items FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND gk_private.has_capability('review_data') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_questionnaire_items ON public.questionnaire_items FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND gk_private.has_capability('review_data') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND gk_private.has_capability('review_data') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_questionnaire_answers BEFORE INSERT OR UPDATE ON gk_private.questionnaire_answers FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE gk_private.questionnaire_answers TO service_role;
GRANT SELECT, INSERT, UPDATE ON gk_private.questionnaire_answers TO authenticated;
CREATE POLICY select_questionnaire_answers ON gk_private.questionnaire_answers FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_questionnaire_answers ON gk_private.questionnaire_answers FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write_private') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_questionnaire_answers ON gk_private.questionnaire_answers FOR UPDATE TO authenticated USING (gk_private.has_capability('write_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write_private') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_attendance_observations BEFORE INSERT OR UPDATE ON public.attendance_observations FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.attendance_observations TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.attendance_observations TO authenticated;
CREATE POLICY select_attendance_observations ON public.attendance_observations FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_attendance_observations ON public.attendance_observations FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_attendance_observations ON public.attendance_observations FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_support_observations BEFORE INSERT OR UPDATE ON public.support_observations FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.support_observations TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.support_observations TO authenticated;
CREATE POLICY select_support_observations ON public.support_observations FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_support_observations ON public.support_observations FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_support_observations ON public.support_observations FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_adl_visits BEFORE INSERT OR UPDATE ON public.adl_visits FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('domain','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE public.adl_visits TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.adl_visits TO authenticated;
CREATE POLICY select_adl_visits ON public.adl_visits FOR SELECT TO authenticated USING (gk_private.has_capability('read') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')) AND (review_state='accepted' OR created_by=auth.uid() OR gk_private.has_capability('review_data')));
CREATE POLICY insert_adl_visits ON public.adl_visits FOR INSERT TO authenticated WITH CHECK (gk_private.has_capability('write') AND origin_kind='manual' AND archived_at IS NULL);
CREATE POLICY update_adl_visits ON public.adl_visits FOR UPDATE TO authenticated USING (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete'))) WITH CHECK (gk_private.has_capability('write') AND (archived_at IS NULL OR gk_private.has_capability('soft_delete')));
CREATE TRIGGER audit_source_artifacts BEFORE INSERT OR UPDATE ON gk_private.source_artifacts FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('technical','none');
GRANT SELECT, INSERT ON TABLE gk_private.source_artifacts TO service_role;
GRANT SELECT ON gk_private.source_artifacts TO authenticated;
CREATE POLICY review_source_artifacts ON gk_private.source_artifacts FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));
CREATE TRIGGER audit_source_records BEFORE INSERT OR UPDATE ON gk_private.source_records FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('technical','none');
GRANT SELECT, INSERT, UPDATE ON TABLE gk_private.source_records TO service_role;
GRANT SELECT ON gk_private.source_records TO authenticated;
CREATE POLICY review_source_records ON gk_private.source_records FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));
CREATE TRIGGER audit_source_provenance BEFORE INSERT OR UPDATE ON gk_private.source_provenance FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('technical','none');
GRANT SELECT, INSERT ON TABLE gk_private.source_provenance TO service_role;
GRANT SELECT ON gk_private.source_provenance TO authenticated;
CREATE POLICY review_source_provenance ON gk_private.source_provenance FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));
CREATE TRIGGER audit_access_memberships BEFORE INSERT OR UPDATE ON gk_private.access_memberships FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('technical','archive');
GRANT SELECT, INSERT, UPDATE ON TABLE gk_private.access_memberships TO service_role;
CREATE TRIGGER audit_identity_candidates BEFORE INSERT OR UPDATE ON gk_private.identity_candidates FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('technical','none');
GRANT SELECT, INSERT, UPDATE ON TABLE gk_private.identity_candidates TO service_role;
GRANT SELECT ON gk_private.identity_candidates TO authenticated;
CREATE POLICY review_identity_candidates ON gk_private.identity_candidates FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));
CREATE TRIGGER audit_recovery_actions BEFORE INSERT OR UPDATE ON gk_private.recovery_actions FOR EACH ROW EXECUTE FUNCTION gk_private.stamp_audit('technical','none');
GRANT SELECT, INSERT ON TABLE gk_private.recovery_actions TO service_role;
GRANT SELECT ON gk_private.recovery_actions TO authenticated;
CREATE POLICY review_recovery_actions ON gk_private.recovery_actions FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));
GRANT SELECT ON gk_private.record_audit_events TO service_role, authenticated;
CREATE POLICY review_audit ON gk_private.record_audit_events FOR SELECT TO authenticated USING (gk_private.has_capability('read_private') AND gk_private.has_capability('review_data'));
COMMIT;
