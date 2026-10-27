#!/usr/bin/env python3
"""Targeted identity/recovery investigation; raw values remain in ignored protected work/."""
import collections,hashlib,hmac,json,os,warnings
from pathlib import Path
import openpyxl
from openpyxl.utils.cell import column_index_from_string
from profile_sources import label,present,formula,digest,norm
from recovery_engine import verified_registry,exact_id,plan_recovery,identity_candidates,reconcile
ROOT=Path(__file__).resolve().parents[1]
def main():
 warnings.filterwarnings('ignore',category=UserWarning)
 profile=json.loads((ROOT/'docs/evidence/data-profile.json').read_text())
 manifest=json.loads((ROOT/'work/source-intake/private-manifest.json').read_text())
 inputs={f['alias']:f for f in manifest};books={}
 for a,f in inputs.items():
  ensure_source_integrity(digest(f['original_path'])==f['sha256'], 'Source hash changed')
  books[a]=openpyxl.load_workbook(f['original_path'],read_only=True,data_only=False)
 rows={}
 for s in profile['sheets']:
  ws=books[s['source']].worksheets[int(s['sheet'][1:])-1]
  rows[(s['source'],s['sheet'])]=list(ws.iter_rows(values_only=False))
 def value(a,t,r,c):
  grid=rows[(a,t)];col=column_index_from_string(c)
  if r>len(grid) or col>len(grid[r-1]):return None
  cell=grid[r-1][col-1];return None if formula(cell) else cell.value
 def ref(a,t,r):return f'{a}/{t}/R{r}'
 spec={('S03','T01'):('child','B',{'display_name':'C','birth_date':'J','joining_date':'I','gender_reported':'L','program':'D'}),('S05','T07'):('caregiver','B',{'display_name':'A'})}
 records=[];canonical={};issues=[]
 for (a,t),(entity,idcol,fields) in spec.items():
  s=next(s for s in profile['sheets'] if (s['source'],s['sheet'])==(a,t))
  rr=[{'entity_kind':entity,'business_id':value(a,t,r,idcol),'identifier_literal':True,'fields':{k:value(a,t,r,c) for k,c in fields.items()},'field_columns':fields,'equivalent_fields':[k for k in fields if k!='program'],'authoritative_fields':[k for k in fields if k!='program'],'reference':ref(a,t,r)} for r in s['record_row_refs']]
  canonical[entity],problems=verified_registry(rr);issues+=problems;records+=rr
 ensure_source_integrity(not issues and len(canonical['child'])==371 and len(canonical['caregiver'])==716, 'Literal authoritative ID validation failed; no constraints approved')
 aliases=collections.defaultdict(list);observations=[];idcoverage=collections.Counter();unresolved=[];pair={}
 for r in next(s for s in profile['sheets'] if (s['source'],s['sheet'])==('S05','T07'))['record_row_refs']:
  cid=value('S05','T07',r,'C');gid=value('S05','T07',r,'B');ensure_source_integrity(cid in canonical['child'], 'Source integrity validation failed');pair[gid]=cid
  aliases[cid].append({'name':value('S05','T07',r,'D'),'reference':ref('S05','T07',r)})
 name_labels=('childname','childnames','nameofchild','nameofthechild','fullnameofthechild','traineename')
 for s in profile['sheets']:
  a,t=s['source'],s['sheet'];fields={label(f['label']):f['column'] for f in s['fields']}
  cidcol=next((fields[k] for k in ['childid','admissionnumber','admissionno'] if k in fields),None)
  gidcol=fields.get('caregiverid');namecol=next((fields[k] for k in name_labels if k in fields),None)
  for r in s['record_row_refs']:
   reference=ref(a,t,r)
   for entity,col in [('child',cidcol),('caregiver',gidcol)]:
    if not col:continue
    identifier=value(a,t,r,col)
    if not present(identifier):continue
    if exact_id(identifier) in canonical[entity]:idcoverage[entity+'_resolved']+=1
    else:idcoverage[entity+'_unresolved']+=1;unresolved.append({'reference':reference,'entity':entity,'column':col})
    if (a,t) in spec or exact_id(identifier) not in canonical[entity]:continue
    equivalent={}
    if entity=='child':
     if namecol:equivalent['display_name']=namecol
     for k in ['dateofbirth','dob']:
      if k in fields:equivalent['birth_date']=fields[k]
     if 'gender' in fields:equivalent['gender_reported']=fields['gender']
    elif 'caregivername' in fields:equivalent['display_name']=fields['caregivername']
    rr={'entity_kind':entity,'business_id':identifier,'identifier_literal':True,'fields':{k:value(a,t,r,c) for k,c in equivalent.items()},'field_columns':equivalent,'equivalent_fields':list(equivalent),'authoritative_fields':[],'reference':reference}
    records.append(rr)
    if entity=='child' and present(rr['fields'].get('display_name')):aliases[identifier].append({'name':rr['fields']['display_name'],'reference':reference})
   if s['kind'] in {'daily_attendance','adl_visit_slots','support_attendance'} and namecol:
    observations.append({'kind':s['kind'],'reference':reference,'name':value(a,t,r,namecol),'business_id':value(a,t,r,cidcol) if cidcol else None,'identifier_literal':bool(cidcol)})
 q=next(s for s in profile['sheets'] if s['kind']=='questionnaire_primary');mismatches=[]
 for r in q['record_row_refs']:
  cid=value('S01','T01',r,'BA');gid=value('S01','T01',r,'AZ')
  ensure_source_integrity(cid in canonical['child'] and gid in canonical['caregiver'] and pair[gid]==cid, 'Exact questionnaire relationship failed')
  if norm(value('S01','T01',r,'A'))!=norm(canonical['child'][cid]['fields']['display_name']):mismatches.append(ref('S01','T01',r))
 ensure_source_integrity(len(mismatches)==60, 'Source integrity validation failed')
 actions=plan_recovery(records,canonical,{'child':{'display_name':'text','birth_date':'date','gender_reported':'text','joining_date':'date'},'caregiver':{'display_name':'text'}})
 candidates=[];attendance=collections.Counter();other_identity_counts=collections.defaultdict(collections.Counter)
 for o in observations:
  c=identity_candidates(o,canonical['child'],aliases)
  counter=attendance if o['kind']=='daily_attendance' else other_identity_counts[o['kind']]
  counter['rows']+=1;counter['verified_rows' if any(x['status']=='verified' for x in c) else 'one_candidate' if len(c)==1 else 'ambiguous' if c else 'unmatched']+=1
  candidates.append({'source_reference':o['reference'],'candidates':c})
 ensure_source_integrity(attendance['rows']==2142, 'Source integrity validation failed')
 dispositions=[]
 for s in profile['sheets']:
  p=ROOT/'work/source-intake/sanitized'/f"{s['source']}_{s['sheet']}.jsonl"
  for line in p.read_text().splitlines():
   row=json.loads(line)
   if any(present(v) for v in row['cells'].values()):dispositions.append({'source_reference':ref(s['source'],s['sheet'],row['row']),'status':'reference_only','target_observations':0})
 expected=[ref(a,t,r) for (a,t),grid in rows.items() for r,cells in enumerate(grid,1) if any(present(c.value) for c in cells)]
 reconciliation=reconcile(expected,dispositions)
 ensure_source_integrity(reconciliation['ok'] and len(expected)==sum(s['nonempty_rows'] for s in profile['sheets']), 'Source integrity validation failed')
 private=ROOT/'work/recovery';private.mkdir(exist_ok=True,mode=0o700);os.chmod(private,0o700)
 def save(name,data):
  p=private/name;p.write_text(json.dumps(data,indent=2,default=str)+'\n');p.chmod(0o600)
 save('recovery-actions.json',actions);save('identity-candidates.json',candidates);save('unresolved-identifiers.json',unresolved);save('source-row-dispositions.json',dispositions);save('expected-source-references.json',expected)
 # Uniform pseudonyms preserve equality; dates/identifiers/values are masked in the AI-safe overlay.
 key=(ROOT/'work/source-intake/pseudonym.key').read_bytes()
 def mask(v):return None if v is None else 'MASK_'+hmac.new(key,str(v).encode(),hashlib.sha256).hexdigest()[:20]
 save('sanitized-recovery-overlay.json',[{**{k:v for k,v in a.items() if k not in ['business_id','original_value','recovered_value']},'business_id':mask(a['business_id']),'original_value':mask(a['original_value']),'recovered_value':mask(a['recovered_value'])} for a in actions])
 for b in books.values():b.close()
 ensure_source_integrity(all(digest(f['original_path'])==f['sha256'] for f in manifest), 'Source integrity validation failed')
 summary={'status':'passed','authoritative_literal_identifiers':{'children':371,'caregivers':716,'caregiver_link_children':len(set(pair.values())),'questionnaire_verified_pairs':106,'questionnaire_name_conflicts':60},'literal_identifier_occurrences':dict(idcoverage),'recovery_actions':dict(collections.Counter(a['validation_status'] for a in actions)),'attendance_investigation':dict(attendance),'additional_identity_investigation':{k:dict(v) for k,v in other_identity_counts.items()},'reconciliation':reconciliation,'scope':'Targeted source-ID and recovery investigation; full profiling reused. All nonempty rows retained as reference_only; no loading performed. Candidates remain unapproved.','originals_unchanged':True,'private_outputs':'Ignored work/recovery; no source values in this summary','limitations':['Only explicit literal ID columns qualify; formulas are not trusted identifiers','Supplement donor authority not approved','No attempt to invent ADL dates or questionnaire scoring','One disposition per retained row is preservation coverage, not semantic import completion']}
 (ROOT/'docs/evidence/recovery-preparation.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

def ensure_source_integrity(condition,message):
 if not condition:raise ValueError(message)

if __name__=='__main__':main()
