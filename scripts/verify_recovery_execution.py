#!/usr/bin/env python3
"""Offline reconciliation of captured Stage 4C live evidence and durable receipts; never connects."""
from collections import Counter
import json
from datetime import datetime
from recovery import ROOT,WORK,load,hashed,sha,required,validate_manifest,Coordinator
E=ROOT/'docs/evidence'
def main():
 m=load(WORK/'manifest.json');series=validate_manifest(m)
 required(hashed(m)=='bfbc196c3f718a9bc8de49619031424955fcf8385d2c893a732b5853b995ec92','Authorized recovery manifest differs')
 c=Coordinator(WORK/'execution',m,{});s=c.state();events=c.events()
 required(s['acknowledged']==179 and not s['inflight'] and not s['stopped'],'Recovery transaction accounting incomplete')
 dispatch=[x for x in events if x['kind']=='dispatch'];acks=[x for x in events if x['kind']=='ack']
 required(len(dispatch)==len(acks)==179 and [x['sequence'] for x in dispatch]==list(range(179)),'Recovery sequence lost/duplicated')
 required([(x['phase'],x['index'],x['request_id']) for x in dispatch]==[(x['phase'],x['index'],x['request_id']) for x in m['batches']],'Approved transaction subset/order differs')
 public_receipts=[{**{k:d[k] for k in ['sequence','phase','index','request_id']},'inserted_by_table':a['inserted_by_table'],'outcome':'validated_commit_acknowledgment'} for d,a in zip(dispatch,acks)]
 (E/'stage4c-committed-recovery-receipts.json').write_text(json.dumps(public_receipts,indent=2)+'\n')
 inserted=Counter()
 for x in acks:inserted.update(x['inserted_by_table'])
 expected=Counter({k:v for k,v in m['expected_final_direct_counts'].items() if v});expected.subtract({'source_artifacts':12,'source_records':9988})
 required(+inserted==+expected and sum(inserted.values())==24077,'Receipt insert accounting differs')
 actual=load(E/'stage4c-final-live-reconciliation.json');want=load(E/'stage4b-expected-full-live-checks.json')
 required(all(actual.get(k)==v for k,v in want.items() if k not in ['plan_sha256','manifest_sha256','foreign_key_checks']),'Live source-level reconciliation mismatch')
 required(actual['foreign_key_violations']=={} and want['foreign_key_checks']==99,'Live FK integrity failed')
 required(load(WORK/'fresh-snapshot.json')==series[-1],'Live final keys/payloads/status/audit differ')
 required(load(WORK/'fresh-anchor.json')==m['prefix_immutable_metadata'],'Existing immutable prefix changed')
 required(load(WORK/'fresh-catalog.json')==load(E/'expected-deployment-catalog.json'),'Schema/RLS/privileges/triggers changed')
 required(load(WORK/'fresh-ledger.json')==m['migration_ledger'],'Ledger changed')
 required(load(WORK/'fresh-control.json')=={'active_imports':0,'database_role':'postgres','server_version_num':170011},'Active import/role/version differs')
 plan=load(ROOT/'work/etl/plan.json');rows=[x for u in plan['units'] for x in u];aliases={x['values']['id']:x['values']['file_code'] for x in rows if x['table']=='source_artifacts'}
 targets={x['source_record_id']:x['database_status'] for x in plan['source_statuses']};summary={}
 for x in rows:
  if x['table']!='source_records':continue
  v=x['values'];entry=summary.setdefault(aliases[v['artifact_id']],{'source_rows':0,'resolved':0,'reference_only':0,'blocked':0,'identity_pending':0,'business_pending':0});entry['source_rows']+=1;entry[targets[v['id']]]+=1
  if v['diagnostics']['planned_status']=='awaiting_identity_resolution':entry['identity_pending']+=1
  if v['diagnostics']['planned_status']=='awaiting_business_rule_approval':entry['business_pending']+=1
 required(load(E/'stage4c-final-live-source-summary.json')==summary,'Per-source live classification differs')
 sec=load(E/'stage4c-final-live-security.json');required(sec['status']=='passed' and sec['checks']['anonymous_read_denied'] and all(v==0 for k,v in sec['checks'].items() if k!='anonymous_read_denied'),'Live access denial failed')
 auth=load(WORK/'owner-authorization-archived.json');times=load(E/'stage4c-execution-times.json')
 required(auth['recovery_manifest_sha256']==hashed(m),'Archived authorization differs')
 required(datetime.fromisoformat(auth['issued_at'])<=datetime.fromisoformat(times['started_at'])<datetime.fromisoformat(times['finished_at'])<datetime.fromisoformat(auth['expires_at']),'Execution outside authorization window')
 required(not (WORK/'owner-authorization.json').exists(),'Completed authorization still active')
 counts={k:v['rows'] for k,v in load(WORK/'fresh-snapshot.json')['tables'].items()}
 r={'status':'passed','scope':'Captured ACTUAL live PostgreSQL reconciliation plus validated durable receipts','recovery_manifest_sha256':hashed(m),'recovery_transactions':179,'prior_transactions_preserved':40,'original_total_transactions':219,'additional_direct_inserts':24077,'final_direct_rows':sum(v for k,v in counts.items() if k!='record_audit_events'),'final_audit_rows':counts['record_audit_events'],'source_updates':actual['audit_by_table_operation']['gk_private.source_records/UPDATE'],'source_states':actual['source_states'],'planned_dispositions':actual['planned_dispositions'],'live_table_counts':counts,'remaining_transactions':0,'failed_or_uncertain_transactions':0,'foreign_keys_checked':99,'foreign_key_violations':0,'immutable_prefix_preserved':True,'schema_security_unchanged':True,'journal_sha256':sha((WORK/'execution/journal.jsonl').read_bytes()),'authorization_archived':True,'migration_complete_within_approved_scope':True,'business_acceptance_complete':False}
 (E/'stage4c-execution-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
