#!/usr/bin/env python3
"""Prepare protected sanitized migration bundles and public aggregate evidence; never opens a database."""
from collections import Counter,defaultdict
import csv
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
from etl_core import ROOT,VERSION,POINTERS,canonical,fingerprint,stable_id,reference,required,validate_plan,reconcile_rows,sanitized_recovery_overlay
from profile_sources import present
from recovery_engine import missing

PRIVATE=ROOT/'work/etl'
SENSITIVE=re.compile(r'aadh|adhar|udid|niramaya|income|\bfees?\b|concession|address|phone|contact|email|diagnos|disability|blood|religion|caste|consent',re.I)
DATE_FIELDS={'joining_date','dropout_date','birth_date','assessment_date','transition_date','promotion_date'}

def private_save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(path.parent,0o700)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    with os.fdopen(fd,'w') as stream:json.dump(value,stream,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
    os.chmod(path,0o600)

class Builder:
    def __init__(self,rows,sheets,artifacts,mappings):
        self.rows=rows;self.sheets=sheets;self.artifacts=artifacts;self.mappings=mappings
        self.units=[];self.references=set();self.projected=defaultdict(list);self.notes=defaultdict(list)
        self.status={};self.source_ids={};self.children={};self.caregivers={};self.pairs={}
        self.fields_by_table={};self.ref_units=[];self.domain_units=defaultdict(list)
        self.target_specs={t['name']:t for t in json.loads((ROOT/'docs/evidence/final-model.json').read_text())['tables']}
        self.ref_counts=Counter();self.overlays={};self.recovery_evidence=[]
        for ref,row in rows.items():
            self.source_ids[ref]=stable_id(VERSION,'row',artifacts[row['source']]['id'],row['sheet'],row['row'])

    def cells(self,ref):
        return {**self.rows[ref]['cells'],**{col:value for (r,col),value in self.overlays.items() if r==ref}}

    def note(self,ref,reason,target='source_records',resolution='Review source evidence; no automatic correction'):
        self.notes[ref].append({'reason':reason,'target_entity':target,'recommended_resolution':resolution})

    def provenance(self,table,values,ref,columns,fields,rule):
        cols=sorted(set(columns));targets=sorted(set(fields));required(cols and targets,'Empty projection lineage')
        p={'id':stable_id(VERSION,'provenance',table,values,ref,cols,targets,rule),
           'source_record_id':self.source_ids[ref],'source_columns':cols,'target_fields':targets,
           'rule_reference':VERSION+'.'+rule,'contribution_state':'selected'}
        if table=='reference_values':p.update(reference_vocabulary=values['vocabulary'],reference_code=values['code'])
        else:p[POINTERS[table]]=values['child_id'] if table=='child_private_profiles' else values['id']
        return {'table':'source_provenance','values':p,'source_refs':[ref]}

    def project(self,table,values,ref,columns,rule):
        values=dict(values);values.update(origin_kind='import',review_state='pending')
        record={'table':table,'values':values,'source_refs':[ref]}
        provenance=self.provenance(table,values,ref,columns,list(values),rule)
        unit=[record,provenance]
        for recovery in self.recovery_evidence:
            if recovery['target_reference']==ref and recovery['validation_status']=='auto_recovered' and recovery['field_key'] in values:
                unit.append(self.provenance(table,values,recovery['source_reference'],[recovery['donor_column']],[recovery['field_key']],'verified_recovery_donor'))
        self.domain_units[table].append(unit);self.projected[ref].append(table)
        return values

    def lookup(self,vocabulary,value,ref,column):
        if missing(value):return None
        source=self.rows[ref]['source'];code=source.lower()+'_'+fingerprint([type(value).__name__,value])[:24]
        key=(vocabulary,code)
        if key not in self.references:
            self.references.add(key)
            values={'vocabulary':vocabulary,'code':code,'label':str(value),'active':False,
                    'permissions':{},'origin_kind':'import','review_state':'pending'}
            self.ref_units.append([{'table':'reference_values','values':values,'source_refs':[ref]},
                self.provenance('reference_values',values,ref,[column],['vocabulary','code','label'],'source_scoped_literal_lookup')])
        self.note(ref,'category_definition_pending',vocabulary,'Approve source-scoped category meanings before activation; values remain inactive/pending')
        return code

    def build_master(self):
        for ref,row in self.rows.items():
            if (row['source'],row['sheet'])!=('S03','T01') or row['row'] not in self.sheets[('S03','T01')]['record_row_refs']:continue
            cells=self.cells(ref);business=cells.get('B')
            required(isinstance(business,str) and business.startswith('MASK_') and business not in self.children,'Invalid or duplicate sanitized child ID')
            child=stable_id('child',business);self.children[business]=child
            values={'id':child,'child_business_id':business,'display_name':cells.get('C')};cols=['B','C']
            for col,field,vocab in [('D','current_program_code','program'),('E','child_status_code','child_status'),('F','admitted_program_code','program')]:
                if not missing(cells.get(col)):values[field]=self.lookup(vocab,cells[col],ref,col);cols.append(col)
            self.project('children',values,ref,cols,'authoritative_child_registry')
            private={};private_cols=[]
            for mapping in self.mappings:
                if (mapping['source'],mapping['sheet'])!=('S03','T01'):continue
                target=mapping['operational_target'];col=mapping['column']
                if not target.startswith('child_private_profiles.'):continue
                field=target.split('.')[1];value=cells.get(col)
                if missing(value):continue
                typ=self.target_specs['child_private_profiles']['fields'][field]['type']
                if field in DATE_FIELDS or typ in {'numeric','integer'}:
                    self.note(ref,'date_fidelity_pending' if field in DATE_FIELDS else 'sensitive_numeric_withheld',target,'Retain source cell; approve date fidelity or deidentified financial representation')
                    continue
                private[field]=str(value);private_cols.append(col)
            if private:self.project('child_private_profiles',{'child_id':child,**private},ref,['B']+private_cols,'direct_sanitized_private_fields')
            for col in ['I','AR']:
                if not missing(cells.get(col)):self.note(ref,'date_fidelity_pending','children','Approve coherent sanitized date policy; destination date remains NULL')
            for slot,(program_col,date_col) in enumerate([('AW','AX'),('AY','AZ'),('BA','BB'),('BC','BD'),('BE','BF')],1):
                if not missing(cells.get(program_col)):
                    self.project('program_changes',{'id':stable_id('program-slot',child,slot),
                     'child_id':child,'source_slot':slot,'program_code':self.lookup('program',cells[program_col],ref,program_col)},ref,['B',program_col],'explicit_master_program_slot')
                    if not missing(cells.get(date_col)):self.note(ref,'date_fidelity_pending','program_changes','Source slot retained; no effective date inferred')
            # Parent details cannot be attributed to a specific caregiver merely from mother/father headings.
            if any(not missing(cells.get(c)) for c in ['O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB']):
                self.note(ref,'parent_to_caregiver_mapping_pending','caregivers','Require a verified parent/caregiver ID crosswalk; retain parent cells source-only')

    def build_caregivers(self):
        s=self.sheets[('S05','T07')]
        for rownum in s['record_row_refs']:
            ref=reference('S05','T07',rownum);cells=self.cells(ref);gid=cells.get('B');cid=cells.get('C')
            required(isinstance(gid,str) and gid.startswith('MASK_') and gid not in self.caregivers,'Invalid or duplicate sanitized caregiver ID')
            required(cid in self.children,'Caregiver link references unknown child')
            caregiver=stable_id('caregiver',gid);self.caregivers[gid]=caregiver
            self.project('caregivers',{'id':caregiver,'caregiver_business_id':gid,'display_name':cells.get('A')},ref,['A','B'],'authoritative_caregiver_registry')
            pair=stable_id('child-caregiver',cid,gid);self.pairs[(cid,gid)]=pair
            self.project('child_caregivers',{'id':pair,'child_id':self.children[cid],'caregiver_id':caregiver},ref,['B','C'],'verified_id_pair')

    def build_questionnaires(self):
        sheet=self.sheets[('S01','T01')];header=reference('S01','T01',sheet['header_row'])
        definition='s01_t01_'+self.artifacts['S01']['version_sha256'][:16]
        values={'vocabulary':'questionnaire_definition','code':definition,'label':'Source instrument S01/T01',
                'active':False,'permissions':{},'origin_kind':'import','review_state':'pending'}
        item_columns=[chr(c) for c in range(ord('E'),ord('Z')+1)]+['AA','AB','AC','AD','AE','AF','AG','AH','AI']
        self.ref_units.append([{'table':'reference_values','values':values,'source_refs':[header]},self.provenance('reference_values',values,header,item_columns,['code','label'],'source_instrument_version')])
        labels={f['column']:f['label'] for f in sheet['fields']};items={}
        for ordinal,col in enumerate(item_columns,1):
            kind='numeric' if ordinal<=27 else 'text' if col!='AI' else 'recommendation'
            item=stable_id('question-item',definition,col);items[col]=item
            self.project('questionnaire_items',{'id':item,'definition_key':definition,'item_key':'source_column_'+col,
                'prompt':labels[col],'value_kind':kind,'ordinal':ordinal},header,[col],'source_question_header')
        aux=json.loads((ROOT/'docs/evidence/additional-checks.json').read_text())['id_pair_checks']
        conflicts={int(x) for x in aux['name_disagreement_row_refs']}
        for rownum in sheet['record_row_refs']:
            ref=reference('S01','T01',rownum);cells=self.cells(ref);pair=self.pairs.get((cells.get('BA'),cells.get('AZ')))
            required(pair is not None,'Questionnaire child/caregiver pair is not verified')
            response=stable_id('questionnaire-response',self.source_ids[ref])
            v={'id':response,'child_caregiver_id':pair,'definition_key':definition};cols=['AZ','BA']
            for col,field,vocab in [('B','program_code','program'),('C','centre_code','centre')]:
                if not missing(cells.get(col)):v[field]=self.lookup(vocab,cells[col],ref,col);cols.append(col)
            self.project('questionnaire_responses',v,ref,cols,'questionnaire_verified_pair')
            self.note(ref,'questionnaire_scoring_pending','questionnaire_responses','Preserve literal answers; do not calculate totals, percentages or bands')
            if not missing(cells.get('D')):self.note(ref,'date_fidelity_pending','questionnaire_responses','Do not treat synthetic dates as actual assessment dates')
            if rownum in conflicts:self.note(ref,'questionnaire_source_name_disagreement','questionnaire_responses','Use verified ID pair; original reported names remain in sanitized source evidence')
            for ordinal,col in enumerate(item_columns,1):
                value=cells.get(col);answer={'id':stable_id('answer',response,items[col]),'response_id':response,
                    'item_id':items[col],'definition_key':definition,'answer_state':'missing'}
                if not missing(value):
                    if ordinal<=27:
                        if type(value) not in {int,float}:
                            self.note(ref,'invalid_numeric_answer_representation','questionnaire_answers','Keep source cell; no coercion or zero substitution');continue
                        answer.update(numeric_value=value,answer_state='needs_review' if col=='S' and rownum==9 else 'recorded')
                    else:answer.update(text_value=str(value),answer_state='recorded')
                self.project('questionnaire_answers',answer,ref,[col],'literal_answer_or_explicit_missing')

    def build_candidates(self,key):
        path=ROOT/'work/recovery/identity-candidates.json'
        required(path.is_file(),'Reusable identity investigation missing')
        for row in json.loads(path.read_text()):
            ref=row['source_reference'];required(ref in self.rows,'Stale candidate source reference')
            for candidate in row['candidates']:
                masked='MASK_'+hmac.new(key,str(candidate['business_id']).encode(),hashlib.sha256).hexdigest()[:20]
                required(masked in self.children,'Candidate does not resolve to sanitized registry')
                method=candidate['method'];required(candidate['status']=='candidate','Unexpected automatic identity approval')
                value={'id':stable_id('candidate',self.source_ids[ref],self.children[masked],method),
                       'source_record_id':self.source_ids[ref],'child_id':self.children[masked],
                       'match_method':method,'resolution_status':'candidate','evidence':{'references':candidate['evidence'],
                         'approval':'unapproved_name_context_only'}}
                self.domain_units['identity_candidates'].append([{'table':'identity_candidates','values':value,'source_refs':[ref]}])

    def build_recoveries(self,key):
        for a in self.recovery_evidence:
            business='MASK_'+hmac.new(key,str(a['business_id']).encode(),hashlib.sha256).hexdigest()[:20]
            identities=self.children if a['entity_kind']=='child' else self.caregivers
            required(business in identities,'Recovery identity not in verified registry')
            target=a['target_reference'];donor=a['source_reference']
            v={'id':stable_id(VERSION,'recovery',target,a['source_column'],a['field_key'],donor),
               'source_record_id':self.source_ids[target],'donor_source_record_id':self.source_ids[donor],
               'child_id' if a['entity_kind']=='child' else 'caregiver_id':identities[business],
               'source_column':a['source_column'],'field_key':a['field_key'],'original_value':a['original_value'],
               'recovered_value':a['recovered_value'],'method':a['method'],'validation_status':a['validation_status'],
               'identity_verified':a['identity_verified'],'authoritative_source':a['authoritative_source'],
               'meaning_equivalent':a['meaning_equivalent'],'has_conflict':a['has_conflict'],
               'run_id':stable_id(VERSION,'run',[x['version_sha256'] for x in self.artifacts.values()]),
               'evidence':{'donor_reference':donor,'donor_column':a['donor_column'],'policy':'sanitized_donor_only'}}
            self.domain_units['recovery_actions'].append([{'table':'recovery_actions','values':v,'source_refs':[target,donor]}])

    def finish(self):
        ledger=[]
        for ref,row in self.rows.items():
            si=self.sheets[(row['source'],row['sheet'])];candidate=row['row'] in si['record_row_refs'];kind=si['kind']
            if self.projected[ref]:status='successfully_transformed'
            elif candidate and kind in {'daily_attendance','adl_visit_slots','support_attendance'}:
                status='awaiting_identity_resolution';self.note(ref,'identity_unverified',kind,'Approve exact-ID crosswalk; never approve name-only matches')
                if kind=='daily_attendance':self.note(ref,'attendance_calendar_and_mark_semantics_pending',kind,'Keep each original mark/date heading; approve date fidelity and mark meanings')
                if kind=='adl_visit_slots':self.note(ref,'adl_visit_identity_or_date_pending',kind,'Retain checked slots and missing dates; do not fabricate dates')
            elif candidate and kind in {'visit_activity_log','support_event_summary','historical_visits'}:
                status='awaiting_business_rule_approval';self.note(ref,'event_grain_or_mapping_pending',kind,'Approve source grain and operational target')
            else:status='preserved_as_source_only'
            reasons=self.notes[ref]
            if not reasons and status=='preserved_as_source_only':reasons=[{'reason':'retained_header_summary_view_or_unprojected_field','target_entity':'source_records','recommended_resolution':'Preserve source; do not count as an additional operational record'}]
            ledger.append({'reference':ref,'source_file':row['source'],'worksheet':row['sheet'],'row':row['row'],
                           'status':status,'targets':sorted(set(self.projected[ref])),'exceptions':reasons})
        status_index={r['reference']:r['status'] for r in ledger}
        self.units=[[{'table':'source_artifacts','values':a,'source_refs':[]}] for a in self.artifacts.values()]
        for ref,row in self.rows.items():
            v={'id':self.source_ids[ref],'artifact_id':self.artifacts[row['source']]['id'],
               'native_sheet_key':str(self.sheets[(row['source'],row['sheet'])]['google_sheet_id']),
               'source_row':row['row'],'cell_payload':row['cells'],'processing_state':'staged',
               'diagnostics':{'reference':ref,'planned_status':status_index[ref]}}
            self.units.append([{'table':'source_records','values':v,'source_refs':[ref]}])
        self.units+=self.ref_units
        for table in ['children','child_private_profiles','caregivers','child_caregivers','program_changes',
                      'questionnaire_items','questionnaire_responses','questionnaire_answers','identity_candidates','recovery_actions']:
            self.units+=self.domain_units[table]
        plan={'version':VERSION,'sanitized':True,'date_projection':'withheld_pending_fidelity_approval',
              'destination_reference':'hmlbdozsqxlwzvjimjwh','remote_loading_authorized':False,'units':self.units,
              'source_statuses':[{'source_record_id':self.source_ids[r['reference']],'reference':r['reference'],
                 'database_status':'resolved' if r['status']=='successfully_transformed' else 'blocked' if r['status'].startswith('awaiting') or r['status']=='rejected_validation' else 'reference_only'} for r in ledger]}
        return plan,ledger

def build():
    profile=json.loads((ROOT/'docs/evidence/data-profile.json').read_text());manifest=json.loads((ROOT/'work/source-intake/private-manifest.json').read_text())
    key=(ROOT/'work/source-intake/pseudonym.key').read_bytes();sheets={(s['source'],s['sheet']):s for s in profile['sheets']};sources={s['source']:s for s in profile['sources']}
    mappings=list(csv.DictReader((ROOT/'docs/evidence/final-source-target-coverage.csv').open()))
    rows={};artifacts={};privacy_masks=0
    for f in manifest:
        required(hashlib.sha256(Path(f['original_path']).read_bytes()).hexdigest()==f['sha256'],'Original snapshot hash changed')
        alias=f['alias'];worksheet_manifest={};sanitized_hashes={}
        for si in profile['sheets']:
            if si['source']!=alias:continue
            sid=si['sheet'];p=ROOT/'work/source-intake/sanitized'/f'{alias}_{sid}.jsonl'
            digest=hashlib.sha256(p.read_bytes()).hexdigest();required(digest==sources[alias]['sanitized_sha256'][sid],'Sanitized input changed')
            labels={x['column']:x['source_field_label'] for x in mappings if (x['source'],x['sheet'])==(alias,sid)}
            worksheet_manifest[sid]={'native_sheet_key':str(si['google_sheet_id']),'header_row':si['header_row'],
              'columns':labels,'input_sanitized_sha256':digest,'source_snapshot_sha256':f['sha256']}
            sanitized_hashes[sid]=digest
            for line in p.read_text().splitlines():
                row=json.loads(line)
                if not any(present(v) for v in row['cells'].values()):continue
                ref=reference(alias,sid,row['row']);required(ref not in rows,'Duplicate extracted row reference')
                for col,value in row['cells'].items():
                    if row['row']!=si['header_row'] and SENSITIVE.search(labels.get(col,'')) and type(value) in {int,float}:
                        row['cells'][col]='MASK_'+hmac.new(key,('sensitive_number:'+repr(value)).encode(),hashlib.sha256).hexdigest()[:20];privacy_masks+=1
                rows[ref]=row
        version=fingerprint([VERSION,alias,sanitized_hashes,worksheet_manifest,'sensitive-numeric-overlay','dates-unprojected'])
        artifacts[alias]={'id':stable_id('artifact',alias,version),'source_namespace':'kc2-sanitized-pilot',
          'file_code':alias,'version_sha256':version,'source_locator':'authorized-private-snapshot:'+alias,
          'worksheet_manifest':worksheet_manifest}
    required(len(rows)==sum(s['nonempty_rows'] for s in profile['sheets']),'Extracted row count mismatch')
    expected=json.loads((ROOT/'work/recovery/expected-source-references.json').read_text())
    b=Builder(rows,sheets,artifacts,mappings)
    actions=json.loads((ROOT/'work/recovery/recovery-actions.json').read_text())
    b.overlays,b.recovery_evidence=sanitized_recovery_overlay(rows,actions)
    b.build_master();b.build_caregivers();b.build_questionnaires();b.build_candidates(key);b.build_recoveries(key)
    for issue in profile['issues']:
        for cell in issue.get('references',[]):
            match=re.fullmatch(r'[A-Z]*(\d+)',str(cell))
            if match:
                ref=reference(issue['source'],issue['sheet'],int(match.group(1)))
                if ref in rows:b.note(ref,'source_quality_'+issue['code'],'source_records','Preserve source issue; review original evidence before correction')
    for adl in json.loads((ROOT/'docs/evidence/additional-checks.json').read_text())['adl']:
        for cell in adl['checked_without_date_refs']:
            number=int(re.search(r'\d+',cell).group())
            b.note(reference('S12',adl['sheet'],number),'checked_adl_visit_missing_date','adl_visits','Retain checked slot and missing date; do not invent visit date')
    plan,ledger=b.finish();stats=validate_plan(plan);reconciliation=reconcile_rows(expected,ledger)
    catalog=json.loads((ROOT/'docs/evidence/live-deployment-catalog.json').read_text())
    audited={t['table'] for t in catalog['triggers'] if t['name'].startswith('history_') and 'INSERT' in t['definition']}
    plan['expected_generated_audit_rows']=sum(n for table,n in stats['by_table'].items() if table in audited)+len(rows)
    required(len(b.children)==371 and len(b.caregivers)==716 and len(b.pairs)==716,'Registry cardinalities changed')
    required(sum('questionnaire_source_name_disagreement' in [e['reason'] for e in r['exceptions']] for r in ledger)==60,'Known questionnaire disagreements changed')
    private_save(PRIVATE/'plan.json',plan);private_save(PRIVATE/'exception-ledger.json',ledger)
    failure_rows=[]
    for r in ledger:
        for e in r['exceptions']:
            failure_rows.append({'source_file':r['source_file'],'worksheet':r['worksheet'],'row_reference':r['reference'],
                'target_entity':e['target_entity'],'reason':e['reason'],'resolution':e['recommended_resolution'],'processing_status':r['status']})
    private_save(PRIVATE/'failure-report-rows.json',failure_rows)
    rec=json.loads((ROOT/'docs/evidence/recovery-preparation.json').read_text())
    required(sum(rec['recovery_actions'].values())==len(actions),'Recovery evidence count differs from investigation')
    summary={'status':'passed','files':len(manifest),'worksheets':len(sheets),'source_nonempty_rows':len(rows),
       'candidate_rows_including_views':profile['totals']['record_rows_including_views'],'input_cells':profile['totals']['nonempty_cells'],
       'expected_target_counts':{t:stats['by_table'].get(t,0) for t in b.target_specs},'reconciliation':reconciliation,
       'identities':{'children':371,'caregivers':716,'child_caregiver_pairs':716,'linked_children':370,'questionnaire_pairs':106,'source_name_disagreements':60},
       'exceptions_by_reason':dict(Counter(x['reason'] for x in failure_rows)),'exception_report_rows':len(failure_rows),
       'expected_generated_audit_rows':plan['expected_generated_audit_rows'],'safe_recoveries':sum(a['validation_status']=='auto_recovered' for a in b.recovery_evidence),'additional_sensitive_numbers_masked':privacy_masks,'plan_sha256':hashlib.sha256((PRIVATE/'plan.json').read_bytes()).hexdigest(),
       'date_policy':'All operational dates withheld until coherent pilot date fidelity approved; sanitized source date evidence preserved',
       'unsupported_operational_categories':['attendance','ADL','support matrices/aggregate events','alternate questionnaire views','activity logs'],
       'remote_load_performed':False,'private_bundles':'Ignored owner-only work/etl; no records committed',
       'ready_scope':'Source preservation and verified-ID/literal pending facts only; no accepted business categories, scoring or unresolved identity facts'}
    (ROOT/'docs/evidence/etl-preparation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2));return plan,ledger,summary

if __name__=='__main__':build()
