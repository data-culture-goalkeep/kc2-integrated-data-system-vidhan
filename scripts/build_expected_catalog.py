#!/usr/bin/env python3
"""Generate the approved schema catalog in a throwaway local database, without any records."""
import json
import time
import uuid
from run_postgres_tests import LocalDatabase,ROOT,IMAGE

def main():
    db=LocalDatabase('gk-kc2-catalog-'+uuid.uuid4().hex[:12])
    start=db.docker('run','--rm','-d','--network','none','--name',db.name,
                    '--label','gk.kc2.disposable=true','--tmpfs','/var/lib/postgresql/data',
                    '-e','POSTGRES_HOST_AUTH_METHOD=trust',IMAGE)
    if start.returncode:raise RuntimeError('Local disposable startup failed')
    try:
        for _ in range(50):
            if db.sql('SELECT 1').returncode==0:break
            time.sleep(0.2)
        else:raise RuntimeError('Local readiness failed')
        db.execute((ROOT/'tests/sql/local-auth-bootstrap.sql').read_text())
        for p in sorted((ROOT/'supabase/migrations').glob('*.sql')):db.execute(p.read_text())
        query=(ROOT/'scripts/sql/inspect_ids_catalog.sql').read_text()
        result=json.loads(db.execute('BEGIN READ ONLY; SET LOCAL search_path=pg_catalog;'+query+'ROLLBACK;'))
        (ROOT/'docs/evidence/expected-deployment-catalog.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:len(v) for k,v in result.items()}))
    finally:
        if db.docker('rm','-f',db.name).returncode:raise RuntimeError('Disposable cleanup failed')
if __name__=='__main__':main()
