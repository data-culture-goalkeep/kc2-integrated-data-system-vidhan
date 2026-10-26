#!/usr/bin/env python3
"""Negative regression tests for model specification/diagram validation, using no source records."""
import copy,json,unittest
from pathlib import Path
from check_model_review import validate_model,parse_mermaid,validate_provenance_shape
ROOT=Path(__file__).resolve().parents[1]
class ReviewTests(unittest.TestCase):
 def setUp(self):self.model=json.loads((ROOT/'docs/evidence/optimized-model-draft.json').read_text())
 def test_valid_specification(self):self.assertEqual(len(validate_model(self.model)),17)
 def test_fk_type_mismatch_rejected(self):
  next(t for t in self.model['tables'] if t['name']=='children')['fields']['id']['type']='text'
  with self.assertRaises(ValueError):validate_model(self.model)
 def test_optional_dependency_requires_gate(self):
  t=next(t for t in self.model['tables'] if t['name']=='source_provenance');next(f for f in t['foreign_keys'] if f['target']=='activity_logs').pop('enabled_if')
  with self.assertRaises(ValueError):validate_model(self.model)
 def test_independent_questionnaire_ids_rejected(self):
  next(t for t in self.model['tables'] if t['name']=='questionnaire_responses')['fields']['child_id']={'type':'uuid','nullable':False}
  with self.assertRaises(ValueError):validate_model(self.model)
 def test_provenance_accepts_one_typed_target(self):
  spec=next(t for t in self.model['tables'] if t['name']=='source_provenance')
  self.assertTrue(validate_provenance_shape({'source_record_id':'fixture-source','source_columns':['B'],'target_fields':['source_admission_number'],'child_id':'fixture-child'},spec))
 def test_provenance_rejects_multiple_targets(self):
  spec=next(t for t in self.model['tables'] if t['name']=='source_provenance')
  with self.assertRaises(ValueError):validate_provenance_shape({'child_id':'fixture-child','caregiver_id':'fixture-caregiver'},spec)
 def test_provenance_rejects_partial_reference_key(self):
  spec=next(t for t in self.model['tables'] if t['name']=='source_provenance')
  with self.assertRaises(ValueError):validate_provenance_shape({'reference_vocabulary':'fixture'},spec)
 def test_invalid_mermaid_reference_rejected(self):
  with self.assertRaises(ValueError):parse_mermaid('```mermaid\nerDiagram\n A ||--o{ MISSING : bad\n```')
 def test_invalid_mermaid_field_rejected(self):
  with self.assertRaises(ValueError):parse_mermaid('```mermaid\nerDiagram\n A {\n invalid-field-syntax\n }\n```')
if __name__=='__main__':unittest.main()
