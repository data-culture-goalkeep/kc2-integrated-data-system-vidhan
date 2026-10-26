#!/usr/bin/env python3
"""Build a draft architecture specification and full field mapping from frozen Stage 1 evidence.
No database API, connection, SQL or source-record mutation is involved.
"""
import collections,csv,json,re
from pathlib import Path
from openpyxl.utils import get_column_letter,column_index_from_string
ROOT=Path(__file__).resolve().parents[1]

def table(name,purpose,grain,spec,pk='id',optional=False):
 fields={}
 for token in spec.split():
  name_,type_=token.split(':');required=type_.endswith('!');fields[name_]={'type':type_.rstrip('!'),'nullable':not required,'status':'draft_recommendation'}
 return {'name':name,'purpose':purpose,'grain':grain,'fields':fields,'primary_key':pk.split(','),'foreign_keys':[],'unique_keys':[],'checks':[],'indexes':[],'optional':optional}

def main():
 p=json.loads((ROOT/'docs/evidence/data-profile.json').read_text());models=[]
 def add(*a,**kw):
  t=table(*a,**kw);models.append(t);return t
 add('reference_values','Database-controlled source-scoped categories; replaces separate PROGRAM-only lookup','One approved vocabulary/code', 'vocabulary:text! code:text! label:text! active:boolean! sort_order:integer',pk='vocabulary,code')
 add('children','Canonical operational identity/context under RLS; display names remain personal','One resolved source master identity','id:uuid! source_namespace:text source_admission_number:text display_name:text current_program_code:text admitted_program_code:text child_status_code:text program_vocabulary:text! status_vocabulary:text! joining_date:date dropout_date:date')
 add('child_private_profiles','Separates restricted child/family/health/financial attributes from operational reads','Zero or one restricted profile per child','child_id:uuid! birth_date:date gender_reported:text child_national_id:text blood_group_reported:text contact_address:text sibling_count_reported:text diagnosis_1:text diagnosis_2:text udid_number:text udid_disability_reported:text udid_validity_reported:text udid_percentage_reported:text insurance_number:text assessment_date:date assessment_age_reported:text family_income_reported:text economic_category_reported:text assessment_fee:numeric monthly_fee:numeric monthly_fee_remarks:text concession_reported:text social_category_reported:text religion_reported:text consent_reported:text dropout_reason_reported:text transition_date:date comments:text severity_reported:text',pk='child_id')
 add('caregivers','Resolved caregiver identity; no global person deduplication by display name','One identified caregiver source identity pending scope review','id:uuid! display_name:text birth_date:date contact_phone:text contact_email:text national_id:text employment_reported:text education_reported:text')
 add('child_caregivers','Preserves the verified child/caregiver pair and source identifier scope','One child/caregiver association','id:uuid! child_id:uuid! caregiver_id:uuid! source_namespace:text source_caregiver_code:text role_code:text role_vocabulary:text!')
 add('program_changes','Unpivots promotion slots without inventing interval ends','One source promotion observation','id:uuid! child_id:uuid! program_code:text program_vocabulary:text! promotion_date:date source_slot:integer')
 add('questionnaire_responses','Submission context; references the validated pair instead of redundant independent IDs','One approved response row/submission','id:uuid! child_caregiver_id:uuid! definition_key:text! definition_vocabulary:text! assessment_date:date program_code:text program_vocabulary:text! centre_code:text centre_vocabulary:text!')
 add('questionnaire_items','Actual question definitions; one version key without premature questionnaire-framework tables','One actual question column within an approved definition','id:uuid! definition_key:text! definition_vocabulary:text! item_key:text! prompt:text! section_label:text value_kind:text! ordinal:integer!')
 add('questionnaire_answers','Typed values replace untyped recorded_value; preserves missing answers separately','One response/item','id:uuid! response_id:uuid! item_id:uuid! definition_key:text! numeric_value:numeric text_value:text answer_state:text!')
 add('attendance_observations','Dated source marks kept distinct by service; unresolved names/dates remain staged','One resolved child/service/source-date observation','id:uuid! child_id:uuid! service_code:text! service_vocabulary:text! attendance_date:date! mark_code:text! mark_vocabulary:text! program_code:text program_vocabulary:text! batch_reported:text child_status_reported:text')
 add('support_observations','Source-cell support observations; not necessarily one person or a daily P/A event','One approved support matrix cell','id:uuid! child_id:uuid! participant_link_id:uuid event_reference:text! event_date:date program_code:text program_vocabulary:text! numeric_value:numeric text_value:text')
 add('adl_visits','Preserves true visit flags and undated historical exceptions','One checked visit-slot observation','id:uuid! child_id:uuid! program_code:text program_vocabulary:text! visit_flag:boolean! visit_date:date source_slot:integer')
 add('activity_logs','Structured activity records only after row-grain/workflow approval; archive retained regardless','One approved activity event, not each candidate content row','id:uuid! activity_description:text activity_date:date source_status_reported:text batch_reported:text participant_count_reported:text',optional=True)
 add('source_artifacts','Immutable snapshot identity and worksheet/column schema','One authorized source-file version','id:uuid! source_namespace:text! file_code:text! version_sha256:text! source_locator:text worksheet_manifest:jsonb! captured_at:timestamptz!')
 add('source_records','Restricted staging/reconciliation for every nonempty source row, including unresolved/derived fields','One artifact/native-sheet/original-row','id:uuid! artifact_id:uuid! native_sheet_key:text! source_row:integer! cell_payload:jsonb! processing_state:text! diagnostics:jsonb')
 provenance_targets={'child_id':'children','private_profile_child_id':'child_private_profiles','caregiver_id':'caregivers','child_caregiver_id':'child_caregivers','program_change_id':'program_changes','response_id':'questionnaire_responses','item_id':'questionnaire_items','answer_id':'questionnaire_answers','attendance_id':'attendance_observations','support_id':'support_observations','adl_id':'adl_visits','activity_id':'activity_logs'}
 add('source_provenance','Many-source-row/cell to one target without unconstrained polymorphic IDs','One source-column group -> one typed target/field group','id:uuid! source_record_id:uuid! source_columns:text[]! target_fields:text[]! rule_reference:text! contribution_state:text! '+' '.join(k+':uuid' for k in provenance_targets)+' reference_vocabulary:text reference_code:text')
 add('access_memberships','Application authorization independent of Google sign-in and business caregivers','One admitted auth user in this dedicated project','user_id:uuid! approved_email_domain:text! role_code:text! role_vocabulary:text! active:boolean!',pk='user_id')
 by={t['name']:t for t in models}
 common={'created_at':('timestamptz',False),'updated_at':('timestamptz',False),'created_by':('uuid',True),'updated_by':('uuid',True),'actor_ref':('text',False)}
 for t in models:
  for k,(typ,null) in common.items():t['fields'][k]={'type':typ,'nullable':null,'status':'proposed_technical_audit_field'}
  if t['name'] not in {'source_artifacts','source_records','source_provenance','access_memberships','reference_values'}:
   t['fields']['origin_kind']={'type':'text','nullable':False,'status':'technical_import_or_manual'};t['fields']['review_state']={'type':'text','nullable':False,'status':'technical_review_metadata'}
  t['checks'].append('Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs')
  for k in ['created_by','updated_by']:t['foreign_keys'].append({'columns':[k],'target':'auth.users','target_columns':['id'],'basis':'proposed technical audit','on_delete':'RESTRICT'})
 def fk(t,cols,target,target_cols='id',basis='draft design; no database exists'):
  by[t]['foreign_keys'].append({'columns':cols.split(','),'target':target,'target_columns':target_cols.split(','),'basis':basis,'on_delete':'RESTRICT'})
 def unique(t,*cols):by[t]['unique_keys'].append(list(cols))
 def lookup(t,code,vocab,tag):
  fk(t,vocab+','+code,'reference_values','vocabulary,code','proposed controlled vocabulary');by[t]['checks'].append(vocab+' is server-generated fixed '+tag+' discriminator; MATCH SIMPLE composite FK permits unknown code NULL')
 fk('child_private_profiles','child_id','children')
 fk('child_caregivers','child_id','children',basis='716/716 source child IDs resolve to 371-key master')
 fk('child_caregivers','caregiver_id','caregivers',basis='caregiver identity scope remains Q02')
 unique('child_caregivers','id','child_id');unique('child_caregivers','source_namespace','child_id','source_caregiver_code')
 fk('program_changes','child_id','children')
 fk('questionnaire_responses','child_caregiver_id','child_caregivers',basis='106/106 observed pairs consistent, authority Q01 pending');unique('questionnaire_responses','id','definition_key')
 unique('questionnaire_items','definition_key','item_key');unique('questionnaire_items','definition_key','ordinal');unique('questionnaire_items','id','definition_key')
 fk('questionnaire_answers','response_id,definition_key','questionnaire_responses','id,definition_key');fk('questionnaire_answers','item_id,definition_key','questionnaire_items','id,definition_key');unique('questionnaire_answers','response_id','item_id')
 fk('attendance_observations','child_id','children',basis='future curated rows only; unresolved source identities remain source_records')
 fk('support_observations','child_id','children',basis='conditional on approved identity crosswalk');fk('support_observations','participant_link_id,child_id','child_caregivers','id,child_id',basis='when a single participant resolves, require the same child')
 fk('adl_visits','child_id','children',basis='conditional on approved identity crosswalk')
 fk('source_records','artifact_id','source_artifacts');unique('source_artifacts','source_namespace','file_code','version_sha256');unique('source_records','artifact_id','native_sheet_key','source_row')
 fk('source_provenance','source_record_id','source_records')
 for col,target in provenance_targets.items():fk('source_provenance',col,target,'child_id' if target=='child_private_profiles' else 'id')
 fk('source_provenance','reference_vocabulary,reference_code','reference_values','vocabulary,code')
 fk('access_memberships','user_id','auth.users',basis='Supabase-managed authentication identity, not NGO caregiver identity')
 for t,code,vocab,tag in [('questionnaire_responses','definition_key','definition_vocabulary','questionnaire_definition'),('questionnaire_items','definition_key','definition_vocabulary','questionnaire_definition'),('children','current_program_code','program_vocabulary','program'),('children','admitted_program_code','program_vocabulary','program'),('children','child_status_code','status_vocabulary','child_status'),('child_caregivers','role_code','role_vocabulary','caregiver_role'),('program_changes','program_code','program_vocabulary','program'),('questionnaire_responses','program_code','program_vocabulary','program'),('questionnaire_responses','centre_code','centre_vocabulary','centre'),('attendance_observations','service_code','service_vocabulary','service_context'),('attendance_observations','mark_code','mark_vocabulary','attendance_mark'),('attendance_observations','program_code','program_vocabulary','program'),('support_observations','program_code','program_vocabulary','program'),('adl_visits','program_code','program_vocabulary','program'),('access_memberships','role_code','role_vocabulary','access_role')]:lookup(t,code,vocab,tag)
 by['source_provenance']['target_groups']=[[k] for k in provenance_targets]+[['reference_vocabulary','reference_code']]
 by['source_provenance']['checks']+=['Exactly one complete target group, all other target columns NULL; partial reference vocabulary/code pair forbidden','source_columns and target_fields nonempty; field/column membership checked by bounded mapping validator','rule_reference identifies approved transformation/mapping version; contribution_state distinguishes selected/supporting/conflict evidence, without treating links as business approval','Import idempotency must use immutable artifact/sheet/row/column/slot plus target-kind and approved rule identity; repeated exports/business events need approved reconciliation keys, not random UUID deduplication','Before promotion of imported target rows, deferred constraint trigger or transactional import validator requires >=1 provenance link; update provenance atomically with edits']
 by['questionnaire_answers']['checks']+=['At most one numeric_value/text_value; both NULL allowed only for explicit missing answer_state','Value kind agrees with item definition via constrained server write path; no 1..5 range until Q05']
 by['attendance_observations']['checks']+=['No unique(child_id,date): multiple services and observations can coexist','Resolved child/date/code required in curated rows; unknowns remain staged, never invented']
 by['adl_visits']['checks']+=['visit_flag must be true for this fact grain; false/blank source slots retained in source_records','visit_date may be NULL only for imported pending-date record with provenance; future manual entry requires date']
 by['children']['checks']+=['Source admission uniqueness is a proposed partial unique(source_namespace,source_admission_number), gated on Q02; never unique(display_name)','Birth/joining inequality is not imposed until correction/exception handling approved; original 3 conflicts preserved']
 by['reference_values']['checks']+=['Never seed canonical meanings, roles or synonym mappings without analyst approval; preserve source-scoped distinctions']
 for t in models:
  t['indexes']=[{'columns':fk_['columns'],'reason':'FK lookup/referential action candidate; benchmark before redundant indexes','status':'recommended'} for fk_ in t['foreign_keys'] if fk_['target']!='auth.users']
 for name,cols in [('attendance_observations',['child_id','attendance_date']),('questionnaire_responses',['child_caregiver_id','assessment_date']),('adl_visits',['child_id','visit_date']),('program_changes',['child_id','promotion_date']),('source_records',['processing_state','artifact_id'])]:by[name]['indexes'].append({'columns':cols,'reason':'proposed common entry/report filter','status':'recommended'})
 # A PK/unique or longer recommended index covers an identical leading key.
 for t in models:
  for relation in t['foreign_keys']:
   if relation['target'] in by and by[relation['target']]['optional']:
    relation['enabled_if']=relation['target'];
    for column in relation['columns']:t['fields'][column]['enabled_if']=relation['target']
  candidates={tuple(x['columns']):x for x in t['indexes']}
  existing=[tuple(t['primary_key'])]+[tuple(k) for k in t['unique_keys']]
  t['indexes']=[x for cols,x in candidates.items() if not any(len(other)>=len(cols) and other[:len(cols)]==cols for other in existing+[k for k in candidates if k!=cols])]
 for t in models:
  for index in t['indexes']:
   gates={t['fields'][c].get('enabled_if') for c in index['columns']}-{None}
   if gates:index['enabled_if']=sorted(gates)
 model={'status':'DRAFT_UNAPPROVED_NO_DATABASE_IMPLEMENTATION','baseline_commit':'de729f993e60b2af7f33e115bc811ee27aa38b21','baseline_entity_count':12,'proposed_table_count':len(models),'core_table_count':sum(not x['optional'] for x in models),'optional_tables':[x['name'] for x in models if x['optional']],'managed_external_tables':['auth.users'],'tables':models,'facts':'All technical keys/audit/staging/auth fields are recommendations, not invented NGO source fields','authorization':'Stage 2 review only; SQL, migrations and frontend prohibited'}
 (ROOT/'docs/evidence/optimized-model-draft.json').write_text(json.dumps(model,indent=2)+'\n')
 # Each profiled field has an explicit retained location, and a separate operational projection/disposition.
 child_map={'B':('children','source_admission_number'),'C':('children','display_name'),'D':('children','current_program_code'),'E':('children','child_status_code'),'F':('children','admitted_program_code'),'I':('children','joining_date'),'AR':('children','dropout_date')}
 private_map={'AV':'dropout_reason_reported','G':'diagnosis_1','H':'diagnosis_2','J':'birth_date','L':'gender_reported','M':'child_national_id','N':'blood_group_reported','AC':'contact_address','AD':'sibling_count_reported','AE':'udid_number','AF':'udid_disability_reported','AG':'udid_validity_reported','AH':'udid_percentage_reported','AI':'insurance_number','AJ':'assessment_date','AK':'assessment_age_reported','AL':'family_income_reported','AM':'economic_category_reported','AN':'assessment_fee','AO':'monthly_fee','AP':'monthly_fee_remarks','AQ':'concession_reported','AT':'social_category_reported','AU':'religion_reported','BG':'transition_date','BH':'consent_reported','BI':'comments','BK':'severity_reported'}
 caregiver_map={'O':'display_name','P':'contact_phone','Q':'contact_email','R':'national_id','S':'birth_date','T':'employment_reported','U':'education_reported','V':'display_name','W':'contact_phone','X':'contact_email','Y':'national_id','Z':'birth_date','AA':'employment_reported','AB':'education_reported'}
 mappings=[]
 def dest(t,f):assert t in by and f in by[t]['fields'];return t+'.'+f
 for s in p['sheets']:
  fields=list(s['fields'])
  if not fields:
   safe_path=ROOT/'work/source-intake/sanitized'/(s['source']+'_'+s['sheet']+'.jsonl')
   safe_rows=[json.loads(line) for line in safe_path.read_text().splitlines()]
   header=next((r['cells'] for r in safe_rows if r['row']==s['header_row']),{})
   for column in range(1,s['max_column']+1):
    letter=get_column_letter(column);value=header.get(letter)
    label_=str(value).replace('\n',' ').strip() if isinstance(value,str) and not value.startswith('MASK_') and value!='[FORMULA]' else 'COORDINATE_'+letter
    fields.append({'column':letter,'label':label_,'rows':s['record_rows'],'missing':s['record_rows'],'metadata_only':True})
  for f in fields:
   col=f['column'];idx=column_index_from_string(col);target='';disposition='retained_reference_only';gate='Source authority/grain approval before operational use';why='Derived/ancillary/reference content retained without treating it as a new fact';kind=s['kind']
   if f['label'].startswith(('UNLABELED_','COORDINATE_')) or not f['label'].strip():
    why='Unlabeled or empty source column explicitly retained; no invented business field'
   elif (s['source'],s['sheet'])==('S03','T01'):
    if col in child_map:target=dest(*child_map[col]);disposition='conditional_projection';gate='Q01,Q02,Q09';why='Canonical source identity/context with original retained'
    elif col in private_map:target=dest('child_private_profiles',private_map[col]);disposition='conditional_projection';gate='Q09,Q10';why='Restricted scalar source attribute; invalid parsing stays staged'
    elif col in caregiver_map:target=dest('caregivers',caregiver_map[col]);disposition='conditional_projection';gate='Q02,Q03,Q10,parent-role crosswalk';why='Mother/father source role must resolve before attributing caregiver field'
    elif 49<=idx<=58:target=dest('program_changes','program_code' if idx%2 else 'promotion_date');disposition='conditional_unpivot';gate='Q09';why='Five numbered program/date pairs become separate observations'
    else:why='Source serial, derived age/year, or unused structure retained for reconciliation; not duplicated canonical truth'
   elif (s['source'],s['sheet'])==('S05','T07'):
    target={'A':dest('caregivers','display_name'),'B':dest('child_caregivers','source_caregiver_code'),'C':dest('child_caregivers','child_id'),'D':''}.get(col,'');disposition='conditional_projection' if target else disposition;gate='Q01,Q02';why='Preserve pair and source code; resolve child via admission crosswalk, not UUID cast'
   elif (s['source'],s['sheet'])==('S01','T01'):
    if col in ['A','AZ','BA']:target=dest('questionnaire_responses','child_caregiver_id') if col!='A' else '';disposition='conditional_pair_resolution' if target else disposition;gate='Q01,Q02,Q04';why='AZ/BA resolve one validated association; reported name retained as conflicting source evidence'
    elif col in ['B','C','D']:target=dest('questionnaire_responses',{'B':'program_code','C':'centre_code','D':'assessment_date'}[col]);disposition='conditional_projection';gate='Q04,Q09,categories';why='Submission-time context is not inferred from current child state'
    elif 5<=idx<=35:target=dest('questionnaire_answers','numeric_value' if idx<=31 else 'text_value');disposition='conditional_unpivot';gate='Q04,Q05';why='Actual question header -> item definition; actual value -> typed answer; blanks retained explicitly'
    else:why='Derived score/interpretation or unused columns retained for comparison, not authoritative recalculation'
   elif kind=='daily_attendance':
    if col=='A':target=dest('attendance_observations','child_id');why='Name/trainee identifier needs approved crosswalk; not direct string-to-UUID';gate='Q03,trainee population scope'
    elif col=='B':target=dest('attendance_observations','batch_reported' if 'batch' in f['label'].casefold() else 'program_code');why='Batch is not automatically a program';gate='Q06,categories'
    elif col=='C':target=dest('attendance_observations','child_status_reported');why='Observation-time source status retained';gate='Q06'
    elif 7<=idx<=37:target=dest('attendance_observations','mark_code');why='Date header and mark unpivot jointly; source_columns includes header lineage';gate='Q03,Q06,date resolution'
    if target:disposition='conditional_unpivot'
   elif kind=='adl_visit_slots':
    if col=='A':target=dest('adl_visits','child_id')
    elif col=='B':target=dest('adl_visits','program_code')
    elif 3<=idx<=12:target=dest('adl_visits','visit_flag' if idx%2 else 'visit_date')
    if target:disposition='conditional_unpivot';gate='Q03,Q08';why='Pair source checkbox/date by slot; do not manufacture events/dates'
   elif kind=='support_attendance':
    if col=='A':target=dest('support_observations','child_id')
    elif 'name' in f['label'].casefold() or 'caregiver' in f['label'].casefold():target=dest('support_observations','participant_link_id')
    elif f['label'].casefold()=='program':target=dest('support_observations','program_code')
    elif f['label'].casefold()!='total':target=dest('support_observations','text_value')
    if target:disposition='conditional_interpretation';gate='Q03,Q07';why='Value/type/event interpretation needed; numeric inputs use numeric_value when approved, composite parent codes never invent one participant'
   elif kind=='visit_activity_log':
    disposition='optional_projection_deferred';gate='Q11';why='Optional activity_logs held behind row-grain/workflow approval; all content remains retained'
   mappings.append({'source':s['source'],'sheet':s['sheet'],'native_sheet_id':s['google_sheet_id'],'column':col,'source_field_label':f['label'],'coverage_class':'coordinate_or_header_only' if f.get('metadata_only') else 'profiled_field','candidate_rows':f['rows'],'missing':f['missing'],'retained_target':dest('source_records','cell_payload')+'['+col+']','header_retained_target':dest('source_artifacts','worksheet_manifest')+'['+s['sheet']+'].columns['+col+']','header_projection':dest('questionnaire_items','prompt') if s['source']=='S01' and s['sheet']=='T01' and 5<=idx<=35 else '','operational_target':target,'disposition':disposition,'approval_gate':gate,'reason':why})
 with (ROOT/'docs/evidence/source-target-coverage.csv').open('w',newline='') as out:
  w=csv.DictWriter(out,fieldnames=list(mappings[0]),lineterminator='\n');w.writeheader();w.writerows(mappings)
 summary={'source_column_slots':len(mappings),'profiled_source_field_instances':sum(len(s['fields']) for s in p['sheets']),'additional_header_or_coordinate_slots':sum(x['coverage_class']=='coordinate_or_header_only' for x in mappings),'retained_field_instances':sum(bool(x['retained_target']) for x in mappings),'operationally_projected_field_instances':sum(bool(x['operational_target']) for x in mappings),'without_named_operational_projection':sum(not x['operational_target'] for x in mappings),'dispositions':dict(collections.Counter(x['disposition'] for x in mappings)),'headerless_worksheets':sum(s['header_row'] is None for s in p['sheets']),'source_worksheet_coverage':len(p['sheets']),'unrepresented_fields':0,'warning':'Retained provenance coverage is not proof of a typed operational field or approved future workflow; archive-only fields are explicitly listed'}
 (ROOT/'docs/evidence/model-mapping-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps({'tables':len(models),'core':model['core_table_count'],'mapping':summary},indent=2))

if __name__=='__main__':main()
