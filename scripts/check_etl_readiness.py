#!/usr/bin/env python3
"""Check private bundle coverage and captured local/remote evidence; performs no database writes."""
import csv
import hashlib
import json
from pathlib import Path
from etl_core import ROOT,validate_plan,reconcile_rows,required,model_tables

def read(path):return json.loads((ROOT/path).read_text())
def main():
    e='docs/evidence/'
    prep=read(e+'etl-preparation.json');runtime=read(e+'etl-runtime-tests.json')
    plan_bytes=(ROOT/'work/etl/plan.json').read_bytes();plan=json.loads(plan_bytes)
    digest=hashlib.sha256(plan_bytes).hexdigest()
    required(digest==prep['plan_sha256']==runtime['plan_sha256'],'Tested bundle hash differs')
    required(plan['remote_loading_authorized'] is False and plan['sanitized'],'Unapproved or unsanitized plan')
    stats=validate_plan(plan)
    expected=read('work/recovery/expected-source-references.json');ledger=read('work/etl/exception-ledger.json')
    reconciliation=reconcile_rows(expected,ledger)
    required(reconciliation==prep['reconciliation'],'Source reconciliation changed')
    required(stats['target_rows']==34077 and reconciliation['source_rows']==20432,'Unexpected bundle counts')
    required(prep['identities']=={'children':371,'caregivers':716,'child_caregiver_pairs':716,'linked_children':370,'questionnaire_pairs':106,'source_name_disagreements':60},'Identity evidence differs')
    records=[r for u in plan['units'] for r in u]
    tables=model_tables()
    for record in records:
        name=record['table'];v=record['values']
        required(name not in {'access_memberships','record_audit_events'},'Forbidden direct insert')
        for key,field in tables[name]['fields'].items():
            if field['type']=='date':required(v.get(key) is None,'Operational date projected before fidelity approval')
        if 'origin_kind' in tables[name]['fields']:required(v['origin_kind']=='import' and v['review_state']=='pending','Fact unexpectedly accepted')
        if name=='reference_values':required(not v['active'] and v['permissions']=={} and v['vocabulary']!='access_role','Access or categories activated')
    mappings=list(csv.DictReader((ROOT/e/'etl-source-target-mapping.csv').open()))
    frozen=list(csv.DictReader((ROOT/e/'final-source-target-coverage.csv').open()))
    coordinates=lambda rows:{(x['source'],x['sheet'],x['column']) for x in rows}
    required(len(mappings)==len(coordinates(mappings))==5186 and coordinates(mappings)==coordinates(frozen),'Mapping coordinate loss or duplicate')
    required(all(x['mapping_class'] in {'CONFIRMED','TECHNICAL','PENDING'} and x['source_retention'] for x in mappings),'Unclassified or unretained column')
    contracts=read(e+'etl-worksheet-contracts.json');required(len(contracts)==155,'Worksheet contract missing')
    manifest_columns=sum(len(s['columns']) for r in records if r['table']=='source_artifacts' for s in r['values']['worksheet_manifest'].values())
    required(manifest_columns==5186,'Source header lineage loss')
    drive=read(e+'etl-drive-verification.json');required(drive['files']==12 and drive['worksheets']==155 and all(x['modified_time_unchanged'] for x in drive['sources']),'Source versions changed')
    manifest=read('work/source-intake/private-manifest.json');profile=read(e+'data-profile.json')
    for item in manifest:required(hashlib.sha256(Path(item['original_path']).read_bytes()).hexdigest()==item['sha256'],'Original snapshot changed')
    for source in profile['sources']:
        for sheet,want in source['sanitized_sha256'].items():
            required(hashlib.sha256((ROOT/'work/source-intake/sanitized'/f"{source['source']}_{sheet}.jsonl").read_bytes()).hexdigest()==want,'Sanitized snapshot changed')
    required(runtime['status']=='passed' and runtime['negative_and_transaction_tests']==9 and runtime['container_removed'],'Runtime tests incomplete')
    required(runtime['second_load']['inserted']==0 and runtime['second_load']['all_table_counts_unchanged'],'Replay not idempotent')
    required(runtime['target_reconciliation']['status']=='passed' and runtime['target_reconciliation']['audit_rows_database_generated']==prep['expected_generated_audit_rows']==28293,'Audit/count reconciliation failed')
    remote=read(e+'etl-remote-readonly.json')
    required(remote['project_reference']=='hmlbdozsqxlwzvjimjwh' and remote['region']=='ap-northeast-1' and len(remote['application_table_counts'])==19 and all(n==0 for n in remote['application_table_counts'].values()),'Remote target changed or nonempty')
    deployed=read(e+'deployment-manifest.json')
    for item in deployed['migration_files']:required(hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest()==item['sha256'],'Applied migration altered')
    report=read(e+'etl-google-failure-log.json');report_plan=read(e+'etl-failure-log-plan.json')
    required(report['private_owner_only'] and report['total_rows']==report_plan['total_rows']==11222 and len(report['tabs'])==12 and all(t['full_readback_equal'] for t in report['tabs']),'Failure report unverified')
    for number in range(22,27):required(len(list((ROOT/'docs').glob(str(number)+'-*.md')))==1,'Required documentation missing')
    result={'status':'passed','plan_sha256':digest,'source_rows_reconciled':20432,'source_columns_retained':5186,'worksheets':155,'files':12,'target_records_local':34077,'generated_audit_local':28293,'runtime_negative_tests':9,'idempotent_replay_insertions':0,'remote_records_loaded':0,'remote_all_tables_empty':True,'google_report_rows_verified':11222,'scope':prep['ready_scope'],'business_rules_validated':False,'remote_loading_authorized':False,'execution_gates':['Explicit Stage 4B authorization','Destination-bound executor and fresh target/source/schema preflight'],'operational_category_gates':prep['unsupported_operational_categories']+['date fidelity','canonical categories and scoring','unverified parent crosswalk and sensitive numeric retention']}
    (ROOT/e/'etl-readiness.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
