#!/usr/bin/env python3
"""Validate captured preflight and isolated adapter evidence. Never opens a database."""
from collections import Counter
import hashlib
import json
import re
from etl_core import ROOT,required,canonical
from remote_etl import prepared,PROJECT,REGION

def read(name):return json.loads((ROOT/'docs/evidence'/name).read_text())
def main():
    live=read('stage4b-live-preflight.json');catalog=read('stage4b-live-catalog.json')
    required(live['project_reference']==PROJECT and live['region']==REGION,'Wrong target')
    required(catalog==read('expected-deployment-catalog.json'),'Live schema/security drift')
    required(len(live['counts'])==19 and all(n==0 for n in live['counts'].values()),'Unexpected live data')
    required(live['migrations']==read('deployed-migration-ledger.json')['migrations'],'Ledger drift')
    p=live['permissions'];required(p['database_role']==p['session_role']=='postgres' and p['server_version_num']==170011,'Migration identity/version mismatch')
    required(len(p['effective_privileges'])==19 and all(all(x[k] for k in ['select','insert','update','schema_usage']) for x in p['effective_privileges']),'Insufficient migration permissions')
    required(all(t['rls'] for t in catalog['tables']),'RLS changed')
    required(not any(x['allowed'] for x in catalog['table_privileges'] if x['role']=='anon' or x['privilege'] in ['DELETE','TRUNCATE']),'Application privileges widened')
    source=read('stage4b-source-verification.json');required(source['all_twelve_drive_versions_unchanged'] and len(source['files'])==12 and all(x['modified_time_unchanged'] for x in source['files']),'Drive versions changed')
    required(source['private_failure_destination_verified'] and source['google_report_shared'] is False,'Failure destination not private')
    plan,requests,manifest=prepared();summary=read('stage4b-batch-manifest.json');runtime=read('stage4b-adapter-runtime.json')
    required(summary['manifest_sha256']==hashlib.sha256(canonical(manifest).encode()).hexdigest(),'Prepared manifest changed')
    required(summary['plan_sha256']==runtime['plan_sha256']==read('etl-preparation.json')['plan_sha256'],'Bundle changed')
    required(runtime['code_sha256']==manifest['code_sha256'],'Adapter tests do not bind current code')
    required(runtime['status']=='passed' and runtime['runtime_cases']==9 and runtime['failures']==runtime['errors']==0 and runtime['container_removed'],'Isolated adapter tests failed')
    required(runtime['replay_insertions']==0 and runtime['all_counts_and_audit_unchanged'],'Replay changed data or history')
    required(runtime['target_reconciliation']['status']=='passed' and runtime['target_reconciliation']['audit_rows_database_generated']==28293,'Target/audit mismatch')
    required(read('stage4b-bridge-tests.json')['bridge_sha256']==manifest['code_sha256']['mcp_etl_bridge.mjs'],'Bridge test evidence stale')
    unit_log=(ROOT/'work/stage4b-unit-tests.txt').read_text();required(re.search(r'Ran 64 tests',unit_log) and unit_log.rstrip().endswith('OK'),'Python tests incomplete')
    required(read('stage4b-bridge-tests.json')['status']=='passed' and read('stage4b-bridge-tests.json')['tests']==9,'Bridge tests failed')
    required(read('stage4b-live-bridge.json')['status']=='passed' and read('stage4b-live-bridge.json')['remote_data_writes']==0,'Live default-readonly bridge unverified')
    capacity=read('stage4b-mcp-capacity.json');required(capacity['status']=='passed' and capacity['sql_bytes']>=summary['max_batch_sql_bytes'] and capacity['receipt_rows']==250,'Batch exceeds verified transport capacity')
    required(summary['data_batches']==137 and summary['status_batches']==82 and summary['max_records']<=250,'Batch bounds/order count changed')
    required(sum(summary['direct_inserts'].values())==34077 and summary['generated_audit_inserts']==28293 and summary['source_record_updates']==20432,'Write budget changed')
    required(not manifest['remote_write_authorized'] and not (ROOT/'work/remote-etl/owner-authorization.json').exists(),'Preflight must not activate authorization')
    for f in read('deployment-manifest.json')['migration_files']:required(hashlib.sha256((ROOT/f['file']).read_bytes()).hexdigest()==f['sha256'],'Applied migration changed')
    ledger=json.loads((ROOT/'work/etl/exception-ledger.json').read_text());statuses=Counter(x['status'] for x in ledger)
    required(statuses=={'successfully_transformed':1194,'preserved_as_source_only':15301,'awaiting_identity_resolution':3623,'awaiting_business_rule_approval':314},'Exception/source totals changed')
    result={'status':'passed','project_reference':PROJECT,'region':REGION,'server_version':'17.11','plan_sha256':summary['plan_sha256'],'manifest_sha256':summary['manifest_sha256'],'source_rows':20432,'direct_expected_inserts':34077,'expected_generated_audit_inserts':28293,'expected_source_updates':20432,'expected_total_row_mutations':82802,'data_batches':137,'status_batches':82,'python_tests':64,'offline_bridge_tests':9,'local_database_cases':9,'remote_write_tests':0,'remote_schema_differences':0,'live_all_tables_empty':True,'owner_authorization_still_required':True,'scope':'Sanitized source preservation plus verified-ID literal pending projections only','ready_for_owner_authorization':True,'business_rules_validated':False}
    (ROOT/'docs/evidence/stage4b-preflight-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
