#!/usr/bin/env python3
"""Destination-bound MCP adapter. Preflight prepares only; serve requires separate owner authorization.
No credentials, URLs, HTTP clients or arbitrary SQL execution entry point are accepted.
"""
from collections import Counter
from datetime import datetime,timezone,timedelta
import argparse
import hashlib
import json
import os
import uuid
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from etl_core import ROOT,required,validate_plan,ordered_batches,compile_batch,compile_record,sql_text,canonical
from etl_loader import status_batches,load_plan
from prepare_etl import private_save

PROJECT='hmlbdozsqxlwzvjimjwh'
NAME='kc2-integrated-data-system'
REGION='ap-northeast-1'
PROTOCOL='goalkeep-mcp-etl-v1'
SCOPE='source-preservation-and-pending-verified-id-v1'
PRIVATE=ROOT/'work/remote-etl'

def sha(value):return hashlib.sha256(value).hexdigest()
def result_rows(response):
    required(isinstance(response,dict) and response.get('isError') is not True,'MCP execution error; outcome unknown')
    data=response.get('structuredContent')
    if data is None:
        blocks=[x['text'] for x in response.get('content',[]) if x.get('type')=='text']
        required(len(blocks)==1,'Unexpected MCP content')
        data=json.loads(blocks[0])
    if isinstance(data,dict) and 'result' in data:
        if isinstance(data['result'],list):return data['result']
        wrapper=data['result']
        match=re.search(r'\n<untrusted-data-([^>]+)>\s*([\s\S]*?)\s*</untrusted-data-\1>',wrapper)
        required(match is not None,'Unknown MCP result wrapper; outcome unknown')
        data=json.loads(match.group(2))
    required(isinstance(data,list),'Unexpected MCP result shape; outcome unknown')
    return data

def verify_target(project):
    required(project.get('id')==PROJECT and project.get('name')==NAME and project.get('region')==REGION,'Destination mismatch')
    required(project.get('status')=='ACTIVE_HEALTHY' and project.get('database',{}).get('postgres_engine')=='17','Target unhealthy or database version changed')

def mcp_batch(records,request_id):
    # Last SELECT carries every receipt; individual result sets are not relied upon by MCP.
    return ("BEGIN; SET LOCAL standard_conforming_strings=on; SET LOCAL lock_timeout='5s'; SET LOCAL statement_timeout='60s';\n"
        "SET LOCAL application_name='goalkeep-kc2-sanitized-import'; SET LOCAL \"gk.etl_receipts\"='[]';\n"
        "DO $role$ BEGIN IF current_user <> 'postgres' THEN RAISE EXCEPTION 'ETL_MIGRATION_IDENTITY_REQUIRED'; END IF; END; $role$;\n"
        +''.join(compile_record(r,aggregate_receipts=True) for r in records)
        +"SET CONSTRAINTS ALL IMMEDIATE;\n"+envelope_select(request_id)+"COMMIT;\n")

def envelope_select(request_id):
    return "SELECT jsonb_build_object('protocol',"+sql_text(PROTOCOL)+",'request_id',"+sql_text(request_id)+",'receipts',current_setting('gk.etl_receipts')::jsonb,'outcome','completed') AS etl_receipt;\n"

def requests_for(plan):
    for n,records in enumerate(ordered_batches(plan)):
        local=compile_batch(records);rid=sha(('data:'+str(n)+':'+sha(local.encode())).encode())
        yield {'phase':'data','index':n,'request_id':rid,'local_sql':local,'query':mcp_batch(records,rid),
               'tables':[r['table'] for r in records],
               'source_references':sorted({x for r in records for x in r.get('source_refs',[])})}
    for n,local in enumerate(status_batches(plan)):
        rid=sha(('status:'+str(n)+':'+sha(local.encode())).encode())
        required(local.endswith('COMMIT;'),'Status transaction contract changed')
        wire=local[:-len('COMMIT;')]+"SET LOCAL application_name='goalkeep-kc2-sanitized-import'; SET LOCAL \"gk.etl_receipts\"='[]';\n"+envelope_select(rid)+'COMMIT;'
        yield {'phase':'source_status','index':n,'request_id':rid,'local_sql':local,'query':wire,'tables':[],
               'source_references':[x['reference'] for x in plan['source_statuses'][n*250:(n+1)*250]]}

def prepared():
    data=(ROOT/'work/etl/plan.json').read_bytes();plan=json.loads(data)
    evidence=json.loads((ROOT/'docs/evidence/etl-preparation.json').read_text())
    required(sha(data)==evidence['plan_sha256'],'Snapshot differs from Stage 4A')
    required(plan['destination_reference']==PROJECT and plan['sanitized'] and plan['remote_loading_authorized'] is False,'Unsafe plan')
    validate_plan(plan);requests=list(requests_for(plan))
    manifest={'protocol':PROTOCOL,'project_reference':PROJECT,'project_name':NAME,'region':REGION,'scope':SCOPE,
        'plan_sha256':sha(data),'remote_write_authorized':False,'batch_size':250,
        'code_sha256':{x:sha((ROOT/'scripts'/x).read_bytes()) for x in ['remote_etl.py','etl_core.py','etl_loader.py','mcp_etl_bridge.mjs']},
        'batches':[{'phase':r['phase'],'index':r['index'],'request_id':r['request_id'],'query_sha256':sha(r['query'].encode()),
            'sql_bytes':len(r['query'].encode()),'records':len(r['tables']),'source_rows':len(r['source_references'])} for r in requests],
        'direct_inserts':evidence['expected_target_counts'],'source_record_updates':len(plan['source_statuses']),
        'generated_audit_inserts':plan['expected_generated_audit_rows']}
    return plan,requests,manifest

def authorize(authorization,manifest,now=None):
    now=now or datetime.now(timezone.utc)
    required(authorization.get('approved') is True and authorization.get('project_reference')==PROJECT and authorization.get('scope')==SCOPE,'Explicit scoped owner authorization required')
    required(authorization.get('plan_sha256')==manifest['plan_sha256'] and authorization.get('manifest_sha256')==sha(canonical(manifest).encode()),'Authorization does not bind current manifest')
    required(isinstance(authorization.get('approval_reference'),str) and bool(authorization['approval_reference'].strip()),'Owner approval evidence reference required')
    issued=datetime.fromisoformat(authorization['issued_at']);expires=datetime.fromisoformat(authorization['expires_at'])
    required(issued.tzinfo is not None and expires.tzinfo is not None and issued<=now<expires and expires-issued<=timedelta(hours=24),'Authorization expired, future-dated or too broad')

class MCPExecutor:
    """An exact compiled-query allowlist implements existing loader db.sql through connected MCP.
    transport(project_id, query, request_id) must return the complete MCP tool result.
    No automatic retries: network/receipt/commit ambiguity is a stop, followed by reconciliation.
    """
    def __init__(self,transport,project,requests,manifest,authorization,event_sink=None):
        verify_target(project);authorize(authorization,manifest)
        required(manifest['project_reference']==PROJECT,'Wrong manifest destination')
        actual=[{'phase':r['phase'],'index':r['index'],'request_id':r['request_id'],'query_sha256':sha(r['query'].encode()),
            'sql_bytes':len(r['query'].encode()),'records':len(r['tables']),'source_rows':len(r['source_references'])} for r in requests]
        required(actual==manifest['batches'],'Compiled requests differ from authorized manifest')
        self.transport=transport;self.project=PROJECT;self.allowed={sha(r['local_sql'].encode()):dict(r) for r in requests}
        required(len(self.allowed)==len(requests),'Repeated batch request')
        self.used=set();self.stopped=False;self.events=[];self.event_sink=event_sink
    def emit(self,event):
        self.events.append(event)
        if self.event_sink is not None:self.event_sink(event)
    def sql(self,query):
        required(not self.stopped,'Executor stopped; reconcile before creating a new run')
        digest=sha(query.encode());required(digest in self.allowed,'SQL outside reviewed compiled manifest')
        r=self.allowed[digest];required(digest not in self.used,'Duplicate in-flight request; reconcile instead of retrying')
        self.used.add(digest)
        # Durable metadata precedes the tool call so interruption leaves an identifiable in-flight request.
        self.emit({'phase':r['phase'],'index':r['index'],'request_id':r['request_id'],'outcome':'submission_pending','source_references':r['source_references']})
        try:
            response=self.transport(project_id=PROJECT,query=r['query'],request_id=r['request_id'])
            rows=result_rows(response)
            required(len(rows)==1 and set(rows[0])=={'etl_receipt'},'Missing final batch envelope; outcome unknown')
            receipt=rows[0]['etl_receipt']
            required(receipt.get('protocol')==PROTOCOL and receipt.get('request_id')==r['request_id'] and receipt.get('outcome')=='completed','Receipt binding failed; outcome unknown')
            values=receipt['receipts'];required([v.get('table') for v in values]==r['tables'],'Receipt table/cardinality mismatch')
            required(all(type(v.get('inserted')) is int and v['inserted'] in (0,1) and set(v)=={'table','inserted'} for v in values),'Invalid receipt')
            self.emit({'phase':r['phase'],'index':r['index'],'request_id':r['request_id'],'outcome':'acknowledged','source_references':r['source_references'],'inserted_by_table':dict(Counter(v['table'] for v in values if v['inserted']==1))})
            return SimpleNamespace(returncode=0,stdout='\n'.join(json.dumps(v) for v in values),stderr='')
        except Exception:
            self.stopped=True
            try:self.emit({'phase':r['phase'],'index':r['index'],'request_id':r['request_id'],'outcome':'unknown_or_failed','source_references':r['source_references'],'resolution':'Stop; inspect live counts and exact payloads before authorized replay'})
            except OSError:pass
            return SimpleNamespace(returncode=1,stdout='',stderr='ERROR: UNKNOWN: MCP outcome unknown or failed; reconcile before replay')

def verify_bridge_request():
    manifest=json.loads((PRIVATE/'manifest.json').read_text());authorization=json.loads((PRIVATE/'owner-authorization.json').read_text())
    authorize(authorization,manifest)
    for file,digest in manifest['code_sha256'].items():required(sha((ROOT/'scripts'/file).read_bytes())==digest,'Adapter code changed')
    request=json.loads((PRIVATE/'request.json').read_text())
    required(request['project_id']==PROJECT,'Bridge destination mismatch')
    batches=[b for b in manifest['batches'] if b['request_id']==request['request_id']]
    required(len(batches)==1 and batches[0]['query_sha256']==sha(request['query'].encode()),'Bridge query outside authorized manifest')


class FileTransport:
    """Credential-free bridge to the active session's authorized Supabase tool; never prints SQL."""
    def __call__(self,**request):
        path=PRIVATE/'request.json';private_save(path,request)
        print(json.dumps({'request_file':'work/remote-etl/request.json','request_id':request['request_id'],'query_bytes':len(request['query'].encode())}),flush=True)
        ack=json.loads(sys.stdin.readline())
        required(ack=={'response_ready':request['request_id']},'MCP bridge acknowledgement mismatch')
        response=json.loads((PRIVATE/'response.json').read_text())
        return response

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--serve-approved',type=Path);args=parser.parse_args()
    plan,requests,manifest=prepared()
    if args.serve_approved:
        # Only the orchestration bridge should start this after fresh online preflight.
        auth=json.loads(args.serve_approved.read_text());authorize(auth,manifest)
        if sys.stdin.isatty():
            import termios
            mode=termios.tcgetattr(sys.stdin.fileno());mode[3]&=~termios.ECHO;termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,mode)
        project=json.loads((PRIVATE/'fresh-project.json').read_text())
        run_id=uuid.uuid4().hex
        def journal(event):
            path=PRIVATE/'execution-journal.jsonl'
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
            with os.fdopen(fd,'w') as stream:
                stream.write(canonical({'run_id':run_id,'project_reference':PROJECT,'plan_sha256':manifest['plan_sha256'],**event})+'\n');stream.flush();os.fsync(stream.fileno())
        journal({'outcome':'run_started','manifest_sha256':sha(canonical(manifest).encode()),'approval_reference':auth['approval_reference']})
        db=MCPExecutor(FileTransport(),project,requests,manifest,auth,event_sink=journal)
        try:
            receipt=load_plan(db,plan);private_save(PRIVATE/'load-receipt.json',receipt)
            print(json.dumps({'complete':receipt['status'],'inserted':sum(receipt['inserted'].values())}),flush=True)
        finally:private_save(PRIVATE/'execution-events.json',db.events)
        return 0 if receipt['status']=='passed' else 1
    private_save(PRIVATE/'manifest.json',manifest)
    summary={k:v for k,v in manifest.items() if k!='batches'}
    summary.update(manifest_sha256=sha(canonical(manifest).encode()),data_batches=sum(x['phase']=='data' for x in requests),status_batches=sum(x['phase']=='source_status' for x in requests),
        total_sql_bytes=sum(x['sql_bytes'] for x in manifest['batches']),max_batch_sql_bytes=max(x['sql_bytes'] for x in manifest['batches']),max_records=max(x['records'] for x in manifest['batches']))
    (ROOT/'docs/evidence/stage4b-batch-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
