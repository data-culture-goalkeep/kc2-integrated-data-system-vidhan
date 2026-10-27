"""Deterministic ETL contracts and SQL compiler. Does not open a remote connection."""
from collections import Counter
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
import uuid

ROOT=Path(__file__).resolve().parents[1]
VERSION='kc2-etl-v1'
NS=uuid.uuid5(uuid.NAMESPACE_URL,'goalkeep.net/kc2/sanitized-pilot')
FORBIDDEN={'access_memberships','record_audit_events'}
POINTERS={'children':'child_id','child_private_profiles':'private_profile_child_id','caregivers':'caregiver_id',
 'child_caregivers':'child_caregiver_id','program_changes':'program_change_id','questionnaire_responses':'response_id',
 'questionnaire_items':'item_id','questionnaire_answers':'answer_id','attendance_observations':'attendance_id',
 'support_observations':'support_id','adl_visits':'adl_id'}
STATUSES={'successfully_transformed','preserved_as_source_only','awaiting_identity_resolution',
          'awaiting_business_rule_approval','rejected_validation'}

def stable_id(*parts):return str(uuid.uuid5(NS,json.dumps(parts,ensure_ascii=False,separators=(',',':'))))
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def fingerprint(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def reference(source,sheet,row):return f'{source}/{sheet}/R{row}'
def model_tables():return {t['name']:t for t in json.loads((ROOT/'docs/evidence/final-model.json').read_text())['tables']}
def required(ok,message):
    if not ok:raise ValueError(message)

def validate_record(record,tables=None):
    tables=tables or model_tables();name=record['table'];values=record['values']
    required(name in tables and name not in FORBIDDEN,'Disallowed ETL target')
    spec=tables[name]
    required(set(values)<=set(spec['fields']),'Unknown target column')
    required(not set(values)&{'created_at','updated_at','created_by','updated_by','actor_ref','archived_at','archived_by'},'ETL cannot forge audit/archive fields')
    required(not any(c.endswith('_vocabulary') and c!='reference_vocabulary' for c in values),'ETL cannot override generated vocabulary')
    for key in spec['primary_key']:required(values.get(key) is not None,'Missing deterministic primary key')
    if 'origin_kind' in spec['fields']:required(values.get('origin_kind')=='import' and values.get('review_state')=='pending','Imported facts must remain pending')
    if name=='reference_values':
        required(values['vocabulary']!='access_role' and values.get('active') is False and values.get('permissions')=={},'No role definition or approved vocabulary activation')
    for key,value in values.items():sql_value(value,spec['fields'][key]['type'],key)
    return True

def sql_identifier(value):
    required(re.fullmatch('[a-z_][a-z_0-9]*',value) is not None,'Invalid SQL identifier')
    return '"'+value+'"'

def sql_text(value):
    required(isinstance(value,str) and '\x00' not in value,'Invalid PostgreSQL text')
    return "E'"+value.replace("\\","\\\\").replace("'","''")+"'"

def sql_value(value,typ,field=''):
    if value is None:return "'null'::jsonb" if typ=='jsonb' and field=='original_value' else 'NULL::'+typ
    if typ=='jsonb':return sql_text(canonical(value))+'::jsonb'
    if typ=='text[]':
        required(isinstance(value,list) and all(isinstance(x,str) for x in value),'Invalid text array')
        return 'ARRAY['+','.join(sql_text(x) for x in value)+']::text[]'
    if typ=='uuid':return sql_text(str(uuid.UUID(value)))+'::uuid'
    if typ=='boolean':
        required(type(value) is bool,'Invalid boolean')
        return 'true' if value else 'false'
    if typ in {'numeric','integer'}:
        required(type(value) in {int,float} and math.isfinite(value),'Invalid numeric')
        required(typ!='integer' or type(value) is int,'Invalid integer')
        return str(value)+'::'+typ
    if typ=='date':return sql_text(date.fromisoformat(value).isoformat())+'::date'
    required(typ=='text','Unsupported ETL type')
    return sql_text(value)

def dollar_block(body):
    tag='$etl_'+hashlib.sha256(body.encode()).hexdigest()+'$'
    required(tag not in body,'Unexpected dollar tag collision')
    return tag+body+tag

def compile_record(record,tables=None):
    tables=tables or model_tables();validate_record(record,tables);spec=tables[record['table']];v=record['values']
    q=sql_identifier(spec['schema'])+'.'+sql_identifier(spec['name'])
    columns=list(v);literals={c:sql_value(v[c],spec['fields'][c]['type'],c) for c in columns}
    keys=','.join(sql_identifier(c) for c in spec['primary_key'])
    insert=f"INSERT INTO {q} ({','.join(sql_identifier(c) for c in columns)}) VALUES ({','.join(literals[c] for c in columns)}) ON CONFLICT ({keys}) DO NOTHING RETURNING 1"
    receipt=f"WITH inserted AS ({insert}) SELECT jsonb_build_object('table',{sql_text(spec['name'])},'inserted',count(*)) FROM inserted;"
    # Audit/default fields are deliberately excluded. Mutable source processing diagnostics are not identity payload.
    compared=[c for c in columns if not(spec['name']=='source_records' and c in {'processing_state','diagnostics'})]
    predicate=' AND '.join(sql_identifier(c)+' IS NOT DISTINCT FROM '+literals[c] for c in compared)
    body=f"BEGIN IF NOT EXISTS(SELECT 1 FROM {q} WHERE {predicate}) THEN RAISE EXCEPTION 'ETL_EXISTING_PAYLOAD_CONFLICT'; END IF; END;"
    return receipt+'\nDO '+dollar_block(body)+';\n'

def compile_batch(records,tables=None):
    tables=tables or model_tables()
    return "BEGIN; SET LOCAL standard_conforming_strings=on; SET LOCAL lock_timeout='5s'; SET LOCAL statement_timeout='60s';\n"+''.join(compile_record(r,tables) for r in records)+"SET CONSTRAINTS ALL IMMEDIATE; COMMIT;\n"

def ordered_batches(plan,batch_size=250):
    required(1<=batch_size<=500,'Batch size outside approved bounds')
    batch=[]
    for unit in plan['units']:
        required(len(unit)<=batch_size,'Oversized atomic unit')
        if batch and len(batch)+len(unit)>batch_size:
            yield batch;batch=[]
        batch.extend(unit)
    if batch:yield batch

def validate_plan(plan):
    tables=model_tables();seen=set();indexes={}
    for unit in plan['units']:
        for r in unit:
            validate_record(r,tables);spec=tables[r['table']];v=r['values'];pk=tuple(v[c] for c in spec['primary_key'])
            required((r['table'],pk) not in seen,'Duplicate target identity in plan');seen.add((r['table'],pk))
            for cols in [spec['primary_key']]+spec['unique_keys']:
                if all(v.get(c) is not None for c in cols):
                    bucket=indexes.setdefault((r['table'],tuple(cols)),set());values=tuple(v[c] for c in cols)
                    required(values not in bucket,'Conflicting business uniqueness in plan');bucket.add(values)
    namespaces={'program_vocabulary':'program','status_vocabulary':'child_status','centre_vocabulary':'centre','definition_vocabulary':'questionnaire_definition','service_vocabulary':'service_context','mark_vocabulary':'attendance_mark','role_vocabulary':'caregiver_role'}
    for unit in plan['units']:
        for r in unit:
            for fk in tables[r['table']]['foreign_keys']:
                if fk['target']=='auth.users':continue
                vals=[namespaces[c] if c in namespaces else r['values'].get(c) for c in fk['columns']]
                if any(x is None for x in vals):continue
                required(tuple(vals) in indexes.get((fk['target'],tuple(fk['target_columns'])),set()),'Missing foreign-key target in plan')
    return {'target_rows':sum(len(u) for u in plan['units']),'by_table':dict(Counter(r['table'] for u in plan['units'] for r in u))}

def reconcile_rows(expected,ledger):
    expected=list(expected);counts=Counter(r['reference'] for r in ledger)
    required(len(set(expected))==len(expected),'Repeated source identity')
    required(set(expected)==set(counts) and all(n==1 for n in counts.values()),'Source row lost, duplicated or invented')
    required(all(r['status'] in STATUSES for r in ledger),'Unknown processing status')
    return {'source_rows':len(expected),'extracted_rows':len(ledger),'by_status':dict(Counter(r['status'] for r in ledger)),
            'loaded_remotely':0,'missing_rows':0,'duplicate_dispositions':0}

def sanitized_recovery_overlay(rows,actions):
    """Use sanitized donor cells, never raw values from the protected recovery evidence.
    Date recovery remains suggested until date-fidelity approval; contradictory/unknown actions never fill.
    """
    overlays={};evidence=[]
    for action in actions:
        target=action['target_reference'];donor=action['source_reference'];column=action['source_column'];donor_col=action['donor_column']
        required(target in rows and donor in rows,'Recovery reference not in extraction')
        old=rows[target]['cells'].get(column);value=rows[donor]['cells'].get(donor_col)
        missing_old=old is None or isinstance(old,str) and not old.strip()
        nonmissing=value is not None and not(isinstance(value,str) and not value.strip())
        flags=all(action.get(k) is True for k in ['identity_verified','authoritative_source','meaning_equivalent']) and action.get('has_conflict') is False
        safe=(action['validation_status']=='auto_recovered' and flags and missing_old and nonmissing
              and action['field_key'] in {'display_name','gender_reported'})
        status='auto_recovered' if safe else 'blocked_conflict' if action.get('has_conflict') else 'suggested'
        if safe:
            key=(target,column)
            required(key not in overlays or overlays[key]==value,'Conflicting recovery overlay')
            overlays[key]=value
        evidence.append({**{k:v for k,v in action.items() if k not in {'original_value','recovered_value'}},
                         'original_value':old,'recovered_value':value,'validation_status':status})
    return overlays,evidence
