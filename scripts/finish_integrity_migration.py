#!/usr/bin/env python3
"""Deterministic trigger bindings for prepared SQL. Does not apply migrations."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 model=json.loads((ROOT/'docs/evidence/final-model.json').read_text());p=ROOT/'supabase/migrations/20261026171202_ids_integrity.sql'
 text=p.read_text().split('-- GENERATED TRIGGER BINDINGS')[0];out=['-- GENERATED TRIGGER BINDINGS']
 evidence={'source_artifacts','source_records','source_provenance','recovery_actions','record_audit_events'}
 pointers={'children':'child_id','child_private_profiles':'private_profile_child_id','caregivers':'caregiver_id','child_caregivers':'child_caregiver_id','program_changes':'program_change_id','questionnaire_responses':'response_id','questionnaire_items':'item_id','questionnaire_answers':'answer_id','attendance_observations':'attendance_id','support_observations':'support_id','adl_visits':'adl_id','reference_values':'reference_vocabulary'}
 for t in model['tables']:
  n=t['name'];q=t['schema']+'.'+n
  if n in evidence:
   out.append(f'CREATE TRIGGER protect_{n} BEFORE UPDATE OR DELETE ON {q} FOR EACH ROW EXECUTE FUNCTION gk_private.reject_evidence_mutation();')
   out.append(f'CREATE TRIGGER protect_truncate_{n} BEFORE TRUNCATE ON {q} FOR EACH STATEMENT EXECUTE FUNCTION gk_private.reject_evidence_mutation();')
  if n not in {'source_artifacts','source_provenance','recovery_actions','record_audit_events'}:
   keys=','.join("'"+c+"'" for c in t['primary_key']);ops='UPDATE' if n=='source_records' else 'INSERT OR UPDATE OR DELETE'
   out.append(f'CREATE TRIGGER history_{n} AFTER {ops} ON {q} FOR EACH ROW EXECUTE FUNCTION gk_private.capture_row_change({keys});')
  vocabularies=[f['columns'][0]+':'+f['columns'][1] for f in t['foreign_keys'] if f['target']=='reference_values' and f['columns'][0]!='reference_vocabulary']
  if vocabularies:
   args=','.join("'"+c+"'" for c in vocabularies)
   out.append(f'CREATE TRIGGER values_{n} AFTER INSERT OR UPDATE ON {q} FOR EACH ROW EXECUTE FUNCTION gk_private.check_reference_state({args});')
  if n in pointers:
   out.append(f"CREATE CONSTRAINT TRIGGER lineage_{n} AFTER INSERT OR UPDATE ON {q} DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION gk_private.require_import_provenance('{pointers[n]}','{t['primary_key'][0]}');")
  if n not in evidence:
   fixed=list(t['primary_key'])
   if n=='children':fixed+=['child_business_id']
   if n=='caregivers':fixed+=['caregiver_business_id']
   if n=='child_caregivers':fixed+=['child_id','caregiver_id']
   if n=='questionnaire_responses':fixed+=['child_caregiver_id','definition_key']
   if n=='questionnaire_items':fixed+=['definition_key','item_key','prompt','value_kind']
   if n=='questionnaire_answers':fixed+=['response_id','item_id','definition_key']
   if n in ['attendance_observations','support_observations','adl_visits','program_changes']:fixed+=['child_id']
   args=','.join("'"+c+"'" for c in dict.fromkeys(fixed))
   out.append(f'CREATE TRIGGER identity_{n} BEFORE UPDATE ON {q} FOR EACH ROW EXECUTE FUNCTION gk_private.reject_identity_change({args});')
 out += ['COMMIT;',''];p.write_text(text+'\n'.join(out));print('Prepared audit/lineage/identity trigger bindings; not executed.')
if __name__=='__main__':main()
