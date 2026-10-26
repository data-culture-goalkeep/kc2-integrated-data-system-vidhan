#!/usr/bin/env python3
"""Finalize the logical specification from analyst decisions; no database operations."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def field(typ,nullable=True):return {'type':typ,'nullable':nullable,'status':'technical_preparation'}
def main():
 old=json.loads((ROOT/'docs/evidence/optimized-model-draft.json').read_text());m=copy.deepcopy(old)
 m['tables']=[t for t in m['tables'] if t['name']!='activity_logs'];by={t['name']:t for t in m['tables']}
 for t in m['tables']:
  t['optional']=False
  private=t['name'] in {'caregivers','child_private_profiles','questionnaire_answers','source_artifacts','source_records','source_provenance','access_memberships'}
  t['schema']='gk_private' if private else 'public'
  if t['name'] not in {'source_artifacts','source_records','source_provenance'}:
   t['fields']['archived_at']=field('timestamptz');t['fields']['archived_by']=field('uuid')
   t['foreign_keys'].append({'columns':['archived_by'],'target':'auth.users','target_columns':['id'],'on_delete':'RESTRICT','basis':'soft-delete audit'})
  t['foreign_keys']=[f for f in t['foreign_keys'] if f['target']!='activity_logs']
  for f in t['foreign_keys']:f.pop('enabled_if',None)
  for f in t['fields'].values():f.pop('enabled_if',None)
  t['indexes']=[i for i in t['indexes'] if 'activity_id' not in i['columns']]
  t['checks']=[] # Replace draft prose with the explicit final SQL invariants.
  for f in t['fields'].values():f['status']='recommended_pending_migration_approval'
 by['children']['fields']['child_business_id']=by['children']['fields'].pop('source_admission_number');by['children']['fields']['child_business_id']['nullable']=False
 by['children']['fields'].pop('source_namespace',None);by['children']['unique_keys']=[['child_business_id']]
 by['caregivers']['grain']='One caregiver per verified authoritative caregiver business identifier';by['caregivers']['fields']['caregiver_business_id']=field('text',False);by['caregivers']['unique_keys']=[['caregiver_business_id']]
 cc=by['child_caregivers'];cc['fields'].pop('source_namespace',None);cc['fields'].pop('source_caregiver_code',None)
 cc['purpose']='Preserves each child/caregiver association independently from person identity';cc['unique_keys']=[['id','child_id'],['child_id','caregiver_id']]
 for fk in cc['foreign_keys']:
  if fk['target']=='caregivers':fk['basis']='Owner confirmed globally unique caregiver business identifiers; exact IDs verified'
 for t in m['tables']:
  t['indexes']=[i for i in t['indexes'] if all(c in t['fields'] for c in i['columns'])]
 prov=by['source_provenance'];prov['fields'].pop('activity_id',None);prov['target_groups']=[g for g in prov['target_groups'] if g!=['activity_id']]
 rv=by['reference_values'];rv['fields'].update({'permissions':field('jsonb',False),'approval_reference':field('text'),'origin_kind':field('text',False),'review_state':field('text',False)})
 by['access_memberships']['fields'].update({'private_read':field('boolean',False),'private_write':field('boolean',False),'approval_reference':field('text')})
 audit={k:field(v,n) for k,v,n in [('created_at','timestamptz',False),('updated_at','timestamptz',False),('created_by','uuid',True),('updated_by','uuid',True),('actor_ref','text',False)]}
 def add(name,purpose,grain,fields):
  t={'name':name,'schema':'gk_private','purpose':purpose,'grain':grain,'optional':False,'primary_key':['id'],'fields':{'id':field('uuid',False),**fields,**copy.deepcopy(audit)},'foreign_keys':[],'unique_keys':[],'checks':[],'indexes':[]};m['tables'].append(t);by[name]=t;return t
 cand=add('identity_candidates','Preserve exact-ID matches and unapproved name/context candidates','One staged row/candidate identity/method',{'source_record_id':field('uuid',False),'child_id':field('uuid'),'caregiver_id':field('uuid'),'match_method':field('text',False),'resolution_status':field('text',False),'evidence':field('jsonb',False)})
 rec=add('recovery_actions','Append-only original/proposed value, donor, method and validation audit','One recovery/suggestion per source cell and run',{'source_record_id':field('uuid',False),'donor_source_record_id':field('uuid'),'child_id':field('uuid'),'caregiver_id':field('uuid'),'source_column':field('text',False),'field_key':field('text',False),'original_value':field('jsonb',False),'recovered_value':field('jsonb'),'method':field('text',False),'validation_status':field('text',False),'identity_verified':field('boolean',False),'authoritative_source':field('boolean',False),'meaning_equivalent':field('boolean',False),'has_conflict':field('boolean',False),'evidence':field('jsonb',False),'run_id':field('uuid',False)})
 for t in [cand,rec]:
  for c,target,tc in [('source_record_id','source_records','id'),('child_id','children','id'),('caregiver_id','caregivers','id')]:t['foreign_keys'].append({'columns':[c],'target':target,'target_columns':[tc],'on_delete':'RESTRICT','basis':'technical evidence/audit'})
  for c in ['created_by','updated_by']:t['foreign_keys'].append({'columns':[c],'target':'auth.users','target_columns':['id'],'on_delete':'RESTRICT','basis':'audit'})
  t['indexes']=[{'columns':['source_record_id'],'reason':'source investigation'}]
 rec['foreign_keys'].append({'columns':['donor_source_record_id'],'target':'source_records','target_columns':['id'],'on_delete':'RESTRICT','basis':'recovery donor lineage'})
 add('record_audit_events','Append-only operational and access-change history; no API insertion','One database-generated row change event',{'schema_name':field('text',False),'table_name':field('text',False),'record_key':field('jsonb',False),'operation':field('text',False),'before_value':field('jsonb'),'after_value':field('jsonb')})
 for t in m['tables']:
  for c in ['created_by','updated_by']:
   if c in t['fields'] and not any(f['columns']==[c] for f in t['foreign_keys']):t['foreign_keys'].append({'columns':[c],'target':'auth.users','target_columns':['id'],'on_delete':'RESTRICT','basis':'audit'})
 for t in m['tables']:
  keys=[t['primary_key']]+t['unique_keys']
  t['indexes']=[i for i in t['indexes'] if not any(k[:len(i['columns'])]==i['columns'] for k in keys)]
 m.update(status='FINAL_RECOMMENDATION_PREPARED_NOT_APPLIED',previous_draft_tables=17,proposed_table_count=len(m['tables']),core_table_count=len(m['tables']),optional_tables=[],authorized_project={'name':'kc2-integrated-data-system','region':'ap-northeast-1','environment':'non-production pilot','reference_id':None,'verified':False},role_matrix={'status':'draft_not_activated','domain':'goalkeep.net','proposed_roles':['Admin','Member'],'automatic_member_provisioning':'only after explicit owner approval and active accepted role definition','admin_assignment':'explicit_only'},approval_scope='Analyst IDs/name/recovery rules approved; SQL generation only; no application or migrations',source_note='Activity source data retained in source_records; no activity table until event grain approved')
 # Preserve a reference only after actual read-only identity verification.
 config=ROOT/'config/authorized-supabase-project.json'
 if config.exists():m['authorized_project']=json.loads(config.read_text())
 (ROOT/'docs/evidence/final-model.json').write_text(json.dumps(m,indent=2)+'\n')
 config=ROOT/'config/authorized-supabase-project.json'
 if not config.exists():config.write_text(json.dumps(m['authorized_project'],indent=2)+'\n')
 print('Final recommendation:',len(m['tables']),'tables; zero database changes.')
if __name__=='__main__':main()
