"""Combine preserved journals and independent live evidence before completion.

No database connection, source modification or SQL dispatch. Original approved
execution code/packets are immutable. Only aggregate metadata is published.
"""
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import attendance_execution as base
from attendance_indexed_execution import configuration
from attendance_guard_optimization import W
from attendance_reconcile import expected
from recovery import atomic_save, source_integrity

ROOT = base.ROOT
FIRST = ROOT / 'work/attendance-resumption'
SECOND = ROOT / 'work/attendance-prefix172'


def journal(path):
    items = [json.loads(line) for line in path.read_text().splitlines()]
    previous = None
    for item in items:
        value = {k: v for k, v in item.items() if k != 'sha256'}
        base.required(item['previous_sha256'] == previous and base.sha(base.canonical(value).encode()) == item['sha256'], 'Invalid journal chain')
        previous = item['sha256']
    return items


def main():
    manifest, original, digest = configuration()
    base.required(digest == 'd990a38ee68612363dda031dd036b95e905d81ee40d0e52b5917fe707f474307', 'Owner-approved manifest differs')
    base.required(source_integrity()['source_snapshot_sha256'] == manifest['source_snapshot_sha256'], 'Source snapshot changed')
    prefix_plan = base.load(base.E / 'attendance-prefix172-continuation-plan.json')
    base.required(base.sha(base.canonical(prefix_plan).encode()) == 'e137a5008ea428acf0e045386f464c5546f6500884f5e282bfa79d55c3ae9a6f', 'Prior checkpoint plan changed')
    first = journal(FIRST / 'journal.jsonl')
    base.required(base.sha((FIRST / 'journal.jsonl').read_bytes()) == prefix_plan['committed_prefix']['journal_sha256'], 'First journal changed')
    old_ack = [x for x in first if x['event'] == 'committed_ack']
    verified = [x for x in first if x['event'] == 'commit_verified_readonly']
    base.required([x['index'] for x in old_ack] == list(range(171)) and len(verified) == 1 and verified[0]['index'] == 171, 'First prefix incomplete')
    for item in old_ack + verified:
        base.required(item['request_id'] == original['batches'][item['index']]['request_id'], 'Old receipt identity differs')
    second = journal(SECOND / 'journal.jsonl')
    base.required(base.sha((SECOND / 'journal.jsonl').read_bytes()) == manifest['checkpoint']['journal_sha256'], 'Second journal changed')
    second_ack = [x for x in second if x['event'] == 'committed_ack']
    second_fail = [x for x in second if x['event'] == 'failed_or_uncertain']
    second_proof = [x for x in second if x['event'] == 'failure_verified_readonly']
    base.required(len(second_ack) == len(second_fail) == len(second_proof) == 1 and second_ack[0]['index'] == 172 and second_fail[0]['index'] == second_proof[0]['index'] == 173 and not second_proof[0]['committed'], 'Previous failure accounting differs')
    base.required(second_ack[0]['request_id'] == original['batches'][172]['request_id'], 'Batch 172 differs')
    second_raw = base.load(SECOND / 'receipt-172.json')
    base.required(base.response_is_acknowledged(second_raw) and base.sha(base.canonical(second_raw).encode()) == second_ack[0]['response_sha256'], 'Batch 172 raw receipt differs')
    items = journal(W / 'journal.jsonl')
    sent = [x for x in items if x['event'] == 'submitted']
    done = [x for x in items if x['event'] == 'committed_ack']
    base.required(not any(x['event'] == 'failed_or_uncertain' for x in items), 'Revised execution contains failed/uncertain request')
    base.required([x['index'] for x in sent] == [x['index'] for x in done] == list(range(173, 216)), 'Not all 43 approved transactions accounted for')
    all_indices = [x['index'] for x in old_ack + verified + second_ack + done]
    base.required(sorted(all_indices) == list(range(216)) and len(set(all_indices)) == 216, 'Missing/replayed committed transaction')
    for request, receipt, batch in zip(sent, done, manifest['batches']):
        base.required(request['index'] == batch['index'] and request['request_id'] == receipt['request_id'] == batch['request_id'] and request['query_sha256'] == batch['query_sha256'], 'Approved request/SQL binding differs')
        raw = base.load(W / ('receipt-' + str(request['index']) + '.json'))
        base.required(base.response_is_acknowledged(raw) and base.sha(base.canonical(raw).encode()) == receipt['response_sha256'], 'Raw durable acknowledgement differs')
    approval = base.load(W / 'authorization.json')
    start = datetime.fromisoformat(approval['issued_at'].replace('Z', '+00:00'))
    expiry = datetime.fromisoformat(approval['expires_at'].replace('Z', '+00:00'))
    base.required((expiry-start).total_seconds() == 14400 and approval['indexed_manifest_sha256'] == digest, 'Authorization window/hash changed')
    base.required(all(start <= datetime.fromisoformat(x['at_utc']) < expiry for x in sent + done), 'Execution outside approved window')
    records = base.load(base.PACKETS / 'records.json')
    live = base.load(W / 'final-reconciliation.json')
    distributions = {
        'kinds': dict(Counter(x['observation_kind'] for x in records)),
        'identity_all': dict(Counter(x['identity_status'] for x in records)),
        'identity_cells': dict(Counter(x['identity_status'] for x in records if x['observation_kind'] != 'SOURCE_CONTEXT')),
        'dates_all': dict(Counter(x['date_status'] for x in records)),
        'dates_cells': dict(Counter(x['date_status'] for x in records if x['observation_kind'] != 'SOURCE_CONTEXT')),
    }
    for key, value in distributions.items():
        base.required(live[key] == value, 'Classification differs: ' + key)
    base.required(live['total'] == 43160 and live['sheets'] == 107 and live['source_rows'] == 14132, 'Source coverage differs')
    base.required(live['daily_rosters'] == 2142 and live['daily_pa_marks'] == 24687, 'Roster/observation grain differs')
    base.required(live['reviews'] == {'pending': 43160} and live['codes'] == {'PENDING': 43160}, 'Unapproved review/code promotion')
    for key in ['duplicate_coordinates', 'parsed_dates', 'verified_children', 'invalid_source_links', 'source_mark_disagreements', 'header_disagreements', 'invalid_candidates', 'operational_attendance']:
        base.required(live[key] == 0, 'Live integrity issue: ' + key)
    buckets = base.load(W / 'final-payload-buckets.json')
    base.required(buckets == expected(records), 'Expected keys/full payloads missing, changed or extra')
    base.required(base.load(W / 'pre-prefix-metadata.json') == base.load(W / 'final-prefix-metadata.json') == manifest['checkpoint']['complete_stage_metadata'], 'Old 34600 staging rows or timestamps changed')
    base.required(base.load(W / 'pre-snapshot.json') == base.load(W / 'final-snapshot.json') == manifest['original_table_fingerprints'], 'Original records/timestamps/audit changed')
    base.required(base.load(W / 'pre-catalog.json') == base.load(W / 'final-catalog.json'), 'Schema/constraints/RLS/privileges/triggers changed')
    base.required(base.load(W / 'pre-ledger.json') == base.load(W / 'final-ledger.json') == manifest['migration_ledger'], 'Ledger changed')
    sheets = defaultdict(Counter)
    for r in records:
        s = sheets[r['source_file'], r['source_sheet']]
        s['staged_records'] += 1
        s['contexts' if r['observation_kind'] == 'SOURCE_CONTEXT' else 'cells'] += 1
        s['daily_marks'] += int(r['observation_kind'] == 'MARK' and r['provenance']['sheet_kind'] == 'daily_attendance')
    actual_sheets = base.load(W / 'final-sheets.json')
    base.required(len(actual_sheets) == len(sheets) == 107, 'Worksheet coverage differs')
    for r in actual_sheets:
        s = sheets[r['source_file'], r['source_sheet']]
        base.required(all(r[k] == s[k] for k in ['staged_records', 'contexts', 'cells', 'daily_marks']), 'Per-sheet reconciliation differs')
    denials = base.load(W / 'final-denials.json')
    base.required({x['role'] for x in denials} == {'anon', 'authenticated', 'service_role'} and all(x['read_denied'] for x in denials), 'Live denial checks incomplete')
    base.required(base.load(W / 'final-control.json')['active_imports'] == 0, 'Import still active')
    base.W = W
    if not any(x['event'] == 'completed_live_verified' for x in items):
        base.append({'event': 'completed_live_verified', 'revised_commits': 43, 'total_commits': 216, 'staging_rows': 43160})
    atomic_save(W / 'authorization.json', {**approval, 'active': False, 'completed_at_utc': base.now()})
    now = datetime.now(timezone.utc)
    report = {
        'status': 'completed_live_reconciled', 'project_reference': base.PROJECT, 'region': 'ap-northeast-1',
        'checked_at_utc': now.isoformat(), 'checked_at_ist': now.astimezone(ZoneInfo('Asia/Kolkata')).isoformat(),
        'approved_indexed_manifest_sha256': digest, 'original_import_manifest_sha256': base.IMPORT,
        'approval_issued_at_utc': approval['issued_at'], 'approval_expiry_utc': approval['expires_at'],
        'approval_issued_at_ist': approval['issued_at_ist'], 'approval_expiry_ist': approval['expires_at_ist'],
        'approval_timestamp_basis': approval['timestamp_basis'], 'authorization_window_satisfied': True,
        'revised_transactions_committed': 43, 'new_staging_rows': 8560, 'total_committed_transactions_accounted_for': 216,
        'acknowledged_commits_all_runs': 215, 'prior_commit_independently_verified_readonly': 1,
        'revised_run_failed_or_uncertain_requests': 0, 'unresolved_outcomes': 0, 'revised_run_retries': 0,
        'historical_timeout_attempt_preserved': {'original_index': 173, 'committed': False, 'sqlstate': '57014'},
        'first_dispatch_utc': sent[0]['at_utc'], 'last_acknowledgement_utc': done[-1]['at_utc'],
        'actual_reconciliation': live, 'all_expected_keys_and_full_payloads_match': True,
        'hash_bucket_count': len(buckets), 'missing_extra_or_changed_expected_records': 0, 'unexplained_source_losses': 0,
        'all_prior_34600_staging_rows_including_timestamps_unchanged': True,
        'all_original_19_tables_complete_rows_and_timestamps_unchanged': True,
        'existing_table_counts': {k: v['count'] for k, v in base.load(W / 'final-snapshot.json').items()},
        'schema_rls_permissions_constraints_triggers_ledger_unchanged': True,
        'live_read_denials': denials, 'application_tables': 20, 'statement_timeout_seconds': 60,
        'new_indexes_or_schema_changes': 0, 'memberships_or_oauth_activated': False,
        'prior_journal_sha256': manifest['checkpoint']['journal_sha256'],
        'revised_journal_sha256': base.sha((W / 'journal.jsonl').read_bytes()),
        'authorization_active': False, 'active_imports': 0, 'business_operational_approval': False,
    }
    (base.E / 'attendance-final-live-reconciliation.json').write_text(json.dumps(report, indent=2) + '\n')
    (base.E / 'attendance-final-live-sheets.json').write_text(json.dumps(actual_sheets, indent=2) + '\n')
    print(base.canonical({'status': report['status'], 'revised_commits': 43, 'total_commits': 216,
                          'staging_records': 43160, 'daily_pa_marks': 24687, 'operational_attendance': 0}))


if __name__ == '__main__':
    main()
