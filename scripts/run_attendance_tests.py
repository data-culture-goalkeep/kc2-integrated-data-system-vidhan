#!/usr/bin/env python3
"""Attendance migration + complete sanitized import in isolated local PostgreSQL only. Never accepts a remote URL."""
import json,time
from copy import deepcopy
from attendance_import import ROOT,WORK,build,batches,insert_sql,SOURCE_TABLE
from etl_core import required
from etl_loader import load_plan
from build_recovery_reference import start_db,snapshot

def main():
 rows,summary=build();db=start_db('attendance-only');report={'scope':'Network=none disposable PostgreSQL; approved sanitized inputs; no remote writes','tests':{}}
 try:
  plan=json.loads((ROOT/'work/etl/plan.json').read_text());initial=load_plan(db,plan);required(initial['status']=='passed','Local baseline seed failed');before=snapshot(db)
  report['tests']['local_new_migration_applied']=True
  for n,sql in enumerate(batches(rows)):
   r=db.sql(sql);required(r.returncode==0,'Local attendance batch failed (private details withheld)')
   if n%50==0:print('Local attendance batch '+str(n),flush=True)
  count=lambda:int(db.execute('SELECT count(*) FROM '+SOURCE_TABLE))
  required(count()==len(rows),'Attendance count differs');report['tests']['all_source_cells_and_contexts_loaded']=True
  chosen={r['id']:r for r in rows[:200]+rows[-200:]}
  for kind in {r['observation_kind'] for r in rows}:
   for r in [x for x in rows if x['observation_kind']==kind][:20]:chosen[r['id']]=r
  for state in {r['identity_status'] for r in rows}:
   for r in [x for x in rows if x['identity_status']==state][:20]:chosen[r['id']]=r
  replay=list(chosen.values())
  for sql in batches(replay):required(db.sql(sql).returncode==0,'Replay failed')
  required(count()==len(rows),'Replay duplicated rows');report['tests']['representative_idempotent_replay_all_kinds_and_identity_states']=True
  # Exact preexisting 19-table source/business/audit state must not change.
  required(snapshot(db)==before,'Existing source, IDs, questionnaires or audit history changed');report['tests']['all_original_19_tables_unchanged']=True
  probe=rows[0];copy=deepcopy(probe);copy['review_notes']='CONFLICT'
  required(db.sql('BEGIN;'+insert_sql(copy)+'COMMIT;').returncode!=0,'Conflicting existing payload accepted');report['tests']['conflicting_existing_record_rejected']=True
  required(db.sql('BEGIN; UPDATE '+SOURCE_TABLE+" SET original_mark='\"P\"'::jsonb WHERE id='"+probe['id']+"'; ROLLBACK;").returncode!=0,'Source mutation accepted');report['tests']['immutable_source_evidence_protected']=True
  for role in ['anon','authenticated','service_role']:
   required(db.sql('BEGIN; SET LOCAL ROLE '+role+'; SELECT count(*) FROM '+SOURCE_TABLE+'; ROLLBACK;').returncode!=0,'Private staging readable by '+role)
   required(db.sql('BEGIN; SET LOCAL ROLE '+role+'; INSERT INTO '+SOURCE_TABLE+'(id) SELECT gen_random_uuid() WHERE false; ROLLBACK;').returncode!=0,'Private staging writable by '+role)
  report['tests']['three_unapproved_roles_denied_read_write']=True
  fresh=deepcopy(rows[1]);fresh['source_column']='A';fresh['observation_kind']='AUXILIARY_VALUE';fresh['id']='00000000-0000-4000-8000-000000000001'
  source=next(x['values'] for u in plan['units'] for x in u if x['table']=='source_records' and x['values']['id']==fresh['source_record_id']);header=next(x['values'] for u in plan['units'] for x in u if x['table']=='source_records' and x['values']['id']==fresh['header_source_record_id']);fresh['original_mark']=source['cell_payload'].get('A');fresh['original_header']=header['cell_payload'].get('A')
  good=insert_sql(fresh);required(db.sql('BEGIN;'+good+'ROLLBACK;').returncode==0,'First partial-batch fixture must be valid');bad=deepcopy(fresh);bad['source_record_id']='00000000-0000-4000-8000-999999999999';bad['source_column']='ZZY';bad['id']='00000000-0000-4000-8000-000000000002'
  required(db.sql('BEGIN;'+good+insert_sql(bad)+'COMMIT;').returncode!=0,'Invalid source FK accepted');required(count()==len(rows),'Failed batch leaked rows');report['tests']['partial_batch_failure_atomic_rollback']=True
  for sql in ['DELETE FROM '+SOURCE_TABLE+' WHERE id=\''+probe['id']+'\'','TRUNCATE '+SOURCE_TABLE]:required(db.sql('BEGIN;'+sql+'; ROLLBACK;').returncode!=0,'Evidence deletion allowed')
  report['tests']['delete_truncate_denied']=True
  bad=deepcopy(fresh);bad['candidate_child_ids']=['00000000-0000-4000-8000-999999999999'];bad['identity_status']='PROVISIONAL_MATCH'
  required(db.sql('BEGIN;'+insert_sql(bad)+'COMMIT;').returncode!=0,'Invalid candidate FK accepted');report['tests']['invalid_candidate_rejected']=True
  required(db.execute("SELECT count(*) FROM "+SOURCE_TABLE+" WHERE parsed_date IS NOT NULL OR verified_child_id IS NOT NULL OR review_status<>'pending'")=='0','Unverified fields promoted');report['tests']['no_fabricated_identity_date_or_approval']=True
  required(snapshot(db)==before,'Negative probes changed originals');report.update(status='passed',staged_rows=count(),operational_attendance=int(db.execute('SELECT count(*) FROM public.attendance_observations')),original_audit_rows=before['tables']['record_audit_events']['rows'],replayed_rows=len(replay),reconciliation=summary['observation_kinds'])
 except Exception as e:report.update(status='failed',reason=str(e))
 finally:report['container_removed']=db.docker('rm','-f',db.name).returncode==0
 (ROOT/'docs/evidence/attendance-local-tests.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0 if report.get('status')=='passed' and report['container_removed'] else 1
if __name__=='__main__':raise SystemExit(main())
