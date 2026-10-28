"""Focused synthetic attendance safety tests; no external access."""
import unittest
from attendance_import import date_status,operational_projection
class AttendanceSafety(unittest.TestCase):
 def test_sanitized_date_never_becomes_verified(self):
  self.assertEqual(date_status('2025-06-01'),('SANITIZED_UNTRUSTED',None))
 def test_formula_and_missing_date(self):
  self.assertEqual(date_status('[FORMULA]'),('FORMULA_UNRESOLVED',None));self.assertEqual(date_status(None),('MISSING',None))
 def test_ambiguous_date_not_guessed(self):self.assertEqual(date_status('03/04/2025'),('UNPARSED',None))
 def base(self):return {'observation_kind':'MARK','identity_status':'VERIFIED','date_status':'VERIFIED','code_status':'VERIFIED','verified_child_id':'00000000-0000-4000-8000-000000000001','parsed_date':'2025-01-01','source_record_id':'00000000-0000-4000-8000-000000000002','source_column':'H','source_reference':'DEMO/T01/R2'}
 def test_name_candidate_cannot_project(self):
  r=self.base();r['identity_status']='PROVISIONAL_MATCH';self.assertIsNone(operational_projection(r,'DEMO','DEMO'))
 def test_all_gates_required(self):
  for field in ['date_status','code_status']:
   r=self.base();r[field]='PENDING';self.assertIsNone(operational_projection(r,'DEMO','DEMO'))
 def test_verified_projection_stable_and_has_lineage(self):
  r=self.base();a=operational_projection(r,'DEMO','DEMO');self.assertEqual(a,operational_projection(r,'DEMO','DEMO'));self.assertEqual([x['table'] for x in a],['attendance_observations','source_provenance']);self.assertEqual(a[0]['values']['review_state'],'pending')
if __name__=='__main__':unittest.main()
