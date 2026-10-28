"""Local transport/journal controls for the owner's pinned Stage 6 attendance import.

No database connection, SQL generation or automatic retry. The reviewed SQL and
loader remain byte-for-byte unchanged. All private evidence stays in work/.
"""
import base64
import fcntl
import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from etl_core import ROOT, canonical, required
from recovery import atomic_save, check_hashes, source_integrity

W = ROOT / 'work/attendance-execution'
E = ROOT / 'docs/evidence'
PACKETS = ROOT / 'work/attendance'
DEPLOY = '7973aaf818b255d8f2411b74a1c3725a9a57f6f771bebcda32cc37348cc0dba4'
IMPORT = '911c47968c61fb19a0227e0ab86eae2937dec2e673b9b94c4713ed08bb3ab4ed'
PROJECT = 'hmlbdozsqxlwzvjimjwh'
APPROVAL = Path('/workspace/attachments/98a4cdd1-b565-4503-803f-db06e98b20fb/Pasted text.txt')


def load(p):
    return json.loads(p.read_text())


def sha(b):
    return hashlib.sha256(b).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def manifests():
    d = load(E / 'attendance-deployment-manifest.json')
    m = load(E / 'attendance-import-manifest.json')
    required(sha(canonical(d).encode()) == DEPLOY, 'Deployment manifest changed')
    required(sha(canonical(m).encode()) == IMPORT, 'Import manifest changed')
    required(d['project_reference'] == m['project_reference'] == PROJECT, 'Wrong project')
    required(d['region'] == m['region'] == 'ap-northeast-1', 'Wrong region')
    required(sha((ROOT / d['migration_file']).read_bytes()) == d['migration_sha256'], 'SQL changed')
    check_hashes(m['code_sha256'])
    required(sha((PACKETS / 'records.json').read_bytes()) == m['records_sha256'], 'Records changed')
    return d, m


def packet(index, m):
    b = m['batches'][index]
    data = (PACKETS / b['packet_file']).read_bytes()
    required(sha(data) == b['packet_sha256'] and len(data) == b['packet_bytes'], 'Packet changed')
    req = json.loads(gzip.decompress(data))
    required(req['project_id'] == PROJECT and req['request_id'] == b['request_id'], 'Request changed')
    required(sha(req['query'].encode()) == b['query_sha256'], 'Query changed')
    return b


def journal():
    p = W / 'journal.jsonl'
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def append(event):
    events = journal()
    event = {**event, 'at_utc': now(), 'previous_sha256': events[-1]['sha256'] if events else None}
    event['sha256'] = sha(canonical(event).encode())
    fd = os.open(W / 'journal.jsonl', os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, 'a') as f:
        f.write(canonical(event) + '\n')
        f.flush()
        os.fsync(f.fileno())


def response_is_acknowledged(response):
    """A tool-level denial, unknown transport outcome or malformed result fails closed."""
    if response.get('isError'):
        return False
    for content in response.get('content', []):
        if content.get('type') == 'text':
            try:
                value = json.loads(content['text'])
                if isinstance(value, dict) and isinstance(value.get('result'), str) and not value.get('error'):
                    return True
            except (ValueError, TypeError):
                pass
    return False


def authorize():
    d, m = manifests()
    required(not journal(), 'Existing journal; no automatic restart')
    required(source_integrity()['source_snapshot_sha256'] == m['source_snapshot_sha256'], 'Source snapshot changed')
    for b in m['batches']:
        packet(b['index'], m)
    p = load(W / 'project.json')
    required(p['id'] == PROJECT and p['name'] == d['project_name'] and p['region'] == d['region'], 'Project differs')
    required(load(W / 'pre-ledger.json') == d['baseline_migration_ledger'], 'Ledger differs')
    required(sha(canonical(load(W / 'pre-catalog.json')).encode()) == d['baseline_catalog_sha256'], 'Catalog/security differs')
    required({t: x['count'] for t, x in load(W / 'pre-snapshot.json').items()} == d['baseline_counts'], 'Counts differ')
    control = load(W / 'pre-control.json')
    required(not control['staging_exists'] and control['active_imports'] == 0 and control['database_role'] == 'postgres', 'Unsafe initial state')
    approval = APPROVAL.read_text()
    required(DEPLOY in approval and IMPORT in approval and PROJECT in approval and 'I authorize' in approval, 'Owner evidence missing')
    atomic_save(W / 'authorization.json', {
        'project_reference': PROJECT, 'deployment_manifest_sha256': DEPLOY,
        'import_manifest_sha256': IMPORT, 'approval_message_sha256': sha(APPROVAL.read_bytes()),
        'owner_reference': 'Current user-pasted request: Goalkeep KC-2 — Stage 6: Attendance Deployment and Import',
        'recorded_at_utc': now(), 'scope': 'one exact staging migration; 216 pinned import transactions; 43160 pending records; zero operational attendance',
        'continuation': 'This execution only; any failed/uncertain request stops all subsequent writes; no automatic resume',
        'active': True,
    })
    append({'event': 'authorized', 'manifest_sha256': IMPORT})
    return {'status': 'preflight_passed', 'transactions': len(m['batches']), 'records': m['expected_staging_inserts']}


def main():
    W.mkdir(exist_ok=True, mode=0o700)
    with (W / 'control.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cmd = sys.argv[1]
        if cmd == 'authorize':
            result = authorize()
        elif cmd == 'packet':
            _, m = manifests()
            result = packet(int(sys.argv[2]), m)
        elif cmd == 'dispatch':
            _, m = manifests()
            a = load(W / 'authorization.json')
            required(a['active'] and a['import_manifest_sha256'] == IMPORT, 'Inactive authorization')
            n = int(sys.argv[2])
            events = journal()
            done = [x for x in events if x['event'] == 'committed_ack']
            submitted = [x for x in events if x['event'] == 'submitted']
            required(len(submitted) == len(done) == n, 'Wrong order or uncertain transaction; stop')
            required(any(x['event'] == 'deployment_verified' for x in events), 'Deployment not verified')
            b = packet(n, m)
            append({'event': 'submitted', 'index': n, 'request_id': b['request_id'], 'query_sha256': b['query_sha256']})
            result = {'dispatched': n}
        elif cmd == 'accept':
            n = int(sys.argv[2])
            events = journal()
            required(events[-1]['event'] == 'submitted' and events[-1]['index'] == n, 'Invalid acknowledgement order')
            r = load(W / 'response.json')
            error = not response_is_acknowledged(r)
            append({'event': 'failed_or_uncertain' if error else 'committed_ack', 'index': n,
                    'request_id': events[-1]['request_id'], 'response_sha256': sha(canonical(r).encode())})
            required(not error, 'Remote failure/uncertain outcome; stop, inspect read-only; no retry')
            result = {'checkpoint': n + 1}
        else:
            raise ValueError('Unsupported command')
        print(canonical(result))


if __name__ == '__main__':
    main()
