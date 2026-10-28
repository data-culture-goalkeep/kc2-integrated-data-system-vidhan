"""Destination-bound original-date UPDATE + append-only evidence preparation.

No network/executor. Each single-unit transaction is atomic and replay requires
the deterministic recovery marker as well as the exact date and target values.
"""
import json
from collections import Counter
from etl_core import ROOT, canonical, required, stable_id, sql_text, sql_value, compile_record, validate_record
from historical_recovery import W, E, sha
from recovery import atomic_save


def unit(update):
    required(update['table'] in {'program_changes','questionnaire_responses'}, 'Unapproved update table')
    field={'program_changes':'promotion_date','questionnaire_responses':'assessment_date'}[update['table']]
    required(update['field']==field and update['before'] is None,'Only NULL original-date recovery allowed')
    values=update['expected_target_values'];required(values['id']==update['id'] and values['review_state']=='pending','Wrong target binding')
    validate_record({'table':update['table'],'values':values,'source_refs':[]})
    marker=stable_id('original-date-recovery-v1',update['id'],field,update['after'],update['source_sha256'])
    target='public.'+update['table'];rid=sql_text(update['id'])+'::uuid';value=sql_value(update['after'],'date')
    predicates=' AND '.join(k+' IS NOT DISTINCT FROM '+sql_value(v, 'uuid' if k in {'id','child_id','child_caregiver_id'} else 'integer' if k=='source_slot' else 'text') for k,v in values.items())
    # Lock exact row; concurrent changes/archival or a conflicting date stop.
    body=f'''DO $date_recovery$ BEGIN
 IF NOT EXISTS(SELECT 1 FROM {target} WHERE {predicates} AND archived_at IS NULL FOR UPDATE) THEN RAISE EXCEPTION 'HISTORICAL_TARGET_CHANGED'; END IF;
 IF EXISTS(SELECT 1 FROM gk_private.recovery_actions WHERE id={sql_text(marker)}::uuid) THEN
   IF NOT EXISTS(SELECT 1 FROM {target} WHERE id={rid} AND {field}={value}) THEN RAISE EXCEPTION 'HISTORICAL_REPLAY_CONFLICT'; END IF;
 ELSE
   UPDATE {target} SET {field}={value} WHERE id={rid} AND {field} IS NULL;
   IF NOT FOUND THEN RAISE EXCEPTION 'HISTORICAL_DATE_CONFLICT'; END IF;
 END IF;
END $date_recovery$;
'''
    evidence={'table':'recovery_actions','values':{'id':marker,'source_record_id':update['source_record_id'],
      'donor_source_record_id':update['source_record_id'],'child_id':update['child_id'],'source_column':update['source_column'],
      'field_key':update['table']+'.'+field,'original_value':None,'recovered_value':update['after'],
      'method':'original_snapshot_exact_id_date','validation_status':'auto_recovered','identity_verified':True,
      'authoritative_source':True,'meaning_equivalent':True,'has_conflict':False,
      'evidence':{'target_id':update['id'],'original_file_sha256':update['source_sha256'],'original_cell':update['date_source_cell'],
        'method':update['method'],'dependencies':update['source_dependencies'],'sanitized_value_not_used':True},
      'run_id':stable_id('original-date-recovery-run-v1')},'source_refs':[]}
    pointer='program_change_id' if update['table']=='program_changes' else 'response_id'
    provenance={'table':'source_provenance','values':{'id':stable_id('date-provenance',marker),'source_record_id':update['source_record_id'],
      'source_columns':[update['source_column']],'target_fields':[field],pointer:update['id'],
      'rule_reference':'original-date-recovery-v1; separately approved manifest required','contribution_state':'selected'},'source_refs':[]}
    receipt="SELECT jsonb_build_object('recovery_id',"+sql_text(marker)+",'target_id',"+sql_text(update['id'])+",'outcome','completed') AS receipt;\n"
    return ("BEGIN; SET LOCAL lock_timeout='5s'; SET LOCAL statement_timeout='60s'; SET LOCAL application_name='goalkeep-original-date-recovery';\n"+
            body+compile_record(evidence)+compile_record(provenance)+'SET CONSTRAINTS ALL IMMEDIATE; '+receipt+'COMMIT;\n')


def main():
    from pglast import parse_sql
    updates=json.loads((W/'date-recovery-updates.json').read_text())
    folder=W/'date-batches';folder.mkdir(exist_ok=True,mode=0o700);batches=[]
    for i,u in enumerate(updates):
        query=unit(u);parse_sql(query);path=folder/f'{i:04}.sql';path.write_text(query);path.chmod(0o600)
        batches.append({'index':i,'query_sha256':sha(query.encode()),'request_id':sha(('original-date-v1:'+query).encode()),
                        'table':u['table'],'updates':1,'evidence_inserts':2,'target_id':u['id'],
                        'recovery_id':stable_id('original-date-recovery-v1',u['id'],u['field'],u['after'],u['source_sha256'])})
    counts=dict(Counter(u['table'] for u in updates))
    manifest={'version':'original-date-recovery-v1','project_reference':'hmlbdozsqxlwzvjimjwh','region':'ap-northeast-1',
      'environment':'non-production internal pilot','remote_execution_authorized':False,
      'source_binding':json.loads((E/'historical-original-recovery.json').read_text())['source_snapshot'],
      'private_updates_sha256':sha((W/'date-recovery-updates.json').read_bytes()),
      'code_sha256':{p:sha((ROOT/p).read_bytes()) for p in ['scripts/historical_recovery.py','scripts/historical_projection.py','scripts/prepare_historical_increment.py','scripts/historical_execution.py','scripts/etl_core.py']},
      'starting_table_fingerprints':json.loads((W/'live-state.json').read_text())['tables'],
      'starting_state_sha256':sha(canonical(json.loads((W/'live-state.json').read_text())).encode()),
      'catalog_sha256':sha(canonical(json.loads((W/'live-catalog.json').read_text())).encode()),
      'migration_ledger':json.loads((W/'live-ledger.json').read_text()),'batches':batches,
      'expected_updates':counts,'expected_inserts':{'gk_private.recovery_actions':len(updates),'gk_private.source_provenance':len(updates)},
      'expected_generated_audit_events':len(updates),'operational_attendance_adl_support_inserts':0,
      'staging_updates':0,'source_record_updates':0,'schema_changes':0,'business_acceptance_changes':0,
      'failure_rule':'Stop at failed or uncertain receipt; read-only diagnosis, no automatic retry or deletion.',
      'replay':'Exact target values and original date plus deterministic matching evidence; otherwise reject.',
      'approval_required':['Approve original-date fidelity and scoped disclosure of these dates in the protected pilot.',
          'Approve exact manifest and transaction/code/source hashes before any remote write.']}
    (E/'historical-date-increment-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (E/'historical-date-increment-hash.json').write_text(json.dumps({'manifest_sha256':sha(canonical(manifest).encode()),'transactions':len(updates),'remote_authorized':False},indent=2)+'\n')
    print(json.dumps({'transactions':len(updates),'updates':counts,'remote_writes':0}))


if __name__=='__main__':main()
