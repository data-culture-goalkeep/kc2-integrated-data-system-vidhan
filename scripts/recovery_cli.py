#!/usr/bin/env python3
"""Stateless recovery packet/checkpoint commands; default prepare and read-only preflight never dispatch SQL."""
import argparse,gzip,json,sys,time
from pathlib import Path
from recovery import *
from recovery_snapshot import snapshot_sql

def preflight(manifest):
    series=validate_manifest(manifest);project=load(WORK/'fresh-project.json');verify_target(project)
    required(load(WORK/'fresh-catalog.json')==load(ROOT/'docs/evidence/expected-deployment-catalog.json'),'Live schema/security changed')
    required(load(WORK/'fresh-ledger.json')==manifest['migration_ledger'],'Live migration ledger changed')
    control=load(WORK/'fresh-control.json');required(control=={'active_imports':0,'database_role':'postgres','server_version_num':170011},'Active import or migration identity/version differs')
    required(load(WORK/'fresh-anchor.json')==manifest['prefix_immutable_metadata'],'Existing source content/ingestion metadata changed')
    snap=load(WORK/'fresh-snapshot.json');coordinator=Coordinator(WORK/'execution',manifest,{})
    state=coordinator.state();required(not state['inflight'] and not state['stopped'],'In-flight/unknown request: no automatic resume')
    required(snap==series[state['acknowledged']],'Live key/payload/status checkpoint differs')
    required(all(time.time()-(WORK/name).stat().st_mtime<120 for name in ['fresh-project.json','fresh-catalog.json','fresh-ledger.json','fresh-snapshot.json','fresh-control.json','fresh-anchor.json']),'Live preflight evidence too old')
    return series,project,snap,state

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','check','start','status','packet','dispatch','accept','diagnose']);p.add_argument('sequence',nargs='?',type=int);a=p.parse_args()
    if a.command=='prepare':
        m=build();path=WORK/'snapshot.sql';path.write_text(snapshot_sql());path.chmod(0o600)
        from recovery_snapshot import anchor_sql
        path=WORK/'anchor.sql';path.write_text(anchor_sql());path.chmod(0o600)
        print(json.dumps({'manifest_sha256':hashed(m),'remaining':179,'compressed_bytes':sum(x['packet_bytes'] for x in m['batches']),'original_sql_bytes':sum(x['sql_bytes'] for x in m['batches']),'max_packet_bytes':max(x['packet_bytes'] for x in m['batches'])}));return
    m=load(WORK/'manifest.json');series=validate_manifest(m)
    if a.command=='check':
        _,_,_,state=preflight(m);print(json.dumps({'status':'passed','checkpoint':state['acknowledged'],'remote_writes':0,'manifest_sha256':hashed(m)}));return
    if a.command=='status':print(json.dumps(Coordinator(WORK/'execution',m,{}).state()));return
    if a.command=='diagnose':print(json.dumps(Coordinator(WORK/'execution',m,{}).diagnose(load(WORK/'fresh-snapshot.json'),series)));return
    auth=load(WORK/'owner-authorization.json');authorize(auth,m);c=Coordinator(WORK/'execution',m,auth)
    if a.command=='start':
        _,project,snap,_=preflight(m);state=c.verify_checkpoint(project,snap,series,load(WORK/'fresh-anchor.json'));print(json.dumps({'status':'started','checkpoint':state['acknowledged']}));return
    required(a.sequence is not None,'Sequence required')
    if a.command=='packet':batch,_=c.packet(a.sequence);print(json.dumps(batch));return
    if a.command=='dispatch':batch=c.dispatch(a.sequence);print(json.dumps({'status':'dispatch_journaled','request_id':batch['request_id']}));return
    if a.command=='accept':
        response=json.loads(gzip.decompress((WORK/'response.json.gz').read_bytes()));state=c.accept(a.sequence,response)
        print(json.dumps({'status':'acknowledged','checkpoint':state['acknowledged'],'journal_digest':state['journal_digest']}))
if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'status':'blocked','error_type':type(exc).__name__,'reason':str(exc)[:220]}),file=sys.stderr);raise SystemExit(1)
