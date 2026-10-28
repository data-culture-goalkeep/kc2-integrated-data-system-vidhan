#!/usr/bin/env python3
"""Build/read aggregate-only live reconciliation evidence. Never connects or writes to a database."""
from collections import Counter,defaultdict
import argparse
import hashlib
import json
from pathlib import Path
from etl_core import ROOT,model_tables,POINTERS,sql_text,sql_identifier,required,ordered_batches
from prepare_etl import private_save

PLAN_SHA='7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f'
MANIFEST_SHA='8cf2df9dd09a74234b26f1a99c61d17ed7f1f733eca2f016a4f0429c869471b4'
E=ROOT/'docs/evidence';W=ROOT/'work/remote-etl'
def digest(lines):return hashlib.sha256('|'.join(sorted(lines)).encode()).hexdigest()
def table_sql(t):return sql_identifier(t['schema'])+'.'+sql_identifier(t['name'])
def prepare(prefix=False):
    data=(ROOT/'work/etl/plan.json').read_bytes();required(hashlib.sha256(data).hexdigest()==PLAN_SHA,'Approved plan changed')
    plan=json.loads(data);tables=model_tables();records=defaultdict(list)
    units=plan['units']
    if prefix:
        journal=[json.loads(x) for x in (W/'execution-journal.jsonl').read_text().splitlines()]
        acks=[x for x in journal if x['outcome']=='acknowledged']
        required(len(acks)==40 and all(x['phase']=='data' and x['index']==i for i,x in enumerate(acks)),'Unexpected acknowledged prefix')
        units=[r for i,b in enumerate(ordered_batches(plan)) if i<40 for r in [b]]
    for unit in units:
        for r in unit:records[r['table']].append(r['values'])
    expected_keys={};parts=[];checks={};fkparts=[];dates=[];pending=[];lineage=[];audits=Counter()
    catalog=json.loads((E/'expected-deployment-catalog.json').read_text())
    audited={(t['schema'],t['table']) for t in catalog['triggers'] if t['name'].startswith('history_') and 'INSERT' in t['definition']}
    for name,t in tables.items():
        if name=='record_audit_events':continue
        pk=t['primary_key'];lines=['/'.join(str(v[k]) for k in pk) for v in records[name]];expected_keys[name]=digest(lines)
        key=" || '/' || ".join(sql_identifier(k)+'::text' for k in pk)
        parts.append('SELECT '+sql_text(name)+" name,encode(sha256(convert_to(COALESCE(string_agg("+key+",'|' ORDER BY ("+key+") COLLATE \"C\"),''),'UTF8')),'hex') value FROM "+table_sql(t))
        if (t['schema'],name) in audited and records[name]:audits[t['schema']+'.'+name+'/INSERT']=len(records[name])
        if 'origin_kind' in t['fields']:
            pending.append('SELECT count(*) n FROM '+table_sql(t)+" WHERE origin_kind IS DISTINCT FROM 'import' OR review_state IS DISTINCT FROM 'pending'")
            if name in POINTERS:
                pointer=POINTERS[name];pkcol='child_id' if name=='child_private_profiles' else 'id'
                lineage.append('SELECT count(*) n FROM '+table_sql(t)+' x WHERE NOT EXISTS(SELECT 1 FROM gk_private.source_provenance p WHERE p.'+pointer+'=x.'+pkcol+" AND p.contribution_state='selected')")
            elif name=='reference_values':lineage.append("SELECT count(*) n FROM public.reference_values x WHERE NOT EXISTS(SELECT 1 FROM gk_private.source_provenance p WHERE p.reference_vocabulary=x.vocabulary AND p.reference_code=x.code AND p.contribution_state='selected')")
        for c,f in t['fields'].items():
            if f['type']=='date':dates.append('SELECT count(*) n FROM '+table_sql(t)+' WHERE '+sql_identifier(c)+' IS NOT NULL')
        for fk in t['foreign_keys']:
            dest=fk['target'];dt={'schema':'auth','name':'users'} if dest=='auth.users' else tables[dest]
            nonnull=' AND '.join('s.'+sql_identifier(c)+' IS NOT NULL' for c in fk['columns'])
            match=' AND '.join('s.'+sql_identifier(a)+'=d.'+sql_identifier(b) for a,b in zip(fk['columns'],fk['target_columns']))
            label=name+'('+','.join(fk['columns'])+')->'+dest
            fkparts.append('SELECT '+sql_text(label)+' name,count(*) n FROM '+table_sql(t)+' s WHERE '+nonnull+' AND NOT EXISTS(SELECT 1 FROM '+table_sql(dt)+' d WHERE '+match+')')
    # Audit itself also has managed-Auth FKs; all generated actor UUID fields are expected NULL.
    for fk in tables['record_audit_events']['foreign_keys']:
        required(fk['target']=='auth.users','Unexpected audit FK target')
        nonnull=' AND '.join('s.'+sql_identifier(c)+' IS NOT NULL' for c in fk['columns']);match=' AND '.join('s.'+sql_identifier(a)+'=d.'+sql_identifier(b) for a,b in zip(fk['columns'],fk['target_columns']))
        fkparts.append('SELECT '+sql_text('record_audit_events('+','.join(fk['columns'])+')->auth.users')+' name,count(*) n FROM gk_private.record_audit_events s WHERE '+nonnull+' AND NOT EXISTS(SELECT 1 FROM auth.users d WHERE '+match+')')
    if not prefix:audits['gk_private.source_records/UPDATE']=20432
    def summed(parts):return '(SELECT COALESCE(sum(n),0) FROM ('+' UNION ALL '.join(parts)+') q)'
    checks.update({
      'duplicate_child_business_ids':"(SELECT count(*) FROM (SELECT child_business_id FROM public.children GROUP BY child_business_id HAVING count(*)>1) q)",
      'duplicate_caregiver_business_ids':"(SELECT count(*) FROM (SELECT caregiver_business_id FROM gk_private.caregivers GROUP BY caregiver_business_id HAVING count(*)>1) q)",
      'duplicate_child_caregiver_pairs':"(SELECT count(*) FROM (SELECT child_id,caregiver_id FROM public.child_caregivers GROUP BY child_id,caregiver_id HAVING count(*)>1) q)",
      'duplicate_source_coordinates':"(SELECT count(*) FROM (SELECT artifact_id,native_sheet_key,source_row FROM gk_private.source_records GROUP BY artifact_id,native_sheet_key,source_row HAVING count(*)>1) q)",
      'unapproved_operational_rows':"(SELECT (SELECT count(*) FROM public.attendance_observations)+(SELECT count(*) FROM public.adl_visits)+(SELECT count(*) FROM public.support_observations))",
      'memberships_or_role_definitions':"(SELECT (SELECT count(*) FROM gk_private.access_memberships)+(SELECT count(*) FROM public.reference_values WHERE vocabulary='access_role'))",
      'activated_or_privileged_references':"(SELECT count(*) FROM public.reference_values WHERE active OR permissions<>'{}'::jsonb)",
      'accepted_or_nonimported_facts':summed(pending),
      'operational_dates':summed(dates),
      'missing_selected_provenance':summed(lineage),
      'approved_identity_candidates':"(SELECT count(*) FROM gk_private.identity_candidates WHERE resolution_status<>'candidate')",
      'questionnaire_pair_or_definition_mismatch':"(SELECT (SELECT count(*) FROM public.questionnaire_responses r WHERE NOT EXISTS(SELECT 1 FROM public.child_caregivers p WHERE p.id=r.child_caregiver_id))+(SELECT count(*) FROM gk_private.questionnaire_answers a JOIN public.questionnaire_responses r ON r.id=a.response_id JOIN public.questionnaire_items i ON i.id=a.item_id WHERE a.definition_key IS DISTINCT FROM r.definition_key OR a.definition_key IS DISTINCT FROM i.definition_key))",
      'duplicate_audit_key_operation':"(SELECT count(*) FROM (SELECT schema_name,table_name,record_key,operation FROM gk_private.record_audit_events GROUP BY schema_name,table_name,record_key,operation HAVING count(*)>1) q)",
      'nonbackend_audit_actor':"(SELECT count(*) FROM gk_private.record_audit_events WHERE actor_ref NOT LIKE 'db:postgres/%' OR actor_ref IS NULL OR created_by IS NOT NULL OR updated_by IS NOT NULL)",
      'unexpected_audit_operation':"(SELECT count(*) FROM gk_private.record_audit_events WHERE operation NOT IN ('INSERT','UPDATE'))",
      'canonical_child_source_disagreement':"(SELECT count(*) FROM public.children c WHERE NOT EXISTS(SELECT 1 FROM gk_private.source_provenance p JOIN gk_private.source_records s ON s.id=p.source_record_id WHERE p.child_id=c.id AND 'display_name'=ANY(p.target_fields) AND c.child_business_id IS NOT DISTINCT FROM s.cell_payload->>'B' AND c.display_name IS NOT DISTINCT FROM s.cell_payload->>'C'))",
      'canonical_caregiver_source_disagreement':"(SELECT count(*) FROM gk_private.caregivers c WHERE NOT EXISTS(SELECT 1 FROM gk_private.source_provenance p JOIN gk_private.source_records s ON s.id=p.source_record_id WHERE p.caregiver_id=c.id AND c.caregiver_business_id IS NOT DISTINCT FROM s.cell_payload->>'B' AND c.display_name IS NOT DISTINCT FROM s.cell_payload->>'A'))",
      'relationship_source_id_disagreement':"(SELECT count(*) FROM public.child_caregivers x JOIN public.children c ON c.id=x.child_id JOIN gk_private.caregivers g ON g.id=x.caregiver_id WHERE NOT EXISTS(SELECT 1 FROM gk_private.source_provenance p JOIN gk_private.source_records s ON s.id=p.source_record_id WHERE p.child_caregiver_id=x.id AND c.child_business_id IS NOT DISTINCT FROM s.cell_payload->>'C' AND g.caregiver_business_id IS NOT DISTINCT FROM s.cell_payload->>'B'))",
      'questionnaire_source_id_disagreement':"(SELECT count(*) FROM public.questionnaire_responses r JOIN public.child_caregivers x ON x.id=r.child_caregiver_id JOIN public.children c ON c.id=x.child_id JOIN gk_private.caregivers g ON g.id=x.caregiver_id WHERE NOT EXISTS(SELECT 1 FROM gk_private.source_provenance p JOIN gk_private.source_records s ON s.id=p.source_record_id WHERE p.response_id=r.id AND c.child_business_id IS NOT DISTINCT FROM s.cell_payload->>'BA' AND g.caregiver_business_id IS NOT DISTINCT FROM s.cell_payload->>'AZ'))",
      'source_payload_or_coordinates_changed_in_status_updates':"(SELECT count(*) FROM gk_private.record_audit_events WHERE schema_name='gk_private' AND table_name='source_records' AND operation='UPDATE' AND (before_value->'cell_payload' IS DISTINCT FROM after_value->'cell_payload' OR before_value->'artifact_id' IS DISTINCT FROM after_value->'artifact_id' OR before_value->'native_sheet_key' IS DISTINCT FROM after_value->'native_sheet_key' OR before_value->'source_row' IS DISTINCT FROM after_value->'source_row'))",
      'source_status_diagnostic_mismatch':"(SELECT count(*) FROM gk_private.source_records WHERE processing_state IS DISTINCT FROM CASE diagnostics->>'planned_status' WHEN 'successfully_transformed' THEN 'resolved' WHEN 'preserved_as_source_only' THEN 'reference_only' WHEN 'awaiting_identity_resolution' THEN 'blocked' WHEN 'awaiting_business_rule_approval' THEN 'blocked' ELSE 'invalid' END)"})
    if prefix:checks['source_status_diagnostic_mismatch']="(SELECT count(*) FROM gk_private.source_records WHERE processing_state<>'staged')"
    source_coords=[v['artifact_id']+'/'+v['native_sheet_key']+'/R'+str(v['source_row']) for v in records['source_records']]
    expected={'plan_sha256':PLAN_SHA,'manifest_sha256':MANIFEST_SHA,'record_key_digests':expected_keys,'source_coordinate_digest':digest(source_coords),'audit_by_table_operation':dict(audits),'zero_checks':{k:0 for k in checks},'foreign_key_checks':len(fkparts),'source_states':{'resolved':1194,'reference_only':15301,'blocked':3937},'planned_dispositions':{'successfully_transformed':1194,'preserved_as_source_only':15301,'awaiting_identity_resolution':3623,'awaiting_business_rule_approval':314},'linked_children':370,'missing_numeric_answers':86}
    if prefix:
        expected.update(source_states={'staged':len(records['source_records'])},planned_dispositions=dict(Counter(v['diagnostics']['planned_status'] for v in records['source_records'])),linked_children=0,missing_numeric_answers=0)
    stem='partial' if prefix else 'full'
    sql="BEGIN READ ONLY; SELECT jsonb_build_object(\n"
    sql+="'record_key_digests',(SELECT jsonb_object_agg(name,value) FROM ("+' UNION ALL '.join(parts)+") ids),\n"
    sql+="'source_coordinate_digest',(SELECT encode(sha256(convert_to(COALESCE(string_agg(artifact_id::text||'/'||native_sheet_key||'/R'||source_row::text,'|' ORDER BY (artifact_id::text||'/'||native_sheet_key||'/R'||source_row::text) COLLATE \"C\"),''),'UTF8')),'hex') FROM gk_private.source_records),\n"
    sql+="'audit_by_table_operation',(SELECT COALESCE(jsonb_object_agg(name,n),'{}'::jsonb) FROM (SELECT schema_name||'.'||table_name||'/'||operation name,count(*) n FROM gk_private.record_audit_events GROUP BY schema_name,table_name,operation) q),\n"
    sql+="'source_states',(SELECT jsonb_object_agg(processing_state,n) FROM (SELECT processing_state,count(*) n FROM gk_private.source_records GROUP BY processing_state) q),\n"
    sql+="'planned_dispositions',(SELECT jsonb_object_agg(status,n) FROM (SELECT diagnostics->>'planned_status' status,count(*) n FROM gk_private.source_records GROUP BY diagnostics->>'planned_status') q),\n"
    sql+="'linked_children',(SELECT count(DISTINCT child_id) FROM public.child_caregivers),\n"
    sql+="'missing_numeric_answers',(SELECT count(*) FROM gk_private.questionnaire_answers a JOIN public.questionnaire_items i ON i.id=a.item_id WHERE i.value_kind='numeric' AND a.answer_state='missing' AND a.numeric_value IS NULL),\n"
    sql+="'foreign_key_violations',(SELECT COALESCE(jsonb_object_agg(name,n) FILTER(WHERE n<>0),'{}'::jsonb) FROM ("+' UNION ALL '.join(fkparts)+") f),\n"
    sql+="'zero_checks',jsonb_build_object("+','.join(sql_text(k)+','+v for k,v in checks.items())+")) AS reconciliation; COMMIT;\n"
    private_save(W/('expected-'+stem+'-live-checks.json'),expected)
    path=W/('verify-'+stem+'-live-data.sql');path.write_text(sql);path.chmod(0o600)
    (E/('stage4b-expected-'+stem+'-live-checks.json')).write_text(json.dumps(expected,indent=2)+'\n')
    print(json.dumps({'read_only_sql_prepared':True,'foreign_key_checks':len(fkparts),'tables_with_expected_row_key_digests':len(expected_keys),'query_bytes':len(sql.encode())}))

def check(prefix=False):
    stem='partial' if prefix else 'full'
    expected=json.loads((W/('expected-'+stem+'-live-checks.json')).read_text());actual=json.loads((E/('stage4b-'+stem+'-live-data-checks.json')).read_text())
    differences={k:{'expected':v,'actual':actual.get(k)} for k,v in expected.items() if k not in ['plan_sha256','manifest_sha256','foreign_key_checks'] and actual.get(k)!=v}
    required(actual.get('foreign_key_violations')=={},'Live FK violation detected')
    report={'status':'passed' if not differences else 'failed','differences':differences,'foreign_key_checks':expected['foreign_key_checks'],'record_key_set_tables':len(expected['record_key_digests']),'source_rows_reconciled':sum(expected['source_states'].values()) if not differences else None,'scope':'Live key sets, source coordinates/statuses, relationships, provenance, audit and excluded categories; does not approve business meaning'}
    (E/('stage4b-'+stem+'-live-reconciliation-verification.json')).write_text(json.dumps(report,indent=2)+'\n');required(not differences,'Live reconciliation differs from approved plan');print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--prefix',action='store_true');args=p.parse_args()
    check(args.prefix) if args.check else prepare(args.prefix)
