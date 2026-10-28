"""Synthetic database tests; invoked only by scripts/run_postgres_tests.py in its own local container."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = None

def uid(n):
    return f'00000000-0000-4000-8000-{n:012d}'

def session(user=2, role='authenticated', **overrides):
    claims = {'sub': uid(user), 'role': role, 'email': f'synthetic{user}@goalkeep.net',
              'app_metadata': {'provider': 'google'}, 'amr': [{'method': 'oauth'}]}
    claims.update(overrides)
    text = json.dumps(claims).replace("'", "''")
    return f"SET LOCAL ROLE {role}; SET LOCAL request.jwt.claims = '{text}';"

FIXTURES = '''
INSERT INTO auth.users(id,email,email_confirmed_at)
SELECT ('00000000-0000-4000-8000-'||lpad(n::text,12,'0'))::uuid, 'synthetic'||n||'@goalkeep.net',now()
FROM generate_series(1,7) n;
INSERT INTO auth.identities(user_id,provider,identity_data)
SELECT id,'google',jsonb_build_object('email',email,'email_verified',true,'hd','goalkeep.net') FROM auth.users;
INSERT INTO public.reference_values(vocabulary,code,label,active,review_state,approval_reference,permissions) VALUES
('access_role','admin','Synthetic administrator',true,'accepted','SYNTHETIC-TEST-ONLY','{"read":true,"write":true,"manage_access":true,"soft_delete":true,"review_data":true}'),
('access_role','member','Synthetic member',true,'accepted','SYNTHETIC-TEST-ONLY','{"read":true,"write":true}'),
('questionnaire_definition','synthetic','Synthetic definition',true,'accepted','SYNTHETIC-TEST-ONLY','{}');
INSERT INTO gk_private.access_memberships(user_id,approved_email_domain,role_code,active,private_read,private_write,approval_reference) VALUES
('00000000-0000-4000-8000-000000000001','goalkeep.net','admin',true,true,true,'SYNTHETIC-TEST-ONLY'),
('00000000-0000-4000-8000-000000000002','goalkeep.net','member',true,false,false,'SYNTHETIC-TEST-ONLY');
INSERT INTO public.children(id,child_business_id,display_name,review_state,joining_date)
VALUES('00000000-0000-4000-8000-000000000100','SYNTHETIC-001','Synthetic child','accepted','2020-01-01');
INSERT INTO gk_private.child_private_profiles(child_id,birth_date,review_state)
VALUES('00000000-0000-4000-8000-000000000100','2015-01-01','accepted');
'''

class AUnactivatedPolicyTests(unittest.TestCase):
    def test_empty_schema_has_no_roles_or_memberships(self):
        self.assertEqual(DB.execute('SELECT (SELECT count(*) FROM public.reference_values)+(SELECT count(*) FROM gk_private.access_memberships)'), '0')

    def test_self_registration_fails_before_role_activation(self):
        sql = "BEGIN; INSERT INTO auth.users VALUES ('"+uid(8)+"','synthetic8@goalkeep.net',now()); INSERT INTO auth.identities(user_id,provider,identity_data) VALUES ('"+uid(8)+"','google','{\"email\":\"synthetic8@goalkeep.net\",\"email_verified\":true,\"hd\":\"goalkeep.net\"}');"+session(8)+"SELECT public.gk_register_member();ROLLBACK;"
        result=DB.sql(sql);self.assertNotEqual(result.returncode,0);self.assertIn('Pilot role matrix not activated',result.stderr)

class DatabaseReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fixtures activate roles only inside the throwaway database, never in migrations.
        DB.execute('BEGIN;'+FIXTURES+'COMMIT;')

    def check_sql(self, body, expected=None, fail_code=None, actor=2, **claims):
        result = DB.sql('BEGIN;'+session(actor, **claims)+body+';ROLLBACK;')
        if fail_code:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(fail_code, result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)
            if expected is not None:
                self.assertEqual(result.stdout.strip(), str(expected))
        return result

    def test_all_19_tables_have_rls(self):
        self.assertEqual(DB.execute("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','gk_private') AND c.relkind='r' AND c.relrowsecurity"), '19')

    def test_unauthenticated_has_no_table_access(self):
        self.check_sql('SELECT * FROM public.children', role='anon', fail_code='42501')

    def test_eligible_nonmember_has_no_operational_rows(self):
        self.check_sql('SELECT count(*) FROM public.children', actor=3, expected=0)

    def test_member_reads_operational_rows(self):
        self.check_sql('SELECT count(*) FROM public.children', expected=1)

    def test_member_cannot_read_restricted_profile(self):
        self.check_sql('SELECT count(*) FROM gk_private.child_private_profiles', expected=0)

    def test_member_can_create_and_update_own_record(self):
        self.check_sql("INSERT INTO public.children(child_business_id,display_name) VALUES('SYNTHETIC-NEW','Synthetic new'); UPDATE public.children SET display_name='Synthetic edit' WHERE child_business_id='SYNTHETIC-NEW'; SELECT count(*) FROM public.children WHERE display_name='Synthetic edit'", expected=1)

    def test_member_cannot_create_definition_items(self):
        self.check_sql("INSERT INTO public.questionnaire_items(definition_key,item_key,prompt,value_kind,ordinal) VALUES('synthetic','unauthorized','Synthetic injected question','numeric',99)", fail_code='42501')

    def test_member_cannot_accept_records(self):
        self.check_sql("UPDATE public.children SET review_state='needs_review'", fail_code='P0001')

    def test_member_cannot_soft_delete(self):
        self.check_sql("UPDATE public.children SET archived_at=now()", fail_code='P0001')

    def test_member_cannot_permanently_delete(self):
        self.check_sql('DELETE FROM public.children', fail_code='42501')

    def test_admin_with_private_grant_reads_profile(self):
        self.check_sql('SELECT count(*) FROM gk_private.child_private_profiles', actor=1, expected=1)

    def test_admin_can_soft_delete_and_restore(self):
        self.check_sql("UPDATE public.children SET archived_at=now(); UPDATE public.children SET archived_at=NULL; SELECT count(*) FROM public.children WHERE archived_at IS NULL", actor=1, expected=1)

    def test_member_cannot_manage_roles(self):
        self.check_sql(f"SELECT public.gk_manage_membership('{uid(3)}','admin',true,false,false,'SYNTHETIC')", fail_code='P0001')

    def test_admin_cannot_self_escalate(self):
        self.check_sql(f"SELECT public.gk_manage_membership('{uid(1)}','admin',true,true,true,'SYNTHETIC')", actor=1, fail_code='P0001')

    def test_admin_can_assign_approved_member(self):
        self.check_sql(f"SELECT public.gk_manage_membership('{uid(3)}','member',true,false,false,'SYNTHETIC')", actor=1)

    def test_direct_membership_write_denied(self):
        self.check_sql('UPDATE gk_private.access_memberships SET private_read=true', fail_code='42501')

    def test_password_session_denied(self):
        self.check_sql('SELECT count(*) FROM public.children', expected=0, amr=[{'method':'password'}])

    def test_wrong_domain_denied(self):
        self.check_sql('SELECT count(*) FROM public.children', expected=0, email='synthetic@example.invalid')

    def test_workspace_claim_missing_denied(self):
        result = DB.sql("BEGIN; UPDATE auth.identities SET identity_data=identity_data-'hd' WHERE user_id='"+uid(2)+"';"+session()+"SELECT count(*) FROM public.children;ROLLBACK;")
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'0')

    def test_actor_fields_are_server_stamped(self):
        self.check_sql(f"INSERT INTO public.children(child_business_id,created_by,updated_by,actor_ref) VALUES('SYNTHETIC-AUDIT','{uid(1)}','{uid(1)}','forged'); SELECT created_by='{uid(2)}'::uuid AND updated_by='{uid(2)}'::uuid AND actor_ref='user:{uid(2)}' FROM public.children WHERE child_business_id='SYNTHETIC-AUDIT'", expected='t')

    def test_private_audit_cannot_be_forged_or_mutated(self):
        self.check_sql("INSERT INTO gk_private.record_audit_events(schema_name,table_name,record_key,operation) VALUES('public','children','{}','UPDATE')", actor=1, fail_code='42501')
        r=DB.sql('BEGIN; UPDATE gk_private.record_audit_events SET operation=\'forged\'; ROLLBACK;');self.assertNotEqual(r.returncode,0);self.assertIn('P0001',r.stderr)

    def test_birth_after_joining_rejected_on_constraint_flush(self):
        self.check_sql("UPDATE gk_private.child_private_profiles SET birth_date='2021-01-01'; SET CONSTRAINTS ALL IMMEDIATE", actor=1, fail_code='P0001')

    def test_duplicate_literal_child_id_rejected(self):
        self.check_sql("INSERT INTO public.children(child_business_id) VALUES('SYNTHETIC-001')", fail_code='23505')

    def test_identity_change_rejected(self):
        self.check_sql("UPDATE public.children SET child_business_id='SYNTHETIC-CHANGED'", actor=1, fail_code='P0001')

    def test_import_requires_provenance(self):
        r=DB.sql("BEGIN; INSERT INTO public.children(child_business_id,origin_kind) VALUES('SYNTHETIC-IMPORT','import');SET CONSTRAINTS ALL IMMEDIATE;ROLLBACK;")
        self.assertNotEqual(r.returncode,0);self.assertIn('Imported target requires source provenance',r.stderr)

    def test_bad_foreign_key_rejected(self):
        self.check_sql(f"INSERT INTO public.child_caregivers(child_id,caregiver_id) VALUES('{uid(100)}','{uid(999)}')",fail_code='23503')

    def test_manual_adl_without_date_rejected(self):
        self.check_sql(f"INSERT INTO public.adl_visits(child_id,visit_flag) VALUES('{uid(100)}',true)",fail_code='23514')

    def test_audit_history_created(self):
        self.check_sql("UPDATE public.children SET display_name='Synthetic audit'; SELECT count(*)>0 FROM gk_private.record_audit_events WHERE table_name='children' AND operation='UPDATE'",actor=1,expected='t')


    def test_service_role_has_no_delete_or_truncate_privileges(self):
        # Supabase public defaults initially grant ALL. A narrower GRANT alone cannot remove it.
        result=DB.execute("SELECT bool_or(has_table_privilege('service_role',c.oid,'DELETE') OR has_table_privilege('service_role',c.oid,'TRUNCATE')) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','gk_private') AND c.relkind='r'")
        self.assertEqual(result,'f')

    def test_service_role_cannot_truncate_evidence(self):
        self.check_sql('TRUNCATE gk_private.source_provenance', role='service_role', fail_code='42501')

    def test_immutable_tables_have_truncate_guard(self):
        result=DB.sql('BEGIN; TRUNCATE gk_private.source_provenance; ROLLBACK;')
        self.assertNotEqual(result.returncode,0);self.assertIn('Evidence is append-only',result.stderr)

    def test_admin_can_create_definition_item(self):
        self.check_sql("INSERT INTO public.questionnaire_items(definition_key,item_key,prompt,value_kind,ordinal) VALUES('synthetic','authorized','Synthetic approved question','numeric',98)",actor=1)

    def test_backend_actor_cannot_impersonate_a_person(self):
        result=DB.execute("BEGIN; INSERT INTO public.children(child_business_id,actor_ref) VALUES('SYNTHETIC-SERVICE','user:forged'); SELECT actor_ref LIKE 'db:%' FROM public.children WHERE child_business_id='SYNTHETIC-SERVICE'; ROLLBACK;")
        self.assertEqual(result,'t')

    def source_setup(self):
        return f"INSERT INTO gk_private.source_artifacts(id,source_namespace,file_code,version_sha256) VALUES('{uid(200)}','SYNTHETIC','SYNTHETIC',repeat('a',64)); INSERT INTO gk_private.source_records(id,artifact_id,native_sheet_key,source_row,cell_payload) VALUES('{uid(201)}','{uid(200)}','T01',2,'{{\"A\":\"Synthetic\"}}');"

    def test_import_with_valid_provenance_succeeds(self):
        sql=self.source_setup()+f"INSERT INTO public.children(id,child_business_id,origin_kind) VALUES('{uid(202)}','SYNTHETIC-IMPORT','import'); INSERT INTO gk_private.source_provenance(source_record_id,source_columns,target_fields,rule_reference,contribution_state,child_id) VALUES('{uid(201)}',ARRAY['A'],ARRAY['child_business_id'],'SYNTHETIC-MAPPING','selected','{uid(202)}'); SET CONSTRAINTS ALL IMMEDIATE;"
        self.assertEqual(DB.sql('BEGIN;'+sql+'ROLLBACK;').returncode,0)

    def test_blank_or_null_lineage_columns_rejected(self):
        for columns in ["ARRAY[NULL]::text[]", "ARRAY[' ']", "ARRAY[E'\\t']"]:
            sql=self.source_setup()+f"INSERT INTO gk_private.source_provenance(source_record_id,source_columns,target_fields,rule_reference,contribution_state,child_id) VALUES('{uid(201)}',{columns},ARRAY['child_business_id'],'SYNTHETIC','selected','{uid(100)}');"
            result=DB.sql('BEGIN;'+sql+'ROLLBACK;');self.assertNotEqual(result.returncode,0);self.assertIn('23514',result.stderr)

    def test_original_payload_cannot_be_rewritten(self):
        result=DB.sql('BEGIN;'+self.source_setup()+"UPDATE gk_private.source_records SET cell_payload='{}';ROLLBACK;")
        self.assertNotEqual(result.returncode,0);self.assertIn('immutable',result.stderr)

    def test_duplicate_source_coordinates_rejected(self):
        result=DB.sql('BEGIN;'+self.source_setup()+f"INSERT INTO gk_private.source_records(artifact_id,native_sheet_key,source_row) VALUES('{uid(200)}','T01',2);ROLLBACK;")
        self.assertNotEqual(result.returncode,0);self.assertIn('23505',result.stderr)

    def test_name_only_candidate_cannot_be_verified(self):
        result=DB.sql('BEGIN;'+self.source_setup()+f"INSERT INTO gk_private.identity_candidates(source_record_id,child_id,match_method,resolution_status) VALUES('{uid(201)}','{uid(100)}','name_candidate','verified');ROLLBACK;")
        self.assertNotEqual(result.returncode,0);self.assertIn('23514',result.stderr)

    def test_automatic_recovery_requires_all_verification_flags(self):
        result=DB.sql('BEGIN;'+self.source_setup()+f"INSERT INTO gk_private.recovery_actions(source_record_id,source_column,field_key,original_value,recovered_value,method,validation_status,run_id) VALUES('{uid(201)}','A','display_name','null','\"Synthetic\"','synthetic','auto_recovered','{uid(900)}');ROLLBACK;")
        self.assertNotEqual(result.returncode,0);self.assertIn('23514',result.stderr)

    def test_revocation_does_not_require_target_still_eligible(self):
        sql=f"BEGIN; UPDATE auth.identities SET identity_data=identity_data-'hd' WHERE user_id='{uid(2)}';"+session(1)+f"SELECT public.gk_manage_membership('{uid(2)}','member',false,false,false,'SYNTHETIC-REVOKE');RESET ROLE;SELECT active FROM gk_private.access_memberships WHERE user_id='{uid(2)}';ROLLBACK;"
        result=DB.sql(sql);self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'f')

    def test_private_grant_revocation_is_immediate(self):
        sql=f"BEGIN; UPDATE gk_private.access_memberships SET private_read=false,private_write=false WHERE user_id='{uid(1)}';"+session(1)+"SELECT count(*) FROM gk_private.child_private_profiles;ROLLBACK;"
        result=DB.sql(sql);self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'0')

    def test_inactive_membership_denied_without_jwt_refresh(self):
        sql=f"BEGIN; UPDATE gk_private.access_memberships SET active=false WHERE user_id='{uid(2)}';"+session()+"SELECT count(*) FROM public.children;ROLLBACK;"
        result=DB.sql(sql);self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'0')

    def test_second_fresh_database_replay_and_atomic_failure(self):
        DB.execute('CREATE DATABASE gk_review_replay')
        bootstrap=(ROOT/'tests/sql/local-auth-bootstrap.sql').read_text()
        bootstrap='\n'.join(line for line in bootstrap.splitlines() if not line.startswith('CREATE ROLE'))
        DB.execute(bootstrap,'gk_review_replay')
        migrations=sorted((ROOT/'supabase/migrations').glob('*.sql'))
        wrong=DB.sql(migrations[1].read_text(),'gk_review_replay')
        self.assertNotEqual(wrong.returncode,0)
        broken=DB.sql(migrations[0].read_text().replace('COMMIT;','SELECT 1/0; COMMIT;'),'gk_review_replay')
        self.assertNotEqual(broken.returncode,0);self.assertIn('22012',broken.stderr)
        self.assertEqual(DB.execute("SELECT count(*) FROM pg_namespace WHERE nspname='gk_private'",'gk_review_replay'),'0')
        for path in migrations:DB.execute(path.read_text(),'gk_review_replay')
        self.assertEqual(DB.execute("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','gk_private') AND c.relkind='r'",'gk_review_replay'),'19')

    def test_repeat_schema_fails_without_partial_changes(self):
        schema=(ROOT/'supabase/migrations/20261026171200_ids_schema.sql').read_text()
        result=DB.sql(schema);self.assertNotEqual(result.returncode,0);self.assertIn('42P06',result.stderr)
        self.assertEqual(DB.execute("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','gk_private') AND c.relkind='r'"),'19')
