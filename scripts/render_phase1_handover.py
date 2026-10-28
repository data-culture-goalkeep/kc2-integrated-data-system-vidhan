#!/usr/bin/env python3
"""Render actual deployed metadata and concise handover, offline. No remote access or source values."""
import json,re,subprocess,html,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict
from etl_core import ROOT,canonical,required
V=ROOT/'docs/visual';E=ROOT/'docs/evidence'
def read(p):return json.loads((ROOT/p).read_text())
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def ident(q):return q.replace('.','_').upper()
def graph(name,dot):
 (V/(name+'.dot')).write_text(dot)
 subprocess.run(['dot','-Tsvg',str(V/(name+'.dot')),'-o',str(V/(name+'.svg'))],check=True,capture_output=True)
def main():
 V.mkdir(exist_ok=True);live=read('work/handover/live.json');catalog=live['catalog'];counts=live['counts']['record_counts'];actual=live['reconciliation']
 required(catalog==read('docs/evidence/stage4c-final-live-catalog.json'),'Live schema/security changed')
 required(actual==read('docs/evidence/stage4c-final-live-reconciliation.json'),'Live source/key/relationship reconciliation changed')
 expected=read('docs/evidence/stage4c-execution-verification.json')['live_table_counts'];required({q.split('.')[1]:v for q,v in counts.items()}==expected,'Live counts changed')
 when=datetime.fromisoformat(live['checked_at_utc'].replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Kolkata')).strftime('%d %B %Y, %H:%M IST')
 tables={t['schema']+'.'+t['name']:t for t in catalog['tables']};required(len(tables)==19 and all(t['rls'] for t in tables.values()),'Table/RLS mismatch')
 constraints=catalog['constraints'];fks=[];primary={};unique=defaultdict(list)
 for c in constraints:
  q=c['schema']+'.'+c['table']
  if c['type'] in ['p','u']:
   cols=re.search(r'\((.*?)\)',c['definition'])[1].split(', ');unique[q].append(cols)
   if c['type']=='p':primary[q]=cols
  if c['type']=='f':
   m=re.search(r'FOREIGN KEY \((.*?)\) REFERENCES ([\w.]+)\((.*?)\)',c['definition']);required(m is not None,'Unknown FK rendering')
   fks.append({'name':c['name'],'child':q,'columns':m[1].split(', '),'parent':m[2],'parent_columns':m[3].split(', '),'definition':c['definition']})
 required(len(fks)==99,'FK count differs');columns={(c['schema']+'.'+c['table'],c['name']):c for c in catalog['columns']}
 # Every actual FK is retained in Mermaid and the machine manifest. Parallel source/target FKs are collapsed only in the SVG.
 mer=['erDiagram'];groups=defaultdict(list)
 for q in [*tables,'auth.users']:
  fields=primary[q] if q in primary else ['id'];mer.append('    '+ident(q)+' {')
  for col in fields:mer.append('        '+('uuid' if q=='auth.users' else columns[(q,col)]['type'].split('(')[0].replace(' ','_'))+' '+col+' PK')
  mer.append('    }')
 for fk in fks:
  cols=fk['columns'];many=not any(set(key)<=set(cols) for key in unique[fk['child']]);optional=any(not columns[(fk['child'],c)]['not_null'] for c in cols)
  mer.append('    '+ident(fk['parent'])+(' |o' if optional else ' ||')+'--'+('o{' if many else 'o|')+' '+ident(fk['child'])+' : "'+fk['name']+'"');groups[(fk['child'],fk['parent'])].append(fk)
 (V/'deployed-er.mmd').write_text('\n'.join(mer)+'\n')
 dot=['digraph deployed {','graph [rankdir=LR, bgcolor="white", pad=.35, nodesep=.28, ranksep=1.1, splines=polyline, fontname="DejaVu Sans", label="Goalkeep KC-2 · Actual deployed schema · 19 application tables + managed Auth\\nBlue = public (RLS protected); peach = restricted gk_private. Parallel FKs grouped; common Auth actor links bundled in note. All 99 exact constraints in Mermaid/key reference.", labelloc=t];','node [shape=plain,fontname="DejaVu Sans"]; edge [fontname="DejaVu Sans",fontsize=8,color="#8391a5",arrowsize=.6];']
 for schema,color in [('public','#e5f0ff'),('gk_private','#fff0df')]:
  dot+=['subgraph cluster_'+schema+' { label="'+schema+(' · restricted' if schema=='gk_private' else ' · RLS protected')+'"; color="#c9d1da";']
  for q,t in tables.items():
   if t['schema']!=schema:continue
   names=primary[q]+[x['name'] for x in catalog['columns'] if x['schema']+'.'+x['table']==q and x['name'] not in primary[q] and x['name'] not in ['created_by','updated_by','archived_by'] and any(x['name'] in f['columns'] for f in fks if f['child']==q)]
   txt='<BR ALIGN="LEFT"/>'.join(html.escape(n)+('  [PK]' if n in primary[q] else '  [FK]') for n in names)
   dot.append(ident(q)+' [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="7"><TR><TD BGCOLOR="'+color+'"><B>'+t['name']+'</B><BR/>'+str(counts[q])+(' rows · PRIVATE' if schema=='gk_private' else ' rows')+'</TD></TR><TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">'+txt+'</FONT></TD></TR></TABLE>>];')
  dot.append('}')
 dot.append('AUTH_USERS [label="auth.users\\nManaged authentication\\nCommon created_by / updated_by / archived_by\\nFKs bundled here; see exact key reference\\nOutside 19-table application count",shape=box,style="rounded,dashed",color="#a0a0a0"];')
 for (child,parent),fs in groups.items():
  audit=parent=='auth.users'
  if audit:
   fs=[f for f in fs if f['columns'] not in [['created_by'],['updated_by'],['archived_by']]]
   if not fs:continue
  dot.append(ident(child)+' -> '+ident(parent)+' [label="'+str(len(fs))+' FK'+('s' if len(fs)>1 else '')+'",'+('color="#d5d5d5",fontcolor="#969696",style=dashed,constraint=false' if audit else 'color="#6b7e98"')+'];')
 dot.append('}');graph('deployed-er','\n'.join(dot))
 # Business view includes only relationships that exist; no implied approved candidate link.
 business='''digraph business { graph [rankdir=LR,bgcolor=white,pad=.4,nodesep=.5,ranksep=.9,fontname="DejaVu Sans",labelloc=t,label="Goalkeep KC-2 · Business relationships (existing schema)\\nPeach = restricted. Imported projections are pending; candidates are not accepted identities."]; node [shape=box,style="rounded,filled",fillcolor="#e5f0ff",fontname="DejaVu Sans",fontsize=12,margin=.18];edge[fontname="DejaVu Sans",fontsize=10,color="#536b8a"];
 children[label="Children\\n371 · public.children"];
 profiles[label="Restricted child profiles\\n371 · gk_private.child_private_profiles",fillcolor="#fff0df"];
 caregivers[label="Caregivers\\n716 · gk_private.caregivers",fillcolor="#fff0df"];
 links[label="Verified ID relationships\\n716 · public.child_caregivers"];
 responses[label="Questionnaire responses\\n106 · public.questionnaire_responses"];
 items[label="Question definitions\\n31 · public.questionnaire_items"];
 answers[label="Literal answer slots\\n3,286 · gk_private.questionnaire_answers",fillcolor="#fff0df"];
 programmes[label="Programme source slots\\n128 pending · public.program_changes\\nDates NULL"];
 candidates[label="Identity candidates\\n2,089 unapproved\\ngk_private.identity_candidates",fillcolor="#fff0df"];
 observations[label="Attendance / ADL / support\\n3 deployed tables · all empty"];
 children -> profiles[label="0..1 profile per child"];
 children -> links[label="0..many links"];
 caregivers -> links[label="0..many links"];
 links -> responses[label="0..many responses"];
 responses -> answers[label="0..many answers"];
 items -> answers[label="0..many answers\\nsame form definition enforced"];
 children -> programmes[label="0..many source slots"];
 children -> observations[label="0..many future observations"];
 children -> candidates[label="possible match only",style=dashed];
}''';graph('business-relationships',business)
 (V/'business-relationships.mmd').write_text('''flowchart LR
 CHILDREN[Children: 371] -->|0..1| PRIVATE[Restricted child profiles: 371]
 CHILDREN -->|many links| LINKS[Child-caregiver links: 716]
 CAREGIVERS[Restricted caregivers: 716] -->|many links| LINKS
 LINKS --> RESPONSES[Questionnaire responses: 106]
 RESPONSES --> ANSWERS[Restricted answers: 3286]
 ITEMS[Item definitions: 31] --> ANSWERS
 CHILDREN --> PROGRAMMES[Programme slots: 128 pending, dates NULL]
 CHILDREN -. possible match only .-> CANDIDATES[Restricted candidates: 2089 unapproved]
 CHILDREN --> OBS[Attendance / ADL / support: empty]
''')
 graph('spreadsheet-to-supabase','''digraph flow { graph[rankdir=LR,bgcolor=white,pad=.3,fontname="DejaVu Sans",labelloc=t,label="Spreadsheet → Supabase · existing migration path"];node[shape=box,style="rounded,filled",fillcolor="#e5f0ff",fontname="DejaVu Sans",margin=.2];edge[color="#536b8a",fontname="DejaVu Sans"]; originals[label="Authorized originals\\n12 spreadsheets / 155 sheets\\nPreserved privately, never changed"]; sanitized[label="Frozen sanitized copies\\nVerified hashes / deterministic IDs"]; source[label="Restricted source preservation\\n12 artifacts + 20,432 source rows",fillcolor="#fff0df"]; typed[label="Verified-ID pending projections\\nChildren / caregivers / questionnaires\\n128 programme source slots"]; blocked[label="Retained exceptions\\n3,623 identity + 314 business pending\\n15,301 source-only",fillcolor="#fff0df"]; provenance[label="Restricted provenance + audit\\n5,772 lineage rows / 28,293 events",fillcolor="#fff0df"]; originals->sanitized->source;source->typed[label="exact IDs + supported values"];source->blocked[label="preserve, do not guess"];typed->provenance;source->provenance[label="source references + status history"];}''')
 # Actual primary/foreign keys, grouped by table, no source values.
 keys=['# Deployed primary and foreign keys','',f'Verified {when}. PK identifies a row; FK requires a related row to exist. Composite keys must be used together. All 99 deployed FKs are listed below; common actor FKs point to managed auth.users. SVG lines group parallel table pairs. Source provenance targets are mutually exclusive per row; a graph edge is a permitted link, not proof every row uses it.','']
 for q in tables:
  keys+=['## '+q,'','Primary key: `'+', '.join(primary[q])+'`.','']
  for fk in [f for f in fks if f['child']==q]:keys.append('- `'+', '.join(fk['columns'])+'` → `'+fk['parent']+'('+', '.join(fk['parent_columns'])+')` — `'+fk['name']+'`.')
  keys.append('')
 (V/'deployed-keys.md').write_text('\n'.join(keys).rstrip()+'\n')
 (E/'phase1-visual-model.json').write_text(json.dumps({'catalog_sha256':digest(catalog),'application_tables':list(tables),'managed_external':['auth.users'],'primary_keys':primary,'foreign_keys':fks,'fk_table_pair_groups':len(groups),'svg_drawn_relationship_groups':sum(1 for (child,parent),fs in groups.items() if parent!='auth.users' or any(f['columns'] not in [['created_by'],['updated_by'],['archived_by']] for f in fs)),'svg_common_actor_fks_bundled':sum(1 for f in fks if f['parent']=='auth.users' and f['columns'] in [['created_by'],['updated_by'],['archived_by']]),'mermaid_relationships':len(fks),'private_tables':[q for q,t in tables.items() if t['schema']=='gk_private']},indent=2)+'\n')
 live_report={'status':'passed','checked_at_utc':live['checked_at_utc'],'checked_at_ist':when,'project_reference':'hmlbdozsqxlwzvjimjwh','region':'ap-northeast-1','application_tables':19,'table_counts':counts,'catalog_sha256':digest(catalog),'schema_rls_privileges_triggers_unchanged':True,'full_source_reconciliation_matches_verified_load':True,'foreign_keys_checked':99,'foreign_key_violations':0,'duplicate_and_integrity_zero_checks':actual['zero_checks'],'remote_writes':0,'previous_tests_reused':True}
 (E/'phase1-handover-live.json').write_text(json.dumps(live_report,indent=2)+'\n')
 inventory='\n'.join('| `'+q+'` | '+str(counts[q])+' | '+('Restricted' if t['schema']=='gk_private' else 'RLS protected')+' |' for q,t in tables.items())
 report=f'''# Phase 1 — Fast-track handover\n\nVerified {when}. Exact project **kc2-integrated-data-system / hmlbdozsqxlwzvjimjwh**, Tokyo `ap-northeast-1`, PostgreSQL 17.11; owner-designated non-production pilot. Tokyo is the explicit exception to Mumbai. **The deployed backend and approved preservation/pending-record migration are complete. Business-approved operational data and application access are not complete.** No new remote write or migration batch was executed in this handover.\n\n## View the model\n\n- [Full deployed ER diagram](visual/deployed-er.svg): all 19 tables; peach marks restricted entities, blue public entities remain RLS protected. Managed Auth is outside the application count. SVG lines group parallel FKs and bundle common actor links into the Auth note; [exact Mermaid](visual/deployed-er.mmd) and [all primary/foreign keys](visual/deployed-keys.md) preserve all 99 constraints.\n- [Simplified business relationships](visual/business-relationships.svg): child → caregiver link → questionnaire → answer; programme slots and unresolved candidates shown separately.\n- [Spreadsheet-to-Supabase flow](visual/spreadsheet-to-supabase.svg): originals → sanitized snapshot → source retention → pending projections or preserved exceptions → provenance/audit.\n- [Safe inspection and preview guide](visual/data-preview.md), using the existing authenticated Supabase project dashboard; no public preview or RLS change.\n\n## Current live inventory\n\n| Table | Rows | Boundary |\n| --- | ---: | --- |\n{inventory}\n\nTotals: **34,077 direct rows + 28,293 generated audit events**; all 219 original transactions accounted for. All 20,432 source rows retained: resolved 1,194, reference-only 15,301, blocked 3,937 (identity 3,623 + business 314). Resolved means source processing, not business acceptance. Source-only includes headers, summaries and repeated views; never compare these grains to people or observations.\n\nInternal UUIDs are relational keys; child/caregiver business IDs remain unique. Child profiles are one-to-one with children; children and caregivers join through child_caregivers. Responses reference that verified pair, and answer/definition composite FKs prevent mixing form versions. reference_values uses `(vocabulary, code)`. Source artifacts/rows/provenance retain file-sheet-row-column lineage. Audit history is append-only; JSON record keys in audit events are not invented domain FKs.\n\n## Remaining operational imports\n\n**Additional records eligible now: 0 verified, 0 safely pending.** All uncertain rows already exist in restricted source storage, so this is not data loss. The local [gate analysis](evidence/phase1-operational-eligibility.json) independently checked the frozen sanitized snapshot without reopening/reprofiling workbooks. No name-only candidate was promoted.\n\n| Dataset / grain | Available evidence | Additional safe import | Decision or evidence needed |\n| --- | --- | ---: | --- |\n| Daily attendance roster rows | 2,142: 1,009 single candidate, 74 ambiguous, 1,059 unmatched | 0 | Verified ID crosswalk; trustworthy per-mark calendar; approve service/mark codes. Attendance date is NOT NULL; pending cannot waive it. |\n| ADL roster rows / checked slots | 1,219 roster rows; 194 true slots, four without dates; zero verified literal-ID rows | 0 | Approve exact child crosswalk and true-slot semantics. Nullable visit_date permits explicit pending NULL only after identity/grain is verified. |\n| Support attendance rows | 262: 249 single candidate, six ambiguous, seven unmatched | 0 | Exact child crosswalk and per-event grain/value mapping. Required child_id/event_reference cannot be invented. |\n| Other support/activity/history rows | 15 support summaries + 144 activity rows + 155 historical rows (314 business-pending) | 0 | Approve source grain, identity and actual observation meaning; aggregate counts are not invented child events. |\n| Programme source slots | 128 already migrated pending with NULL dates | 0 new | Date-fidelity policy and category/history meaning; no replay, no invented effective dates. |\n| Questionnaire primary form | 106 responses / 3,286 literal answer slots already migrated pending | 0 new | Approve scoring, missing-answer policy, form/category meaning and dates. 29 subset rows + 84 view rows are not new submissions. |\n\nA single name candidate is not a verified identity. All attendance/ADL/support typed tables require a child FK; neither pending status nor a NULL date creates identity evidence. The 190 ADL slots with reported dates are not chronologically trusted: sanitized date fidelity remains unapproved. No acceptance is inferred from syntactic date parsing.\n\n**Ready preparation:** a private row-level gate ledger reconciles 4,518 candidate rows across prioritized datasets and related views. It retains source record IDs/coordinates and blockers. Reuse existing `etl_core` validation/UUID/compiler and `Builder.project` typed provenance after gates are resolved; deterministic observation IDs must include source record ID and actual source cell/slot. Validate against existing keys, use bounded transactions and a new destination/scope-bound incremental manifest. Do not reuse the consumed initial-load or recovery authorization, change the schema, or run an import with unresolved facts.\n\n## Security and frontend readiness\n\nThe 19-table schema, RLS, privileges and triggers exactly match the deployed reference. Fresh counts, key/source reconciliation, duplicate checks and all 99 FK checks pass; prior 82 Python/isolated recovery/security tests were reused rather than repeated. See [lightweight live evidence](evidence/phase1-handover-live.json). No policy, membership or OAuth configuration changed.\n\n**Ready for frontend scaffolding and contract work**, using synthetic fixtures and existing schema. **Authenticated live-user workflows are not ready to activate:** separately approve the pilot role matrix/private-data permissions and designated Admin provisioning; configure Google OAuth for verified Goalkeep Workspace `goalkeep.net` identity; verify server eligibility/session/membership enforcement and real HTTP/RLS behavior. A domain suffix alone must never grant access. No service-role credentials belong in the browser. Restricted tables need an approved backend/Data API access path; do not expose gk_private broadly.\n\nBefore operational data-entry/analytics acceptance, approve each relevant date/vocabulary/event/identity rule; unrelated synthetic UI scaffolding need not wait. Approve scope and credentials through supported secrets, and retain sticky header/collapsible icon sidebar, button-triggered forms and consistent responsive components. No frontend was built here. PR #1 remains subject to required review; no automatic merge.\n\n## Quality limitations and handover gates\n\nSixty questionnaire source-name conflicts remain evidence, 86 numeric answers are missing, and one known answer outlier is retained for review. Attendance header/calendar issues (610 marks without recognized headers, four malformed headers, seven calendar mismatches), four missing ADL dates and three birth/joining chronology conflicts remain unresolved. Zero dates, scores or missing values were fabricated. Categories are inactive and all imported projections pending.\n\nPM/owner next actions: approve scoped exact identity crosswalks and date policy first; questionnaire interpretation/category meanings separately; role/OAuth activation separately. Google Docs context-sync destination and final PM acceptance remain outstanding organisational handover items. Current Markdown context, model, mappings and private failure report are available; raw sources/private ledgers stay outside Git. Complete execution/reconciliation history is in [34](34-recovery-execution-report.md), [35](35-final-migration-reconciliation.md) and [36](36-post-migration-data-quality.md).\n'''
 (ROOT/'docs/37-phase1-handover-summary.md').write_text(report)
 print(json.dumps({'tables':19,'foreign_keys':99,'fk_table_pair_groups':len(groups),'svg_drawn_relationship_groups':sum(1 for (child,parent),fs in groups.items() if parent!='auth.users' or any(f['columns'] not in [['created_by'],['updated_by'],['archived_by']] for f in fs)),'svg_common_actor_fks_bundled':sum(1 for f in fks if f['parent']=='auth.users' and f['columns'] in [['created_by'],['updated_by'],['archived_by']]),'fresh_live_integrity':'passed','remote_writes':0}))
if __name__=='__main__':main()
