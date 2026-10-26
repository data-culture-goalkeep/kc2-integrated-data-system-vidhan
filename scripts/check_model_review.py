#!/usr/bin/env python3
"""Check draft architecture/mappings/docs. No SQL execution or database connectivity."""
import collections,csv,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def need(ok,message):
 if not ok:raise ValueError(message)

def validate_model(model):
 tables=model['tables'];by={t['name']:t for t in tables}
 need(len(by)==len(tables)==model['proposed_table_count']==17,'Table names/count mismatch')
 need(sum(not t['optional'] for t in tables)==model['core_table_count']==16,'Core table count mismatch')
 signatures=[]
 for t in tables:
  fields=t['fields'];need(t['purpose'] and t['grain'],'Missing table purpose/grain')
  need(all(c in fields and not fields[c]['nullable'] for c in t['primary_key']),'Nullable/missing primary key')
  signatures.append((t['grain'],tuple(sorted(fields))))
  for key in t['unique_keys']:need(all(c in fields for c in key),'Unknown unique-key field')
  for fk in t['foreign_keys']:
   need(all(c in fields for c in fk['columns']),'Unknown FK source field')
   if fk['target']=='auth.users':target_fields={'id':{'type':'uuid'}};target_keys=[['id']]
   else:
    need(fk['target'] in by,'Unknown FK target table');dest=by[fk['target']];target_fields=dest['fields'];target_keys=[dest['primary_key']]+dest['unique_keys']
    if not t['optional'] and dest['optional']:need(fk.get('enabled_if')==dest['name'] and all(fields[c].get('enabled_if')==dest['name'] for c in fk['columns']),'Core model depends unconditionally on optional table')
   need(fk['target_columns'] in target_keys,'FK target is not a declared PK/unique key')
   need(len(fk['columns'])==len(fk['target_columns']),'FK arity mismatch')
   need(all(fields[a]['type']==target_fields[b]['type'] for a,b in zip(fk['columns'],fk['target_columns'])),'FK type mismatch')
   need(fk['on_delete']=='RESTRICT','Unreviewed destructive cascading delete')
  keys=[tuple(t['primary_key'])]+[tuple(k) for k in t['unique_keys']];seen=[]
  for index in t['indexes']:
   cols=tuple(index['columns']);need(all(c in fields for c in cols),'Unknown index field');need(cols not in seen,'Duplicate index');seen.append(cols)
   need(not any(len(k)>=len(cols) and k[:len(cols)]==cols for k in keys),'Index already covered by PK/unique prefix')
  need(not any(a!=b and len(b)>=len(a) and b[:len(a)]==a for a in seen for b in seen),'Redundant index prefix')
 need(len(set(signatures))==len(signatures),'Structurally duplicate entity/grain')
 response=by['questionnaire_responses'];need('child_id' not in response['fields'] and 'caregiver_id' not in response['fields'],'Redundant independent questionnaire identity FKs')
 need(any(f['columns']==['child_caregiver_id'] and f['target']=='child_caregivers' for f in response['foreign_keys']),'Missing pair-integrity relationship')
 answer=by['questionnaire_answers']
 for field,target in [('response_id','questionnaire_responses'),('item_id','questionnaire_items')]:need(any(f['columns']==[field,'definition_key'] and f['target']==target for f in answer['foreign_keys']),'Missing questionnaire definition integrity')
 prov=by['source_provenance'];groups=prov['target_groups'];need(len(groups)==13,'Unexpected typed provenance target groups')
 need(all(any(f['columns']==g for f in prov['foreign_keys']) for g in groups),'Provenance target lacks FK')
 importable=set(by)-{'source_artifacts','source_records','source_provenance','access_memberships'}
 need(importable.issubset({f['target'] for f in prov['foreign_keys']}),'Imported domain/lookup table lacks provenance target')
 need(all(f['enabled_if'] in by and by[f['enabled_if']]['optional'] for t in tables for f in t['foreign_keys'] if f.get('enabled_if')),'Invalid optional activation gate')
 return by

def validate_provenance_shape(row, specification):
 groups=specification['target_groups'];complete=0
 for group in groups:
  values=[row.get(c) is not None for c in group]
  need(not any(values) or all(values),'Partial typed provenance target')
  complete+=int(all(values))
 need(complete==1,'Provenance must identify exactly one typed target')
 need(row.get('source_record_id') and row.get('source_columns') and row.get('target_fields'),'Provenance lacks source/field lineage')
 return True

def parse_mermaid(text):
 block=re.search(r'```mermaid\n(.*?)```',text,re.S);need(block is not None,'Mermaid block absent')
 lines=[s.strip() for s in block.group(1).splitlines() if s.strip()];need(lines.pop(0)=='erDiagram','Wrong Mermaid diagram type')
 entities={};edges=[];current=None
 for line in lines:
  if current:
   if line=='}':current=None;continue
   m=re.fullmatch(r'([A-Za-z_]\w*(?:\[\])?)\s+([A-Za-z_]\w*)(?:\s+((?:PK|FK|UK)(?:,(?:PK|FK|UK))*))?',line)
   need(m is not None,'Invalid Mermaid field syntax');need(m.group(2) not in entities[current],'Duplicate Mermaid field');entities[current][m.group(2)]=m.group(1);continue
  m=re.fullmatch(r'([A-Z_]\w*)\s+\{',line)
  if m:current=m.group(1);need(current not in entities,'Duplicate Mermaid entity');entities[current]={};continue
  m=re.fullmatch(r'([A-Z_]\w*)\s+([|o}{]+)(--|\.\.)([|o}{]+)\s+([A-Z_]\w*)\s*:\s*([A-Za-z_]\w*)',line)
  need(m is not None,'Invalid Mermaid relationship syntax');need(m.group(2) in {'||','o|','|o','}|','}o'} and m.group(4) in {'||','o|','|{','o{','}|','}o'},'Invalid ER cardinality marker')
  edges.append((m.group(1),m.group(5)))
 need(current is None,'Unclosed Mermaid entity block');need(all(a in entities and b in entities for a,b in edges),'Mermaid edge references undefined entity')
 return entities,edges

def main():
 load=lambda name:json.loads((ROOT/'docs/evidence'/name).read_text())
 model=load('optimized-model-draft.json');by=validate_model(model);profile=load('data-profile.json');summary=load('model-mapping-summary.json');gap=load('attendance-review-gap.json')
 matrix=list(csv.DictReader((ROOT/'docs/evidence/source-target-coverage.csv').open()))
 expected={(s['source'],s['sheet'],str(s['google_sheet_id']),str(c)) for s in profile['sheets'] for c in range(1,s['max_column']+1)}
 from openpyxl.utils import column_index_from_string
 actual={(r['source'],r['sheet'],r['native_sheet_id'],str(column_index_from_string(r['column']))) for r in matrix}
 need(len(matrix)==len(actual)==len(expected)==5186 and actual==expected,'Source coordinate coverage incomplete/duplicated')
 for r in matrix:
  for key in ['retained_target','header_retained_target','operational_target','header_projection']:
   v=r[key]
   if not v:need(key in ['operational_target','header_projection'],'Missing lineage retention');continue
   t,field=v.split('.',1);field=field.split('[')[0];need(t in by and field in by[t]['fields'],'Mapping references undefined target field')
  need(r['approval_gate'] and r['disposition'] not in {'approved','implemented'},'A mapping silently asserts approval')
 need(sum(bool(r['operational_target']) for r in matrix)==summary['operationally_projected_field_instances']==3366,'Operational projection count mismatch')
 need(sum(not r['operational_target'] for r in matrix)==summary['without_named_operational_projection']==1820,'Unprojected field count mismatch')
 need(sum(r['coverage_class']=='coordinate_or_header_only' for r in matrix)==142,'Missing coordinate-only addendum')
 need(sum(bool(r['header_projection']) for r in matrix)==31,'Question header definition projection incomplete')
 need(gap['all_daily_attendance_totals']=={'rows':2142,'unique_match_to_master_rows':736,'ambiguous_match_rows':11,'unmatched_rows':1395},'Attendance addendum inconsistent')
 need(gap['additional_rows_compared']==350 and gap['source_checksums_unchanged'],'Targeted attendance gap not reconciled')
 entities,edges=parse_mermaid((ROOT/('docs/archive/stage2-er-diagram.md' if (ROOT/'docs/evidence/final-model.json').exists() else 'docs/07-entity-relationship-diagram.md')).read_text())
 need(set(entities)=={n.upper() for n in by}|{'AUTH_USERS'},'ER diagram and table set differ')
 for t in model['tables']:
  need(set(t['primary_key']).issubset(entities[t['name'].upper()]),'Diagram omits PK')
  for fk in t['foreign_keys']:
   if fk['columns'] in [['created_by'],['updated_by']]:continue
   src='AUTH_USERS' if fk['target']=='auth.users' else fk['target'].upper()
   need((src,t['name'].upper()) in edges,'Diagram omits FK target relationship')
 archive=(ROOT/'docs/archive/stage1-er-diagram.md').read_text();base_entities,_=parse_mermaid(archive)
 need(len(base_entities)==12,'Original model count not preserved')
 required=['09-data-model-review.md','10-raw-vs-organized-model.md','11-optimized-data-model.md','12-data-model-comparison-matrix.md','13-data-quality-decision-register.md','14-project-standards-and-acceptance-criteria.md']
 for name in required:need((ROOT/'docs'/name).stat().st_size>500,'Review deliverable missing/empty')
 for path in (ROOT/'docs').rglob('*.md'):
  for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
   if '://' not in target and not target.startswith('#'):need((path.parent/target.split('#')[0]).is_file(),'Broken documentation link: '+str(path.relative_to(ROOT)))
 for name in ['data-profile.json','additional-checks.json','source-inspection.json']:
  original=subprocess.check_output(['git','show','de729f9:docs/evidence/'+name],cwd=ROOT)
  need(hashlib.sha256(original).digest()==hashlib.sha256((ROOT/'docs/evidence'/name).read_bytes()).digest(),'Frozen Stage 1 evidence modified')
 standards=(ROOT/'AGENTS.md').read_text()+(ROOT/'docs/project-context.md').read_text()
 for token in ['Google','NGO','sidebar','icons','Add/Record/Edit','secret','first implementation PR','simplification','raw/organized']:
  need(token.casefold() in standards.casefold(),'Permanent standard missing: '+token)
 for path in (ROOT/'scripts').glob('*.py'):compile(path.read_text(),str(path),'exec')
 for args in [['git','diff','--check'],['git','diff','--cached','--check']]:subprocess.run(args,cwd=ROOT,check=True,capture_output=True)
 need(subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='feature/phase1-data-backend','Wrong work branch')
 need(not list(ROOT.glob('supabase/migrations/*.sql')) or (ROOT/'docs/evidence/preparation-verification.json').is_file(),'Prepared SQL must pass the current preparation checker')
 result={'status':'passed','scope':'Draft architecture and source-coverage consistency; no business-rule or database-runtime validation','counts':{'original_conceptual_entities':12,'proposed_tables':17,'core_tables':16,'conditional_tables':1,'source_columns_mapped':5186,'profiled_field_instances':5044,'additional_coordinate_slots':142,'conditional_operational_projections':3366,'no_named_operational_projection':1820,'daily_attendance_rows_compared':2142},'checks':['PK/FK field, type and target-key compatibility','Questionnaire pair and definition-consistency design invariants','Optional activity variant dependency closure','Typed provenance target coverage and cardinality check specification','No exact duplicate entity/grain or redundant declared indexes','Exhaustive cell/header retention and conditional operational mapping coverage','Mermaid grammar/cardinality syntax, entity/PK and FK target references','All review/archival document links and permanent-standard registration','Frozen Stage 1 evidence unchanged and attendance gap addendum reconciled','Python syntax, Git branch and whitespace integrity'],'limitations':['Technical FK checks validate a proposed specification, not live PostgreSQL constraints','Only supported ER grammar parsed locally; official Mermaid renderer/layout unavailable','Business identity/scoring/category/domain/role approvals remain open','No SQL, migration, RLS execution, OAuth or frontend tests exist at this review stage','Remote Stage 1 commit/feature branch absent; no remote publication performed']}
 (ROOT/'docs/evidence/model-review-verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))

if __name__=='__main__':main()
