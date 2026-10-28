#!/usr/bin/env python3
"""Incremental sanitized attendance preparation. No network/remote executor; originals and existing plan immutable."""
import json,hashlib,re,gzip
from collections import Counter,defaultdict
from pathlib import Path
from datetime import date
from etl_core import ROOT,required,stable_id,canonical,sql_text,sql_value,sql_identifier,compile_batch
from recovery import source_integrity,atomic_save
from profile_sources import label,present
from recovery_engine import parse_date
WORK=ROOT/'work/attendance';E=ROOT/'docs/evidence';VERSION='attendance-cell-v1'
KINDS={'daily_attendance','annual_attendance_summary','support_attendance'}
SOURCE_TABLE='gk_private.attendance_import_staging'

def colnum(s):
 n=0
 for c in s:n=n*26+ord(c)-64
 return n

def date_status(value):
 if value is None:return 'MISSING',None
 if value=='[FORMULA]':return 'FORMULA_UNRESOLVED',None
 result=parse_date(value)
 # A parseable pseudodate is not a trustworthy attendance date. No approved fidelity donor exists.
 return ('SANITIZED_UNTRUSTED' if result['status'].startswith('valid') else 'UNPARSED'),None

def operational_projection(row,service_code=None,mark_code=None):
 if not (row['observation_kind']=='MARK' and row['identity_status']=='VERIFIED' and row['date_status']=='VERIFIED' and row['code_status']=='VERIFIED' and row['verified_child_id'] and row['parsed_date'] and service_code and mark_code):return None
 values={'id':stable_id(VERSION,'operational',row['source_record_id'],row['source_column']),'child_id':row['verified_child_id'],'attendance_date':row['parsed_date'],'service_code':service_code,'mark_code':mark_code,'origin_kind':'import','review_state':'pending'}
 provenance={'id':stable_id(VERSION,'provenance',values['id']),'source_record_id':row['source_record_id'],'source_columns':[row['source_column']],'target_fields':list(values),'attendance_id':values['id'],'contribution_state':'selected','rule_reference':VERSION+'.verified_operational'}
 return [{'table':'attendance_observations','values':values,'source_refs':[row['source_reference']]},{'table':'source_provenance','values':provenance,'source_refs':[row['source_reference']]}]

def build():
 integrity=source_integrity();profile=json.loads((E/'data-profile.json').read_text());plan=json.loads((ROOT/'work/etl/plan.json').read_text());items=[x for u in plan['units'] for x in u]
 artifacts={x['values']['id']:x['values'] for x in items if x['table']=='source_artifacts'}
 allrows=defaultdict(dict)
 for x in items:
  if x['table']=='source_records':v=x['values'];allrows[(v['artifact_id'],v['native_sheet_key'])][v['source_row']]=v
 children={x['values']['child_business_id']:x['values']['id'] for x in items if x['table']=='children'}
 candidates=defaultdict(set)
 for x in items:
  if x['table']=='identity_candidates' and x['values']['child_id']:candidates[x['values']['source_record_id']].add(x['values']['child_id'])
 name_candidates=defaultdict(set)
 for x in items:
  if x['table']=='children' and isinstance(x['values'].get('display_name'),str):name_candidates[x['values']['display_name']].add(x['values']['id'])
 output=[];stats=[];mark_tallies=Counter();source_row_ids=set();source_cells=set()
 for s in profile['sheets']:
  extra_cols=[f['column'] for f in s['fields'] if 'attendance' in label(f['label']) or label(f['label']) in {'totaldayspresent','totaldaysabsent','perchildtotalintervention'}]
  if s['kind'] not in KINDS and not extra_cols:continue
  artifact=next(a for a in artifacts.values() if a['file_code']==s['source']);rows=allrows[(artifact['id'],str(s['google_sheet_id']))];hr=s['header_row'];header=rows.get(hr);headercells=header['cell_payload'] if header else {};fields={f['column']:f['label'] for f in s['fields']};labels={label(v):k for k,v in fields.items()}
  if s['kind']=='daily_attendance':cols=[c for c in fields if 7<=colnum(c)<=37]
  elif s['kind']=='annual_attendance_summary':cols=[c for c in fields if 3<=colnum(c)<=14]
  elif s['kind']=='support_attendance':
   total=next((colnum(c) for c,v in fields.items() if label(v)=='total'),max((colnum(c) for c in fields),default=3)+1);cols=[c for c in fields if 4<=colnum(c)<total]
  else:cols=extra_cols
  namecol=next((labels[k] for k in ['childname','childnames','nameofchild','nameofthechild','fullnameofthechild','traineename'] if k in labels),None);idcol=next((labels[k] for k in ['childid','admissionnumber','admissionno'] if k in labels),None)
  programcol=next((labels[k] for k in ['program','programme'] if k in labels),None)
  ss=Counter(roster_rows=len(s['record_row_refs']),source_rows=len(rows),grid_columns=len(cols),nonempty_grid_cells=0,blank_roster_slots=0,source_contexts=0,roster_literal_marks=0,roster_formulas=0,auxiliary_values=0,summary_values=0)
  for rn,sr in sorted(rows.items()):
   source_row_ids.add(sr['id']);cells=sr['cell_payload'];cid=cells.get(idcol) if idcol else None;verified=children.get(cid) if isinstance(cid,str) else None;possible=sorted(candidates[sr['id']])
   if not possible and s['kind']=='annual_attendance_summary' and namecol:possible=sorted(name_candidates.get(cells.get(namecol),set()))
   identity='VERIFIED' if verified else 'PROVISIONAL_MATCH' if len(possible)==1 else 'AMBIGUOUS' if possible else 'UNMATCHED'
   is_roster=rn in s['record_row_refs'];ref=f"{s['source']}/{s['sheet']}/R{rn}"
   def record(c,mark,kind):
    header_value=headercells.get(c);ds,parsed=date_status(header_value)
    flags=([identity] if identity!='VERIFIED' else [])+['DATE_PENDING','CODE_PENDING']
    if kind=='SUMMARY_VALUE':flags.append('ALTERNATE_AGGREGATE_VIEW')
    if kind=='FORMULA':flags.append('FORMULA_UNRESOLVED')
    if not is_roster:flags.append('NON_ROSTER_CONTEXT')
    return {'id':stable_id(VERSION,sr['id'],c),'source_record_id':sr['id'],'header_source_record_id':header['id'] if header else None,'artifact_id':artifact['id'],'source_file':s['source'],'source_sheet':s['sheet'],'native_sheet_key':sr['native_sheet_key'],'source_row':rn,'source_column':c,'source_reference':ref,'observation_kind':kind,'recorded_child_identifier':cid,'recorded_child_name':cells.get(namecol) if is_roster else None,'original_mark':mark,'original_header':header_value,'header_label':fields.get(c),'program_reported':cells.get(programcol) if programcol else None,'parsed_date':parsed,'verified_child_id':verified,'candidate_child_ids':possible,'identity_status':identity,'date_status':ds,'code_status':'PENDING','review_status':'pending','flags':flags,'provenance':{'version':VERSION,'source_version_sha256':artifact['version_sha256'],'sheet_kind':s['kind'],'row_date_cells':[{'column':col,'value':cells.get(col)} for col,text in fields.items() if 'date' in label(text) and present(cells.get(col)) and rn>hr],'header_row':hr,'name_column':namecol,'identifier_column':idcol,'program_column':programcol,'roster_row':is_roster,'sanitized':True,'date_fidelity_approved':False},'review_notes':''}
   # One row-context record accounts for every nonempty attendance source row, including blank rosters/headers/totals.
   output.append(record('__ROW__',None,'SOURCE_CONTEXT'));ss['source_contexts']+=1
   if not hr or rn<=hr:continue
   for c in cols:
    value=cells.get(c)
    if not present(value):
     if is_roster:ss['blank_roster_slots']+=1
     continue  # Blank is not absence; raw row retains the absent/missing cell and its grid contract.
    key=(sr['id'],c);required(key not in source_cells,'Duplicate source coordinate');source_cells.add(key)
    kind='SUMMARY_VALUE' if s['kind'] in {'annual_attendance_summary','support_event_summary'} else 'AUXILIARY_VALUE' if s['kind'] not in KINDS else 'FORMULA' if value=='[FORMULA]' else 'MARK' if is_roster else 'AUXILIARY_VALUE'
    output.append(record(c,value,kind));ss['nonempty_grid_cells']+=1
    if kind=='MARK':ss['roster_literal_marks']+=1;mark_tallies[str(value) if str(value).upper() in {'P','A','H','L','M','F','-','0','1'} else '[other sanitized literal]']+=1
    if kind=='FORMULA':ss['roster_formulas']+=int(is_roster)
    if kind=='AUXILIARY_VALUE':ss['auxiliary_values']+=1
    if kind=='SUMMARY_VALUE':ss['summary_values']+=1
  stats.append({'source':s['source'],'sheet':s['sheet'],'kind':s['kind'],**ss})
 required(len(output)==len({r['id'] for r in output}) and len(source_cells)==sum(x['nonempty_grid_cells'] for x in stats),'Attendance coordinate accounting failed')
 required(sum(s['roster_rows'] for s in stats if s['kind']=='daily_attendance')==2142,'Daily roster denominator changed')
 # Compare literal daily mark extraction against the independently frozen original-workbook profile.
 for st in stats:
  if st['kind']=='daily_attendance':
   si=next(s for s in profile['sheets'] if s['source']==st['source'] and s['sheet']==st['sheet']);required(st['roster_literal_marks']==si['attendance']['nonempty_marks'],'Daily original/sanitized literal count differs')
 atomic_save(WORK/'records.json',output)
 summary={'version':VERSION,'source_integrity':integrity,'worksheets':len(stats),'daily_worksheets':sum(s['kind']=='daily_attendance' for s in stats),'daily_roster_rows':2142,'support_roster_rows':sum(s['roster_rows'] for s in stats if s['kind']=='support_attendance'),'annual_summary_roster_rows':sum(s['roster_rows'] for s in stats if s['kind']=='annual_attendance_summary'),'source_rows_covered':len(source_row_ids),'observation_candidates':len(source_cells),'staged_records':len(output),'source_context_records':len(output)-len(source_cells),'daily_roster_identity_counts':dict(Counter(r['identity_status'] for r in output if r['observation_kind']=='SOURCE_CONTEXT' and r['provenance']['sheet_kind']=='daily_attendance' and r['provenance']['roster_row'])),'eligible_operational':sum(operational_projection(r) is not None for r in output),'identity_observation_counts':dict(Counter(r['identity_status'] for r in output if r['observation_kind']!='SOURCE_CONTEXT')),'date_observation_counts':dict(Counter(r['date_status'] for r in output if r['observation_kind']!='SOURCE_CONTEXT')),'observation_kinds':dict(Counter(r['observation_kind'] for r in output)),'literal_mark_tallies':dict(mark_tallies),'non_pa_literal_marks':sum(r['observation_kind']=='MARK' and str(r['original_mark']).upper() not in {'P','A'} for r in output),'daily_literal_marks':sum(r['observation_kind']=='MARK' and r['provenance']['sheet_kind']=='daily_attendance' for r in output),'blank_roster_slots_retained_in_source':sum(s['blank_roster_slots'] for s in stats),'code_pending_observations':len(source_cells),'source_observations_not_represented':0,'duplicate_coordinates':0,'sheets':stats,'remote_loaded':False}
 (E/'attendance-reconciliation.json').write_text(json.dumps(summary,indent=2)+'\n');return output,summary

# No arbitrary table names/SQL or remote URL is accepted. Local DB adapter is injected by the isolated runner.
JSON_FIELDS={'recorded_child_identifier','recorded_child_name','original_mark','original_header','program_reported','provenance'}
def insert_sql(row):
 cols=list(row);vals=[]
 for k,v in row.items():
  if k in JSON_FIELDS:vals.append(sql_text(canonical(v))+'::jsonb')
  elif k=='candidate_child_ids':vals.append('ARRAY['+','.join(sql_text(x)+'::uuid' for x in v)+']::uuid[]')
  elif k=='flags':vals.append('ARRAY['+','.join(sql_text(x) for x in v)+']::text[]')
  elif k in ['id','source_record_id','header_source_record_id','artifact_id','verified_child_id']:vals.append('NULL::uuid' if v is None else sql_text(v)+'::uuid')
  elif k=='source_row':vals.append(str(v)+'::integer')
  elif k=='parsed_date':vals.append('NULL::date' if v is None else sql_text(v)+'::date')
  else:vals.append('NULL::text' if v is None else sql_text(v))
 predicate=' AND '.join(sql_identifier(c)+' IS NOT DISTINCT FROM '+v for c,v in zip(cols,vals))
 return 'INSERT INTO '+SOURCE_TABLE+' ('+','.join(sql_identifier(c) for c in cols)+') VALUES ('+','.join(vals)+') ON CONFLICT (source_record_id,source_column) DO NOTHING;\nDO $guard$ BEGIN IF NOT EXISTS(SELECT 1 FROM '+SOURCE_TABLE+' WHERE '+predicate+") THEN RAISE EXCEPTION 'ATTENDANCE_REPLAY_CONFLICT'; END IF; END $guard$;\n"
def batches(rows,size=200):
 for i in range(0,len(rows),size):
  part=rows[i:i+size];cols=list(part[0]);payload=sql_text(canonical(part))+'::jsonb';incoming='jsonb_populate_recordset(NULL::'+SOURCE_TABLE+','+payload+') x'
  def val(c):return "COALESCE(x."+sql_identifier(c)+",'null'::jsonb)" if c in JSON_FIELDS else 'x.'+sql_identifier(c)
  columnlist=','.join(sql_identifier(c) for c in cols)
  predicate=' AND '.join('t.'+sql_identifier(c)+' IS NOT DISTINCT FROM '+val(c) for c in cols)
  yield "BEGIN; SET LOCAL lock_timeout='5s'; SET LOCAL statement_timeout='60s';\nINSERT INTO "+SOURCE_TABLE+' ('+columnlist+') SELECT '+','.join(val(c) for c in cols)+' FROM '+incoming+' ON CONFLICT (source_record_id,source_column) DO NOTHING;\nDO $batch$ BEGIN IF EXISTS(SELECT 1 FROM '+incoming+' WHERE NOT EXISTS(SELECT 1 FROM '+SOURCE_TABLE+' t WHERE '+predicate+")) THEN RAISE EXCEPTION 'ATTENDANCE_REPLAY_CONFLICT'; END IF; END $batch$;\nCOMMIT;"
if __name__=='__main__':
 rows,s=build();print(json.dumps({k:v for k,v in s.items() if k!='sheets'},indent=2))
