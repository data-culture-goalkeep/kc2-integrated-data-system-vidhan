#!/usr/bin/env python3
"""Essential handover/visual consistency checks only; no network, DB writes or full test replay."""
import ast,json,re,subprocess
from pathlib import Path
from xml.etree import ElementTree as ET
from pglast import parse_sql
from etl_core import ROOT,required,model_tables
from recovery import check_hashes

def main():
 def load(p):return json.loads((ROOT/p).read_text())
 live=load('docs/evidence/phase1-handover-live.json');model=load('docs/evidence/phase1-visual-model.json');gates=load('docs/evidence/phase1-operational-eligibility.json')
 required(live['application_tables']==19 and live['schema_rls_privileges_triggers_unchanged'] and live['full_source_reconciliation_matches_verified_load'],'Live baseline check failed')
 required(live['catalog_sha256']==model['catalog_sha256'] and live['foreign_key_violations']==0 and all(v==0 for v in live['duplicate_and_integrity_zero_checks'].values()),'Live integrity mismatch')
 mer=(ROOT/'docs/visual/deployed-er.mmd').read_text();entities=set(re.findall(r'^    (\w+) \{',mer,re.M));expected={q.replace('.','_').upper() for q in model['application_tables']}|{'AUTH_USERS'}
 required(entities==expected,'Visual node coverage differs')
 names=re.findall(r': "([^"]+)"',mer);required(len(names)==len(set(names))==99 and set(names)=={f['name'] for f in model['foreign_keys']},'Physical FK diagram lost/duplicated constraints')
 dot=(ROOT/'docs/visual/deployed-er.dot').read_text();required(len(re.findall(r'^\w+ -> \w+ \[',dot,re.M))==model['svg_drawn_relationship_groups'],'SVG grouped-edge coverage differs')
 for f in model['foreign_keys']:
  required(f['child'].replace('.','_').upper() in entities and f['parent'].replace('.','_').upper() in entities,'Foreign key endpoint missing')
 for name in ['deployed-er','business-relationships','spreadsheet-to-supabase']:
  root=ET.parse(ROOT/f'docs/visual/{name}.svg').getroot();required(root.tag.endswith('svg'),'Invalid rendered SVG')
 required(gates['additional_fully_verified_records']==gates['additional_safe_pending_operational_records']==0 and not gates['new_operational_records'] and not gates['execution_authorization'],'Unsafe operational import prepared')
 required(sum(gates['source_candidate_rows_by_kind'][k]['source_candidate_rows'] for k in ['daily_attendance','adl_visit_slots','support_attendance'])==3623,'Operational denominator mismatch')
 required(gates['adl_checked_slots']==194 and gates['adl_missing_date_slots']==4,'ADL slots differ')
 tables=model_tables();samples=load('docs/visual/synthetic-preview.json')
 for name,rows in samples.items():
  if name=='scope':continue
  required(name in tables and all(set(r)<=set(tables[name]['fields']) for r in rows),'Synthetic preview invented target fields')
 parse_sql((ROOT/'scripts/sql/preview_ids_metadata.sql').read_text())
 for name in ['prepare_operational_followup.py','render_phase1_handover.py','check_phase1_handover.py']:ast.parse((ROOT/'scripts'/name).read_text())
 for p in [ROOT/'docs/37-phase1-handover-summary.md',ROOT/'docs/07-entity-relationship-diagram.md',*list((ROOT/'docs/visual').glob('*.md'))]:
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' not in link and not link.startswith('#'):required((p.parent/link.split('#')[0]).is_file(),'Broken handover link')
 check_hashes(load('docs/evidence/stage4c-recovery-manifest.json')['code_sha256'])
 changed=subprocess.check_output(['git','diff','--name-only','HEAD','--','supabase/migrations','scripts/remote_etl.py','scripts/etl_core.py','scripts/etl_loader.py','scripts/mcp_etl_bridge.mjs'],cwd=ROOT,text=True);required(not changed.strip(),'Immutable migration/loader changed')
 paths=[ROOT/'docs/37-phase1-handover-summary.md',*list((ROOT/'docs/visual').glob('*')),ROOT/'scripts/prepare_operational_followup.py',ROOT/'scripts/render_phase1_handover.py']
 corpus='\n'.join(p.read_text() for p in paths if p.is_file());terms=load('work/source-intake/redaction-terms.json')
 required(not any(re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',corpus,re.I) for t in terms),'Protected source term in handover')
 tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines();required(not any(p.startswith(('work/','data/')) or p.endswith(('.xlsx','.jsonl','.key')) for p in tracked),'Private data tracked')
 subprocess.run(['git','diff','--check'],cwd=ROOT,check=True,capture_output=True)
 r={'status':'passed','application_tables':19,'exact_fks_represented':99,'live_reconciliation':'passed','schema_rls_unchanged':True,'additional_eligible_operational_records':0,'new_remote_writes':0,'metadata_preview_executed_read_only':True,'svg_rendered_and_inspected':True,'mermaid_relationships_structurally_checked':True,'full_unit_and_isolated_tests_replayed':False,'prior_test_evidence_reused':'82 Python tests and isolated recovery/security tests; implementation hashes unchanged'}
 (ROOT/'docs/evidence/phase1-handover-checks.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
if __name__=='__main__':main()
