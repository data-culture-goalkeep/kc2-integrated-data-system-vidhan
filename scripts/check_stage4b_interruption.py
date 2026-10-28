#!/usr/bin/env python3
"""Validate the actual interrupted prefix and evidence. No database connection or write path."""
from collections import Counter
import hashlib,json,re
from pathlib import Path
from etl_core import ROOT,required,canonical

def read(name):return json.loads((ROOT/'docs/evidence'/name).read_text())
def main():
    result=read('stage4b-interrupted-execution-results.json');live=read('stage4b-interruption-live-state.json')
    required(result['status']=='interrupted_incomplete' and result['migration_complete'] is False,'Incomplete migration mislabeled')
    required(result['confirmed_committed_transactions']==40 and result['remaining_transactions']==179,'Transaction accounting differs')
    required(len(live['live_counts'])==19 and sum(live['live_counts'].values())==10000 and live['live_counts']['gk_private.source_records']==9988 and live['live_counts']['gk_private.source_artifacts']==12,'Actual row counts differ')
    required(live['active_import_transactions']==0 and live['source_states']=={'staged':9988},'Unexpected active import or source states')
    required(read('stage4b-after-live-catalog.json')==read('expected-deployment-catalog.json'),'Schema/security changed')
    proof=read('stage4b-partial-live-reconciliation-verification.json');required(proof['status']=='passed' and proof['source_rows_reconciled']==9988 and proof['foreign_key_checks']==99 and not proof['differences'],'Prefix not verified')
    sec=read('stage4b-interruption-security.json');required(sec['status']=='passed' and sec['anonymous_read']=='denied_42501' and all(v==0 for v in sec['unapproved_authenticated_visible_rows'].values()),'Live denial checks failed')
    required(sec['migrations']==read('deployed-migration-ledger.json')['migrations'],'Ledger changed')
    required(read('stage4b-post-interruption-integrity.json')['status']=='passed','Source/code integrity failed')
    w=ROOT/'work/remote-etl';manifest=json.loads((w/'manifest.json').read_text())
    required(hashlib.sha256(canonical(manifest).encode()).hexdigest()=='8cf2df9dd09a74234b26f1a99c61d17ed7f1f733eca2f016a4f0429c869471b4','Approved manifest differs')
    for name,want in manifest['code_sha256'].items():required(hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()==want,'Bound implementation changed')
    required(hashlib.sha256((ROOT/'work/etl/plan.json').read_bytes()).hexdigest()=='7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f','Plan differs')
    required(not (w/'owner-authorization.json').exists(),'Interrupted authorization still active')
    authorization=read('stage4b-owner-authorization.json');required(authorization['active_authorization_artifact_removed'] and (ROOT/authorization['archived_artifact'].removeprefix('Ignored ')).is_file(),'Authorization evidence not archived')
    rows=json.loads((w/'partial-source-execution-outcomes.json').read_text());expected=json.loads((ROOT/'work/recovery/expected-source-references.json').read_text())
    required(len(rows)==len({r['reference'] for r in rows})==20432 and {r['reference'] for r in rows}==set(expected),'Source-outcome ledger lost/duplicated rows')
    required(Counter(r['execution_status'] for r in rows)=={'source_preserved_staged':9988,'interrupted_request_not_committed':250,'not_attempted_after_stop':10194},'Outcome accounting differs')
    required(all(r['operational_projection_status']=='not_attempted' for r in rows),'Uncreated projections mislabeled')
    recovery=read('stage4b-bounded-recovery-plan.json');required(recovery['remaining_batches']==manifest['batches'][40:] and len(recovery['remaining_batches'])==179 and not recovery['recovery_execution_enabled'],'Recovery scope expanded/activated')
    required(sum(recovery['expected_additional_direct_inserts'].values())==24077,'Recovery insert budget differs')
    required(hashlib.sha256(canonical(recovery).encode()).hexdigest()==result['recovery_plan_sha256'],'Recovery proposal hash differs')
    report=read('stage4b-google-interruption-report.json');required(report['status']=='passed' and report['owner_private'] and report['preparation_rows_preserved']==11222 and report['interrupted_source_rows']==250 and report['execution_summary_rows']==12 and report['appended_native_rows_style_verified']==262,'Report unverified')
    for n in [28,29,30]:required(len(list((ROOT/'docs').glob(str(n)+'-*.md')))==1,'Required report missing')
    for p in (ROOT/'docs').glob('*.md'):
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in link and not link.startswith('#'):required((p.parent/link.split('#')[0]).is_file(),'Broken documentation link')
    evidence={'status':'passed','scope':'Interrupted execution accounting and safe stopped state, not migration completion','committed_transactions':40,'outstanding_transactions':179,'preserved_source_rows':9988,'not_loaded_source_rows':10444,'all_source_outcomes_accounted':20432,'schema_security_unchanged':True,'active_authorization':False,'recovery_authorized':False,'migration_complete':False}
    (ROOT/'docs/evidence/stage4b-interruption-verification.json').write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
