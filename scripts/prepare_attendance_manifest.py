#!/usr/bin/env python3
"""Produce exact destination-bound attendance deployment/import manifests and private SQL packets. No remote writes."""
import json,hashlib,gzip
from attendance_import import ROOT,WORK,E,build,batches,VERSION
from etl_core import canonical,required
from recovery import atomic_save
PROJECT='hmlbdozsqxlwzvjimjwh';REGION='ap-northeast-1'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 rows,summary=build();path=next((ROOT/'supabase/migrations').glob('*_attendance_import_staging.sql'))
 migration={'project_reference':PROJECT,'project_name':'kc2-integrated-data-system','region':REGION,'environment':'non-production pilot','migration_file':str(path.relative_to(ROOT)),'migration_sha256':SHA(path.read_bytes()),'baseline_migration_ledger':json.loads((E/'stage4c-final-live-ledger.json').read_text()),'baseline_counts':json.loads((E/'attendance-remote-preflight.json').read_text())['counts'],'baseline_catalog_sha256':SHA(canonical(json.loads((E/'stage4c-final-live-catalog.json').read_text())).encode()),'changes':['one restricted staging table and its new guard function/triggers/indexes'],'existing_19_tables_modified':False,'existing_policies_modified':False,'existing_audit_history_modified':False,'remote_execution_authorized':False}
 atomic_save(WORK/'deployment-manifest.json',migration);(E/'attendance-deployment-manifest.json').write_text(json.dumps(migration,indent=2)+'\n')
 entries=[];folder=WORK/'batches';folder.mkdir(exist_ok=True,mode=0o700)
 for i,query in enumerate(batches(rows)):
  payload={'project_id':PROJECT,'query':query,'request_id':SHA((VERSION+':'+str(i)+':'+SHA(query.encode())).encode())};data=gzip.compress(canonical(payload).encode(),mtime=0);file=folder/f'{i:04}.json.gz';file.write_bytes(data);file.chmod(0o600)
  entries.append({'index':i,'request_id':payload['request_id'],'rows':len(rows[i*200:(i+1)*200]),'query_sha256':SHA(query.encode()),'packet_sha256':SHA(data),'packet_bytes':len(data),'packet_file':str(file.relative_to(WORK))})
 manifest={'project_reference':PROJECT,'region':REGION,'version':VERSION,'migration_manifest_sha256':SHA(canonical(migration).encode()),'source_snapshot_sha256':summary['source_integrity']['source_snapshot_sha256'],'records_sha256':SHA((WORK/'records.json').read_bytes()),'staging_table':'gk_private.attendance_import_staging','expected_staging_inserts':len(rows),'expected_operational_inserts':0,'source_rows_modified':0,'existing_audit_events_modified_or_added':0,'batch_size':200,'batch_count':len(entries),'batches':entries,'code_sha256':{p:SHA((ROOT/p).read_bytes()) for p in ['scripts/attendance_import.py','scripts/prepare_attendance_manifest.py']},'counts':{k:v for k,v in summary.items() if k!='sheets'},'failure_rule':'Stop after first failed/uncertain transaction; preserve acknowledgments, inspect read-only; no automatic retry','safe_replay':'same source coordinate and exact payload required; conflicting record or later review state rejects whole transaction','owner_authorization_required':True,'remote_execution_authorized':False}
 atomic_save(WORK/'import-manifest.json',manifest);(E/'attendance-import-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 hashes={'deployment_manifest_sha256':SHA(canonical(migration).encode()),'import_manifest_sha256':SHA(canonical(manifest).encode()),'migration_sql_sha256':migration['migration_sha256'],'remote_applied':False}
 (E/'attendance-approval-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n');print(json.dumps({**hashes,'batches':len(entries),'staging_records':len(rows)}))
if __name__=='__main__':main()
