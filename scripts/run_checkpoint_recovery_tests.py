#!/usr/bin/env python3
"""Full isolated recovery and fault simulation. No remote client or URL is accepted."""
from copy import deepcopy
import gzip,json,tempfile,time
from pathlib import Path
from recovery import WORK,ROOT,Coordinator,load,required,hashed
from recovery_snapshot import anchor_sql
from build_recovery_reference import start_db,snapshot
from remote_etl import prepared
from test_remote_etl import project_fixture,wrapper
from test_checkpoint_recovery import approval

def anchor(db):return json.loads(db.execute(anchor_sql()))
def response(db,packet,force_rollback=False):
    sql=packet['query']
    if force_rollback:
        required(sql.endswith('COMMIT;\n'),'Unexpected transaction suffix')
        sql=sql[:-len('COMMIT;\n')]+"SELECT 1/0; COMMIT;\n"
    r=db.sql(sql)
    if r.returncode:return {'isError':True,'content':[{'type':'text','text':'Local injected SQL failure; source/error payload withheld'}]}
    values=[json.loads(x) for x in r.stdout.splitlines() if x.startswith('{')]
    required(len(values)==1,'Local receipt shape differs')
    return wrapper([{'etl_receipt':values[0]}])
def main():
    manifest=load(WORK/'manifest.json');series=load(ROOT/'docs/evidence/stage4c-reference-checkpoints.json');_,requests,_=prepared()
    report={'scope':'LOCAL network=none PostgreSQL only; exact deployed schema and approved sanitized snapshot','remote_writes':0,'recovery_manifest_sha256':hashed(manifest),'tests':{}}
    db=start_db('checkpoint-recovery');faultdb=None
    try:
        for r in requests[:40]:required(db.sql(r['query']).returncode==0,'Local committed-prefix setup failed')
        required(snapshot(db)==series[0],'Local 40-batch prefix differs')
        original_anchor=anchor(db);test_manifest=deepcopy(manifest);test_manifest['prefix_immutable_metadata']=original_anchor
        report['local_timestamp_fixture']='Only immutable ingestion/creation metadata anchor is local; original SQL/code/reference checkpoint series unchanged'
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);auth=approval(test_manifest)
            def coord(name):return Coordinator(base/name,test_manifest,auth)
            # Actual changed existing diagnostics are detected. Roll back local fault fixture.
            pk=db.execute('SELECT id FROM gk_private.source_records ORDER BY id LIMIT 1')
            changed=db.sql("BEGIN; UPDATE gk_private.source_records SET diagnostics=diagnostics||'{\"synthetic_conflict\":true}'::jsonb WHERE id='"+pk+"';"+__import__('recovery_snapshot').snapshot_sql().removeprefix('BEGIN READ ONLY; ').removesuffix(' COMMIT;')+' ROLLBACK;')
            required(changed.returncode==0,'Local conflict fixture failed')
            bad=json.loads([x for x in changed.stdout.splitlines() if x.startswith('{')][-1])
            try:coord('conflict').verify_checkpoint(project_fixture(),bad,series,original_anchor)
            except ValueError:report['tests']['conflicting_existing_record_rejected']=True
            else:raise ValueError('Changed existing record accepted')
            required(snapshot(db)==series[0],'Local conflict rollback changed prefix')
            c=coord('rollback');c.verify_checkpoint(project_fixture(),series[0],series,original_anchor);_,packet=c.packet(0)
            c.dispatch(0);reply=response(db,packet,True)
            try:c.accept(0,reply)
            except ValueError:pass
            else:raise ValueError('Failed transaction acknowledged')
            required(snapshot(db)==series[0] and c.state()['stopped'],'Rollback leaked changes')
            report['tests']['transaction_rollback_preserves_prefix']=True
            # Loss before an RPC executes produces a durable unresolved checkpoint, with no retry.
            c=coord('connection');c.verify_checkpoint(project_fixture(),series[0],series,original_anchor);c.dispatch(0)
            try:c.accept(0,{'isError':True})
            except ValueError:pass
            required(c.diagnose(snapshot(db),series)['database_diagnosis']=='matches_acknowledged_checkpoint','No-commit diagnosis wrong')
            report['tests']['connection_failure_blocks_and_diagnoses']=True
            # Full recovery: exactly the original remaining requests, never indices 0..39.
            c=coord('success');c.verify_checkpoint(project_fixture(),series[0],series,original_anchor);executed=[];begin=time.monotonic()
            for n,b in enumerate(manifest['batches']):
                _,packet=c.packet(n);c.dispatch(n);reply=response(db,packet);c.accept(n,reply);executed.append((b['phase'],b['index'],b['request_id']))
                required(snapshot(db)==series[n+1],'Checkpoint payload/key/status mismatch')
                if n==7:
                    # Restart stateless controller from persisted known acknowledgments; no record replay.
                    c=coord('success');c.verify_checkpoint(project_fixture(),snapshot(db),series,original_anchor)
                if n%30==0:print('Verified recovery checkpoint '+str(n+1)+'/179',flush=True)
            required(executed==[(r['phase'],r['index'],r['request_id']) for r in requests[40:]],'Wrong transaction subset/order')
            report['tests']['exact_179_remaining_transactions']=True
            report['tests']['known_ack_checkpoint_resume_without_replay']=True
            try:c.dispatch(0)
            except ValueError:report['tests']['duplicate_completed_transaction_rejected']=True
            else:raise ValueError('Duplicate transaction accepted')
            required(anchor(db)==original_anchor,'Existing source IDs/payload/coordinates/diagnostics/creation or artifact metadata changed')
            report['tests']['committed_prefix_immutable_fields_preserved']=True
            required(c.state()['acknowledged']==179 and not c.state()['inflight'],'Recovery journal incomplete')
            report.update(runtime_seconds=round(time.monotonic()-begin,3),final_counts={k:v['rows'] for k,v in snapshot(db)['tables'].items()},source_states=snapshot(db)['source_states'])
            required(report['final_counts']['record_audit_events']==28293 and report['source_states']==manifest['expected_source_states'],'Final audit/source states differ')
            report['tests']['audit_and_source_status_totals']=True
            # Run full source-level reconciliation, including all 99 FKs, actual answer/source links and guards.
            import verify_stage4b_execution
            verify_stage4b_execution.prepare(False)
            sql=(ROOT/'work/remote-etl/verify-full-live-data.sql').read_text();actual=json.loads(db.execute(sql));expected=load(ROOT/'work/remote-etl/expected-full-live-checks.json')
            required(all(actual.get(k)==v for k,v in expected.items() if k not in ['plan_sha256','manifest_sha256','foreign_key_checks']) and actual['foreign_key_violations']=={},'Full source reconciliation failed')
            report['tests']['full_source_lineage_identity_fk_reconciliation']=True
            # Catalog remains byte-for-object equal to the immutable schema/security reference.
            cat=json.loads(db.execute('BEGIN READ ONLY; SET LOCAL search_path=pg_catalog; '+(ROOT/'scripts/sql/inspect_ids_catalog.sql').read_text()+' COMMIT;'))
            required(cat==load(ROOT/'docs/evidence/expected-deployment-catalog.json'),'Local schema/security changed')
            report['tests']['schema_rls_privileges_and_triggers_unchanged']=True
            faultdb=start_db('checkpoint-lost-ack')
            for r in requests[:40]:required(faultdb.sql(r['query']).returncode==0,'Lost-ack prefix setup failed')
            fault_m=deepcopy(manifest);fault_m['prefix_immutable_metadata']=anchor(faultdb);lost=Coordinator(base/'lost-ack',fault_m,approval(fault_m));lost.verify_checkpoint(project_fixture(),snapshot(faultdb),series,fault_m['prefix_immutable_metadata'])
            _,packet=lost.packet(0);lost.dispatch(0);reply=response(faultdb,packet)
            required(not reply['isError'],'Lost-ack local commit failed')
            required(lost.diagnose(snapshot(faultdb),series)['database_diagnosis']=='committed_without_ack','Lost acknowledgment commit not detected')
            try:lost.dispatch(0)
            except ValueError:report['tests']['lost_ack_committed_not_retried']=True
            else:raise ValueError('Unacknowledged commit replayed')
        report['status']='passed'
    except Exception as exc:report.update(status='failed',reason=str(exc))
    finally:
        removed=[db.docker('rm','-f',db.name).returncode==0]
        if faultdb:removed.append(faultdb.docker('rm','-f',faultdb.name).returncode==0)
        report['containers_removed']=all(removed)
        (ROOT/'docs/evidence/stage4c-runtime-tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return 0 if report['status']=='passed' and report['containers_removed'] else 1
if __name__=='__main__':raise SystemExit(main())
