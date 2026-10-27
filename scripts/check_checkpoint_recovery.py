#!/usr/bin/env python3
"""Offline integrity/readiness checks for Stage 4C. Never connects to any database."""
import ast,json,subprocess
from pathlib import Path
from recovery import ROOT,WORK,load,sha,hashed,validate_manifest,required

def main():
 m=load(WORK/'manifest.json');series=validate_manifest(m)
 required(load(ROOT/'docs/evidence/stage4c-recovery-manifest.json')==m,'Published manifest differs')
 required(len(series)==180 and m['remaining_transactions']==179,'Checkpoint/request coverage differs')
 required([(b['phase'],b['index']) for b in m['batches']]==[('data',i) for i in range(40,137)]+[('source_status',i) for i in range(82)],'Wrong transaction order')
 required(len({b['request_id'] for b in m['batches']})==179,'Duplicate request IDs')
 for b in m['batches']:
  import gzip
  data=(WORK/b['packet_file']).read_bytes();required(sha(data)==b['packet_sha256'] and len(data)==b['packet_bytes'],'Packet changed')
  p=json.loads(gzip.decompress(data));required(p['project_id']==m['project_reference'] and p['request_id']==b['request_id'] and sha(p['query'].encode())==b['query_sha256'],'Packet SQL/destination changed')
 required(load(ROOT/'docs/evidence/stage4c-live-checkpoint.json')==series[0],'Live checkpoint differs from committed prefix')
 required(load(ROOT/'docs/evidence/stage4c-live-anchor.json')==m['prefix_immutable_metadata'],'Live immutable anchor differs')
 required(load(ROOT/'docs/evidence/stage4c-live-catalog.json')==load(ROOT/'docs/evidence/expected-deployment-catalog.json'),'Saved live catalog differs')
 final={k:v['rows'] for k,v in series[-1]['tables'].items()}
 required(final['record_audit_events']==28293 and sum(v for k,v in final.items() if k!='record_audit_events')==34077,'Expected final count differs')
 required(final=={**m['expected_final_direct_counts'],'record_audit_events':28293},'Manifest/reference counts disagree')
 required(series[-1]['source_states']==m['expected_source_states'],'Source status totals disagree')
 runtime=load(ROOT/'docs/evidence/stage4c-runtime-tests.json');required(runtime['status']=='passed' and all(runtime['tests'].values()) and runtime['containers_removed'] and runtime['recovery_manifest_sha256']==hashed(m),'Runtime tests incomplete or stale')
 for name in ['stage4c-bridge-tests.json','stage4c-security-tests.json']:
  r=load(ROOT/'docs/evidence'/name);required(r['status']=='passed','Offline bridge/security test failure')
 required(load(ROOT/'docs/evidence/stage4c-bridge-tests.json')['packets_verified']==179,'Bridge packet coverage incomplete')
 required(len(load(ROOT/'docs/evidence/stage4c-security-tests.json')['checks'])==11,'Denial tests incomplete')
 live=load(ROOT/'docs/evidence/stage4c-live-preflight.json');required(live['status']=='passed' and live['manifest_sha256']==hashed(m) and live['checkpoint']==0 and live['remote_writes']==0,'Final-code live read-only preflight missing')
 from pglast import parse_sql
 for name in ['snapshot.sql','anchor.sql']:parse_sql((WORK/name).read_text())
 for entry in load(ROOT/'scripts/vendor/recovery-dependencies.json'):required(sha((ROOT/entry['file']).read_bytes())==entry['sha256'],'Vendor source changed')
 for name in [31,32,33]:required(len(list((ROOT/'docs').glob(str(name)+'-*.md')))==1,'Recovery document missing')
 required(hashed(m) in (ROOT/'docs/33-recovery-execution-readiness.md').read_text(),'Readiness manifest hash missing')
 for p in (ROOT/'scripts').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for p in ['scripts/recovery_bridge.mjs','tests/test_recovery_bridge.mjs']:subprocess.run(['node','--check',p],cwd=ROOT,check=True,capture_output=True)
 required(not (WORK/'owner-authorization.json').exists() and not (ROOT/'work/remote-etl/owner-authorization.json').exists(),'Unexpected active authorization')
 required(not (WORK/'execution/journal.jsonl').exists(),'Recovery execution journal unexpectedly active')
 required(subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='feature/phase1-data-backend','Wrong branch')
 required(subprocess.check_output(['git','diff','--name-only','e09c5da','--','supabase/migrations','scripts/remote_etl.py','scripts/etl_core.py','scripts/etl_loader.py','scripts/mcp_etl_bridge.mjs'],cwd=ROOT,text=True).strip()=='','Immutable implementation modified')
 subprocess.run(['git','diff','--check'],cwd=ROOT,check=True,capture_output=True)
 r={'status':'passed','recovery_manifest_sha256':hashed(m),'remaining_transactions':179,'reference_checkpoints':180,'packets_sha256_verified':179,'original_loader_sql_unchanged':True,'live_checkpoint_verified':0,'remote_recovery_writes':0,'execution_authorized':False,'unit_tests':82,'isolated_recovery_cases':len(runtime['tests']),'offline_bridge_cases':len(load(ROOT/'docs/evidence/stage4c-bridge-tests.json')['tests']),'local_denial_checks':11}
 (ROOT/'docs/evidence/stage4c-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
