"""Render senior-review package from fresh live metadata and private recovery aggregates.

No network, source disclosure, database mutation or historical report regeneration.
"""
import json
import re
from collections import Counter
from datetime import datetime
from zoneinfo import ZoneInfo
from etl_core import ROOT, canonical, required
from historical_recovery import W, E, sha
from render_phase1_handover import graph, ident

V=ROOT/'docs/visual'
def read(path):return json.loads(path.read_text())


def main():
    c=read(W/'live-catalog.json');state=read(W/'live-state.json');counts={k:v['count'] for k,v in state['tables'].items()}
    prior=read(ROOT/'work/attendance-indexed-tail/final-catalog.json')
    required(c==prior,'Actual schema/security differs from completed attendance baseline')
    required(read(W/'live-original-snapshot.json')==read(ROOT/'work/attendance-indexed-tail/final-snapshot.json'),'Original data/timestamps differ')
    required(read(W/'live-ledger.json')['migrations']==read(ROOT/'work/attendance-indexed-tail/final-ledger.json'),'Migration ledger differs')
    from attendance_reconcile import expected
    required(read(W/'live-staging-buckets.json')==expected(read(ROOT/'work/attendance/records.json')),'Staging payload/keys differ')
    required(len(c['tables'])==20 and all(t['rls'] for t in c['tables']),'Table/RLS mismatch')
    fks=read(W/'live-fks.json');required(int(fks['violations'])==0,'Live FK violation')
    recovery=read(E/'historical-original-recovery.json');runtime=read(E/'historical-runtime-tests.json')
    required(runtime['status']=='passed' and runtime['container_removed'],'Focused runtime test failed')
    units=read(E/'historical-unit-tests.json');required(units['status']=='passed','Unit tests failed')
    when=datetime.fromisoformat(state['checked_at_utc'].replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Kolkata')).strftime('%d %B %Y, %H:%M IST')
    tables={t['schema']+'.'+t['name']:t for t in c['tables']}
    pks={};fklist=[];unique={q:[] for q in tables}
    for k in c['constraints']:
        q=k['schema']+'.'+k['table']
        if k['type'] in {'p','u'}:
            cols=re.search(r'\((.*?)\)',k['definition'])[1].split(', ');unique[q].append(cols)
            if k['type']=='p':pks[q]=cols
        if k['type']=='f':
            m=re.search(r'FOREIGN KEY \((.*?)\) REFERENCES ([\w.]+)\((.*?)\)',k['definition'])
            fklist.append({'table':q,'name':k['name'],'columns':m[1].split(', '),'parent':m[2],'parent_columns':m[3].split(', '),'definition':k['definition']})
    columns={(x['schema']+'.'+x['table'],x['name']):x for x in c['columns']}
    mer=['erDiagram'];dot=['digraph final { graph[rankdir=LR,bgcolor=white,fontname="DejaVu Sans",labelloc=t,label="Goalkeep KC-2 · Actual deployed model · 20 tables\\nPeach: restricted private; blue: public, RLS protected. Managed Auth excluded from count."]; node[shape=box,style="rounded,filled",fontname="DejaVu Sans"];edge[color="#7c8da8",arrowsize=.6];']
    for q in [*tables,'auth.users']:
        mer.append('    '+ident(q)+' {')
        fields=pks.get(q,['id'])
        foreign_fields=sorted({col for f in fklist if f['table']==q for col in f['columns']})
        for field in fields+[f for f in foreign_fields if f not in fields]:
            mer.append('        '+('uuid' if q=='auth.users' else columns[(q,field)]['type'].replace(' ','_').replace('[]','_array'))+' '+field+(' PK,FK' if field in fields and field in foreign_fields else ' PK' if field in fields else ' FK'))
        mer.append('    }')
        dot.append(ident(q)+' [label="'+q+'\\n'+(', '.join(fields))+' [PK]'+('\\n'+str(counts[q])+' rows' if q in tables else '\\nmanaged, external')+'",fillcolor="'+('#fff0df' if q.startswith('gk_private') else '#e5f0ff')+'"];')
    drawn=set()
    for fk in fklist:
        child=fk['table'];parent=fk['parent'];optional=any(not columns[(child,col)]['not_null'] for col in fk['columns'])
        many=not any(set(key)<=set(fk['columns']) for key in unique[child])
        mer.append('    '+ident(parent)+(' |o' if optional else ' ||')+'--'+('o{' if many else 'o|')+' '+ident(child)+' : "'+fk['name']+'"')
        if (child,parent) not in drawn:
            dot.append(ident(child)+' -> '+ident(parent)+(' [style=dashed,color="#c3c9d1",constraint=false]' if parent=='auth.users' else '')+';');drawn.add((child,parent))
    dot.append('}');(V/'final-deployed-er.mmd').write_text('\n'.join(mer)+'\n');graph('final-deployed-er','\n'.join(dot))
    business='''flowchart LR
 CHILDREN[Children: 371] --> LINKS[Verified ID child-caregiver links: 716]
 CAREGIVERS[Restricted caregivers: 716] --> LINKS
 CHILDREN --> PRIVATE[Restricted child profiles: 371]
 LINKS --> Q[Questionnaire responses: 106 pending]
 Q --> A[Restricted literal answer slots: 3286]
 CHILDREN --> P[Programme slots: 128 pending]
 SOURCE[Restricted source rows: 20432] --> STAGE[Restricted attendance staging: 43160 pending]
 SOURCE --> CANDIDATES[Restricted identity candidates: 2089]
 CHILDREN -. requires verified child and event evidence .-> OPS[Attendance / ADL / support: 0]
 STAGE -. no approved promotion yet .-> OPS
'''
    (V/'final-business-relationships.mmd').write_text(business)
    graph('final-business-relationships','''digraph business {graph[rankdir=LR,bgcolor=white,fontname="DejaVu Sans"];node[shape=box,style="rounded,filled",fillcolor="#e5f0ff",fontname="DejaVu Sans"];children[label="Children · 371"];caregivers[label="Restricted caregivers · 716",fillcolor="#fff0df"];links[label="Verified ID links · 716"];q[label="Questionnaires · 106 pending"];answers[label="Restricted answers · 3286",fillcolor="#fff0df"];programmes[label="Programme slots · 128 pending"];source[label="Restricted source rows · 20432",fillcolor="#fff0df"];staging[label="Restricted attendance · 43160 pending",fillcolor="#fff0df"];ops[label="Operational attendance / ADL / support · 0"];children->links;caregivers->links;links->q;q->answers;children->programmes;source->staging;children->ops;staging->ops[style=dashed,label="requires verified evidence"]; }''')
    flow='''flowchart LR
 ORIGINAL[12 unchanged originals / 155 sheets] --> LOCAL[Local privacy processing]
 LOCAL --> SOURCE[20432 sanitized source rows]
 SOURCE --> ID[Verified-ID pending projections]
 SOURCE --> STAGING[43160 attendance staging rows]
 ORIGINAL --> RECOVERY[Private original-date recovery ledger]
 RECOVERY --> APPROVAL[197 date updates prepared: owner approval required]
 ID --> TRACE[Source provenance and append-only audit]
 STAGING -. authoritative ID + calendar + semantics .-> OP[Operational promotion: none eligible now]
'''
    (V/'final-source-flow.mmd').write_text(flow)
    graph('final-source-flow','''digraph flow {graph[rankdir=LR,bgcolor=white];node[shape=box,fontname="DejaVu Sans"];raw[label="12 originals / 155 sheets\\nUnchanged, private"];source[label="20432 sanitized source rows"];typed[label="Verified-ID pending projections"];stage[label="43160 private attendance staging"];dates[label="Private original-date recovery\\n197 existing-row updates prepared"];approval[label="Separate owner manifest approval\\nNo new remote writes"];raw->source;source->typed;source->stage;raw->dates;dates->approval;}''')
    dictionary=['# Final deployed data dictionary','',f'Generated from the actual 20-table PostgreSQL catalog; checked {when}. Private schemas remain restricted. Defaults, nullability, primary/foreign keys and constraints below are actual deployed definitions. This replaces draft specifications for current-schema inspection; historical dictionaries remain evidence.','']
    inventory=['# Final live table and key inventory','',f'Checked {when}; project `hmlbdozsqxlwzvjimjwh`, Tokyo non-production. No writes in this task.','', '| Table | Rows | Primary key | Boundary |','|---|---:|---|---|']
    for q,t in tables.items():
        inventory.append(f"| `{q}` | {counts[q]:,} | `{', '.join(pks[q])}` | {'Restricted' if q.startswith('gk_private') else 'RLS protected'} |")
        dictionary += ['## '+q,'',f"Rows: {counts[q]:,}. RLS enabled: {t['rls']}; FORCE RLS: {t['force_rls']}. Primary key: `{', '.join(pks[q])}`.",'','| Column | PostgreSQL type | Nullable | Default / generation |','|---|---|---|---|']
        for (table,col),spec in columns.items():
            if table==q:dictionary.append(f"| `{col}` | `{spec['type']}` | {'No' if spec['not_null'] else 'Yes'} | `{str(spec.get('default') or '').replace('|',' / ')}` |")
        dictionary += ['','Constraints:','']+[f"- `{k['name']}`: `{k['definition']}`." for k in c['constraints'] if k['schema']+'.'+k['table']==q]+['']
    inventory+=['','## Complete foreign-key reference','']+[f"- `{f['table']}({', '.join(f['columns'])})` → `{f['parent']}({', '.join(f['parent_columns'])})` — `{f['name']}`." for f in fklist]
    (ROOT/'docs/FINAL-DATA-DICTIONARY.md').write_text('\n'.join(dictionary).rstrip()+'\n')
    (ROOT/'docs/FINAL-TABLE-INVENTORY.md').write_text('\n'.join(inventory)+'\n')
    ledger=read(W/'evidence-ledger.json');daily=[r for r in ledger if r['dataset']=='daily_attendance' and r.get('observation_kind')=='MARK']
    report={'status':'passed','checked_at_ist':when,'checked_at_utc':state['checked_at_utc'],'project_reference':'hmlbdozsqxlwzvjimjwh','region':'ap-northeast-1',
      'application_tables':20,'table_counts':counts,'foreign_keys_checked':fks['checked'],'foreign_key_violations':0,
      'schema_rls_permissions_triggers_unchanged':True,'original_19_tables_including_timestamps_unchanged':True,
      'all_43160_staging_keys_and_payloads_match':True,'ledger_unchanged':True,'remote_writes':0,
      'catalog_sha256':sha(canonical(c).encode()),'dictionary_columns':len(columns),'diagram_foreign_keys':len(fklist),
      'daily_pa_marks':len(daily),'daily_pa_dates_recovered_locally':sum(bool(x['recovered_date']) for x in daily),
      'daily_pa_dates_with_source_conflicts':sum(x['date_verification']=='SOURCE_CONFLICT' for x in daily),
      'daily_pa_unresolved_dates':sum(not x['recovered_date'] for x in daily),
      'eligible_new_operational_events':0,'prepared_existing_date_updates':recovery['existing_verified_id_date_update_candidates'],
      'new_unit_tests_passed':units['tests_run'],'new_isolated_runtime_checks_passed':runtime['tests_passed'],'prior_migration_tests_reused':True}
    (E/'phase1-final-delivery-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
