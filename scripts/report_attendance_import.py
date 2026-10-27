"""Validate captured live reconciliation before reporting attendance completion.

Reads protected captured results; never connects to or writes to a database.
"""
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

from attendance_execution import E, PACKETS, ROOT, canonical, load, manifests, required, sha
from attendance_reconcile import expected
from recovery import atomic_save, source_integrity

W = ROOT / 'work/attendance-resumption'


def main():
    _, manifest = manifests()
    required(source_integrity()['source_snapshot_sha256'] == manifest['source_snapshot_sha256'], 'Source snapshot changed during import')
    rows = load(PACKETS / 'records.json')
    events = [json.loads(line) for line in (W / 'journal.jsonl').read_text().splitlines()]
    previous = None
    for event in events:
        payload = {k: v for k, v in event.items() if k != 'sha256'}
        required(event['previous_sha256'] == previous and sha(canonical(payload).encode()) == event['sha256'], 'Journal integrity failed')
        previous = event['sha256']
    submitted = [e for e in events if e['event'] == 'submitted']
    committed = [e for e in events if e['event'] == 'committed_ack']
    required(not any(e['event'] == 'failed_or_uncertain' for e in events), 'Failed or uncertain request remains')
    required(len(submitted) == len(committed) == 216, 'Incomplete journal')
    for i, (sent, done, batch) in enumerate(zip(submitted, committed, manifest['batches'])):
        required(sent['index'] == done['index'] == i and sent['request_id'] == done['request_id'] == batch['request_id'], 'Transaction order/identity differs')
        required(sent['query_sha256'] == batch['query_sha256'], 'Committed SQL binding differs')
    live = load(W / 'final-reconciliation.json')
    expected_distributions = load(W / 'expected-distributions.json')
    for key, value in expected_distributions.items():
        required(live[key] == value, 'Live classification differs: ' + key)
    required(live['total'] == 43160 and live['sheets'] == 107 and live['source_rows'] == 14132, 'Live staging coverage differs')
    required(live['daily_rosters'] == 2142 and live['daily_pa_marks'] == 24687, 'Roster/mark grain mismatch')
    for key in ['duplicate_coordinates', 'parsed_dates', 'verified_children', 'invalid_source_links', 'source_mark_disagreements', 'header_disagreements', 'invalid_candidates', 'operational_attendance']:
        required(live[key] == 0, 'Unexpected data or integrity problem: ' + key)
    required(live['codes'] == {'PENDING': 43160} and live['reviews'] == {'pending': 43160}, 'Unapproved review/code promotion')
    buckets = load(W / 'final-payload-buckets.json')
    required(buckets == expected(rows), 'Actual live keys/full payloads differ from approved records')
    required(load(W / 'expected-codec.json') == load(W / 'actual-codec.json'), 'PostgreSQL digest representation unverified')
    required(load(W / 'pre-snapshot.json') == load(W / 'final-snapshot.json'), 'Existing data changed')
    required(load(W / 'pre-catalog.json') == load(W / 'final-catalog.json'), 'Schema/RLS/privileges/triggers changed')
    required(load(W / 'pre-ledger.json') == load(W / 'final-ledger.json'), 'Migration ledger changed')
    actual_sheets = load(W / 'final-sheets.json')
    sheets = defaultdict(Counter)
    for row in rows:
        item = sheets[row['source_file'], row['source_sheet']]
        item['staged_records'] += 1
        item['contexts' if row['observation_kind'] == 'SOURCE_CONTEXT' else 'cells'] += 1
        item['daily_marks'] += int(row['observation_kind'] == 'MARK' and row['provenance']['sheet_kind'] == 'daily_attendance')
    required(len(actual_sheets) == len(sheets) == 107, 'Sheet coverage differs')
    for sheet in actual_sheets:
        wanted = sheets[sheet['source_file'], sheet['source_sheet']]
        required(all(sheet[k] == wanted[k] for k in ['staged_records', 'contexts', 'cells', 'daily_marks']), 'Per-sheet coverage differs')
    denials = load(W / 'final-denials.json')
    required(len(denials) == 3 and all(x['read_denied'] for x in denials), 'Live staging denial checks incomplete')
    auth = load(W / 'authorization.json')
    issued = datetime.fromisoformat(auth['issued_at'].replace('Z', '+00:00'))
    expiry = datetime.fromisoformat(auth['expires_at'].replace('Z', '+00:00'))
    required(all(issued <= datetime.fromisoformat(e['at_utc']) < expiry for e in submitted), 'Dispatch outside authorization window')
    required(all(datetime.fromisoformat(e['at_utc']) < expiry for e in committed), 'Acknowledgement outside authorization window')
    durations = [{'index': sent['index'], 'seconds': (datetime.fromisoformat(done['at_utc']) - datetime.fromisoformat(sent['at_utc'])).total_seconds()}
                 for sent, done in zip(submitted, committed)]
    # Consume authorization only after actual live reconciliation succeeds.
    # Preserve the old blocked journal and all prior dispatch/receipt events.
    import attendance_execution as execution
    execution.W = W
    if not any(e['event'] == 'completed_live_verified' for e in events):
        execution.append({'event': 'completed_live_verified', 'transactions': 216,
                          'staging_records': 43160, 'operational_records': 0})
    atomic_save(W / 'authorization.json', {**auth, 'active': False,
                'completed_at_utc': datetime.now(timezone.utc).isoformat()})
    report = {
        'status': 'completed_live_reconciled', 'project_reference': manifest['project_reference'],
        'region': manifest['region'], 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'import_manifest_sha256': sha(canonical(manifest).encode()), 'resumption_plan_sha256': auth['resumption_plan_sha256'],
        'approval_timestamp_utc': auth['issued_at'], 'approval_expiry_utc': auth['expires_at'],
        'approval_timestamp_basis': auth['timestamp_basis'], 'completed_import_transactions': len(committed),
        'failed_or_uncertain_transactions': 0, 'retries': 0,
        'first_dispatch_utc': submitted[0]['at_utc'], 'last_acknowledgement_utc': committed[-1]['at_utc'],
        'authorization_window_satisfied': True,
        'longest_dispatch_to_acknowledgement': max(durations, key=lambda x: x['seconds']),
        'long_acknowledgement_delay_cause': 'Not established; no retry or failure; actual live contents verified independently',
        'actual_reconciliation': live, 'all_expected_keys_and_complete_payloads_match': True,
        'payload_hash_bucket_count': len(buckets), 'missing_or_changed_expected_records': 0,
        'original_19_tables_full_payload_fingerprints_unchanged': True,
        'schema_rls_privileges_triggers_ledger_unchanged': True, 'live_denials': denials,
        'existing_table_counts': {k: v['count'] for k, v in load(W / 'final-snapshot.json').items()},
        'application_tables': 20, 'memberships_activated': 0, 'oauth_activated': False,
        'new_schema_changes': 0, 'original_source_rows_modified': 0, 'existing_audit_events_added_or_modified': 0,
        'journal_sha256': sha((W / 'journal.jsonl').read_bytes()), 'previous_rejection_preserved': True,
        'business_acceptance': False, 'operational_projection_approved': False,
    }
    (E / 'attendance-import-live-reconciliation.json').write_text(json.dumps(report, indent=2) + '\n')
    (E / 'attendance-import-live-sheets.json').write_text(json.dumps(actual_sheets, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'transactions': 216, 'staging_rows': 43160, 'daily_marks': 24687, 'operational_attendance': 0}))


if __name__ == '__main__':
    main()
