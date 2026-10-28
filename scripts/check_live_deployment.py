#!/usr/bin/env python3
"""Verify captured live evidence against reviewed SQL/model and its local reference; no DB writes/calls."""
import collections
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name):return json.loads((ROOT/'docs/evidence'/name).read_text())
def require(condition,message):
    if not condition:raise ValueError(message)

def main():
    manifest=load('deployment-manifest.json');expected=load('expected-deployment-catalog.json');live=load('live-deployment-catalog.json')
    access=load('live-access-validation.json');ledger=load('deployed-migration-ledger.json')['migrations']
    model=load('final-model.json');differences=[]
    for category in sorted(set(expected)|set(live)):
        if expected.get(category)!=live.get(category):
            differences.append({'category':category,'expected_only':[x for x in expected.get(category,[]) if x not in live.get(category,[])],
                                'live_only':[x for x in live.get(category,[]) if x not in expected.get(category,[])]})
    (ROOT/'docs/evidence/deployment-catalog-differences.json').write_text(json.dumps(differences,indent=2)+'\n')
    require(not differences,'Live catalog differs from the approved reference')
    require(manifest['project_reference']=='hmlbdozsqxlwzvjimjwh' and manifest['region']=='ap-northeast-1','Wrong target')
    require(len(ledger)==len(manifest['migration_files'])==3,'Migration ledger count mismatch')
    for entry,row in zip(manifest['migration_files'],ledger):
        path=ROOT/entry['file'];require(hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],'Approved SQL changed')
        require(row['name']==path.stem,'MCP ledger/source mapping differs')
    require(len(live['tables'])==model['proposed_table_count']==19,'Wrong table count')
    require({(t['schema'],t['name']) for t in model['tables']}=={(t['schema'],t['name']) for t in live['tables']},'Model/live table set differs')
    for t in model['tables']:
        columns={c['name'] for c in live['columns'] if c['schema']==t['schema'] and c['table']==t['name']}
        require(columns==set(t['fields']),'Model/live column set differs')
    require(all(t['rls'] for t in live['tables']),'RLS missing')
    require(all(t['enabled']=='O' for t in live['triggers']),'Trigger disabled')
    require(all(k['validated'] for k in live['constraints']),'Unvalidated constraint')
    require(all(i['valid'] for i in live['indexes']),'Invalid index')
    require(not any(p['allowed'] for p in live['table_privileges'] if p['role']=='anon'),'Anonymous table grant')
    require(not any(p['allowed'] for p in live['table_privileges'] if p['privilege'] in ('DELETE','TRUNCATE')),'Unintended delete/truncate privilege')
    require(not any(p['execute'] for p in live['function_privileges'] if p['role']=='anon'),'Anonymous function grant')
    require(access['all_passed'] and len(access['checks'])==11 and all(c['passed'] for c in access['checks']),'Live denial check failure')
    require(len(access['record_counts_after_rollback'])==19 and all(v==0 for v in access['record_counts_after_rollback'].values()),'Unexpected application records')
    constraints=collections.Counter(c['type'] for c in live['constraints'])
    result={'status':'passed','project_reference':manifest['project_reference'],'region':manifest['region'],
            'source_commit':manifest['approved_commit'],'remote_migrations_applied':True,
            'catalog_counts':{k:len(v) for k,v in live.items()},'constraint_types':dict(constraints),
            'catalog_exact_match':True,'architecture_differences':[],'all_tables_rls':True,'all_tables_empty':True,
            'live_denial_checks_passed':11,'unauthenticated_table_grants':0,'delete_truncate_grants':0,
            'migration_metadata_difference':'MCP assigned remote version IDs; ledger names retain source file timestamps. Do not blindly use CLI db push against the differing version IDs.',
            'migration_mapping':[{'file':a['file'],'sha256':a['sha256'],'remote_version':b['version'],'remote_name':b['name']} for a,b in zip(manifest['migration_files'],ledger)],
            'security_advisor_disposition':'Two WARN findings for guarded public SECURITY DEFINER RPCs and one INFO for deliberately policy-free private membership table; reviewed controls retained.',
            'limitations':['SQL-role simulations do not verify Google OAuth or HTTP/PostgREST authentication',
                           'No live positive authorized-role workflow or audit event was created; those are covered by separate local synthetic tests',
                           'Data loading, role activation, OAuth and frontend remain outside this authorization']}
    (ROOT/'docs/evidence/deployment-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
