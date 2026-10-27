"""Adversarial synthetic ETL cases, run after the full sanitized load/replay in a local throwaway DB."""
import json
import unittest
from etl_core import stable_id,compile_batch
from etl_loader import load_plan,count_tables
DB=None

class ETLRuntimeTests(unittest.TestCase):
    def row(self,table,values):return {'table':table,'values':values,'source_refs':['SYNTHETIC/T01/R2']}
    def artifact(self,tag):return self.row('source_artifacts',{'id':stable_id('test-artifact',tag),'source_namespace':'SYNTHETIC','file_code':tag,'version_sha256':'a'*64,'worksheet_manifest':{}})
    def test_invalid_fk_rejected_and_transaction_rolled_back(self):
        a=self.artifact('fk-rollback');r=self.row('source_records',{'id':stable_id('bad-source'),'artifact_id':stable_id('absent-artifact'),'native_sheet_key':'T01','source_row':2,'cell_payload':{}})
        result=DB.sql(compile_batch([a,r]));self.assertNotEqual(result.returncode,0);self.assertIn('23503',result.stderr)
        self.assertEqual(DB.execute("SELECT count(*) FROM gk_private.source_artifacts WHERE source_namespace='SYNTHETIC' AND file_code='fk-rollback'"),'0')
    def test_partial_batch_failure_preserves_only_prior_commits(self):
        a=self.artifact('partial-commit');r=self.row('source_records',{'id':stable_id('partial-bad'),'artifact_id':a['values']['id'],'native_sheet_key':'T01','source_row':0,'cell_payload':{}})
        receipt=load_plan(DB,{'units':[[a],[r]],'source_statuses':[]},batch_size=1)
        self.assertEqual(receipt['status'],'failed');self.assertEqual(receipt['committed_batches'],1);self.assertEqual(receipt['failures'][0]['sqlstate'],'23514')
        self.assertEqual(DB.execute("SELECT count(*) FROM gk_private.source_artifacts WHERE file_code='partial-commit'"),'1')
        self.assertEqual(DB.execute("SELECT count(*) FROM gk_private.source_records WHERE id='"+r['values']['id']+"'"),'0')
    def test_changed_immutable_payload_is_not_silently_skipped(self):
        a=self.artifact('payload-conflict');self.assertEqual(DB.sql(compile_batch([a])).returncode,0)
        a['values']['worksheet_manifest']={'changed':True};result=DB.sql(compile_batch([a]))
        self.assertNotEqual(result.returncode,0);self.assertIn('ETL_EXISTING_PAYLOAD_CONFLICT',result.stderr)
    def test_sql_text_roundtrip_cannot_inject(self):
        a=self.artifact('safe-text');a['values']['source_locator']="quote ' ; DROP TABLE public.children; -- \\ backslash $$"
        self.assertEqual(DB.sql(compile_batch([a])).returncode,0)
        q="SELECT source_locator FROM gk_private.source_artifacts WHERE id='"+a['values']['id']+"'"
        self.assertEqual(DB.execute(q),a['values']['source_locator']);self.assertEqual(DB.execute('SELECT count(*) FROM public.children'),'371')
    def test_unmatched_and_missing_date_categories_not_loaded(self):
        for table in ['attendance_observations','adl_visits','support_observations']:
            self.assertEqual(DB.execute('SELECT count(*) FROM public.'+table),'0')
    def test_questionnaire_conflicts_do_not_replace_master_names(self):
        from pathlib import Path
        from etl_core import ROOT
        plan=json.loads((ROOT/'work/etl/plan.json').read_text())
        for u in plan['units']:
            for r in u:
                if r['table']=='children':
                    value=DB.execute("SELECT display_name FROM public.children WHERE id='"+r['values']['id']+"'")
                    self.assertEqual(value,r['values']['display_name'])
    def test_every_imported_child_has_source_lineage(self):
        self.assertEqual(DB.execute('SELECT count(*) FROM public.children c WHERE NOT EXISTS(SELECT 1 FROM gk_private.source_provenance p WHERE p.child_id=c.id)'),'0')
    def test_missing_answers_remain_missing_not_zero(self):
        self.assertEqual(DB.execute("SELECT count(*) FROM gk_private.questionnaire_answers a JOIN public.questionnaire_items i ON i.id=a.item_id WHERE i.value_kind='numeric' AND a.answer_state='missing' AND a.numeric_value IS NULL"),'86')
    def test_no_roles_or_memberships_activated(self):
        self.assertEqual(DB.execute("SELECT (SELECT count(*) FROM public.reference_values WHERE vocabulary='access_role')+(SELECT count(*) FROM gk_private.access_memberships)"),'0')
        self.assertEqual(DB.execute("SELECT count(*) FROM public.reference_values WHERE active OR review_state='accepted'"),'0')
