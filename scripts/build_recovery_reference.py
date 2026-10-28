#!/usr/bin/env python3
"""Derive deterministic checkpoint digests from exact approved SQL, in disposable LOCAL PostgreSQL only."""
import json,time,uuid
from etl_core import ROOT,required
from remote_etl import prepared
from recovery_snapshot import snapshot_sql
from run_postgres_tests import LocalDatabase,IMAGE

def start_db(tag):
    db=LocalDatabase('gk-kc2-'+tag+'-'+uuid.uuid4().hex[:10])
    r=db.docker('run','--rm','-d','--network','none','--name',db.name,'--label','gk.kc2.disposable=true','--tmpfs','/var/lib/postgresql/data','-e','POSTGRES_HOST_AUTH_METHOD=trust',IMAGE)
    required(r.returncode==0,'Local disposable database unavailable')
    for _ in range(50):
        if db.sql('SELECT 1').returncode==0:break
        time.sleep(.2)
    else:raise ValueError('Local readiness timeout')
    db.execute((ROOT/'tests/sql/local-auth-bootstrap.sql').read_text())
    for p in sorted((ROOT/'supabase/migrations').glob('*.sql')):db.execute(p.read_text())
    return db

def snapshot(db):return json.loads(db.execute(snapshot_sql()))
def main():
    _,requests,_=prepared();db=start_db('recovery-reference');report={'scope':'Local network=none reference from exact original SQL; no remote writes'}
    try:
        for r in requests[:40]:required(db.sql(r['query']).returncode==0,'Local prefix load failed')
        series=[snapshot(db)]
        for n,r in enumerate(requests[40:]):
            required(db.sql(r['query']).returncode==0,'Local reference request failed')
            series.append(snapshot(db))
            if n%20==0:print('Reference checkpoint '+str(n+1)+'/179',flush=True)
        required(len(series)==180,'Reference incomplete')
        (ROOT/'docs/evidence/stage4c-reference-checkpoints.json').write_text(json.dumps(series,separators=(',',':'))+'\n')
        report.update(status='passed',checkpoints=180,final_counts={k:v['rows'] for k,v in series[-1]['tables'].items()})
    finally:report['container_removed']=db.docker('rm','-f',db.name).returncode==0
    (ROOT/'docs/evidence/stage4c-reference-build.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
