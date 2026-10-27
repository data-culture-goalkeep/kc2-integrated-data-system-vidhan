"""Unapproved, fail-closed indexed-tail mode. No network or SQL dispatch here.

Requires an explicit new owner artifact for its exact revised manifest. The
original approved code/packets stay immutable, and indices 0–172 are excluded.
"""
import gzip
import json
import sys
from datetime import datetime, timezone

import attendance_execution as base
from attendance_guard_optimization import W, indexed_query
from attendance_reconcile import expected
from recovery import atomic_save, check_hashes, source_integrity

OLD = base.ROOT / 'work/attendance-prefix172'


def window(approval, digest, current=None):
    issued = datetime.fromisoformat(approval['issued_at'].replace('Z', '+00:00'))
    expires = datetime.fromisoformat(approval['expires_at'].replace('Z', '+00:00'))
    current = current or datetime.now(timezone.utc)
    base.required((expires-issued).total_seconds() == 14400 and issued <= current < expires, 'Invalid/expired approval window')
    base.required(approval['project_reference'] == base.PROJECT and approval['original_import_manifest_sha256'] == base.IMPORT, 'Approval project/source scope differs')
    base.required(approval['indexed_manifest_sha256'] == digest, 'Unapproved revised SQL manifest')


def configuration():
    _, original = base.manifests()
    m = base.load(base.E / 'attendance-indexed-tail-manifest.json')
    base.required(m['project_reference'] == base.PROJECT and m['region'] == 'ap-northeast-1' and m['original_import_manifest_sha256'] == base.IMPORT, 'Wrong scope')
    base.required([b['index'] for b in m['batches']] == list(range(173,216)), 'Old or out-of-scope batch')
    check_hashes(m['code_sha256'])
    return m, original, base.sha(base.canonical(m).encode())


def packet(index, manifest, original):
    base.required(173 <= index <= 215, 'Committed or out-of-scope index')
    b = manifest['batches'][index-173]
    base.required(b['packet_file'] == 'batches/%04d.json.gz' % index, 'Packet path differs')
    data = (W / b['packet_file']).read_bytes()
    base.required(base.sha(data) == b['packet_sha256'] and len(data) == b['packet_bytes'], 'Packet changed')
    req = json.loads(gzip.decompress(data))
    base.packet(index, original)
    old = json.loads(gzip.decompress((base.PACKETS / original['batches'][index]['packet_file']).read_bytes()))
    base.required(req['project_id'] == base.PROJECT and req['request_id'] == b['request_id'], 'Request binding differs')
    base.required(base.sha(req['query'].encode()) == b['query_sha256'] and req['query'] == indexed_query(old['query']), 'SQL differs from sole approved amendment')
    return b


def main():
    W.mkdir(exist_ok=True, mode=0o700)
    base.W = W
    with (W/'control.lock').open('a') as lock:
        base.fcntl.flock(lock, base.fcntl.LOCK_EX | base.fcntl.LOCK_NB)
        m, original, digest = configuration()
        command = sys.argv[1]
        a = base.load(W/('approval-evidence.json' if command == 'authorize' else 'authorization.json'))
        if command != 'accept':
            window(a,digest)
        if command == 'authorize':
            base.required(not base.journal() and a.get('owner_reference') and a.get('owner_approval_quote'), 'Missing owner evidence or nonempty journal')
            base.required(source_integrity()['source_snapshot_sha256'] == m['source_snapshot_sha256'], 'Source changed')
            base.required(base.sha((OLD/'journal.jsonl').read_bytes()) == m['checkpoint']['journal_sha256'], 'Parent journal changed')
            meta = base.load(W/'project.json')
            base.required(meta['id'] == base.PROJECT and meta['name']=='kc2-integrated-data-system' and meta['region']=='ap-northeast-1','Wrong project')
            base.required(base.load(W/'pre-ledger.json') == m['migration_ledger'], 'Ledger changed')
            base.required(base.sha(base.canonical(base.load(W/'pre-catalog.json')).encode())==m['catalog_sha256'], 'Schema/security changed')
            base.required(base.load(W/'pre-snapshot.json')==m['original_table_fingerprints'], 'Existing data changed')
            base.required(base.load(W/'pre-prefix-metadata.json')==m['checkpoint']['complete_stage_metadata'], 'Prefix metadata changed')
            base.required(base.load(W/'pre-payload-buckets.json')==expected(base.load(base.PACKETS/'records.json')[:34600]), 'Prefix keys/payloads changed')
            c=base.load(W/'pre-control.json');base.required(c['staging_rows']==34600 and c['active_imports']==0,'Checkpoint/activity changed')
            for b in m['batches']:packet(b['index'],m,original)
            atomic_save(W/'authorization.json',{**a,'active':True})
            base.append({'event':'authorized','indexed_manifest_sha256':digest,'parent_journal_sha256':m['checkpoint']['journal_sha256']})
            result={'first_index':173,'transactions':43,'rows':8560}
        elif command in {'packet','dispatch'}:
            base.required(a['active'],'Inactive approval');n=int(sys.argv[2]);b=packet(n,m,original)
            if command=='dispatch':
                e=base.journal();sent=[x for x in e if x['event']=='submitted'];done=[x for x in e if x['event']=='committed_ack']
                base.required(len(sent)==len(done)==n-173 and e[-1]['event'] in {'authorized','committed_ack'},'Wrong order or failed/uncertain request; stop')
                base.append({'event':'submitted','index':n,'request_id':b['request_id'],'query_sha256':b['query_sha256']})
            result=b
        elif command=='accept':
            n=int(sys.argv[2]);e=base.journal();base.required(e[-1]['event']=='submitted' and e[-1]['index']==n,'Wrong acknowledgement order')
            r=base.load(W/'response.json');ok=base.response_is_acknowledged(r)
            base.append({'event':'committed_ack' if ok else 'failed_or_uncertain','index':n,'request_id':e[-1]['request_id'],'response_sha256':base.sha(base.canonical(r).encode())})
            base.required(ok,'Failed/uncertain outcome; stop; no automatic retry');result={'next_index':n+1}
        else:raise ValueError('Unsupported action')
        print(base.canonical(result))


if __name__=='__main__':main()
