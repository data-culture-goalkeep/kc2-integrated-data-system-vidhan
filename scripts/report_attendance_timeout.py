"""Verify actual stopped state and finalize the unapproved SQL amendment manifest."""
import json
from attendance_execution import E, PACKETS, ROOT, PROJECT, IMPORT, canonical, load, required, sha
from attendance_continue import configuration
from attendance_guard_optimization import W, prepare
from attendance_reconcile import expected
from recovery import atomic_save, source_integrity

OLD = ROOT / 'work/attendance-prefix172'


def main():
    approved, original, old_hash = configuration()
    integrity = source_integrity()
    records = load(PACKETS/'records.json')
    live = load(OLD/'timeout-reconciliation.json')
    required(live['total']==34600 and live['daily_pa_marks']==21103, 'Stopped counts differ')
    buckets=load(OLD/'timeout-payload-buckets.json');required(buckets==expected(records[:34600]), 'Exact committed prefix differs')
    required(load(OLD/'timeout-snapshot.json')==load(OLD/'pre-snapshot.json'), 'Original data changed')
    required(load(OLD/'timeout-prefix-metadata.json')==load(OLD/'pre-prefix-metadata.json'), 'Previous staging rows/timestamps changed')
    required(load(OLD/'timeout-catalog.json')==load(OLD/'pre-catalog.json') and load(OLD/'timeout-ledger.json')==load(OLD/'pre-ledger.json'), 'Schema/security/ledger changed')
    required(load(OLD/'timeout-control.json')['active_imports']==0, 'Import active')
    events=[json.loads(x) for x in (OLD/'journal.jsonl').read_text().splitlines()];previous=None
    for e in events:
        required(e['previous_sha256']==previous and sha(canonical({k:v for k,v in e.items() if k!='sha256'}).encode())==e['sha256'], 'Journal corrupted')
        previous=e['sha256']
    ack=[x for x in events if x['event']=='committed_ack'];failure=[x for x in events if x['event']=='failed_or_uncertain']
    required(len(ack)==1 and ack[0]['index']==172 and len(failure)==1 and failure[0]['index']==173, 'Unexpected execution receipts')
    raw=load(OLD/'receipt-173.json');error=json.loads(raw['content'][0]['text'])['error']['message']
    required(raw['isError'] and '57014' in error and 'statement timeout' in error and 'inline_code_block line 1 at IF' in error, 'Failure cause differs')
    a=load(OLD/'authorization.json');required(not a['active'],'Write approval still active')
    plans={}
    for name in ['original','indexed']:
        root=load(OLD/f'timeout-{name}-explain.json')[0]['QUERY PLAN'][0]['Plan'];nodes=[]
        def walk(n):
            nodes.append({k:n[k] for k in ['Node Type','Join Type','Relation Name','Index Name','Plan Rows','Total Cost'] if k in n})
            for child in n.get('Plans',[]):walk(child)
        walk(root);plans[name]={'root_estimated_cost':root['Total Cost'],'nodes':nodes}
    required(any(x.get('Node Type')=='Seq Scan' for x in plans['original']['nodes']), 'Expected original sequential scan absent')
    required(any(x.get('Index Name')=='attendance_import_staging_pkey' for x in plans['indexed']['nodes']), 'Proposed existing-PK probe absent')
    local=load(E/'attendance-indexed-guard-local-tests.json');required(local['status']=='passed' and all(local['tests'].values()) and local['container_removed'], 'Local fix tests incomplete')
    report={
        'status':'stopped_after_confirmed_statement_timeout','project_reference':PROJECT,'region':'ap-northeast-1',
        'approved_import_manifest_sha256':IMPORT,'approved_continuation_plan_sha256':old_hash,
        'approval_issued_at_ist':a['issued_at_ist'],'approval_expires_at_ist':a['expires_at_ist'],
        'approval_issued_at_utc':a['issued_at'],'approval_expires_at_utc':a['expires_at'],
        'approval_timestamp_basis':a['timestamp_basis'],
        'continuation_transactions_committed':1,'confirmed_total_committed_transactions':173,
        'failed_original_index':173,'failed_request_id':failure[0]['request_id'],'database_error_code':'57014',
        'database_error':'canceling statement due to statement timeout','failure_context':'PL/pgSQL inline replay guard, line 1 at IF',
        'failed_transaction_committed':False,'uncertain_outcomes_remaining':0,'retries':0,
        'remaining_transactions':43,'remaining_records':8560,'next_original_index':173,
        'actual_reconciliation':live,'exact_first_173_transaction_keys_and_full_payloads_match':True,
        'previous_34400_staging_rows_including_timestamps_unchanged':True,'original_19_tables_data_and_audit_unchanged':True,
        'existing_table_counts':{k:v['count'] for k,v in load(OLD/'timeout-snapshot.json').items()},
        'catalog_rls_privileges_triggers_ledger_unchanged':True,'active_imports':0,'authorization_active':False,
        'live_staging_read_denials':load(OLD/'timeout-denials.json'),
        'read_only_query_plans':plans,'proposed_fix_applied_remotely':False,
        'original_statement_timeout_seconds':60,'proposed_statement_timeout_seconds':60,
        'local_amendment_tests':local,'full_migration_complete':False,
        'private_journal_sha256':sha((OLD/'journal.jsonl').read_bytes()),
    }
    (E/'attendance-continuation-timeout-report.json').write_text(json.dumps(report,indent=2)+'\n')
    entries=prepare()
    code=['scripts/attendance_execution.py','scripts/attendance_guard_optimization.py',
          'scripts/attendance_indexed_execution.py','scripts/attendance_indexed_runtime.mjs',
          'scripts/attendance_reconcile.py','scripts/attendance_import.py','scripts/prepare_attendance_manifest.py',
          'scripts/recovery.py','scripts/etl_core.py','scripts/run_attendance_indexed_tests.py']
    manifest={
        'mode':'attendance-indexed-guard-tail-v1','project_reference':PROJECT,'region':'ap-northeast-1','environment':'non-production internal pilot',
        'original_import_manifest_sha256':IMPORT,'previous_approved_continuation_plan_sha256':old_hash,
        'source_snapshot_sha256':integrity['source_snapshot_sha256'],'records_sha256':original['records_sha256'],
        'migration_ledger':load(OLD/'timeout-ledger.json'),'catalog_sha256':sha(canonical(load(OLD/'timeout-catalog.json')).encode()),
        'original_table_fingerprints':load(OLD/'timeout-snapshot.json'),
        'checkpoint':{'committed_batches':173,'staging_records':34600,'next_original_index':173,
                      'journal_sha256':report['private_journal_sha256'],
                      'payload_buckets_sha256':sha(canonical(buckets).encode()),
                      'complete_stage_metadata':load(OLD/'timeout-complete-stage-metadata.json')},
        'batches':entries,'transaction_count':43,'additional_staging_rows':8560,'final_staging_rows':43160,
        'final_daily_pa_marks':24687,'operational_inserts':0,'source_rows_modified':0,'existing_audit_events_added_or_modified':0,
        'sql_amendment':'Add redundant t.id = x.id before the unchanged null-safe full-payload replay predicate. Target id is NOT NULL primary key. INSERT bytes and all remaining checks unchanged.',
        'statement_timeout_seconds':60,'schema_changes':0,'permission_changes':0,
        'must_never_replay_original_indices':'0–172','recovery_policy':'Single-shot ordered transactional requests; stop on first rejection/failure/uncertainty; preserve receipts; no automatic retry',
        'local_test_evidence_sha256':sha((E/'attendance-indexed-guard-local-tests.json').read_bytes()),
        'code_sha256':{f:sha((ROOT/f).read_bytes()) for f in code},
        'owner_authorization_required':True,'execution_authorized':False,
    }
    required(len(entries)==43 and sum(x['rows'] for x in entries)==8560,'Remaining scope mismatch')
    (E/'attendance-indexed-tail-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    digest=sha(canonical(manifest).encode());(E/'attendance-indexed-tail-hash.json').write_text(json.dumps({'indexed_manifest_sha256':digest,'authorized':False},indent=2)+'\n')
    print(canonical({'live_staging_rows':34600,'daily_pa_marks':21103,'remaining_batches':43,'proposed_indexed_manifest_sha256':digest,'remote_fix_executed':False}))


if __name__=='__main__':main()
