#!/usr/bin/env python3
"""Generate reviewable final specs, field mapping and ER diagram without database access."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 model=json.loads((ROOT/'docs/evidence/final-model.json').read_text());tables=model['tables']
 spec=['# Final recommended Phase 1 model — prepared, not applied','','Nineteen tables. Technical recommendation ready for owner review; SQL application and role activation remain prohibited. Supabase-managed auth tables are additional and not counted. Full specification: [final-model.json](evidence/final-model.json).','','## Changes from the 17-table draft','','| Change | Reason and preservation |','| --- | --- |','| Defer activity_logs (−1) | Event versus planning grain remains unresolved; retain every original cell in source_records and headers in source_artifacts. No event is discarded. |','| Add identity_candidates (+1) | Persist attendance candidate identities, evidence, method and resolution independently from accepted facts. |','| Add recovery_actions (+1) | Persist original/recovered values, donor, method, validation flags and run history without mutating originals. |','| Add record_audit_events (+1) | Retain operational and permission change history; current updated_at alone loses historical changes. |','| children | Unique, literal child_business_id replaces source_admission_number; internal UUID references remain. |','| caregivers / child_caregivers | Authoritative caregiver_business_id belongs to person; relationship stores child/caregiver pair, not a child-scoped copy of the person ID. |','| Security and audit | Private schema, explicit membership, approved controlled values, accountable writes, soft deletion and immutable evidence. No role grants become effective without approved role definitions/memberships. |','','## General invariants','','All identifier strings retain exact case and leading zeros. Primary keys are UUIDs except one-to-one child profile, composite vocabulary/code, and auth-user membership. FK deletion is RESTRICT; no API permanent deletion is granted. Missing semantic values stay NULL or staged. Evidence tables retain source versions, native sheet key, row, column and mapping rule. Audit fields are server stamped; append-only audit events retain changes. PostgreSQL defaults and exact CHECK expressions are authoritative in the three prepared SQL files.','','Review states, origin and technical processing flags are implementation vocabulary, not invented NGO categories. No questionnaire scoring, category seeds, missing visit dates or name-only approved identities are fabricated.','','## Complete table specifications','']
 dictionary=['# Data dictionary — final recommendation, not deployed','','Complete target column types and nullability follow. Source positions and original field labels remain in the [final mapping](evidence/final-source-target-coverage.csv); previous source-oriented dictionary is preserved in [Stage 2 archive](archive/stage2-data-dictionary.md). SQL contains exact defaults, checks, grants and triggers.','','']
 graph=['erDiagram']
 for t in tables:
  name=t['name'];q=t['schema']+'.'+name
  spec += ['### '+q,'',t['purpose']+'. Grain: '+t['grain']+'.','','Required because: '+t['purpose']+'.', '', 'Primary key: `'+', '.join(t['primary_key'])+'`. Unique keys: '+('; '.join('`'+', '.join(k)+'`' for k in t['unique_keys']) or 'primary key only')+'.','','| Columns | References | Cardinality / deletion |','| --- | --- | --- |']
  for fk in t['foreign_keys']:
   optional=any(t['fields'][c]['nullable'] for c in fk['columns'])
   spec.append('| '+', '.join(fk['columns'])+' | '+fk['target']+'('+', '.join(fk['target_columns'])+') | '+('0..1' if optional else '1')+' parent per row; RESTRICT |')
  spec+=['','Indexes: '+('; '.join(', '.join(i['columns'])+' ('+i['reason']+')' for i in t['indexes']) or 'Primary/unique keys only')+'. See generated SQL for additional candidate partial indexes.','','']
  dictionary += ['## '+q,'',t['purpose']+'. Grain: '+t['grain']+'.','','| Column | PostgreSQL type | Nullable | Key / purpose |','| --- | --- | --- | --- |']
  fkcols={c for fk in t['foreign_keys'] for c in fk['columns']}
  for c,f in t['fields'].items():
   roles=[]
   if c in t['primary_key']:roles.append('PK')
   if c in fkcols:roles.append('FK')
   if any(c in k for k in t['unique_keys']):roles.append('candidate uniqueness component')
   roles.append(c.replace('_',' '))
   dictionary.append('| '+c+' | '+f['type']+' | '+('yes' if f['nullable'] else 'no')+' | '+'; '.join(roles)+' |')
  dictionary+=['']
  graph.append('    '+name.upper()+' {')
  selected=list(dict.fromkeys(t['primary_key']+[c for c in t['fields'] if c in fkcols or c.endswith('_business_id')]))
  selected=[c for c in selected if c not in ['created_by','updated_by','archived_by'] and not c.endswith('_vocabulary')]
  for c in selected:
   tag=(' PK' if c in t['primary_key'] else ' FK' if c in fkcols else '')
   graph.append('        '+t['fields'][c]['type']+' '+c+tag)
  graph.append('    }')
 graph+=['    AUTH_USERS {','        uuid id PK','    }']
 for t in tables:
  seen=set()
  for fk in t['foreign_keys']:
   if fk['columns'] in [['created_by'],['updated_by'],['archived_by']]:continue
   parent='AUTH_USERS' if fk['target']=='auth.users' else fk['target'].upper()
   # Preserve separate foreign-key roles, including lookup pairs and two source-record references.
   optional=any(t['fields'][c]['nullable'] for c in fk['columns'])
   unique=fk['columns'] in [t['primary_key']]+t['unique_keys']
   edge='    '+parent+' '+('o|' if optional else '||')+'--'+('o|' if unique else 'o{')+' '+t['name'].upper()+' : '+('_'.join(fk['columns']))
   if edge not in seen:graph.append(edge);seen.add(edge)
 (ROOT/'docs/15-final-data-model.md').write_text('\n'.join(spec).rstrip()+'\n')
 (ROOT/'docs/06-data-dictionary-draft.md').write_text('\n'.join(dictionary).rstrip()+'\n')
 (ROOT/'docs/07-entity-relationship-diagram.md').write_text('# Final recommended ER diagram — not applied\n\n19 proposed application/evidence tables; AUTH_USERS is managed by Supabase and excluded. Each edge follows a proposed FK, not a claim of approved source identity. Common audit actor FKs are omitted. Provenance targets are mutually exclusive per row; lookup edges are vocabulary scoped. Attendance candidates remain separate from resolved attendance observations.\n\n```mermaid\n'+'\n'.join(graph)+'\n```\n\nSee [complete specification](15-final-data-model.md), [target dictionary](06-data-dictionary-draft.md), and [previous 17-table diagram](archive/stage2-er-diagram.md).\n')
 matrix=list(csv.DictReader((ROOT/'docs/evidence/source-target-coverage.csv').open()));out=[]
 for row in matrix:
  row=dict(row);row['approval_gate']=row['approval_gate'].replace('Q01','per_record_identity_resolution').replace('Q02','exact_caregiver_id_resolution');target=row['operational_target']
  target=target.replace('children.source_admission_number','children.child_business_id').replace('child_caregivers.source_caregiver_code','caregivers.caregiver_business_id')
  if 'activity_logs.' in target:target='';row['disposition']='retained_reference_only';row['approval_gate']='activity_event_grain';row['reason']='Activity grain unresolved; entire row and headers retained, dedicated entity deferred'
  row['operational_target']=target
  if row['source']=='S05' and row['sheet']=='T07' and row['column']=='B':row['operational_target']='caregivers.caregiver_business_id';row['approval_gate']='literal_id_verified';row['reason']='Global caregiver identifier confirmed by owner and literal uniqueness checked'
  if row['source']=='S03' and row['sheet']=='T01' and row['column']=='B':row['approval_gate']='literal_id_verified'
  out.append(row)
 dest=ROOT/'docs/evidence/final-source-target-coverage.csv'
 with dest.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
 print('Rendered 19-table specification, dictionary, ER and',len(out),'source-coordinate mappings.')
if __name__=='__main__':main()
