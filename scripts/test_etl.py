"""Synthetic ETL safety contracts; no source records are included in tests."""
import copy
import unittest
from etl_core import stable_id,sql_value,validate_record,reconcile_rows,sanitized_recovery_overlay,compile_batch
from prepare_etl import SENSITIVE

class ETLContractTests(unittest.TestCase):
    def test_deterministic_ids_keep_business_identity_distinct(self):
        self.assertEqual(stable_id('child','001'),stable_id('child','001'))
        self.assertNotEqual(stable_id('child','001'),stable_id('child','1'))
        self.assertNotEqual(stable_id('child','A'),stable_id('child','a'))
    def test_no_membership_or_audit_forgery_targets(self):
        for name in ['access_memberships','record_audit_events']:
            with self.assertRaises(ValueError):validate_record({'table':name,'values':{}})
    def test_no_approved_or_active_reference_seed(self):
        v={'vocabulary':'access_role','code':'admin','active':False,'permissions':{},'origin_kind':'import','review_state':'pending'}
        with self.assertRaises(ValueError):validate_record({'table':'reference_values','values':v})
    def test_cannot_override_server_audit(self):
        v={'id':stable_id('x'),'child_business_id':'SYNTHETIC','origin_kind':'import','review_state':'pending','created_by':stable_id('user')}
        with self.assertRaises(ValueError):validate_record({'table':'children','values':v})
    def test_no_nan_boolean_or_fractional_integer(self):
        for value,typ in [(float('nan'),'numeric'),(float('inf'),'numeric'),(True,'numeric'),(1.5,'integer')]:
            with self.assertRaises(ValueError):sql_value(value,typ)
    def test_json_null_recovery_original_not_sql_null(self):
        self.assertEqual(sql_value(None,'jsonb','original_value'),"'null'::jsonb")
    def test_source_row_cannot_disappear_or_repeat(self):
        for ledger in [[],[{'reference':'a','status':'preserved_as_source_only'}]*2]:
            with self.assertRaises(ValueError):reconcile_rows(['a'],ledger)
    def test_reconciliation_never_equates_source_rows_with_facts(self):
        r=reconcile_rows(['a'],[{'reference':'a','status':'successfully_transformed'}]);self.assertEqual(r['source_rows'],1);self.assertEqual(r['loaded_remotely'],0)
    def test_recovery_only_from_sanitized_donor_without_source_mutation(self):
        rows={'t':{'cells':{'C':None}},'d':{'cells':{'A':'MASK_SYNTHETIC'}}}
        action={'target_reference':'t','source_reference':'d','source_column':'C','donor_column':'A','field_key':'display_name',
                'validation_status':'auto_recovered','identity_verified':True,'authoritative_source':True,'meaning_equivalent':True,'has_conflict':False,
                'original_value':None,'recovered_value':'DO NOT COPY RAW VALUE'}
        original=copy.deepcopy(rows);overlay,evidence=sanitized_recovery_overlay(rows,[action])
        self.assertEqual(overlay[('t','C')],'MASK_SYNTHETIC');self.assertEqual(rows,original);self.assertEqual(evidence[0]['recovered_value'],'MASK_SYNTHETIC')
    def test_date_recovery_is_suggested_until_fidelity_approval(self):
        rows={'t':{'cells':{'D':None}},'d':{'cells':{'D':'2001-01-01'}}}
        action={'target_reference':'t','source_reference':'d','source_column':'D','donor_column':'D','field_key':'birth_date','validation_status':'auto_recovered','identity_verified':True,'authoritative_source':True,'meaning_equivalent':True,'has_conflict':False}
        overlay,evidence=sanitized_recovery_overlay(rows,[action]);self.assertEqual(overlay,{});self.assertEqual(evidence[0]['validation_status'],'suggested')
    def test_conflicting_recovery_never_fills(self):
        rows={'t':{'cells':{'A':None}},'d':{'cells':{'A':'MASK_SYNTHETIC'}}}
        a={'target_reference':'t','source_reference':'d','source_column':'A','donor_column':'A','field_key':'display_name','validation_status':'auto_recovered','identity_verified':True,'authoritative_source':True,'meaning_equivalent':True,'has_conflict':True}
        overlay,evidence=sanitized_recovery_overlay(rows,[a]);self.assertEqual(overlay,{});self.assertEqual(evidence[0]['validation_status'],'blocked_conflict')
    def test_financial_masking_does_not_mask_feeling_question_scores(self):
        self.assertIsNotNone(SENSITIVE.search('MONTHLY FEES (P/M INR)'))
        self.assertIsNotNone(SENSITIVE.search('FAMILY INCOME'))
        self.assertIsNone(SENSITIVE.search('I feel emotionally supported by the team'))
if __name__=='__main__':unittest.main()
