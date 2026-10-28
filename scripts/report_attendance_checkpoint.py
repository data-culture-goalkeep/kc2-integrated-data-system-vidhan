"""Validate captured partial live state and prepare a bounded, unapproved continuation.

Never connects to a database, retries SQL, rewrites receipts or grants approval.
"""
import json
from datetime import datetime, timezone

from attendance_execution import E, IMPORT, PACKETS, PROJECT, ROOT, canonical, load, manifests, required, sha
from attendance_reconcile import expected
from recovery import atomic_save, source_integrity

W = ROOT / 'work/attendance-resumption'


def main():
    _, manifest = manifests()
    integrity = source_integrity()
    required(integrity['source_snapshot_sha256'] == manifest['source_snapshot_sha256'], 'Source changed')
    events = [json.loads(s) for s in (W / 'journal.jsonl').read_text().splitlines()]
    previous = None
    for event in events:
        value = {k: v for k, v in event.items() if k != 'sha256'}
        required(event['previous_sha256'] == previous and sha(canonical(value).encode()) == event['sha256'], 'Journal chain changed')
        previous = event['sha256']
    acknowledged = [e for e in events if e['event'] == 'committed_ack']
    submitted = [e for e in events if e['event'] == 'submitted']
    required(len(acknowledged) == 171 and len(submitted) == 172, 'Unexpected checkpoint')
    for n, event in enumerate(submitted):
        required(event['index'] == n and event['request_id'] == manifest['batches'][n]['request_id'] and event['query_sha256'] == manifest['batches'][n]['query_sha256'], 'Request mismatch')
    for n, event in enumerate(acknowledged):
        required(event['index'] == n and event['request_id'] == manifest['batches'][n]['request_id'], 'Receipt mismatch')
    records = load(PACKETS / 'records.json')
    prefix = records[:34400]
    buckets = load(W / 'interruption-payload-buckets.json')
    required(buckets == expected(prefix), 'Actual keys/full payloads do not match exact first 172 transactions')
    required(load(W / 'pre-snapshot.json') == load(W / 'interruption-snapshot.json'), 'Original data changed')
    required(load(W / 'pre-catalog.json') == load(W / 'interruption-catalog.json'), 'Schema/security changed')
    required(load(W / 'pre-ledger.json') == load(W / 'interruption-ledger.json'), 'Ledger changed')
    control = load(W / 'interruption-control.json')
    required(control['staging_rows'] == 34400 and control['active_imports'] == 0, 'Unexpected active import or count')
    live = load(W / 'interruption-reconciliation.json')
    required(live['total'] == 34400 and live['daily_pa_marks'] == 20995, 'Live totals differ')
    for key in ['duplicate_coordinates', 'parsed_dates', 'verified_children', 'invalid_source_links', 'source_mark_disagreements', 'header_disagreements', 'invalid_candidates', 'operational_attendance']:
        required(live[key] == 0, 'Unexpected data: ' + key)
    required(live['reviews'] == {'pending': 34400} and live['codes'] == {'PENDING': 34400}, 'Unapproved promotion')
    authorization = load(W / 'authorization.json')
    required(not authorization['active'], 'Authorization still active')
    import attendance_execution as execution
    execution.W = W
    if not any(e['event'] == 'commit_verified_readonly' for e in events):
        execution.append({'event': 'commit_verified_readonly', 'index': 171,
                          'request_id': submitted[-1]['request_id'],
                          'evidence': 'Exact expected first-172-batch IDs and full payload aggregate hashes match live state; no active import',
                          'payload_bucket_sha256': sha(canonical(buckets).encode()),
                          'acknowledgement_recovered': False})
        execution.append({'event': 'execution_stopped', 'confirmed_committed_batches': 172, 'next_original_index': 172,
                          'remote_write_mode': False, 'requires_new_checkpoint_authorization': True})
    summary = {
        'status': 'interrupted_exact_committed_prefix_verified_readonly',
        'project_reference': PROJECT, 'region': 'ap-northeast-1',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'import_manifest_sha256': IMPORT, 'approved_resumption_plan_sha256': authorization['resumption_plan_sha256'],
        'approval_issued_at_utc': authorization['issued_at'], 'approval_expires_at_utc': authorization['expires_at'],
        'approval_timestamp_basis': authorization['timestamp_basis'],
        'acknowledged_transactions': 171, 'additional_live_verified_commit': {'index': 171, 'request_id': submitted[-1]['request_id']},
        'confirmed_committed_transactions': 172, 'server_failed_transactions': 0,
        'uncertain_transaction_outcomes_remaining': 0, 'retries': 0,
        'remaining_transactions': 44, 'next_original_index': 172, 'remaining_records': 8760,
        'actual_reconciliation': live, 'exact_prefix_keys_and_full_payloads_match': True,
        'missing_or_unexplained_records_within_committed_prefix': 0,
        'original_19_tables_counts_and_full_payload_fingerprints_unchanged': True,
        'schema_rls_privileges_triggers_ledger_unchanged': True,
        'live_read_denials': load(W / 'interruption-denials.json'), 'active_imports': 0,
        'journal_sha256': sha((W / 'journal.jsonl').read_bytes()), 'authorization_active': False,
        'interruption_evidence': 'Wait tool returned aborted by user; execution cell 119 subsequently not found. Request 171 was submitted without a journaled acknowledgement. Read-only exact-prefix comparison establishes that it committed.',
        'migration_complete': False,
    }
    (E / 'attendance-import-interrupted-checkpoint.json').write_text(json.dumps(summary, indent=2) + '\n')
    code = ['scripts/attendance_execution.py', 'scripts/attendance_resume.py',
            'scripts/attendance_reconcile.py', 'scripts/attendance_mcp_runtime.mjs',
            'scripts/attendance_import.py', 'scripts/prepare_attendance_manifest.py',
            'scripts/attendance_continue.py']
    plan = {
        'mode': 'separately-authorized-attendance-prefix-172-continuation',
        'project_reference': PROJECT, 'region': 'ap-northeast-1', 'environment': 'non-production internal pilot',
        'original_import_manifest_sha256': IMPORT,
        'previous_approved_resumption_plan_sha256': authorization['resumption_plan_sha256'],
        'migration_ledger': load(W / 'interruption-ledger.json'),
        'baseline_catalog_sha256': sha(canonical(load(W / 'interruption-catalog.json')).encode()),
        'original_table_fingerprints': load(W / 'interruption-snapshot.json'),
        'source_snapshot_sha256': manifest['source_snapshot_sha256'], 'records_sha256': manifest['records_sha256'],
        'committed_prefix': {'transactions': 172, 'staging_rows': 34400,
                             'expected_payload_buckets_sha256': sha(canonical(buckets).encode()),
                             'journal_sha256': summary['journal_sha256'],
                             'acknowledged_transactions': 171, 'last_commit_verified_readonly_index': 171},
        'remaining_original_indices': {'first': 172, 'last': 215, 'count': 44},
        'batches': manifest['batches'][172:],
        'expected_additional_staging_rows': 8760, 'expected_final_staging_rows': 43160,
        'expected_final_daily_pa_marks': 24687, 'expected_operational_inserts': 0,
        'source_records_modified': 0, 'existing_audit_events_added_or_modified': 0,
        'schema_changes': False, 'reapply_migration': False,
        'scope': 'Only unchanged original packets 172–215. Never replay any of 0–171. Preserve pending values, identities, dates and codes.',
        'preflight': 'Fresh exact target/catalog/ledger/source hashes, no active import, exact 34400-row payload checkpoint and unchanged original data. Separate owner evidence with explicit window.',
        'execution': 'New checkpoint-mode journal linked to prior journal; ordered single-shot transactional dispatch and durable receipts; live full reconciliation before completion.',
        'failure_rule': 'Stop on first failed, rejected or uncertain request; inspect read-only; no automatic retry/reset/delete',
        'code_sha256': {f: sha((ROOT / f).read_bytes()) for f in code},
        'owner_authorization_required': True, 'execution_authorized': False,
    }
    required(sum(b['rows'] for b in plan['batches']) == 8760, 'Remaining count mismatch')
    (E / 'attendance-prefix172-continuation-plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    digest = sha(canonical(plan).encode())
    (E / 'attendance-prefix172-continuation-hash.json').write_text(json.dumps({'continuation_plan_sha256': digest, 'authorized': False}, indent=2) + '\n')
    print(canonical({'confirmed_committed_transactions': 172, 'live_records': 34400,
                     'remaining_transactions': 44, 'remaining_records': 8760,
                     'continuation_plan_sha256': digest}))


if __name__ == '__main__':
    main()
