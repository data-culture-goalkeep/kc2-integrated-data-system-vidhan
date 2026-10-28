-- Nonpersistent live denial probes. No users, memberships or role definitions are created.
BEGIN;
SET LOCAL statement_timeout='15s';
SET LOCAL lock_timeout='2s';
DO $validation$
DECLARE results jsonb := '[]'::jsonb; n bigint; original_role text := current_user; denied boolean;
BEGIN
 EXECUTE 'SET LOCAL ROLE anon';
 BEGIN
  EXECUTE 'SELECT count(*) FROM public.children' INTO n;
  results := results || jsonb_build_array(jsonb_build_object('check','anon_read_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege THEN
  results := results || jsonb_build_array(jsonb_build_object('check','anon_read_denied','passed',true,'sqlstate',SQLSTATE));
 END;
 EXECUTE format('SET LOCAL ROLE %I',original_role);
 PERFORM set_config('request.jwt.claims','{"role":"authenticated","sub":"00000000-0000-4000-8000-999999999999","email":"deployment-validation@goalkeep.net","app_metadata":{"provider":"google"},"amr":[{"method":"oauth"}]}',true);
 EXECUTE 'SET LOCAL ROLE authenticated';
 SELECT NOT gk_private.has_capability('read') AND NOT gk_private.has_capability('write')
  AND NOT gk_private.has_capability('read_private') AND NOT gk_private.has_capability('write_private')
  AND NOT gk_private.has_capability('manage_access') AND NOT gk_private.has_capability('soft_delete') INTO denied;
 results := results || jsonb_build_array(jsonb_build_object('check','unapproved_identity_no_capabilities','passed',denied));
 SELECT count(*) INTO n FROM public.children;
 results := results || jsonb_build_array(jsonb_build_object('check','unapproved_operational_read_zero','passed',n=0));
 SELECT count(*) INTO n FROM gk_private.child_private_profiles;
 results := results || jsonb_build_array(jsonb_build_object('check','restricted_child_profile_read_zero','passed',n=0));
 BEGIN
  -- One rollback-only write attempt is necessary to test runtime enforcement on an empty schema.
  -- Expected to fail before any row exists; the outer transaction always rolls back even if it succeeds.
  INSERT INTO public.children(child_business_id) VALUES ('DEPLOYMENT-VALIDATION-ROLLBACK-ONLY');
  results := results || jsonb_build_array(jsonb_build_object('check','unapproved_operational_insert_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege OR raise_exception THEN
  results := results || jsonb_build_array(jsonb_build_object('check','unapproved_operational_insert_denied','passed',true,'sqlstate',SQLSTATE,'reason',SQLERRM));
 END;
 BEGIN
  UPDATE gk_private.access_memberships SET active=active WHERE false;
  results := results || jsonb_build_array(jsonb_build_object('check','direct_membership_write_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege THEN
  results := results || jsonb_build_array(jsonb_build_object('check','direct_membership_write_denied','passed',true,'sqlstate',SQLSTATE));
 END;
 BEGIN
  PERFORM public.gk_manage_membership('00000000-0000-4000-8000-999999999999','admin',true,false,false,'NOT-AN-APPROVAL-VALIDATION-ONLY');
  results := results || jsonb_build_array(jsonb_build_object('check','privilege_escalation_rpc_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege OR raise_exception THEN
  results := results || jsonb_build_array(jsonb_build_object('check','privilege_escalation_rpc_denied','passed',true,'sqlstate',SQLSTATE,'reason',SQLERRM));
 END;
 BEGIN
  PERFORM public.gk_register_member();
  results := results || jsonb_build_array(jsonb_build_object('check','unapproved_registration_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege OR raise_exception THEN
  results := results || jsonb_build_array(jsonb_build_object('check','unapproved_registration_denied','passed',true,'sqlstate',SQLSTATE,'reason',SQLERRM));
 END;
 BEGIN
  DELETE FROM public.children WHERE false;
  results := results || jsonb_build_array(jsonb_build_object('check','authenticated_delete_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege THEN
  results := results || jsonb_build_array(jsonb_build_object('check','authenticated_delete_denied','passed',true,'sqlstate',SQLSTATE));
 END;
 BEGIN
  INSERT INTO gk_private.record_audit_events(schema_name,table_name,record_key,operation)
   SELECT 'public','children','{}'::jsonb,'UPDATE' WHERE false;
  results := results || jsonb_build_array(jsonb_build_object('check','audit_insert_privilege_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege THEN
  results := results || jsonb_build_array(jsonb_build_object('check','audit_insert_privilege_denied','passed',true,'sqlstate',SQLSTATE));
 END;
 BEGIN
  UPDATE gk_private.source_records SET processing_state=processing_state WHERE false;
  results := results || jsonb_build_array(jsonb_build_object('check','source_evidence_write_denied','passed',false));
 EXCEPTION WHEN insufficient_privilege THEN
  results := results || jsonb_build_array(jsonb_build_object('check','source_evidence_write_denied','passed',true,'sqlstate',SQLSTATE));
 END;
 EXECUTE format('SET LOCAL ROLE %I',original_role);
 PERFORM set_config('gk.deployment_validation_results',results::text,true);
END;
$validation$;
SELECT current_setting('gk.deployment_validation_results')::jsonb AS security_checks;
ROLLBACK;
