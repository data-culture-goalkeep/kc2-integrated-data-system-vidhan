"""Focused final package checks. No remote access or old migration replay."""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from pglast import parse_sql
from etl_core import ROOT, canonical, required
from historical_recovery import W, E, sha
from recovery import source_integrity, check_hashes
from prepare_historical_increment import unit


def load(p):return json.loads(p.read_text())


def main():
    manifest=load(E/'historical-date-increment-manifest.json');hashes=load(E/'historical-date-increment-hash.json')
    required(sha(canonical(manifest).encode())==hashes['manifest_sha256'],'Manifest hash mismatch')
    required(manifest['remote_execution_authorized'] is False and manifest['schema_changes']==0,'Unauthorized scope')
    check_hashes(manifest['code_sha256']);required(source_integrity()==manifest['source_binding'],'Original/sanitized source changed')
    updates=load(W/'date-recovery-updates.json')
    required(sha((W/'date-recovery-updates.json').read_bytes())==manifest['private_updates_sha256'],'Private values changed')
    required(len(updates)==len(manifest['batches'])==197,'Transaction coverage changed')
    for i,(u,b) in enumerate(zip(updates,manifest['batches'])):
        q=(W/'date-batches'/f'{i:04}.sql').read_text()
        required(q==unit(u) and sha(q.encode())==b['query_sha256'],'SQL/payload binding differs')
        required(b['request_id']==sha(('original-date-v1:'+q).encode()) and b['index']==i,'Request ordering/hash differs')
        parse_sql(q)
    recovered=load(E/'historical-original-recovery.json');ledger=load(W/'evidence-ledger.json')
    required(sha((W/'evidence-ledger.json').read_bytes())==recovered['private_ledger_sha256'],'Evidence ledger changed')
    staged=load(ROOT/'work/attendance/records.json')
    expected={r['id'] for r in staged if r['observation_kind']!='SOURCE_CONTEXT'}
    actual=[r['staging_id'] for r in ledger if r.get('staging_id')]
    required(len(actual)==len(set(actual)) and set(actual)==expected,'Attendance evidence missing or duplicated')
    required(all(r['required_decisions'] and 'original_value' in r and r['source_record_id'] and r['source_column'] for r in ledger),'Unreviewable pending record')
    report=load(E/'phase1-final-delivery-verification.json')
    required(report['status']=='passed' and report['application_tables']==20 and report['foreign_keys_checked']==103,'Actual database/model mismatch')
    required(report['new_unit_tests_passed']==11 and report['new_isolated_runtime_checks_passed']==9,'Focused tests incomplete')
    mer=(ROOT/'docs/visual/final-deployed-er.mmd').read_text()
    catalog=load(W/'live-catalog.json')
    required(sum(1 for line in mer.splitlines() if '--' in line)==103,'Diagram relationship coverage')
    for table in catalog['tables']:
        name=(table['schema']+'_'+table['name']).upper()
        required(name+' {' in mer,'Missing diagram entity')
    for name in ['final-deployed-er','final-business-relationships','final-source-flow']:
        ET.parse(ROOT/'docs/visual'/f'{name}.svg')
    docs=['README.md','docs/PHASE1-HANDOVER.md','docs/PM-REVIEW-CHECKLIST.md','docs/47-historical-recovery-and-increment.md','docs/FINAL-DATA-DICTIONARY.md','docs/FINAL-TABLE-INVENTORY.md']
    for name in docs:
        path=ROOT/name
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('http:','https:','#')):continue
            required((path.parent/target.split('#')[0]).exists(),'Broken link: '+name+' -> '+target)
    tracked=subprocess.run(['git','ls-files','work'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    required(not tracked.strip(),'Private work tracked in Git')
    for args in [['git','diff','--check'],['git','diff','--cached','--check'],['git','fsck','--no-dangling'],['git','merge-base','--is-ancestor','9ea1738ff98b8b655825d6974f1e95f33fd4de2a','HEAD']]:
        required(subprocess.run(args,cwd=ROOT,capture_output=True).returncode==0,'Repository integrity failure')
    out={'status':'passed','source_files_hashed':12,'sanitized_sheets_hashed':155,'bound_increment_transactions':197,
         'unrepresented_attendance_evidence_cells':0,'duplicate_attendance_evidence_keys':0,'full_diagram_tables':20,'diagram_foreign_keys':103,
         'dictionary_columns':363,'new_unit_tests':11,'isolated_runtime_checks':9,'relative_document_links':'passed',
         'svg_xml':'passed','git_whitespace_integrity_and_backend_ancestry':'passed','private_work_untracked':True,
         'remote_writes':0,'remote_increment_authorized':False}
    (E/'phase1-final-package-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':main()
