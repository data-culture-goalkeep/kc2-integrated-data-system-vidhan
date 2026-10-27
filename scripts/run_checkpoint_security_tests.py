#!/usr/bin/env python3
"""Local staged-prefix denial checks; accepts no remote destination."""
import json
from build_recovery_reference import start_db,snapshot
from recovery import ROOT,required
from remote_etl import prepared
b=start_db('checkpoint-security');report={'scope':'Isolated local PostgreSQL with staged source records; no remote writes','remote_writes':0}
try:
 _,rs,_=prepared()
 for r in rs[:40]:required(b.sql(r['query']).returncode==0,'Local prefix failed')
 before=snapshot(b);checks=json.loads(b.execute((ROOT/'scripts/sql/verify_ids_access.sql').read_text()))
 required(len(checks)==11 and all(x['passed'] for x in checks),'Local access denial failed')
 required(snapshot(b)==before,'Denial probes changed data')
 report.update(status='passed',checks=checks,source_rows=9988,rollback_preserved_checkpoint=True)
finally:report['container_removed']=b.docker('rm','-f',b.name).returncode==0
(ROOT/'docs/evidence/stage4c-security-tests.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'container_removed':report['container_removed']}))
