#!/usr/bin/env python3
"""Load/test sanitized bundles only in a disposable network-isolated PostgreSQL container."""
import hashlib
import importlib.util
import json
import time
import unittest
import uuid
from pathlib import Path
from run_postgres_tests import LocalDatabase,ROOT,IMAGE
from etl_loader import load_plan,count_tables,reconcile_loaded
from etl_core import validate_plan,required

def main():
    db=LocalDatabase('gk-kc2-etl-'+uuid.uuid4().hex[:12])
    start=db.docker('run','--rm','-d','--network','none','--name',db.name,
                    '--label','gk.kc2.disposable=true','--tmpfs','/var/lib/postgresql/data',
                    '-e','POSTGRES_HOST_AUTH_METHOD=trust',IMAGE)
    if start.returncode:raise SystemExit('Isolated ETL database startup failed; no remote fallback')
    report={'scope':'Local PostgreSQL 17 only; sanitized pilot bundle plus synthetic negative cases',
            'image':IMAGE,'network':'none','remote_data_loaded':False}
    try:
        for _ in range(50):
            if db.sql('SELECT 1').returncode==0:break
            time.sleep(.2)
        else:raise ValueError('Local readiness timeout')
        db.execute((ROOT/'tests/sql/local-auth-bootstrap.sql').read_text())
        for path in sorted((ROOT/'supabase/migrations').glob('*.sql')):db.execute(path.read_text())
        plan_path=ROOT/'work/etl/plan.json';plan_bytes=plan_path.read_bytes();plan=json.loads(plan_bytes);validate_plan(plan)
        report['plan_sha256']=hashlib.sha256(plan_bytes).hexdigest()
        print('Running isolated load/replay for validated sanitized bundle.',flush=True)
        first=load_plan(db,plan);required(first['status']=='passed','First sanitized load failed; inspect protected batch report')
        counts=count_tables(db);reconciliation=reconcile_loaded(plan,counts,first)
        required(reconciliation['status']=='passed','Loaded target counts differ')
        required(counts['record_audit_events']==plan['expected_generated_audit_rows'],'Generated audit reconciliation differs')
        second=load_plan(db,plan);required(second['status']=='passed' and sum(second['inserted'].values())==0,'Replay inserted duplicates')
        replay_counts=count_tables(db);required(counts==replay_counts,'Replay changed tables or audit history')
        report.update(first_load={'status':first['status'],'inserted':first['inserted'],'committed_batches':first['committed_batches']},
                      second_load={'status':second['status'],'inserted':sum(second['inserted'].values()),'verified_existing':sum(second['already_present_verified'].values()),'all_table_counts_unchanged':True},
                      target_reconciliation=reconciliation)
        spec=importlib.util.spec_from_file_location('etl_runtime_cases',ROOT/'tests/etl_runtime_cases.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.DB=db
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
        required(hashlib.sha256(plan_path.read_bytes()).hexdigest()==report['plan_sha256'],'Bundle changed during tests')
        report.update(status='passed' if result.wasSuccessful() else 'failed',negative_and_transaction_tests=result.testsRun,
                      failures=[str(t) for t,_ in result.failures],errors=[str(t) for t,_ in result.errors])
    except Exception as exc:
        report.update(status='failed',reason=str(exc))
        if 'first' in locals() and first['status']!='passed':
            (ROOT/'work/etl/load-failure.json').write_text(json.dumps(first,indent=2)+'\n')
    finally:
        report['container_removed']=db.docker('rm','-f',db.name).returncode==0
        (ROOT/'docs/evidence/etl-runtime-tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0 if report['status']=='passed' and report['container_removed'] else 1
if __name__=='__main__':raise SystemExit(main())
