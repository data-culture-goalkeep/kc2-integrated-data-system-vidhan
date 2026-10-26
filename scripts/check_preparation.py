#!/usr/bin/env python3
"""Validate prepared artifacts; never execute SQL or contact a database."""
import csv,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/dependencies'))
from pglast import parse_sql,parse_plpgsql,ast,enums
from check_model_review import parse_mermaid

def need(ok,message):
 if not ok:raise ValueError(message)
def validate_security(sql,by):
 need(not re.search(r'\bINSERT\s+INTO\s+(?:public\.)?reference_values',sql,re.I),'Role/category seeding is forbidden during preparation')
 need(not re.search(r'GRANT\s+(?:ALL|SELECT|INSERT|UPDATE|DELETE).*\bTO\s+anon\b',sql,re.I),'Anonymous grant')
 need(not re.search(r'GRANT\s+DELETE.*\bTO\s+authenticated\b',sql,re.I),'Authenticated permanent deletion grant')
 for token in ['email_verified',"i.provider = 'google'","'hd'","'goalkeep.net'","a ->> 'method' = 'oauth'",'SECURITY DEFINER SET search_path = pg_catalog','Pilot role matrix not activated','Self-role or private-access escalation','read_private','write_private','manage_access']:
  need(token in sql,'Missing security invariant: '+token)
 for t in by.values():
  name=t['name'];q=t['schema']+'.'+name
  need('ALTER TABLE "'+t['schema']+'"."'+name+'" ENABLE ROW LEVEL SECURITY;' in sql,'Missing RLS: '+name)
  need(re.search(r'REVOKE ALL ON TABLE "'+t['schema']+r'"\."'+name+'" FROM PUBLIC, anon, authenticated, service_role;',sql) is not None,'Missing initial denial')
  if name=='access_memberships':need(not re.search(r'GRANT [^;]+ ON (?:TABLE )?gk_private.access_memberships TO authenticated',sql),'Direct membership privileges')
 need(not re.search(r'GRANT (?:ALL|TRUNCATE|DELETE) ON (?:TABLE )?[^;]+ TO service_role',sql),'Excessive backend privilege')
 need('CREATE POLICY review_audit' in sql and 'protect_record_audit_events' in sql,'Missing audit protection')
 return True

def main():
 m=json.loads((ROOT/'docs/evidence/final-model.json').read_text());by={t['name']:t for t in m['tables']}
 need(len(by)==m['proposed_table_count']==19,'Final count mismatch')
 for t in by.values():
  need(t['purpose'] and t['grain'],'Missing purpose or grain')
  need(all(not t['fields'][c]['nullable'] for c in t['primary_key']),'Nullable PK')
  for fk in t['foreign_keys']:
   if fk['target']=='auth.users':fields={'id':{'type':'uuid'}};keys=[['id']]
   else:dest=by[fk['target']];fields=dest['fields'];keys=[dest['primary_key']]+dest['unique_keys']
   need(fk['target_columns'] in keys,'FK not unique')
   need(all(t['fields'][a]['type']==fields[b]['type'] for a,b in zip(fk['columns'],fk['target_columns'])),'FK type mismatch')
   need(fk['on_delete']=='RESTRICT','Unsafe cascade')
 paths=sorted((ROOT/'supabase/migrations').glob('*.sql'));need(len(paths)==3,'Migration set changed')
 sql='\n'.join(p.read_text() for p in paths);parsed={};created={};constraints={};indexes=[]
 for p in paths:
  statements=parse_sql(p.read_text());pl=parse_plpgsql(p.read_text());sql_bodies=re.findall(r'CREATE FUNCTION .*?LANGUAGE sql\b.*?AS \$\$(.*?)\$\$;',p.read_text(),re.S)
  for body in sql_bodies:parse_sql(body)
  parsed[p.name]={'sql_statements':len(statements),'plpgsql_functions':len(pl),'sql_function_bodies':len(sql_bodies),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  for raw in statements:
   node=raw.stmt
   if isinstance(node,ast.CreateStmt):created[node.relation.relname]=node
   if isinstance(node,ast.AlterTableStmt):
    for cmd in node.cmds:
     if isinstance(cmd.def_,ast.Constraint):constraints.setdefault(node.relation.relname,[]).append(cmd.def_)
   if isinstance(node,ast.IndexStmt):indexes.append(node.idxname)
 need(set(created)==set(by),'DDL table set differs from model');need(len(indexes)==len(set(indexes)),'Duplicate index name')
 def strings(values):return [v.sval for v in values or []]
 for name,t in by.items():
  node=created[name];need(node.relation.schemaname==t['schema'],'Wrong schema')
  columns={n.colname:n for n in node.tableElts if isinstance(n,ast.ColumnDef)}
  need(set(columns)==set(t['fields']),'DDL/model column mismatch')
  for c,f in t['fields'].items():
   aliases={'int4':'integer','int8':'bigint','bool':'boolean','float8':'double precision'}
   actual=aliases.get(columns[c].typeName.names[-1].sval,columns[c].typeName.names[-1].sval)+('[]' if columns[c].typeName.arrayBounds else '')
   need(actual==f['type'],'SQL/model datatype mismatch')
   need((any(k.contype==enums.ConstrType.CONSTR_NOTNULL for k in columns[c].constraints or []))== (not f['nullable']),'SQL/model nullability mismatch')
  declared=[n for n in node.tableElts if isinstance(n,ast.Constraint)]
  need(any(n.contype==enums.ConstrType.CONSTR_PRIMARY and strings(n.keys)==t['primary_key'] for n in declared),'DDL PK mismatch')
  for fk in t['foreign_keys']:
   need(any(c.contype==enums.ConstrType.CONSTR_FOREIGN and strings(c.fk_attrs)==fk['columns'] and c.pktable.relname==fk['target'].split('.')[-1] and strings(c.pk_attrs)==fk['target_columns'] for c in constraints.get(name,[])),'DDL FK mismatch')
 validate_security(sql,by)
 need('lineage_reference_values' in sql and all('lineage_'+f['target'] in sql for f in by['source_provenance']['foreign_keys'] if f['target'] not in ['source_records','auth.users']),'Imported target lacks lineage enforcement')
 matrix=list(csv.DictReader((ROOT/'docs/evidence/final-source-target-coverage.csv').open()));old=list(csv.DictReader((ROOT/'docs/evidence/source-target-coverage.csv').open()))
 coordinates=lambda rows:{(r['source'],r['sheet'],r['column']) for r in rows}
 need(len(matrix)==len(coordinates(matrix))==5186 and coordinates(matrix)==coordinates(old),'Source coverage lost or duplicate')
 for r in matrix:
  need(r['retained_target'] and r['header_retained_target'],'Missing cell/header retention')
  for tab,col in re.findall(r'([a-z_][a-z_0-9]*)\.([a-z_][a-z_0-9]*)',r['operational_target']+' '+r['header_projection']):need(tab in by and col in by[tab]['fields'],'Mapping points to absent target field')
 entities,edges=parse_mermaid((ROOT/'docs/07-entity-relationship-diagram.md').read_text());need(set(entities)=={n.upper() for n in by}|{'AUTH_USERS'},'Final ER entity mismatch')
 for t in by.values():
  for fk in t['foreign_keys']:
   if fk['columns'] in [['created_by'],['updated_by'],['archived_by']]:continue
   parent='AUTH_USERS' if fk['target']=='auth.users' else fk['target'].upper();need((parent,t['name'].upper()) in edges,'ER missing FK edge')
 recovery=json.loads((ROOT/'docs/evidence/recovery-preparation.json').read_text());need(recovery['originals_unchanged'] and recovery['reconciliation']['ok'],'Source integrity/reconciliation failed')
 need(recovery['authoritative_literal_identifiers']=={'children':371,'caregivers':716,'caregiver_link_children':370,'questionnaire_verified_pairs':106,'questionnaire_name_conflicts':60},'Source evidence changed')
 for p in (ROOT/'scripts').glob('*.py'):compile(p.read_text(),str(p),'exec')
 for args in [['git','diff','--check'],['git','diff','--cached','--check'],['git','fsck','--no-dangling']]:subprocess.run(args,cwd=ROOT,check=True,capture_output=True)
 need(subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='feature/phase1-data-backend','Wrong branch')
 for p in (ROOT/'docs').rglob('*.md'):
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if '://' not in link and not link.startswith('#'):need((p.parent/link.split('#')[0]).is_file(),'Broken documentation link')
 runtime_path=ROOT/'docs/evidence/postgres-runtime-review.json'
 runtime=json.loads(runtime_path.read_text()) if runtime_path.exists() else {}
 runtime_verified=runtime.get('status')=='passed' and runtime.get('migration_hashes')=={n:v['sha256'] for n,v in parsed.items()}
 connection=json.loads((ROOT/'docs/evidence/supabase-connectivity.json').read_text())
 target=json.loads((ROOT/'config/authorized-supabase-project.json').read_text())
 remote_verified=connection.get('status')=='passed' and connection.get('reference_id')==target.get('reference_id') and target.get('verified')
 limitations=['Live Google OAuth and the complete Supabase Auth/PostgREST stack are not tested by local contract fixtures','Role matrix remains draft; remote role definitions and memberships not activated','Scoring/category and source ambiguities are not approved by technical tests']
 if not runtime_verified:limitations.append('Current SQL has not passed the disposable PostgreSQL suite')
 if not remote_verified:limitations.append('Exact remote project/read connectivity unverified')
 report={'status':'passed','scope':'Static model/SQL/evidence consistency; this checker executes no SQL. Separate local runtime and read-only remote evidence referenced.','table_count':19,'mapping_coordinates':5186,'migration_files':parsed,'nonempty_rows_retained':recovery['reconciliation']['accounted_rows'],'source_business_ids_verified':True,'mermaid':'Local supported grammar/entity/FK checks passed; official renderer not run','deployment_status_evidence':'deployment-validation.json when present; this static checker neither applies nor independently queries remote migrations','local_runtime_verified_for_current_sql':runtime_verified,'remote_connection_verified':bool(remote_verified),'limitations':limitations}
 (ROOT/'docs/evidence/preparation-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
