#!/usr/bin/env python3
"""Verify recovered Stage 1 evidence without repeating full source profiling.
Reads protected originals only for independent core ID/name checks; emits no record values.
"""
import collections,csv,hashlib,json,re,subprocess,sys,warnings
from pathlib import Path
import openpyxl
from inspect_sources import inspect
from profile_sources import norm,present
ROOT=Path(__file__).resolve().parents[1]

def require(condition,message):
 if not condition:raise SystemExit('FAIL: '+message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(name):return json.loads((ROOT/'docs/evidence'/name).read_text())

def main():
 checks=[]
 evidence=load('source-inspection.json');profile=load('data-profile.json');aux=load('additional-checks.json');drive=load('drive-sources.json')
 private=ROOT/'work/source-intake';manifest_path=private/'private-manifest.json'
 require(manifest_path.exists(),'Private snapshot manifest is unavailable; restore authorized snapshots securely')
 manifest=json.loads(manifest_path.read_text());guideline=next(f for f in evidence['files'] if f['role']=='guidelines')
 current=inspect([Path(x['root']) for x in evidence['scan_roots']],Path(guideline['path']),ROOT/evidence['repository_context']['path'],manifest)
 current['repository_context']['path']=evidence['repository_context']['path']
 require(current==evidence,'Source inventory changed; review new inputs before regenerating reports')
 require(all(s['status']=='scanned' for s in evidence['scan_roots']),'A local source root was not scanned')
 require(evidence['summary']['tabular_candidates']==12,'Expected twelve authorized tabular snapshots')
 checks.append('Local source inventory and original guideline/README hashes unchanged')
 require(len(manifest)==len(profile['sources'])==len(drive['sources'])==12,'Source coverage count mismatch')
 require(all(f['unchanged_modified_time'] for f in drive['sources']),'Recorded remote modification times changed during source intake')
 metadata=json.loads((private/'google-sheet-metadata.json').read_text());metadata={x['source']:x['sheets'] for x in metadata}
 totals=profile['totals'];sheets=profile['sheets'];by={(s['source'],s['sheet']):s for s in sheets};total_cells=0
 require(len(sheets)==155==sum(s['worksheets'] for s in profile['sources']),'Worksheet coverage count mismatch')
 for f,s in zip(manifest,profile['sources']):
  require(f['alias']==s['source'],'Source alias mismatch')
  require(sha(f['original_path'])==f['sha256']==s['sha256'],'A source snapshot changed')
  require(len(metadata[s['source']])==s['worksheets'],'Native/export sheet coverage mismatch')
  for sheet,digest in s['sanitized_sha256'].items():
   path=private/'sanitized'/(s['source']+'_'+sheet+'.jsonl')
   require(path.is_file() and sha(path)==digest,'Sanitized copy missing or changed: '+s['source']+' '+sheet)
   si=by[(s['source'],sheet)];rows={}
   for line in path.read_text().splitlines():
    r=json.loads(line)
    require(r['source']==s['source'] and r['sheet']==sheet,'Sanitized lineage mismatch')
    require(r['row'] not in rows,'Sanitized row reference repeated')
    rows[r['row']]=r['cells']
   require(si['google_sheet_id']==metadata[s['source']][int(sheet[1:])-1]['properties']['sheetId'],'Native sheet ID mismatch')
   require(set(si['record_row_refs']).issubset(rows),'Candidate source row lost from sanitized copy')
   nonempty=sum(present(v) for row in rows.values() for v in row.values());total_cells+=nonempty
   require(nonempty==si['nonempty_cells'],'Sanitized copy changed source cell presence')
   require(si['record_rows']==len(si['record_row_refs']),'Candidate row count mismatch')
   require(si['max_row']==si['blank_rows']+si['nonempty_rows'],'Worksheet row totals fail reconciliation')
   require(si['nonempty_rows']==si['record_rows']+si['formula_only_rows']+si['other_nonempty_rows'],'Candidate/template/other rows fail reconciliation')
   for field in si['fields']:
    require(sum(field['types'].values())==field['rows']==si['record_rows'],'Column type denominator mismatch')
    require(field['missing']==sum(not present(rows[r].get(field['column'])) for r in si['record_row_refs']),'Column missing count mismatch')
 require(total_cells==totals['nonempty_cells']==145785,'Nonempty cell total mismatch')
 require(sum(s['record_rows'] for s in sheets)==totals['record_rows_including_views']==6521,'Candidate row total mismatch')
 require(sum(s['formulas'] for s in sheets)==totals['formulas'],'Formula total mismatch')
 checks.append('12 original and 155 sanitized hashes, native sheet IDs, row/cell lineage, cell totals and field denominators verified')
 checks.append('6521 candidate rows and 145785 nonempty cells reconciled without discarding views or unresolved content')
 # Independently re-read only the three key source tables, not all 155 worksheets.
 warnings.filterwarnings('ignore',category=UserWarning)
 inputs={f['alias']:f for f in manifest};raw={}
 for alias,sheet_index in [('S03',0),('S05',6),('S01',0)]:
  wb=openpyxl.load_workbook(inputs[alias]['original_path'],data_only=False,read_only=True)
  raw[alias]=list(wb.worksheets[sheet_index].iter_rows(values_only=True));wb.close()
 master=[r for r in raw['S03'][1:] if present(r[2])];links=[r for r in raw['S05'][1:] if present(r[0])];questionnaire=[r for r in raw['S01'][1:] if present(r[0])]
 admissions=[norm(r[1]) for r in master];caregivers=[norm(r[1]) for r in links]
 require(len(master)==len(set(admissions))==371 and all(present(r[1]) for r in master),'Master candidate admission key failed')
 require(len(links)==len(set(caregivers))==716 and len({norm(r[2]) for r in links})==370,'Caregiver identity/link counts changed')
 names={norm(r[1]):norm(r[2]) for r in master};pair={norm(r[1]):norm(r[2]) for r in links}
 require(all(norm(r[2]) in names for r in links),'Caregiver link has a missing master FK candidate')
 require(len(questionnaire)==106,'Questionnaire primary count changed')
 require(all(norm(r[52]) in names and pair.get(norm(r[51]))==norm(r[52]) for r in questionnaire),'Questionnaire ID relationship integrity changed')
 mismatch=sum(norm(r[0])!=names[norm(r[52])] for r in questionnaire)
 require(mismatch==aux['id_pair_checks']['questionnaire_name_disagrees_with_id_linked_master_rows']==60,'Questionnaire name conflict count changed')
 require(sum(x['checked_visit_slots'] for x in aux['adl'])==194 and sum(x['checked_without_date'] for x in aux['adl'])==4,'ADL derived evidence inconsistent')
 for l in profile['id_linkage_candidates']:
  require(l['source_nonblank_rows']==l['unique_match_rows']+l['ambiguous_match_rows']+l['unmatched_rows'],'ID linkage denominator inconsistent')
 checks.append('Independent core-table check: 371 unique admissions; 716 caregivers/370 children; 106 valid ID pairs; 60 name conflicts preserved')
 checks.append('ADL evidence reconciles 194 checked visits and four missing dates; ID match denominators reconcile')
 required=['01-source-inventory.md','02-data-profiling.md','03-entity-discovery.md','04-assumptions-and-questions.md','05-conceptual-data-model.md','06-data-dictionary-draft.md','07-entity-relationship-diagram.md','08-data-quality-report.md','project-context.md']
 for name in required:require((ROOT/'docs'/name).is_file() and (ROOT/'docs'/name).stat().st_size>100,'Missing/empty required report: '+name)
 for path in (ROOT/'docs').glob('*.md'):
  for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
   if '://' not in target and not target.startswith('#'):require((path.parent/target.split('#')[0]).is_file(),'Broken documentation link')
 table=list(csv.DictReader((ROOT/'docs/evidence/field-profiling.csv').open()))
 require(len(table)==sum(len(s['fields']) for s in sheets),'Column CSV coverage differs from JSON evidence')
 graph=re.search(r'```mermaid\n(.*?)```',(ROOT/'docs/07-entity-relationship-diagram.md').read_text(),re.S)
 require(graph is not None,'Mermaid diagram missing')
 body=graph.group(1);entities=set(re.findall(r'^    ([A-Z_]+) \{',body,re.M));edges=re.findall(r'^    ([A-Z_]+) [|o{}.\-]+ ([A-Z_]+) :',body,re.M)
 require(len(entities)>=10 and len(edges)>=10,'Mermaid structure incomplete')
 require(all(a in entities and b in entities for a,b in edges),'Mermaid edge references missing entity')
 require(body.count(' {')==len(re.findall(r'^    }$',body,re.M)),'Mermaid entity blocks unbalanced')
 checks.append('Nine required documents, relative links, complete field CSV and Mermaid entity references checked')
 # Prevent obvious source identifiers/contacts and private organization terms from entering publishable files.
 public=list((ROOT/'docs').rglob('*'))+list((ROOT/'scripts').glob('*.py'))+list((ROOT/'tests').rglob('*.py'))+list((ROOT/'tests').rglob('*.sql'))+list((ROOT/'supabase').rglob('*.sql'))+list((ROOT/'config').rglob('*.json'))+[ROOT/'AGENTS.md']
 public=[p for p in public if p.is_file() and p.suffix not in {'.pyc'}]
 corpus='\n'.join(p.read_text() for p in public if p.name!='verification.json')
 terms=json.loads((private/'redaction-terms.json').read_text())
 require(not any(re.search(re.escape(t),corpus,re.I) for t in terms if t),'Private organization name appears in public files')
 sensitive=set()
 for r in master:
  for idx in [1,2,12,14,15,16,17,20,21,22,23,24,28,30,34]:
   if idx>=len(r) or not present(r[idx]):continue
   v=r[idx]
   if isinstance(v,str) and len(v.strip())>=6 and v.strip().lower() not in {'not available','unknown','not applicable','no data'}:sensitive.add(v.strip())
 for r in links:
  for idx in [0,1,2,3]:
   if isinstance(r[idx],str) and len(r[idx].strip())>=6:sensitive.add(r[idx].strip())
 folded=corpus.casefold()
 for value in sensitive:
  # Fast literal prefilter avoids thousands of full-corpus regex scans.
  require(value.casefold() not in folded or re.search(r'(?<!\w)'+re.escape(value)+r'(?!\w)',corpus,re.I) is None,'A protected identifier/contact/name candidate appears in public files; inspect locally')
 checks.append('Public documents/code scanned for private organization terms and core source identifiers/names/contact strings')
 for path in (ROOT/'scripts').glob('*.py'):compile(path.read_text(),str(path),'exec')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 require(branch=='feature/phase1-data-backend','Incorrect work branch')
 tracked=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
 require(not any(p.startswith(('work/','data/')) or p.endswith(('.xlsx','.jsonl','.key')) for p in tracked),'Private/raw data is tracked')
 require(not (ROOT/'supabase/migrations').exists() or (ROOT/'docs/evidence/preparation-verification.json').is_file(),'Prepared SQL must pass the current preparation checker')
 subprocess.run(['git','diff','--check'],cwd=ROOT,check=True,capture_output=True)
 subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True,capture_output=True)
 test=subprocess.run([sys.executable,str(ROOT/'scripts/test_profile_sources.py')],cwd=ROOT,text=True,capture_output=True)
 require(test.returncode==0,'Synthetic profiling regression failed; run test locally for details')
 checks.append('Synthetic end-to-end privacy/lineage/duplicate/date/score/link regression passed')
 checks.append('All Python scripts compile; working/staged Git whitespace checks pass; branch/scope/private-file safeguards pass')
 report={'status':'passed','scope':'Recovered Stage 1 source/aggregate integrity, independent critical relationship checks, documentation and synthetic regression; business decisions remain open','counts':totals,'checks':checks,'not_validated':['Analyst/schema approval and unresolved business rules','Live Google formula recalculation and completeness beyond accessible folder results','Mermaid rendered appearance (structural checks only)','Supabase project/region/schema/RLS/migration','Frontend build/lint/TypeScript (no application)','Remote Git writes or PR creation'],'reprocessing':'Reused completed full profiles after verifying snapshot/sanitized hashes; re-read only core identity tables for independent validation'}
 (ROOT/'docs/evidence/verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':'passed','checks':checks,'full_profiling_repeated':False},indent=2))

if __name__=='__main__':main()
