#!/usr/bin/env python3
"""Execute full connector-shaped ETL locally only; no credentials or remote transports accepted."""
import importlib.util
import json
import math
import time
import unittest
import uuid
from run_postgres_tests import LocalDatabase,IMAGE,ROOT
from remote_etl import prepared,MCPExecutor
from test_remote_etl import project_fixture,authorization_fixture,wrapper
from etl_loader import load_plan,count_tables,reconcile_loaded
from etl_core import required

def main():
    plan,requests,manifest=prepared();db=LocalDatabase('gk-kc2-mcp-local-'+uuid.uuid4().hex[:10]);times=[]
    report={'scope':'Connector-shaped local PostgreSQL execution; no remote writes','network':'none','plan_sha256':manifest['plan_sha256'],'code_sha256':manifest['code_sha256']}
    result=db.docker('run','--rm','-d','--network','none','--name',db.name,'--label','gk.kc2.disposable=true','--tmpfs','/var/lib/postgresql/data','-e','POSTGRES_HOST_AUTH_METHOD=trust',IMAGE)
    required(result.returncode==0,'Local adapter test database startup failed')
    try:
        for _ in range(50):
            if db.sql('SELECT 1').returncode==0:break
            time.sleep(.2)
        else:raise ValueError('Local readiness timeout')
        db.execute((ROOT/'tests/sql/local-auth-bootstrap.sql').read_text())
        for p in sorted((ROOT/'supabase/migrations').glob('*.sql')):db.execute(p.read_text())
        def transport(**request):
            t=time.monotonic();r=db.sql(request['query']);times.append(time.monotonic()-t)
            if r.returncode:
                from prepare_etl import private_save
                private_save(ROOT/'work/remote-etl/local-wire-error.json',{'stderr':r.stderr,'request_id':request['request_id']})
                return {'isError':True,'content':[{'type':'text','text':'Synthetic database error details withheld'}]}
            rows=[json.loads(line) for line in r.stdout.splitlines() if line.startswith('{')]
            required(len(rows)==1 and rows[0].get('protocol')=='goalkeep-mcp-etl-v1','Local wire receipt contract failed')
            return wrapper([{'etl_receipt':rows[0]}])
        auth=authorization_fixture(manifest)
        executor=MCPExecutor(transport,project_fixture(),requests,manifest,auth)
        t=time.monotonic();first=load_plan(executor,plan);elapsed=time.monotonic()-t
        report['first_load']=first
        required(first['status']=='passed','Adapter first load failed')
        counts=count_tables(db);reconciled=reconcile_loaded(plan,counts,first)
        required(reconciled['status']=='passed' and counts['record_audit_events']==plan['expected_generated_audit_rows'],'Adapter target/audit reconciliation failed')
        size=db.execute("SELECT jsonb_object_agg(name,bytes) FROM (SELECT 'application_total' name,sum(pg_total_relation_size(c.oid)) bytes FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','gk_private') AND c.relkind='r' UNION ALL SELECT 'audit_total',pg_total_relation_size('gk_private.record_audit_events')) sizes")
        replay=MCPExecutor(transport,project_fixture(),requests,manifest,auth);second=load_plan(replay,plan)
        required(second['status']=='passed' and sum(second['inserted'].values())==0 and count_tables(db)==counts,'Adapter replay mismatch')
        spec=importlib.util.spec_from_file_location('etl_runtime_cases',ROOT/'tests/etl_runtime_cases.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.DB=db
        tests=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(module))
        report.update(status='passed' if tests.wasSuccessful() else 'failed',runtime_cases=tests.testsRun,failures=len(tests.failures),errors=len(tests.errors),
            first_load=first,target_reconciliation=reconciled,replay_insertions=sum(second['inserted'].values()),all_counts_and_audit_unchanged=True,
            first_load_seconds=round(elapsed,3),batch_max_seconds=round(max(times),3),batch_p95_seconds=round(sorted(times)[math.ceil(len(times)*.95)-1],3),
            local_relation_bytes=json.loads(size),remote_performance_estimate='Not measured; local times and physical sizes are indicative only')
    except Exception as exc:report.update(status='failed',reason=str(exc))
    finally:
        report['container_removed']=db.docker('rm','-f',db.name).returncode==0
        (ROOT/'docs/evidence/stage4b-adapter-runtime.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'first_load','target_reconciliation'}},indent=2))
    return 0 if report['status']=='passed' and report['container_removed'] else 1
if __name__=='__main__':raise SystemExit(main())
