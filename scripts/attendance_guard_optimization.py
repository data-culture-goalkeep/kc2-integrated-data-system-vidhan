"""Prepare a NOT-AUTHORIZED indexed replay-guard amendment; originals immutable."""
import gzip
import json
from pathlib import Path
from pglast import parse_sql
from attendance_execution import E, PACKETS, ROOT, PROJECT, IMPORT, canonical, load, manifests, required, sha
from recovery import atomic_save, source_integrity

W = ROOT / 'work/attendance-indexed-tail'
ORIGINAL = 'WHERE t."id" IS NOT DISTINCT FROM x."id"'
INDEXED = 'WHERE t."id" = x."id" AND t."id" IS NOT DISTINCT FROM x."id"'


def indexed_query(query):
    required(query.count(ORIGINAL) == 1, 'Guard marker missing or repeated')
    changed = query.replace(ORIGINAL, INDEXED)
    required(changed.replace(INDEXED, ORIGINAL) == query, 'Unexpected SQL amendment')
    required(changed.split('DO $batch$')[0] == query.split('DO $batch$')[0], 'INSERT payload changed')
    parse_sql(changed)
    return changed


def prepare():
    _, original = manifests()
    required(source_integrity()['source_snapshot_sha256'] == original['source_snapshot_sha256'], 'Source changed')
    W.mkdir(exist_ok=True, mode=0o700)
    folder = W / 'batches'
    folder.mkdir(exist_ok=True, mode=0o700)
    entries = []
    for b in original['batches'][173:]:
        raw = (PACKETS / b['packet_file']).read_bytes()
        required(sha(raw) == b['packet_sha256'], 'Original packet changed')
        req = json.loads(gzip.decompress(raw))
        required(req['project_id'] == PROJECT and sha(req['query'].encode()) == b['query_sha256'], 'Original SQL changed')
        q = indexed_query(req['query'])
        request_id = sha(('attendance-indexed-guard-v1:' + str(b['index']) + ':' + sha(q.encode())).encode())
        data = gzip.compress(canonical({'project_id': PROJECT, 'query': q, 'request_id': request_id}).encode(), mtime=0)
        file = folder / ('%04d.json.gz' % b['index'])
        file.write_bytes(data)
        file.chmod(0o600)
        entries.append({'index': b['index'], 'rows': b['rows'], 'request_id': request_id,
                        'original_request_id': b['request_id'], 'original_query_sha256': b['query_sha256'],
                        'query_sha256': sha(q.encode()), 'packet_sha256': sha(data),
                        'packet_bytes': len(data), 'packet_file': str(file.relative_to(W))})
    atomic_save(W / 'proposed-batches.json', entries)
    return entries


def main():
    items = prepare()
    print(canonical({'proposed_transactions': len(items), 'proposed_rows': sum(x['rows'] for x in items),
                     'remote_execution_authorized': False, 'schema_changes': 0}))


if __name__ == '__main__':
    main()
