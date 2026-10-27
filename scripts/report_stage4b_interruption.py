#!/usr/bin/env python3
"""Preserve an interrupted migration and prepare aggregate evidence, row outcomes and a bounded recovery plan.
No connections, database writes, schema modifications or automatic retries exist in this script.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from etl_core import ROOT,canonical,required,ordered_batches
from prepare_etl import private_save
E=ROOT/'docs/evidence';W=ROOT/'work/remote-etl'

def main():
    manifest=json.loads((W/'manifest.json').read_text());plan=json.loads((ROOT/'work/etl/plan.json').read_text())
    state=json.loads((E/'stage4b-interruption-live-state.json').read_text());proof=json.loads((E/'stage4b-partial-live-reconciliation-verification.json').read_text())
    required(proof['status']=='passed' and proof['source_rows_reconciled']==9988,'Committed prefix not verified')
    after=json.loads((E/'stage4b-after-live-catalog.json').read_text());required(after==json.loads((E/'expected-deployment-catalog.json').read_text()),'Schema/security differs')
    journal_path=W/'execution-journal.jsonl';journal=[json.loads(x) for x in journal_path.read_text().splitlines()]
    acks=[x for x in journal if x['outcome']=='acknowledged'];required(len(acks)==40,'Unexpected prefix size')
    required([(x['phase'],x['index'],x['request_id']) for x in acks]==[(x['phase'],x['index'],x['request_id']) for x in manifest['batches'][:40]],'Prefix sequence differs')
    pending=[x for x in journal if x['outcome']=='submission_pending' and x['request_id'] not in {a['request_id'] for a in acks}]
    required(len(pending)==1 and pending[0]['index']==40,'Unexpected interrupted request')
    batches=list(ordered_batches(plan));committed=[r for b in batches[:40] for r in b];remaining=[r for b in batches[40:] for r in b]
    committed_source={r['values']['id'] for r in committed if r['table']=='source_records'}
    interrupted=set(pending[0]['source_references']);required(len(interrupted)==250,'Unexpected interrupted source-reference count')
    sources={s['reference']:s for s in plan['source_statuses']};ledger=json.loads((ROOT/'work/etl/exception-ledger.json').read_text())
    by_source=defaultdict(Counter);outcomes=[];failures=[]
    for row in ledger:
        loaded=sources[row['reference']]['source_record_id'] in committed_source;affected=row['reference'] in interrupted
        status='source_preserved_staged' if loaded else 'interrupted_request_not_committed' if affected else 'not_attempted_after_stop'
        by_source[row['source_file']][status]+=1
        outcome={'reference':row['reference'],'source_file':row['source_file'],'worksheet':row['worksheet'],'row':row['row'],
          'source_record_id':sources[row['reference']]['source_record_id'],'source_record_loaded':loaded,'live_source_state':'staged' if loaded else 'absent',
          'prepared_disposition':row['status'],'execution_status':status,'operational_projection_status':'not_attempted','target_entities':row['targets'],
          'preparation_findings':row['exceptions'],'resolution':'Preserve committed prefix; separate approved recovery required'}
        outcomes.append(outcome)
        if affected:failures.append({k:outcome[k] for k in ['reference','source_file','worksheet','row','source_record_id','execution_status','resolution']})
    required(len(outcomes)==20432 and sum(x['source_record_loaded'] for x in outcomes)==9988,'Source-outcome totals differ')
    private_save(W/'partial-source-execution-outcomes.json',outcomes);private_save(W/'execution-interruption-exceptions.json',failures)
    all_counts=Counter(r['table'] for r in committed);remaining_counts=Counter(r['table'] for r in remaining)
    expected_keys=json.loads((E/'stage4b-expected-partial-live-checks.json').read_text())
    recovery={'status':'PROPOSED — NOT AUTHORIZED OR EXECUTED','project_reference':'hmlbdozsqxlwzvjimjwh','region':'ap-northeast-1',
      'original_plan_sha256':expected_keys['plan_sha256'],'original_manifest_sha256':expected_keys['manifest_sha256'],
      'confirmed_committed_data_requests':40,'do_not_replay_data_indices':[0,39],'resume_data_indices':[40,136],
      'source_status_indices':[0,81],'remaining_transactions':179,'remaining_data_transactions':97,'remaining_source_status_transactions':82,
      'expected_additional_direct_inserts':{k:remaining_counts.get(k,0) for k in manifest['direct_inserts']},
      'expected_additional_generated_audit_rows':28293,'expected_source_status_updates':20432,
      'verified_prefix_record_key_digests':expected_keys['record_key_digests'],'verified_prefix_source_coordinate_digest':expected_keys['source_coordinate_digest'],
      'remaining_batches':manifest['batches'][40:],'recovery_execution_enabled':False,
      'required_preconditions':['Separate owner approval for reviewed recovery implementation and new execution binding','Fresh exact prefix payload/key/source-coordinate and schema/security verification','No active import transaction or unexpected intervening data','Same original/sanitized source hashes and exact original plan; same remaining SQL request hashes'],
      'required_implementation_review':'Existing approved initial-load bridge deliberately refuses a nonempty target. Preserve that guard and original bound files. Prepare/test a separately reviewed prefix-aware recovery path and binding before requesting permission to execute it.',
      'prohibitions':['No whole-job restart or replay of first 40 data transactions','No reset, repair, deletion or schema/policy changes','No automatic retry, alternate source values or unsupported operational facts']}
    recovery_hash=hashlib.sha256(canonical(recovery).encode()).hexdigest();(E/'stage4b-bounded-recovery-plan.json').write_text(json.dumps(recovery,separators=(',',':'))+'\n')
    run_id=acks[0]['run_id'];tabs={f'S{i:02}':[] for i in range(1,13)}
    for row in failures:
        tabs[row['source_file']].append([row['source_file'],row['reference'],'EXECUTION / NOT COMMITTED: local exec-server transport disconnected. Interrupted request '+pending[0]['request_id']+'. No source row committed for this request; awaiting separately approved bounded recovery.'])
    for source,statuses in sorted(by_source.items()):
        loaded=statuses.get('source_preserved_staged',0);not_loaded=sum(statuses.values())-loaded
        tabs[source].append([source,'EXECUTION / '+run_id[:12],f'EXECUTION / STOPPED: source rows staged={loaded}; not loaded={not_loaded}; interrupted request rows={statuses.get("interrupted_request_not_committed",0)}. No operational projections or source-status finalization ran. Preparation findings remain; separate recovery approval required.'])
    private_save(W/'google-interruption-report-rows.json',tabs)
    receipt={'status':'interrupted_incomplete','project_reference':state['project_reference'],'region':'ap-northeast-1','run_id':run_id,
      'confirmed_committed_transactions':40,'confirmed_direct_inserts':dict(all_counts),'live_counts':state['live_counts'],
      'source_rows_loaded_staged':9988,'source_rows_not_loaded':10444,'source_status_updates':0,'operational_records_loaded':0,'generated_audit_rows':0,
      'interrupted_request':state['interrupted_request'],'interrupted_request_source_rows':250,'other_not_loaded_source_rows':10194,
      'remaining_transactions':179,'remaining_data_transactions':97,'remaining_source_status_transactions':82,
      'schema_security_unchanged':True,'active_import_transactions':0,'source_outcomes':dict(Counter(r['execution_status'] for r in outcomes)),
      'source_rows_by_file':{s:dict(c) for s,c in by_source.items()},'journal_sha256':hashlib.sha256(journal_path.read_bytes()).hexdigest(),
      'private_outcome_ledger':'Ignored work/remote-etl/partial-source-execution-outcomes.json','private_interruption_ledger':'Ignored work/remote-etl/execution-interruption-exceptions.json',
      'google_report_new_rows':{s:len(v) for s,v in tabs.items()},'recovery_plan_sha256':recovery_hash,'recovery_authorized':False,'migration_complete':False,
      'cause':'Approved bridge stopped after exec_command failed: exec-server transport disconnected; no PostgreSQL error response was captured'}
    (E/'stage4b-interrupted-execution-results.json').write_text(json.dumps(receipt,indent=2)+'\n')
    receipts=[{k:a[k] for k in ['phase','index','request_id','outcome','inserted_by_table']} for a in acks]
    (E/'stage4b-committed-transaction-receipts.json').write_text(json.dumps(receipts,separators=(',',':'))+'\n')
    print(json.dumps({k:receipt[k] for k in ['status','confirmed_committed_transactions','source_rows_loaded_staged','source_rows_not_loaded','remaining_transactions','google_report_new_rows','recovery_plan_sha256']}))
if __name__=='__main__':main()
