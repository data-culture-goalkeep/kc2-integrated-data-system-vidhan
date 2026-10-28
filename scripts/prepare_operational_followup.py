#!/usr/bin/env python3
"""Targeted, local-only follow-up gate analysis. Reuses frozen sanitized plan; never connects or writes SQL."""
from collections import Counter,defaultdict
from pathlib import Path
import json,hashlib,sys
from etl_core import ROOT,required,stable_id,reference
from profile_sources import label,present
from recovery import source_integrity,atomic_save

def main():
 source_integrity()  # frozen sources, original code/plan and committed prefix unchanged
 profile=json.loads((ROOT/'docs/evidence/data-profile.json').read_text());plan=json.loads((ROOT/'work/etl/plan.json').read_text())
 records=[r for u in plan['units'] for r in u];children={r['values']['child_business_id']:r['values']['id'] for r in records if r['table']=='children'}
 sources={r['values']['id']:r['values']['file_code'] for r in records if r['table']=='source_artifacts'}
 sheet_index={(s['source'],str(s['google_sheet_id'])):s['sheet'] for s in profile['sheets']}
 rows={reference(sources[r['values']['artifact_id']],sheet_index[(sources[r['values']['artifact_id']],r['values']['native_sheet_key'])],r['values']['source_row']):r['values'] for r in records if r['table']=='source_records'}
 cached=json.loads((ROOT/'work/recovery/identity-candidates.json').read_text());candidate_status={r['source_reference']:('one_candidate' if len(r['candidates'])==1 else 'ambiguous' if r['candidates'] else 'unmatched') for r in cached}
 kinds={'daily_attendance','adl_visit_slots','support_attendance','historical_visits','support_event_summary','visit_activity_log','annual_attendance_summary','adl_annual_summary','adl_goals_summary','questionnaire_view','questionnaire_subset'}
 totals=defaultdict(Counter);ledger=[]
 for s in profile['sheets']:
  if s['kind'] not in kinds:continue
  headers={label(f['label']):f['column'] for f in s['fields']};col=next((headers[k] for k in ['childid','admissionnumber','admissionno'] if k in headers),None)
  for n in s['record_row_refs']:
   ref=reference(s['source'],s['sheet'],n);row=rows[ref];cells=row['cell_payload'];v=cells.get(col) if col else None
   exact=type(v) is str and v in children
   t=totals[s['kind']];t['source_candidate_rows']+=1;t['literal_id_verified_rows']+=int(exact);t[candidate_status.get(ref,'not_name_candidate_investigation')]+=1
   gates=[]
   if not exact:gates.append('verified_child_id_or_approved_exact_crosswalk_required')
   if s['kind']=='daily_attendance':gates+=['date_fidelity_and_calendar','service_and_mark_vocabulary_approval']
   elif s['kind']=='adl_visit_slots':gates+=['slot_level_true_flag_extraction','date_fidelity_or_explicit_NULL_date_policy']
   elif s['kind']=='support_attendance':gates+=['support_event_grain','literal_observation_semantics','date_fidelity_or_explicit_NULL_date_policy']
   else:gates+=['summary_view_or_event_grain_requires_business_approval','avoid_reimporting_existing_source_or_questionnaire_views']
   ledger.append({'source_reference':ref,'source_record_id':row['id'],'kind':s['kind'],'exact_child_id_verified':exact,'candidate_status':candidate_status.get(ref),'blocking_gates':gates,'deterministic_id_rule':'stable_id(version, target_table, source_record_id, verified_source_cell_or_slot)','status':'blocked_no_operational_fact_prepared'})
 required(sum(x['source_candidate_rows'] for k,x in totals.items() if k in {'daily_attendance','adl_visit_slots','support_attendance'})==3623,'Identity-pending source denominator differs')
 required(all(x['literal_id_verified_rows']==0 for x in totals.values()),'New literal identity evidence detected: investigate before declaring zero eligible')
 additional=json.loads((ROOT/'docs/evidence/additional-checks.json').read_text());adl=additional['adl'];checks=sum(x['checked_visit_slots'] for x in adl);missing=sum(x['checked_without_date'] for x in adl)
 required(checks==194 and missing==4,'ADL slot evidence differs')
 atomic_save(ROOT/'work/handover/operational-eligibility-ledger.json',ledger)
 # No records meet every required gate. Do not issue an empty/nonempty-target initial-load plan or owner artifact.
 summary={'status':'prepared_blocked','remote_writes':0,'additional_fully_verified_records':0,'additional_safe_pending_operational_records':0,'source_candidate_rows_by_kind':{k:dict(v) for k,v in sorted(totals.items())},'adl_checked_slots':checks,'adl_missing_date_slots':missing,'already_migrated_pending':{'program_changes':128,'questionnaire_responses':106,'questionnaire_answers':3286},'approved_date_fidelity':False,'new_operational_records':[],'name_only_identity_acceptance':False,'execution_authorization':False,'private_ledger_rows':len(ledger),'private_ledger_sha256':hashlib.sha256((ROOT/'work/handover/operational-eligibility-ledger.json').read_bytes()).hexdigest(),'future_loading':'Reuse etl_core.validate_record, stable_id, typed provenance and compile_batch after verified cell-level mapping and a separately approved incremental manifest; never reuse consumed initial-load/recovery authorization','gates':'Attendance requires non-NULL verified date and approved service/mark codes. ADL/support may use NULL dates but still need a verified child and approved observation grain. Pending does not waive FKs or justify invented facts.'}
 (ROOT/'docs/evidence/phase1-operational-eligibility.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'additional_fully_verified':0,'additional_pending_eligible':0,'classified_source_candidate_rows':len(ledger),'adl_checked_slots':194,'source_profile_rebuilt':False}))
if __name__=='__main__':main()
