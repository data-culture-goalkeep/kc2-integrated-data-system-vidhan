"""Fail-closed, separately authorized continuation after the verified 172 prefix.

No network or SQL generation. Original packet indices 0–171 are never exposed.
Fresh captured checkpoint evidence and a new owner artifact are mandatory.
"""
import sys
from datetime import datetime, timezone

import attendance_execution as base
from attendance_reconcile import expected
from recovery import atomic_save, check_hashes, source_integrity

OLD = base.ROOT / 'work/attendance-resumption'
W = base.ROOT / 'work/attendance-prefix172'


def authorize_window(approval, plan_hash, current=None):
    issued = datetime.fromisoformat(approval['issued_at'].replace('Z', '+00:00'))
    expires = datetime.fromisoformat(approval['expires_at'].replace('Z', '+00:00'))
    current = current or datetime.now(timezone.utc)
    base.required((expires - issued).total_seconds() == 14400 and issued <= current < expires, 'Invalid/expired authorization window')
    base.required(approval['project_reference'] == base.PROJECT and approval['import_manifest_sha256'] == base.IMPORT, 'Approval target/import mismatch')
    base.required(approval['continuation_plan_sha256'] == plan_hash, 'Wrong approved continuation')


def original_index(position):
    base.required(0 <= position < 44, 'Outside remaining transaction range')
    return 172 + position


def configuration():
    _, manifest = base.manifests()
    plan = base.load(base.E / 'attendance-prefix172-continuation-plan.json')
    base.required(plan['original_import_manifest_sha256'] == base.IMPORT and plan['project_reference'] == base.PROJECT, 'Changed plan scope')
    base.required(plan['remaining_original_indices'] == {'first': 172, 'last': 215, 'count': 44}, 'Changed remaining range')
    base.required(plan['batches'] == manifest['batches'][172:], 'Changed original packets')
    check_hashes(plan['code_sha256'])
    return plan, manifest, base.sha(base.canonical(plan).encode())


def main():
    W.mkdir(exist_ok=True, mode=0o700)
    base.W = W
    with (W / 'control.lock').open('a') as lock:
        base.fcntl.flock(lock, base.fcntl.LOCK_EX | base.fcntl.LOCK_NB)
        plan, manifest, plan_hash = configuration()
        command = sys.argv[1]
        approval_path = W / ('approval-evidence.json' if command == 'authorize' else 'authorization.json')
        approval = base.load(approval_path)  # No file means no authorization.
        if command != 'accept':
            authorize_window(approval, plan_hash)
        if command == 'authorize':
            base.required(not base.journal(), 'Existing continuation journal; no restart')
            base.required(approval.get('owner_reference') and approval.get('owner_approval_quote'), 'Missing direct owner evidence')
            base.required(source_integrity()['source_snapshot_sha256'] == plan['source_snapshot_sha256'], 'Source changed')
            base.required(base.sha((OLD / 'journal.jsonl').read_bytes()) == plan['committed_prefix']['journal_sha256'], 'Previous journal changed')
            prefix = base.load(base.PACKETS / 'records.json')[:34400]
            buckets = base.load(W / 'pre-payload-buckets.json')
            base.required(buckets == expected(prefix), 'Live committed prefix differs')
            meta = base.load(W / 'project.json')
            base.required(meta['id'] == base.PROJECT and meta['region'] == 'ap-northeast-1' and meta['name'] == 'kc2-integrated-data-system', 'Project differs')
            base.required(base.load(W / 'pre-ledger.json') == plan['migration_ledger'], 'Ledger differs')
            base.required(base.sha(base.canonical(base.load(W / 'pre-catalog.json')).encode()) == plan['baseline_catalog_sha256'], 'Catalog/security differs')
            base.required(base.load(W / 'pre-snapshot.json') == plan['original_table_fingerprints'], 'Existing data differs')
            control = base.load(W / 'pre-control.json')
            base.required(control['staging_rows'] == 34400 and control['active_imports'] == 0, 'Checkpoint count/activity differs')
            for batch in plan['batches']:
                base.packet(batch['index'], manifest)
            atomic_save(W / 'authorization.json', {**approval, 'active': True})
            base.append({'event': 'authorized', 'continuation_plan_sha256': plan_hash,
                         'parent_journal_sha256': plan['committed_prefix']['journal_sha256']})
            result = {'remaining_transactions': 44, 'remaining_records': 8760, 'first_original_index': 172}
        elif command in {'packet', 'dispatch'}:
            base.required(approval['active'], 'Inactive authorization')
            n = int(sys.argv[2])
            base.required(172 <= n <= 215, 'Previously committed or out-of-scope index')
            batch = base.packet(n, manifest)
            if command == 'dispatch':
                events = base.journal()
                sent = [x for x in events if x['event'] == 'submitted']
                done = [x for x in events if x['event'] == 'committed_ack']
                base.required(len(sent) == len(done) == n - 172 and events[-1]['event'] in {'authorized', 'committed_ack'}, 'Wrong order or uncertain request; stop')
                base.append({'event': 'submitted', 'index': n, 'request_id': batch['request_id'], 'query_sha256': batch['query_sha256']})
            result = batch
        elif command == 'accept':
            n = int(sys.argv[2])
            events = base.journal()
            base.required(events[-1]['event'] == 'submitted' and events[-1]['index'] == n, 'Acknowledgement order differs')
            response = base.load(W / 'response.json')
            accepted = base.response_is_acknowledged(response)
            base.append({'event': 'committed_ack' if accepted else 'failed_or_uncertain', 'index': n,
                         'request_id': events[-1]['request_id'], 'response_sha256': base.sha(base.canonical(response).encode())})
            base.required(accepted, 'Failure/uncertain outcome; stop; no retry')
            result = {'next_original_index': n + 1}
        else:
            raise ValueError('Unsupported action')
        print(base.canonical(result))


if __name__ == '__main__':
    main()
