"""Separate checkpoint recovery controls; original loader, initial-load guard and SQL stay immutable."""
from contextlib import contextmanager
from datetime import datetime,timezone,timedelta
import fcntl,gzip,hashlib,json,os,tempfile
from pathlib import Path
from etl_core import ROOT,required,canonical
from remote_etl import PROJECT,REGION,SCOPE,verify_target,result_rows,prepared

PLAN='7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f'
ORIGINAL='8cf2df9dd09a74234b26f1a99c61d17ed7f1f733eca2f016a4f0429c869471b4'
PLANNING='4fc7f1d0d35443d1d3f80445883924676f6b91563291ff2344717165c6d2022e'
RECOVERY_SCOPE='kc2-prefix-40-checkpoint-recovery-v1'
WORK=ROOT/'work/stage4c'
CODE=['scripts/recovery.py','scripts/recovery_cli.py','scripts/recovery_snapshot.py','scripts/recovery_bridge.mjs',
      'scripts/vendor/fflate-0.8.2.js','scripts/vendor/js-sha256-0.11.1.js','scripts/vendor/recovery-dependencies.json']
def sha(data):return hashlib.sha256(data).hexdigest()
def hashed(value):return sha(canonical(value).encode())
def load(path):return json.loads(path.read_text())
def atomic_save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(path.parent,0o700)
    fd,tmp=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:f.write(canonical(value)+'\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
        d=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(d)
        finally:os.close(d)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def check_hashes(expected,base=ROOT):
    for name,want in expected.items():required(sha((base/name).read_bytes())==want,'Bound file changed: '+name)

def source_integrity():
    original=load(ROOT/'work/remote-etl/manifest.json')
    required(hashed(original)==ORIGINAL,'Original execution manifest changed')
    required(sha((ROOT/'work/etl/plan.json').read_bytes())==PLAN,'Original plan changed')
    check_hashes({'scripts/'+name:want for name,want in original['code_sha256'].items()})
    snapshot={};private=load(ROOT/'work/source-intake/private-manifest.json')
    for f in private:
        required(sha(Path(f['original_path']).read_bytes())==f['sha256'],'Original source changed')
        snapshot[f['alias']]={'original':f['sha256'],'sheets':{}}
    profile=load(ROOT/'docs/evidence/data-profile.json')
    for source in profile['sources']:
        for sheet,want in source['sanitized_sha256'].items():
            required(sha((ROOT/'work/source-intake/sanitized'/f"{source['source']}_{sheet}.jsonl").read_bytes())==want,'Sanitized source changed')
            snapshot[source['source']]['sheets'][sheet]=want
    required(len(snapshot)==12 and sum(len(s['sheets']) for s in snapshot.values())==155,'Source coverage differs')
    proposal=load(ROOT/'docs/evidence/stage4b-bounded-recovery-plan.json');required(hashed(proposal)==PLANNING,'Recovery planning hash changed')
    receipts=load(ROOT/'docs/evidence/stage4b-committed-transaction-receipts.json')
    required([(r['phase'],r['index'],r['request_id']) for r in receipts]==[(r['phase'],r['index'],r['request_id']) for r in original['batches'][:40]],'Committed prefix receipts changed')
    return {'source_snapshot_sha256':hashed(snapshot),'committed_receipts_sha256':hashed(receipts)}

def build():
    integrity=source_integrity();_,requests,original=prepared();required(hashed(original)==ORIGINAL,'Original compilation changed')
    series=load(ROOT/'docs/evidence/stage4c-reference-checkpoints.json')
    required(len(series)==180,'Reference checkpoint series incomplete')
    WORK.mkdir(exist_ok=True,mode=0o700);os.chmod(WORK,0o700);items=[]
    for n,r in enumerate(requests[40:]):
        packet={'project_id':PROJECT,'request_id':r['request_id'],'query':r['query'],'tables':r['tables'],'source_refs':r['source_references']}
        data=canonical(packet).encode();compressed=gzip.compress(data,mtime=0)
        path=WORK/f'packet-{n:03}.json.gz';path.write_bytes(compressed);path.chmod(0o600)
        original_batch=original['batches'][40+n]
        required(sha(r['query'].encode())==original_batch['query_sha256'],'Original SQL changed')
        items.append({**original_batch,'sequence':n,'packet_file':path.name,'packet_sha256':sha(compressed),'packet_bytes':len(compressed),'uncompressed_bytes':len(data)})
    manifest={'mode':RECOVERY_SCOPE,'project_reference':PROJECT,'project_name':'kc2-integrated-data-system','region':REGION,
      'original_plan_sha256':PLAN,'original_execution_manifest_sha256':ORIGINAL,'recovery_planning_sha256':PLANNING,
      **integrity,'committed_prefix_transactions':40,'committed_prefix_snapshot':series[0],
      'prefix_immutable_metadata':load(ROOT/'docs/evidence/stage4c-live-anchor.json'),
      'reference_exclusions':{'audit_fields':['created_at','updated_at','created_by','updated_by','actor_ref'],'source_artifact_ingest_time':'captured_at; sealed separately in live immutable anchor'},
      'reference_checkpoints_sha256':hashed(series),'code_sha256':{p:sha((ROOT/p).read_bytes()) for p in CODE},
      'schema_catalog_sha256':hashed(load(ROOT/'docs/evidence/expected-deployment-catalog.json')),
      'migration_ledger':load(ROOT/'docs/evidence/deployed-migration-ledger.json')['migrations'],
      'scope':SCOPE,'remaining_transactions':179,'batches':items,'expected_final_direct_counts':original['direct_inserts'],
      'expected_additional_direct_inserts':24077,'expected_final_audit_rows':28293,'expected_source_updates':20432,
      'expected_source_states':{'resolved':1194,'reference_only':15301,'blocked':3937},
      'expected_source_dispositions':{'successfully_transformed':1194,'preserved_as_source_only':15301,'awaiting_identity_resolution':3623,'awaiting_business_rule_approval':314},
      'failure_rules':{'rpc_retries':0,'unknown_outcome':'stop; read-only diagnosis and separate approval required',
          'known_ack_resume':'fresh matching database checkpoint and unexpired explicit owner authorization required',
          'local_predispatch_retry_limit':2,'committed_prefix_replay':False,'schema_or_security_changes':False},
      'remote_execution_authorized':False}
    atomic_save(WORK/'manifest.json',manifest)
    (ROOT/'docs/evidence/stage4c-recovery-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest

def validate_manifest(manifest):
    required(manifest['project_reference']==PROJECT and manifest['region']==REGION and manifest['mode']==RECOVERY_SCOPE,'Wrong recovery destination/mode')
    required(manifest['original_plan_sha256']==PLAN and manifest['original_execution_manifest_sha256']==ORIGINAL and manifest['recovery_planning_sha256']==PLANNING,'Original binding differs')
    check_hashes(manifest['code_sha256'])
    required(source_integrity()=={k:manifest[k] for k in ['source_snapshot_sha256','committed_receipts_sha256']},'Source/prefix binding changed')
    original=load(ROOT/'work/remote-etl/manifest.json')
    fields=list(original['batches'][0])
    required([{k:b[k] for k in fields} for b in manifest['batches']]==original['batches'][40:] and len(manifest['batches'])==179,'Remaining transaction scope changed')
    series=load(ROOT/'docs/evidence/stage4c-reference-checkpoints.json');required(hashed(series)==manifest['reference_checkpoints_sha256'],'Reference checkpoint series changed')
    return series

def authorize(auth,manifest,now=None):
    now=now or datetime.now(timezone.utc)
    required(auth.get('approved') is True and auth.get('mode')==RECOVERY_SCOPE,'Explicit recovery authorization required')
    for key,value in [('project_reference',PROJECT),('region',REGION),('original_plan_sha256',PLAN),('original_execution_manifest_sha256',ORIGINAL),('recovery_planning_sha256',PLANNING),('recovery_manifest_sha256',hashed(manifest))]:
        required(auth.get(key)==value,'Recovery approval binding differs: '+key)
    required(bool(auth.get('approval_reference')),'Approval evidence reference required')
    start=datetime.fromisoformat(auth['issued_at']);end=datetime.fromisoformat(auth['expires_at'])
    required(start.tzinfo and end.tzinfo and start<=now<end and end-start<=timedelta(hours=24),'Recovery authorization expired/invalid')

class Coordinator:
    def __init__(self,directory,manifest,auth):
        self.directory=directory;self.manifest=manifest;self.auth=auth
        directory.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(directory,0o700)
    @contextmanager
    def locked(self):
        fd=os.open(self.directory/'lock',os.O_CREAT|os.O_RDWR,0o600)
        try:fcntl.flock(fd,fcntl.LOCK_EX);yield
        finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
    def events(self):
        path=self.directory/'journal.jsonl'
        if not path.exists():return []
        data=path.read_bytes();required(data.endswith(b'\n'),'Torn journal: stop for reconciliation')
        events=[];previous='0'*64
        for line in data.splitlines():
            event=json.loads(line);digest=event.pop('digest')
            required(event['previous']==previous and digest==hashed(event),'Checkpoint journal integrity failed')
            previous=digest;events.append({**event,'digest':digest})
        return events
    def append(self,event):
        old=self.events();event={**event,'previous':old[-1]['digest'] if old else '0'*64}
        event['digest']=hashed(event);fd=os.open(self.directory/'journal.jsonl',os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
        with os.fdopen(fd,'w') as f:f.write(canonical(event)+'\n');f.flush();os.fsync(f.fileno())
        directory_fd=os.open(self.directory,os.O_RDONLY)
        try:os.fsync(directory_fd)
        finally:os.close(directory_fd)
    def state(self):
        events=self.events();n=0;inflight=None;stopped=False;verified=False
        for e in events:
            required(e['kind'] in {'verified_checkpoint','dispatch','ack','unknown'},'Unknown journal event')
            if e['kind']=='verified_checkpoint':
                required(e['manifest_sha256']==hashed(self.manifest) and e['acknowledged']==n,'Journal manifest/checkpoint binding differs');verified=True
            if e['kind']=='dispatch':
                required(verified and e['request_id']==self.manifest['batches'][n]['request_id'],'Unverified or changed request binding')
                required(inflight is None and e['sequence']==n,'Journal ordering conflict');inflight=e
            elif e['kind']=='ack':required(inflight and e['request_id']==inflight['request_id'],'Unbound acknowledgment');n+=1;inflight=None
            elif e['kind']=='unknown':stopped=True
        return {'acknowledged':n,'inflight':inflight,'stopped':stopped,'journal_digest':events[-1]['digest'] if events else None,'verified':verified}
    def verify_checkpoint(self,project,snapshot,series,anchor):
        verify_target(project);authorize(self.auth,self.manifest)
        required(anchor==self.manifest['prefix_immutable_metadata'],'Existing source content/ingestion metadata changed')
        with self.locked():
            state=self.state();required(not state['inflight'] and not state['stopped'],'Unresolved request; diagnosis and separate approval required')
            required(snapshot==series[state['acknowledged']],'Live database checkpoint payload/key/state differs')
            self.append({'kind':'verified_checkpoint','manifest_sha256':hashed(self.manifest),'acknowledged':state['acknowledged'],'snapshot_sha256':hashed(snapshot)})
            return state
    def packet(self,sequence,base=WORK):
        authorize(self.auth,self.manifest);state=self.state()
        required(state['verified'] and not state['inflight'] and not state['stopped'] and sequence==state['acknowledged'] and sequence<179,'Duplicate/out-of-order or unresolved request')
        batch=self.manifest['batches'][sequence];data=(base/batch['packet_file']).read_bytes()
        required(sha(data)==batch['packet_sha256'],'Compressed packet changed')
        packet=json.loads(gzip.decompress(data));required(packet['project_id']==PROJECT and packet['request_id']==batch['request_id'] and sha(packet['query'].encode())==batch['query_sha256'],'Packet/SQL binding failed')
        return batch,packet
    def dispatch(self,sequence,base=WORK):
        with self.locked():
            batch,packet=self.packet(sequence,base)
            self.append({'kind':'dispatch','sequence':sequence,'request_id':batch['request_id'],'phase':batch['phase'],'index':batch['index'],'source_refs':packet['source_refs']})
            return batch
    def accept(self,sequence,response,base=WORK):
        with self.locked():
            authorize(self.auth,self.manifest);state=self.state();batch=self.manifest['batches'][sequence]
            required(not state['stopped'] and state['inflight'] and state['inflight']['sequence']==sequence,'Response has no matching in-flight request')
            try:
                data=(base/batch['packet_file']).read_bytes();required(sha(data)==batch['packet_sha256'],'Packet changed during flight');packet=json.loads(gzip.decompress(data))
                rows=result_rows(response);required(len(rows)==1 and set(rows[0])=={'etl_receipt'},'Final envelope absent')
                r=rows[0]['etl_receipt'];required(r.get('protocol')=='goalkeep-mcp-etl-v1' and r.get('request_id')==batch['request_id'] and r.get('outcome')=='completed','Receipt binding failed')
                receipts=r['receipts'];required([v.get('table') for v in receipts]==packet['tables'],'Receipt cardinality/table mismatch')
                required(all(set(v)=={'table','inserted'} and type(v['inserted']) is int and v['inserted'] in (0,1) for v in receipts),'Invalid insert receipt')
                # Current bounded first recovery expects every remaining data record to be new.
                required(all(v['inserted']==1 for v in receipts),'Unexpected preexisting record; stop for reconciliation')
                counts={}
                for v in receipts:counts[v['table']]=counts.get(v['table'],0)+v['inserted']
                self.append({'kind':'ack','sequence':sequence,'request_id':batch['request_id'],'inserted_by_table':counts})
                return self.state()
            except Exception:
                self.append({'kind':'unknown','sequence':sequence,'request_id':batch['request_id'],'reason':'Tool/commit/receipt outcome unknown or unexpected; no retry'})
                raise ValueError('Recovery stopped; inspect live checkpoint before separate recovery approval') from None
    def diagnose(self,snapshot,series):
        state=self.state();n=state['acknowledged']
        status='matches_acknowledged_checkpoint' if snapshot==series[n] else 'committed_without_ack' if state['inflight'] and snapshot==series[n+1] else 'conflict'
        return {**state,'database_diagnosis':status,'automatic_advance_permitted':False}
