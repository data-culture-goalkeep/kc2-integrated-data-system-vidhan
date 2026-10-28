"""Focused synthetic runtime tests against exact deployed migrations; no remote URL."""
import json
from copy import deepcopy
from etl_core import ROOT, stable_id, required, compile_batch
from build_recovery_reference import start_db
from prepare_historical_increment import unit
from historical_projection import project
from test_historical_recovery import fixture


def main():
    db=start_db('historical-focused');tests={}
    report={'scope':'Synthetic only, disposable network=none PostgreSQL; exact four deployed migrations; no remote writes'}
    try:
        child=stable_id('synthetic-child');source=stable_id('synthetic-source');artifact=stable_id('synthetic-artifact');target=stable_id('synthetic-programme')
        db.execute("INSERT INTO public.children(id,child_business_id) VALUES ('"+child+"','SYNTHETIC-HISTORICAL');")
        artifact_row={'table':'source_artifacts','values':{'id':artifact,'source_namespace':'SYNTHETIC','file_code':'DEMO','version_sha256':'a'*64,'worksheet_manifest':{}},'source_refs':[]}
        source_row={'table':'source_records','values':{'id':source,'artifact_id':artifact,'native_sheet_key':'T01','source_row':2,'cell_payload':{'D':'SYNTHETIC-ONLY'}},'source_refs':[]}
        programme={'table':'program_changes','values':{'id':target,'child_id':child,'origin_kind':'import','review_state':'pending','source_slot':1},'source_refs':[]}
        provenance={'table':'source_provenance','values':{'id':stable_id('seed-provenance'),'source_record_id':source,'program_change_id':target,'source_columns':['C'],'target_fields':['child_id'],'rule_reference':'SYNTHETIC','contribution_state':'selected'},'source_refs':[]}
        db.execute(compile_batch([artifact_row,source_row,programme,provenance]))
        audit=int(db.execute('SELECT count(*) FROM gk_private.record_audit_events'))
        original_source=db.execute('SELECT to_jsonb(t)::text FROM gk_private.source_records t')
        update={'table':'program_changes','id':target,'field':'promotion_date','before':None,'after':'2024-02-29','child_id':child,
            'source_record_id':source,'source_file':'DEMO','source_sheet':'T01','source_row':2,'source_column':'D','date_source_cell':'D2',
            'method':'SYNTHETIC_ONLY','source_dependencies':['D2'],'source_sha256':'a'*64,'expected_target_values':programme['values']}
        query=unit(update);db.execute(query)
        required(db.execute('SELECT promotion_date FROM public.program_changes')=='2024-02-29','Date load failed')
        required(int(db.execute('SELECT count(*) FROM gk_private.record_audit_events'))==audit+1,'Date audit count differs')
        tests['conditional_date_update_evidence_provenance_and_one_audit']=True
        fingerprint=db.execute("SELECT md5(string_agg(to_jsonb(t)::text,'')) FROM public.program_changes t")
        db.execute(query)
        required(db.execute("SELECT md5(string_agg(to_jsonb(t)::text,'')) FROM public.program_changes t")==fingerprint,'Replay changed timestamps')
        required(int(db.execute('SELECT count(*) FROM gk_private.record_audit_events'))==audit+1,'Replay generated audit')
        tests['idempotent_replay_preserves_timestamps_and_audit']=True
        conflict=deepcopy(update);conflict['after']='2024-03-01'
        required(db.sql(unit(conflict)).returncode!=0,'Conflicting date accepted')
        required(db.execute('SELECT count(*) FROM gk_private.recovery_actions')=='1','Failed transaction left evidence')
        tests['conflicting_date_rolls_back_without_evidence']=True
        caregiver=stable_id('synthetic-caregiver');link=stable_id('synthetic-link');response=stable_id('synthetic-response')
        db.execute("INSERT INTO gk_private.caregivers(id,caregiver_business_id) VALUES ('"+caregiver+"','SYNTHETIC-G');"
                   "INSERT INTO public.child_caregivers(id,child_id,caregiver_id) VALUES ('"+link+"','"+child+"','"+caregiver+"');"
                   "INSERT INTO public.reference_values(vocabulary,code,label) VALUES ('questionnaire_definition','DEMO_FORM','Synthetic');")
        qvalues={'id':response,'child_caregiver_id':link,'definition_key':'DEMO_FORM','origin_kind':'import','review_state':'pending'}
        qp=deepcopy(provenance);qp['values'].pop('program_change_id');qp['values'].update(id=stable_id('synthetic-q-provenance'),response_id=response)
        db.execute(compile_batch([{'table':'questionnaire_responses','values':qvalues,'source_refs':[]},qp]))
        qu=deepcopy(update);qu.update(table='questionnaire_responses',id=response,field='assessment_date',expected_target_values=qvalues)
        q_audit=int(db.execute('SELECT count(*) FROM gk_private.record_audit_events'))
        db.execute(unit(qu));db.execute(unit(qu))
        required(db.execute('SELECT assessment_date FROM public.questionnaire_responses')=='2024-02-29','Assessment date update failed')
        required(int(db.execute('SELECT count(*) FROM gk_private.record_audit_events'))==q_audit+1,'Assessment replay audit differs')
        tests['questionnaire_date_update_exact_pair_and_idempotent_audit']=True
        for role in ['anon','authenticated']:
            required(db.sql('BEGIN; SET LOCAL ROLE '+role+'; SELECT * FROM gk_private.recovery_actions; ROLLBACK;').stdout.strip()=='','Private evidence leaked')
        tests['nonmember_private_evidence_not_visible']=True
        db.execute("INSERT INTO public.reference_values(vocabulary,code,label,origin_kind) VALUES ('service_context','DEMO','Synthetic','manual'),('attendance_mark','P','Synthetic','manual');")
        decision={'approved':True,'approval_reference':'SYNTHETIC-ONLY','event_kind':'daily_attendance','service_code':'DEMO','mark_mapping':{'P':'P'}}
        db.execute(compile_batch(project(fixture(),decision)))
        db.execute(compile_batch(project(fixture(),decision)))
        required(db.execute('SELECT count(*) FROM public.attendance_observations')=='1','Duplicate attendance')
        tests['verified_attendance_projection_replay_and_fk']=True
        for kind in ['adl_visit_slots','support_attendance']:
            r=fixture(kind);r['recovered_date']=None;r['date_verification']='UNRESOLVED'
            if kind=='adl_visit_slots':r['original_value']=True;d={'true_means_completed_visit':True}
            else:d={'event_reference':'SYNTHETIC-EVENT','value_mapping':{'P':'SYNTHETIC-PARTICIPATION'}}
            d.update(approved=True,approval_reference='SYNTHETIC-ONLY',event_kind=kind)
            db.execute(compile_batch(project(r,d)))
        tests['adl_and_support_nullable_dates_no_fabrication']=True
        bad=fixture();bad['source_record_id']=stable_id('nonexistent-source');bad['source_column']='Z'
        required(db.sql(compile_batch(project(bad,decision))).returncode!=0,'Missing source accepted')
        required(db.execute('SELECT count(*) FROM public.attendance_observations')=='1','FK failure did not rollback event')
        tests['missing_source_fk_rolls_back_entire_unit']=True
        required(db.execute('SELECT to_jsonb(t)::text FROM gk_private.source_records t')==original_source,'Source mutated')
        required(db.execute('SELECT count(*) FROM gk_private.access_memberships')=='0','Membership activated')
        required(db.execute("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname IN ('public','gk_private') AND c.relkind='r' AND c.relrowsecurity")=='20','RLS changed')
        tests['source_immutability_empty_memberships_and_20_rls_tables']=True
        report.update(status='passed',tests=tests,tests_passed=len(tests))
    except Exception as exc:
        report.update(status='failed',tests=tests,error=str(exc)[:1200])
    finally:
        report['container_removed']=db.docker('rm','-f',db.name).returncode==0
        (ROOT/'docs/evidence/historical-runtime-tests.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='passed' and report['container_removed'] else 1


if __name__=='__main__':raise SystemExit(main())
