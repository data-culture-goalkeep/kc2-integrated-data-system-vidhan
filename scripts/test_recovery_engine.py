import unittest
from recovery_engine import *
class RecoveryTests(unittest.TestCase):
 def row(self,ref,value,authority=False):return {'reference':ref,'business_id':'001','entity_kind':'child','identifier_literal':True,'fields':{'name':value},'equivalent_fields':['name'],'authoritative_fields':['name'] if authority else []}
 def plan(self,rows):return plan_recovery(rows,{'child':{'001':{}}},{'child':{'name':'text'}})
 def test_exact_ids(self):
  self.assertEqual(exact_id('001'),'001');self.assertIsNone(exact_id(1));self.assertIsNone(exact_id(' 001'));self.assertNotEqual(exact_id('a'),exact_id('A'))
 def test_duplicate_authority_is_reported(self):
  _,issues=verified_registry([{'business_id':'001','reference':'a'},{'business_id':'001','reference':'b'}]);self.assertEqual(len(issues),1)
 def test_safe_recovery_and_no_mutation(self):
  rows=[self.row('a','Synthetic Name',True),self.row('b',None)];a=self.plan(rows)[0];self.assertEqual(a['validation_status'],'auto_recovered');self.assertIsNone(rows[1]['fields']['name']);self.assertEqual(a['source_reference'],'a')
 def test_conflicting_secondary_blocks(self):
  a=self.plan([self.row('a','Synthetic A',True),self.row('b','Synthetic B'),self.row('c',None)])[0];self.assertEqual(a['validation_status'],'blocked_conflict')
 def test_untrusted_donor(self):self.assertEqual(self.plan([self.row('a','Synthetic'),self.row('b',None)])[0]['validation_status'],'blocked_untrusted')
 def test_non_equivalent_field(self):
  r=self.row('a','Synthetic',True);r['equivalent_fields']=[];self.assertEqual(self.plan([r,self.row('b',None)]),[])
 def test_computed_id_cannot_recover(self):
  r=self.row('a','Synthetic',True);r['identifier_literal']=False;self.assertEqual(self.plan([r,self.row('b',None)]),[])
 def test_ambiguous_or_invalid_date(self):
  self.assertEqual(parse_date('03/04/2025')['status'],'ambiguous_day_month');self.assertEqual(parse_date('2025-02-30')['status'],'invalid');self.assertEqual(parse_date('03/04/2025','DD/MM/YYYY')['value'],'2025-04-03')
 def test_name_alias_is_not_verified(self):
  reg={'001':{'reference':'master','fields':{'display_name':'Synthetic A'}}};out=identity_candidates({'name':'Synthetic B'},reg,{'001':[{'name':'Synthetic B','reference':'pair'}]});self.assertEqual(out[0]['status'],'candidate')
 def test_literal_vs_computed_candidate(self):
  reg={'001':{'reference':'a','fields':{}}}
  self.assertEqual(identity_candidates({'business_id':'001','identifier_literal':True},reg)[0]['status'],'verified');self.assertEqual(identity_candidates({'business_id':'001'},reg)[0]['status'],'candidate')
 def test_reconciliation_failures(self):
  self.assertFalse(reconcile(['a','b'],[{'source_reference':'a','status':'ready'},{'source_reference':'a','status':'ready'},{'source_reference':'c','status':'bad'}])['ok'])
 def test_reconciliation_retention_is_not_import(self):
  r=reconcile(['a'],[{'source_reference':'a','status':'reference_only'}]);self.assertTrue(r['ok']);self.assertEqual(r['proposed_observations'],0)
if __name__=='__main__':unittest.main()
