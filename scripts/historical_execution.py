"""Local checkpoint/packet gate for a separately approved original-date increment.

No network implementation. Connected MCP must supply fresh read-only state and
official receipts; preparing this coordinator does not grant write permission.
An in-flight/failed/unknown request blocks every following dispatch.
"""
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import fcntl
import json
from etl_core import ROOT, canonical, required
from historical_recovery import W, sha
from recovery import atomic_save, source_integrity, check_hashes
from remote_etl import verify_target, result_rows


def check_approval(auth,manifest,now=None):
    now=now or datetime.now(timezone.utc)
    required(auth.get('approved') is True and auth.get('active') is True,'Separate explicit active owner authorization required')
    required(auth.get('project_reference')==manifest['project_reference']=='hmlbdozsqxlwzvjimjwh','Wrong destination')
    required(manifest['region']=='ap-northeast-1' and manifest['version']=='original-date-recovery-v1','Wrong region/mode')
    required(auth.get('manifest_sha256')==sha(canonical(manifest).encode()),'Wrong approved manifest')
    required(bool(auth.get('approval_reference')),'Owner approval evidence required')
    start=datetime.fromisoformat(auth['issued_at']);end=datetime.fromisoformat(auth['expires_at'])
    required(start.tzinfo and end.tzinfo and start<=now<end and end-start<=timedelta(hours=4),'Approval expired/invalid')


class Coordinator:
    def __init__(self,manifest,auth,directory=None):
        self.manifest=manifest;self.auth=auth;self.directory=directory or W/'execution'
        self.directory.mkdir(exist_ok=True,parents=True,mode=0o700)

    @contextmanager
    def lock(self):
        with (self.directory/'lock').open('a') as f:
            fcntl.flock(f,fcntl.LOCK_EX)
            try:yield
            finally:fcntl.flock(f,fcntl.LOCK_UN)

    def events(self):
        p=self.directory/'journal.json';events=json.loads(p.read_text()) if p.exists() else []
        previous=None
        for e in events:
            data={k:v for k,v in e.items() if k!='sha256'}
            required(e['previous']==previous and sha(canonical(data).encode())==e['sha256'],'Journal integrity failure')
            if e['kind']=='ack':required(sha((self.directory/f"receipt-{e['index']:04}.json").read_bytes())==e['response_file_sha256'],'Receipt integrity failure')
            previous=e['sha256']
        return events

    def append(self,kind,**data):
        events=self.events();event={'kind':kind,**data,'at_utc':datetime.now(timezone.utc).isoformat(),'previous':events[-1]['sha256'] if events else None}
        event['sha256']=sha(canonical(event).encode());atomic_save(self.directory/'journal.json',events+[event])

    def preflight(self,project,state,catalog,ledger):
        check_approval(self.auth,self.manifest);verify_target(project)
        check_hashes(self.manifest['code_sha256'])
        required(source_integrity()==self.manifest['source_binding'],'Source snapshot changed')
        required(sha((W/'date-recovery-updates.json').read_bytes())==self.manifest['private_updates_sha256'],'Recovery values changed')
        required(not self.events(),'Nonempty execution journal: checkpoint diagnosis and separate bounded recovery approval required')
        required(state['tables']==self.manifest['starting_table_fingerprints'] and state['active_imports']==0,'Live starting state changed/import active')
        required(sha(canonical(catalog).encode())==self.manifest['catalog_sha256'] and ledger==self.manifest['migration_ledger'],'Schema/security/ledger changed')
        with self.lock():
            required(not self.events(),'Concurrent execution initialization')
            self.append('preflight',manifest_sha256=sha(canonical(self.manifest).encode()))

    def dispatch(self,index):
        with self.lock():
            check_approval(self.auth,self.manifest);check_hashes(self.manifest['code_sha256'])
            events=self.events();acks=[e for e in events if e['kind']=='ack']
            required(events and events[-1]['kind'] in {'preflight','ack'} and index==len(acks),'Repeated/out-of-order/uncertain request')
            b=self.manifest['batches'][index];required(b['index']==index,'Batch sequence changed')
            query=(W/'date-batches'/f'{index:04}.sql').read_text();required(sha(query.encode())==b['query_sha256'],'SQL packet changed')
            self.append('dispatch',index=index,request_id=b['request_id'])
            return {'project_id':self.manifest['project_reference'],'query':query,'request_id':b['request_id']}

    def accept(self,index,response):
        with self.lock():
            events=self.events();b=self.manifest['batches'][index]
            required(events[-1]['kind']=='dispatch' and events[-1]['index']==index,'No matching in-flight transaction')
            atomic_save(self.directory/f'receipt-{index:04}.json',response)
            try:
                rows=result_rows(response)
                required(rows==[{'receipt':{'recovery_id':b['recovery_id'],'target_id':b['target_id'],'outcome':'completed'}}],'Uncertain or conflicting receipt')
            except Exception:
                self.append('stopped',index=index,request_id=b['request_id']);raise
            self.append('ack',index=index,request_id=b['request_id'],response_file_sha256=sha((self.directory/f'receipt-{index:04}.json').read_bytes()))
