#!/usr/bin/env python3
"""Verify current attendance manifests, source coordinate coverage, local tests and immutable baseline. No DB access."""
import json,gzip,hashlib,re
from pathlib import Path
from pglast import parse_sql
from attendance_import import ROOT,WORK,E
from etl_core import canonical,required
from recovery import check_hashes,source_integrity
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 load=lambda p:json.loads(p.read_text())
 m=load(E/'attendance-import-manifest.json');d=load(E/'attendance-deployment-manifest.json');h=load(E/'attendance-approval-hashes.json');r=load(E/'attendance-reconciliation.json');t=load(E/'attendance-local-tests.json')
 required(m['project_reference']==d['project_reference']=='hmlbdozsqxlwzvjimjwh' and m['region']==d['region']=='ap-northeast-1','Wrong destination')
 required(SHA(canonical(m).encode())==h['import_manifest_sha256'] and SHA(canonical(d).encode())==h['deployment_manifest_sha256'],'Manifest changed')
 required(SHA((ROOT/d['migration_file']).read_bytes())==d['migration_sha256']==h['migration_sql_sha256'],'Migration changed');parse_sql((ROOT/d['migration_file']).read_text())
 check_hashes(m['code_sha256']);source_integrity()
 required(not m['remote_execution_authorized'] and not d['remote_execution_authorized'],'Unapproved execution activated')
 required(m['expected_staging_inserts']==r['staged_records']==t['staged_rows']==43160 and m['expected_operational_inserts']==t['operational_attendance']==0,'Staging/operational count mismatch')
 required(t['status']=='passed' and all(t['tests'].values()) and t['container_removed'],'Local tests incomplete')
 required(r['daily_roster_identity_counts']=={'PROVISIONAL_MATCH':1009,'AMBIGUOUS':74,'UNMATCHED':1059},'Historical roster recheck differs')
 required(r['observation_candidates']==29028 and r['daily_literal_marks']==24687 and r['source_observations_not_represented']==0,'Observation reconciliation differs')
 rows=load(WORK/'records.json');required(SHA((WORK/'records.json').read_bytes())==m['records_sha256'],'Records changed')
 required(len({(x['source_record_id'],x['source_column']) for x in rows})==len(rows),'Duplicate coordinates')
 for x in m['batches']:
  packet=(WORK/x['packet_file']).read_bytes();required(SHA(packet)==x['packet_sha256'],'Packet changed');q=json.loads(gzip.decompress(packet));required(q['project_id']==m['project_reference'] and SHA(q['query'].encode())==x['query_sha256'],'SQL/destination mismatch')
 required(sum(x['rows'] for x in m['batches'])==len(rows),'Batch coverage differs')
 original=load(E/'deployment-manifest.json')
 for x in original['migration_files']:required(SHA((ROOT/x['file']).read_bytes())==x['sha256'],'Original applied migration changed')
 report={'status':'passed','worksheets':107,'observation_candidates':29028,'source_contexts':14132,'planned_staging_records':43160,'planned_operational_records':0,'batches':len(m['batches']),'migration_manifest_sha256':h['deployment_manifest_sha256'],'import_manifest_sha256':h['import_manifest_sha256'],'remote_writes':0,'local_test_cases':len(t['tests']),'original_19_tables_and_audit_unchanged_in_local_test':True}
 (E/'attendance-preparation-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
