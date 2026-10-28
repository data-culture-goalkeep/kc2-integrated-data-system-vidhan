#!/usr/bin/env python3
"""Pure conservative identity/recovery/reconciliation logic. No file mutation, logging or database calls."""
from collections import defaultdict,Counter
from datetime import date,datetime
import json,re

def missing(value):return value is None or (isinstance(value,str) and not value.strip())
def exact_id(value):
 # Business identifiers are text and case-sensitive. Never lose leading zeros or cast numeric aliases.
 return value if isinstance(value,str) and value and value==value.strip() else None

def verified_registry(records):
 index={};issues=[];conflicted=set()
 for record in records:
  identifier=exact_id(record.get('business_id'))
  if identifier is None:issues.append({'code':'missing_or_malformed_identifier','reference':record['reference']});continue
  if identifier in index:
   conflicted.add(identifier)
   issues.append({'code':'duplicate_authoritative_identifier','references':[index[identifier]['reference'],record['reference']]})
  else:index[identifier]=record
 return {k:v for k,v in index.items() if k not in conflicted},issues

def parse_date(value,declared_format=None):
 if isinstance(value,datetime):return {'status':'valid','value':value.date().isoformat()}
 if isinstance(value,date):return {'status':'valid','value':value.isoformat()}
 if missing(value):return {'status':'missing','value':None}
 if not isinstance(value,str):return {'status':'unsupported_representation','value':None}
 text=value.strip()
 try:
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}',text):return {'status':'valid','value':date.fromisoformat(text).isoformat()}
  if re.fullmatch(r'\d{1,2}[/.-]\d{1,2}[/.-]\d{4}',text):
   parts=re.split(r'[/.-]',text);a,b,y=map(int,parts)
   if declared_format=='DD/MM/YYYY':return {'status':'valid_declared_format','value':date(y,b,a).isoformat()}
   if a<=12 and b<=12:return {'status':'ambiguous_day_month','value':None}
  return {'status':'unparsed','value':None}
 except ValueError:return {'status':'invalid','value':None}

def comparable(value,kind):
 if missing(value):return None
 if kind=='date':
  result=parse_date(value)
  return ('date',result['value']) if result['status']=='valid' else ('unparsed',str(value))
 return (type(value).__name__,str(value))

def plan_recovery(records,registries,field_kinds):
 """Recover missing fields only from authoritative, equivalent, uncontradicted literal-ID donors.
 records: entity_kind/business_id/identifier_literal/fields/equivalent_fields/authoritative_fields/reference.
 Full actions contain protected values; callers must keep them in restricted storage.
 """
 grouped=defaultdict(list)
 for r in records:
  identity=exact_id(r.get('business_id'));kind=r['entity_kind']
  if identity in registries.get(kind,{}) and r.get('identifier_literal',False):grouped[(kind,identity)].append(r)
 actions=[]
 for (entity,identifier),members in grouped.items():
  for field,kind in field_kinds[entity].items():
   entries=[r for r in members if field in r.get('equivalent_fields',[]) and not missing(r['fields'].get(field))]
   distinct={comparable(r['fields'][field],kind) for r in entries}
   donors=[r for r in entries if field in r.get('authoritative_fields',[])]
   for target in members:
    if field not in target.get('equivalent_fields',[]) or not missing(target['fields'].get(field)) or not entries:continue
    conflicts=len(distinct)>1
    eligible=[r for r in donors if kind!='date' or comparable(r['fields'][field],kind)[0]=='date']
    state='blocked_conflict' if conflicts else 'auto_recovered' if eligible else 'blocked_untrusted'
    donor=eligible[0] if eligible else entries[0]
    actions.append({'entity_kind':entity,'business_id':identifier,'field_key':field,'original_value':target['fields'].get(field),'recovered_value':donor['fields'][field],'target_reference':target['reference'],'source_reference':donor['reference'],'source_column':target.get('field_columns',{}).get(field,field),'donor_column':donor.get('field_columns',{}).get(field,field),'method':'verified_id_authoritative_consensus' if state=='auto_recovered' else 'suggested_only','validation_status':state,'identity_verified':True,'authoritative_source':bool(eligible),'meaning_equivalent':True,'has_conflict':conflicts,'evidence_references':[r['reference'] for r in entries]})
 return actions

def identity_candidates(observation,registry,aliases=None):
 identity=exact_id(observation.get('business_id'))
 if identity in registry and observation.get('identifier_literal'):
  return [{'business_id':identity,'method':'exact_identifier','status':'verified','evidence':[registry[identity]['reference']]}]
 if identity in registry:
  return [{'business_id':identity,'method':'computed_identifier','status':'candidate','evidence':[registry[identity]['reference']]}]
 if missing(observation.get('name')):return []
 label=' '.join(str(observation['name']).split()).casefold();candidates={}
 for key,r in registry.items():
  canonical=' '.join(str(r['fields'].get('display_name','')).split()).casefold()
  if label and label==canonical:candidates[key]=[r['reference']]
 for key,entries in (aliases or {}).items():
  if key not in registry:continue
  for a in entries:
   if not missing(a.get('name')) and label==' '.join(str(a['name']).split()).casefold():candidates.setdefault(key,[]).append(a['reference'])
 out=[]
 for key,evidence in candidates.items():
  programme=observation.get('program');current=registry[key]['fields'].get('program')
  agrees=bool(programme and current and programme==current)
  out.append({'business_id':key,'method':'name_context' if agrees else 'name_candidate','status':'candidate','evidence':evidence,'program_agreement':agrees,'program_qualification':'Current program is context only; it does not prove historical identity'})
 return out

def duplicate_groups(records):
 by=defaultdict(list)
 for r in records:by[json.dumps(r.get('fields',{}),sort_keys=True,default=str)].append(r['reference'])
 return [refs for refs in by.values() if len(refs)>1]

def reconcile(expected_references,dispositions):
 """Source-row coverage and target-observation counts are different denominators."""
 expected_list=list(expected_references);expected_counts=Counter(expected_list)
 repeated_expected={r:n for r,n in expected_counts.items() if n>1}
 expected=set(expected_list);counts=Counter(d['source_reference'] for d in dispositions)
 unknown=set(counts)-expected;missing_refs=expected-set(counts);duplicates={r:n for r,n in counts.items() if n>1}
 valid_status={'ready','blocked','reference_only','suggested'}
 invalid=[d['source_reference'] for d in dispositions if d['status'] not in valid_status]
 invalid_targets=[d['source_reference'] for d in dispositions if type(d.get('target_observations',0)) is not int or d.get('target_observations',0)<0]
 return {'ok':not(unknown or missing_refs or duplicates or invalid or repeated_expected or invalid_targets),'duplicate_expected_references':repeated_expected,'invalid_target_count_rows':invalid_targets,'expected_rows':len(expected),'accounted_rows':len(expected&set(counts)),'missing_rows':sorted(missing_refs),'unexpected_rows':sorted(unknown),'duplicate_dispositions':duplicates,'invalid_status_rows':invalid,'proposed_observations':sum(d.get('target_observations',0) for d in dispositions if type(d.get('target_observations',0)) is int and d.get('target_observations',0)>=0)}
