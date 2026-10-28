"""Assemble requested Markdown delivery from verified aggregates, never raw records."""
import json
from etl_core import ROOT, required

E=ROOT/'docs/evidence'
def load(name):return json.loads((E/name).read_text())


def main():
    v=load('phase1-final-delivery-verification.json');r=load('historical-original-recovery.json');h=load('historical-date-increment-hash.json')
    required(v['foreign_key_violations']==0 and v['application_tables']==20,'Live verification incomplete')
    datasets=r['datasets'];profiles=load('data-profile.json');counts=v['table_counts']
    inventory='\n'.join(f"| `{name}` | {n:,} |" for name,n in counts.items())
    sources='\n'.join(f"| {s['source']} | {s['worksheets']} | {s['source_record_rows']:,} |" for s in profiles['sources'])
    recovery_table='\n'.join(f"| {name} | {d['evidence_candidates']:,} | {d['original_dates_recovered']:,} | {d['unresolved_dates']:,} | {d['verified_id_candidates']} | 0 |" for name,d in datasets.items())
    handover=f'''# Goalkeep KC-2 — Phase 1 Technical Handover

Prepared for senior Goalkeep and PM review. Live database evidence checked **{v['checked_at_ist']}**. Repository: `data-culture-goalkeep/kc2-integrated-data-system-vidhan`.

## 1. Executive summary

The deployed backend and two historical preservation imports are complete and reconciled. All **20,432 source rows** and **43,160 attendance staging records**, including **24,687 daily P/A marks**, are retained. **Operational attendance, ADL and support tables remain empty** because the historical candidates lack independently verified child links and approved event meanings. This is a business-evidence limitation, not a failed import.

This increment recovers original calendar evidence locally and prepares **197 existing-record date updates: 106 questionnaire assessment dates and 91 programme dates**. They have **not** been written remotely. Seven additional date candidates conflict with original chronology and are excluded. No new child identity, absence, event, score or category meaning was invented.

The complete Phase 1 package is available through stacked PRs #1 and #2 for senior review. Neither PR is merged or approved. Frontend PR #3 remains independent and synthetic-only; no Phase 2 work was performed in this task.

## 2. Original objectives and scope

Build a reproducible, normalized, traceable Supabase PostgreSQL backend from actual NGO spreadsheets; preserve uncertain evidence; automate ETL and reconciliation; protect restricted information; provide PM handover. Official KC-2 organisational requirements are distinguished from explicit owner execution instructions. Tokyo is the owner-approved non-production exception to the original Mumbai standard. Exact target: `kc2-integrated-data-system / hmlbdozsqxlwzvjimjwh / ap-northeast-1`.

Business interpretation, schema deployment, data execution and application access are separate approvals. This task authorizes analysis, code, local tests and GitHub delivery, **not new remote writes**.

## 3. Original spreadsheet inventory

Twelve authorized original spreadsheet exports, 155 worksheets, 20,432 nonempty rows. Originals are unchanged and SHA-256 verified. Source aliases avoid publishing sensitive filenames; the private manifest maps aliases to Drive IDs, original filenames and immutable export paths. [Full inventory](01-source-inventory.md) and [profiling](02-data-profiling.md) preserve worksheet/column coverage.

| Source alias | Worksheets | Nonempty preserved rows |
|---|---:|---:|
{sources}

## 4. Data profiling findings

371 unique authoritative child IDs; 716 unique caregiver IDs; 716 verified ID relationships covering 370 children; 106 questionnaire ID pairs; 60 questionnaire name disagreements preserved. Missing numeric questionnaire answers (86), one known answer outlier, chronology conflicts and undefined scoring/categories remain review items. Name candidates are not accepted identities. Headers, repeated views, summaries, formulas and row contexts have different grains and must not be summed as people or events.

## 5. Final database architecture

The **actual deployed model has 20 application tables**, 363 columns, 103 foreign keys, 241 constraints, 78 indexes, 83 application triggers, 40 policies and 16 application functions. Managed `auth.users` is external to this count. Internal UUIDs reference separate child/caregiver entities through a relationship table. Controlled values are source-scoped/inactive. Original source storage, typed provenance, identity candidates, recovery evidence and audit history remain restricted. Attendance staging adds useful reviewable cell-level structure without weakening operational constraints.

## 6. Data models and ER diagrams

- [Full 20-table deployed ER diagram](visual/final-deployed-er.svg), [exact Mermaid including all 103 FKs](visual/final-deployed-er.mmd).
- [Simplified business diagram](visual/final-business-relationships.svg), [Mermaid](visual/final-business-relationships.mmd).
- [Spreadsheet-to-database flow](visual/final-source-flow.svg), [Mermaid](visual/final-source-flow.mmd).
- [Actual table counts and complete PK/FK reference](FINAL-TABLE-INVENTORY.md).

Peach entities are restricted. Public-schema tables remain RLS protected; public schema does not mean public data access. Dashed candidate/promotion links are not verified relationships.

## 7. Final data dictionary

[Final deployed data dictionary](FINAL-DATA-DICTIONARY.md) lists every actual column, PostgreSQL type, nullability, default/generation expression and constraint for all 20 tables. It supersedes draft models for current inspection. Historical data dictionaries and model comparisons remain preserved.

## 8. Source-to-target mappings

[Final preservation mapping](23-source-target-mapping-final.md), [raw-vs-organized comparison](10-raw-vs-organized-model.md), [attendance mapping](38-attendance-ingestion-and-approval.md), and [original-date increment](47-historical-recovery-and-increment.md). All original fields remain represented in restricted source payloads even when no operational projection is justified. Date recoveries bind the original file hash and cell, not the pseudodate in the frozen sanitized payload. Original and sanitized snapshots are never rewritten.

## 9. ETL implementation

Existing `etl_core`, loader, source-provenance framework and deterministic UUID strategy are reused. Attendance extraction and checkpoint-aware executors preserve complete source coordinates. New `historical_recovery.py` reads originals locally, validates calendars and identifiers, and emits private evidence/review ledgers. `historical_projection.py` compiles gated attendance/ADL/support units only with explicit evidence-linked decisions. `prepare_historical_increment.py` generates exact conditional date-update SQL; `historical_execution.py` adds fail-closed authorization, packet hashes, fsynced hash-linked checkpoints, durable receipts and stop-on-uncertainty handling. These modules do not connect to Supabase automatically.

## 10. Attendance migration

All 216 original attendance batch indices are accounted for. Actual live staging: **43,160 rows over 107 sheets**, including 26,259 literal marks (24,687 daily + 1,572 support), 189 formula cells, 2,579 summary values, one auxiliary value and 14,132 source contexts. The 43,586 blank daily roster slots remain preserved as blanks in source rows/grid contracts; none became fabricated absences.

**Verified operational attendance: 0. Pending staging: 43,160.** Every expected staging key/full payload matches, with zero unexplained losses or duplicate coordinates. [Actual execution](45-attendance-staging-execution-complete.md) and [final reconciliation](46-attendance-final-source-reconciliation.md) retain all historical interruption/timeout evidence.

## 11. Date and calendar recovery

Sanitization replaced datetime cells with unrelated pseudodates and formulas with markers. The unchanged originals still contain recoverable calendar evidence. Of 24,687 actual daily P/A marks, **{v['daily_pa_dates_recovered_locally']:,}** now have locally recovered source dates, including exact observed LET/DATE/SEQUENCE calendar reconstruction and consensus-checked repeated grids. **{v['daily_pa_dates_with_source_conflicts']}** of those dates have calendar/weekday conflicts; **{v['daily_pa_unresolved_dates']}** marks still lack a reliable full date. Thus **{v['daily_pa_unresolved_dates']+v['daily_pa_dates_with_source_conflicts']}** daily marks retain unresolved/conflicting date gates. These are local recovery results, not live date updates.

Only explicit source year/month plus original full-date anchors can establish a day-only calendar. Any disagreeing anchor rejects grid reconstruction. Leap years, invalid dates, month boundaries, formula dependencies/cycles and ambiguous numeric formats are tested. Weekdays are derived from recovered dates; disagreeing source labels remain evidence. No arbitrary century, Excel serial or malformed date correction is guessed.

## 12. ADL, support and programme history

ADL: 194 true visit slots across 1,219 roster rows; **190 original dates recovered**, four missing. No independently verified child identifier exists in those slots, so no ADL event is inserted. Nullable dates do not waive identity requirements.

Support: 1,572 participation marks, 1,018 original full-date headers recovered; other headers often specify only an event/month. Event/participant/code meanings remain unapproved. The source contains 110 caregiver-ID formula cells: 102 cached IDs match the registry and 92 lookup names are unique, but the sole lookup input is a person's name. These are prepared source-defined suggestions requiring independent NGO confirmation, not automatic verified mappings. Another 784 attendance identity formulas reference names without independent child IDs. All formula evidence is retained privately.

Programme: 128 source slots already exist pending, all with NULL dates. Of the original date candidates, 91 pass exact-ID/date/chronology gates, seven conflict, and 30 lack a safe full-date recovery. Questionnaire: all 106 existing verified-pair responses have recoverable original assessment dates. Prepared date updates leave every review state pending and do not approve programme categories, questionnaire scoring or events.

## 13. Actual database migration results

| Table | Actual live rows |
|---|---:|
{inventory}

The original preservation migration inserted 34,077 direct rows and generated 28,293 audit events; attendance added 43,160 staging rows without modifying existing audits. Those are different grains. This finalization task executed **zero remote writes**. The proposed 197 date transactions would add 197 recovery actions and 197 typed provenance rows and generate 197 new audits if separately approved; these are planning expectations, not live results.

## 14. Data-quality findings

Unknown identity, dates and event meanings remain separate blockers. Precise row/cell evidence, original values, candidate UUIDs, recovered dates, formula dependencies, conflicts and required decisions are stored in ignored `work/historical-recovery/`. The existing private source/staging tables already preserve the corresponding source evidence; no extra staging table is needed. Safe aggregate results are committed in [original recovery evidence](evidence/historical-original-recovery.json).

Do not promote a unique name match, interpret a support participation mark as child presence, convert a summary into an event, treat a formula/context as a literal mark, or compare unrelated source-row and event counts. Duplicate source coordinates are zero; alternate views remain preserved, not falsely certified as distinct events. True cross-view event deduplication is pending verified identity/grain.

## 15. Source reconciliation

| Evidence dataset | Candidate cells/rows/slots | Original dates recovered locally | Dates unresolved | Exact verified ID candidates | Eligible new events |
|---|---:|---:|---:|---:|---:|
{recovery_table}

These denominators are intentionally dataset-specific. Daily candidates include 24,687 literal marks and 189 formula cells. Annual and support summaries are aggregate evidence, not individual events. Some activity/summary rows also carry preserved auxiliary cells, so this ledger is not a count of distinct business events. Every eligible projection still requires identity, grain and meaning gates; **newly verified operational identity mappings: 0**. Earlier 1,009 provisional / 74 ambiguous / 1,059 unmatched daily roster classifications remain candidates, not approved identities.

## 16. Testing evidence

**{v['new_unit_tests_passed']} focused synthetic unit tests** and **{v['new_isolated_runtime_checks_passed']} isolated PostgreSQL checks** passed. Runtime applies the exact four deployed migrations in a digest-pinned network=none throwaway container; the container was removed. Checks cover calendar reconstruction/ambiguity, exact identifiers, nullable ADL/support dates, gated literal attendance, deterministic replay, conflicting updates, foreign keys, lineage, transaction rollback, audit generation, unchanged sources, private-data denial and inactive memberships. Unit tests exercise expiry/hash binding, lost/invalid acknowledgements, ordering and receipt tamper detection.

Fresh live read-only checks verify all 20 tables, all **103 foreign keys with zero violations**, complete original-table fingerprints/timestamps, all staging payload buckets, unchanged catalog/RLS/privileges/triggers/four-entry ledger, and no active import. Prior source preservation/attendance runtime evidence is reused, not rerun. SQL parsing is supplementary; it is not presented as successful database execution. [Machine verification](evidence/phase1-final-delivery-verification.json), [new runtime evidence](evidence/historical-runtime-tests.json), [unit evidence](evidence/historical-unit-tests.json).

## 17. Security and privacy controls

All 20 application tables have RLS enabled; private attendance staging also forces RLS. The complete effective permissions and policies match the approved deployed baseline. No memberships are active. Original files, recovered dates, personal values, pseudonym keys, packets and raw journals stay outside Git. Diagram/dictionary/handover examples contain metadata only. Use the authenticated Supabase project dashboard for technical inspection; do not expose private schemas or weaken RLS for previews.

Future Google login requires verified Google Workspace/provider/session evidence and an active approved membership. `@goalkeep.net` alone is not authorization. Service-role credentials must never reach browser code. OAuth, role activation, restricted-data access and initial administrators remain separately approved work.

## 18. Audit logging

Actual audit count remains **28,293**. Triggers are active, audit evidence is append-only, and original rows/timestamps are unchanged. Proposed date restoration records target before=NULL, recovered date, original file SHA-256, donor source record/cell, method and validation flags in protected recovery actions, with typed provenance and database-generated update audit. Idempotent replay produces no second update or audit.

## 19. Recovery and rollback

Each prepared date transaction updates one exact pending imported row only when its date is NULL; changed/archived targets and conflicting dates fail closed. Recovery evidence and provenance commit atomically with the update. Same-value replay requires the deterministic evidence marker and complete payload agreement. Before a future execution, verify source/code/SQL/manifest hashes and fresh live fingerprints, security and ledger; obtain explicit scoped owner authorization.

Stop on any failed or uncertain request. Preserve fsynced receipts/journal, inspect the live state read-only, and obtain a bounded recovery approval. Never automatically retry uncertain requests, replay completed prefixes, remove evidence, delete committed records, reset schemas or rewrite migration history. Correcting a committed erroneous date would need a separately approved compensating update with audit; there is no silent destructive rollback.

## 20. Unresolved business decisions

1. Provide/confirm authoritative row-to-child/caregiver crosswalks independent of names, including the support VLOOKUP suggestions.
2. Confirm daily service/mark semantics, support participant/event meanings, ADL true-slot meaning and duplicate-view rules.
3. Resolve 27 calendar/weekday-conflict marks, 600 missing/unrecoverable daily dates, four missing ADL dates and seven excluded existing-record date candidates.
4. Approve the precise original-date fidelity/disclosure scope and incremental manifest **`{h['manifest_sha256']}`** before its 197 updates and associated evidence/audits are executed.
5. Approve questionnaire scoring/missing-answer/category definitions separately; no formulas have been invented.
6. Approve retention/private access, role matrix, OAuth activation and final PM business acceptance separately. The optional organisational Google Docs context-sync destination remains unspecified; Markdown handover is complete.

## 21. Phase 2 dependencies

No further Phase 2 development in this task. PR #3 remains synthetic-only and unmerged. Before live integration: approve role/private-data matrix and Admin provisioning, configure Google OAuth securely, implement approved backend private-data access, validate actual authenticated HTTP/RLS behavior, and preserve pending-vs-verified separation. Historical identity/meaning decisions block only the corresponding operational features; they do not transform staging into accepted data.

## 22. PM review and acceptance checklist

Use [PM review checklist](PM-REVIEW-CHECKLIST.md). Senior review should examine the combined ancestry of PR #1 (backend → main) and PR #2 (attendance/final delivery → backend), review the original-date manifest and unresolved decisions, then record technical acceptance separately from business/operational acceptance and access activation. PRs #1/#2 have no approving review recorded at preparation; neither is merged. Historical execution evidence is preserved. **Technical delivery is ready for review; full operational/business acceptance remains blocked by the explicit evidence gaps and new execution approval.**
'''
    (ROOT/'docs/PHASE1-HANDOVER.md').write_text(handover)
    (ROOT/'docs/47-historical-recovery-and-increment.md').write_text(f'''# Original-evidence recovery and proposed date increment

Checked {v['checked_at_ist']}; no new remote writes. Read [final handover](PHASE1-HANDOVER.md) for complete source reconciliation.

Original/sanitized hashes match the frozen 12-file/155-sheet snapshot. Real source dates were obscured by sanitization. The private recovery ledger retains original values, original sheet names, native sheet keys, source IDs/cells, candidate children, dependencies, weekday conflicts and reviewer decisions. Original source payloads and deployed staging are unchanged.

Daily literal P/A marks: 24,687; locally recovered dates: {v['daily_pa_dates_recovered_locally']:,}; conflicts among recovered: {v['daily_pa_dates_with_source_conflicts']}; unresolved full dates: {v['daily_pa_unresolved_dates']}. ADL true slots: 194, dates recovered: 190, missing: four. No newly verified attendance/ADL child crosswalk; zero eligible new operational events. The 110 name-derived support caregiver-ID formulas (102 registry-matching cached IDs; 92 unique lookup names) remain review suggestions. Original formula expressions/cached IDs are private, not discarded.

## Exact prepared increment — not executed or authorized

- Target: `hmlbdozsqxlwzvjimjwh`, Tokyo non-production.
- Manifest SHA-256: **`{h['manifest_sha256']}`**.
- 197 atomic transactions: 91 programme `promotion_date` updates and 106 questionnaire `assessment_date` updates, NULL → source-recovered DATE.
- 197 protected recovery-action inserts + 197 typed provenance inserts; expected 197 new trigger audit events.
- Expected post-execution recovery actions 197, provenance 5,969 and audits 28,490. These are proposed totals, not live counts.
- All affected records retain pending review status. No source/staging/child/caregiver/answer updates, new operational observations, schema changes or access activation.
- Seven chronology-conflicting date candidates excluded; 30 programme slots lack safe recoverable dates.
- [Exact manifest](evidence/historical-date-increment-manifest.json), [hash](evidence/historical-date-increment-hash.json), [focused tests](evidence/historical-runtime-tests.json).

The manifest binds original/sanitized snapshot, code hashes, private values, per-transaction SQL hashes, exact destination, complete starting-table fingerprints and actual schema/ledger. `historical_execution.py` requires a separate active owner approval; no authorization artifact has been fabricated. It records dispatch before transport, durable official receipts before acknowledgement, and blocks uncertain/out-of-order/repeated requests. No automatic remote execution is implemented by the preparation command.

## Required next action

Owner review/approval of the exact manifest, original-date fidelity/disclosure and controlled execution window. Then freshly verify target/source/code/catalog/ledger/fingerprints, execute only this increment through the reviewed connected pathway and reconcile actual dates/evidence/audits. Existing transaction approvals are consumed and confer no permission for this scope. Stop on any failure/uncertainty; read-only diagnosis and separately bounded recovery only. No deletes/resets or blind retries.
''')
    (ROOT/'docs/PM-REVIEW-CHECKLIST.md').write_text('''# Phase 1 — Senior Goalkeep / PM review checklist

## Technical delivery evidence

- [x] Twelve original spreadsheets / 155 worksheets inventoried; originals and frozen sanitized hashes verified.
- [x] All 20,432 nonempty source rows preserved with processing outcomes.
- [x] All 43,160 attendance staging records / 24,687 daily P/A marks reconciled, pending and separate from operational reporting.
- [x] Actual 20-table model, 363-column dictionary, full/simplified/flow diagrams and all 103 FK definitions delivered.
- [x] New date/calendar/identity investigation and reproducible gated ETL implemented.
- [x] Eleven unit tests and nine isolated PostgreSQL checks pass; current live FK/payload/security evidence passes.
- [x] Historical execution/receipt evidence retained; originals/credentials/private ledgers excluded from Git.
- [x] Existing data/timestamps/audits unchanged; no new remote writes or schema changes.

## Decisions and controlled implementation

- [ ] Review and approve exact 197-transaction original-date increment (manifest/hash in docs 47); separately authorize execution and date fidelity/disclosure.
- [ ] Supply authoritative child identity crosswalks and independently validate support caregiver-ID lookup suggestions.
- [ ] Approve attendance/service/code, ADL and support event semantics and repeated-view handling.
- [ ] Resolve calendar/chronology conflicts and missing dates; retain irrecoverable evidence explicitly pending.
- [ ] Approve questionnaire scoring, categories and missing-answer policy.
- [ ] Complete extensive senior code review of stacked PRs #1/#2; record actual approving reviews before merge.
- [ ] Decide retention/privacy and pilot role/private-access matrix; separately authorize OAuth and Admin provisioning.
- [ ] Verify live authenticated backend/RLS workflows before any Phase 2 live access.

## Acceptance record

| Review boundary | Reviewer / date | Decision / evidence reference |
|---|---|---|
| Backend architecture, SQL and security | Pending | Pending |
| ETL, data integrity, provenance and recovery | Pending | Pending |
| Proposed original-date recovery scope | Pending | Pending |
| Operational identity and calendar rules | Pending | Pending |
| Questionnaire/ADL/support meaning | Pending | Pending |
| Technical handover acceptance | Pending | Pending |
| Business/operational data acceptance | Pending | Pending |
| Access activation and Phase 2 live dependencies | Pending | Pending |
| PR merge approval | Pending | Pending |

Technical delivery, migration execution, business acceptance and user-access activation are separate approvals. Pending staging is not verified attendance. A PR marked ready for review is neither approved nor merged. See [handover](PHASE1-HANDOVER.md), [live evidence](evidence/phase1-final-delivery-verification.json) and [proposed increment](47-historical-recovery-and-increment.md).
''')
    readme=f'''# Goalkeep KC-2 Integrated Data System

Phase 1 PostgreSQL backend for traceable NGO records, historical evidence and future data-entry/analytics workflows. **Technical delivery is ready for senior review; business-approved historical operational migration remains incomplete.**

Start with the [Phase 1 PM handover](docs/PHASE1-HANDOVER.md) and [senior review checklist](docs/PM-REVIEW-CHECKLIST.md).

## Actual deployed database

Supabase `kc2-integrated-data-system` (`hmlbdozsqxlwzvjimjwh`), Tokyo `ap-northeast-1`, non-production pilot. Tokyo is the owner's documented exception to the original Mumbai standard. Twenty application tables / 363 columns / 103 foreign keys; all RLS enabled. Private entities are restricted. OAuth, memberships and broad application access remain inactive.

![Actual deployed ER diagram](docs/visual/final-deployed-er.svg)

- [Full Mermaid ER](docs/visual/final-deployed-er.mmd), [simplified business view](docs/visual/final-business-relationships.svg), [source flow](docs/visual/final-source-flow.svg).
- [Final data dictionary](docs/FINAL-DATA-DICTIONARY.md), [live counts and complete PK/FK reference](docs/FINAL-TABLE-INVENTORY.md).
- [Actual live verification](docs/evidence/phase1-final-delivery-verification.json), checked {v['checked_at_ist']}.

## Migration status

20,432 source rows; 371 children; 716 caregivers and 716 child-caregiver links; 106 questionnaire responses / 3,286 answer slots; 128 programme slots; 28,293 audit events. All imported projections remain pending business review.

Attendance staging is complete: **43,160 protected pending records**, including **24,687 daily P/A marks**. **Verified operational attendance, ADL visits and support observations: zero.** Names alone do not establish child identity. [Execution](docs/45-attendance-staging-execution-complete.md), [reconciliation](docs/46-attendance-final-source-reconciliation.md).

Original-date recovery is implemented and tested locally. {v['daily_pa_dates_recovered_locally']:,} daily mark dates recovered locally ({v['daily_pa_dates_with_source_conflicts']} conflicting); {v['daily_pa_unresolved_dates']} full dates unresolved. A separately approved [197-transaction date increment](docs/47-historical-recovery-and-increment.md) can restore 106 questionnaire dates and 91 programme dates. **Not executed or authorized.** No attendance batch is replayed.

## Reproducible code and checks

Read [AGENTS.md](AGENTS.md) before work. Install pinned [requirements](requirements-preparation.txt) in a virtual environment. With dependencies installed:

```bash
python -m unittest discover -s scripts -p 'test_historical_recovery.py' -v
python scripts/run_historical_tests.py
git diff --check
```

The runtime runner requires the managed local Docker daemon, creates a digest-pinned **network=none** disposable PostgreSQL database, applies the exact four deployed migrations with synthetic fixtures and removes the container. It accepts no remote database URL. Eleven focused unit tests / nine runtime checks passed. Earlier completed profiling/import tests are retained rather than unnecessarily repeated.

Private source snapshots are required only for `historical_recovery.py` and date-manifest preparation; they are intentionally absent from Git. Those scripts never connect to Supabase. Do not run old loaders or assume a previously approved manifest authorizes new writes. Never reset/repair or reapply deployed migrations.

## Known limitations and review

Authoritative historical child crosswalks, some full dates, event/code meanings, questionnaire scoring and business acceptance remain unresolved. Source-generated caregiver-ID name lookups remain suggestions. Actual source evidence is retained; nothing is silently converted to a child event. [Source mappings](docs/23-source-target-mapping-final.md), [new recovery findings](docs/47-historical-recovery-and-increment.md), [decision register](docs/13-data-quality-decision-register.md).

PR [#1](https://github.com/data-culture-goalkeep/kc2-integrated-data-system-vidhan/pull/1) delivers backend into main; PR [#2](https://github.com/data-culture-goalkeep/kc2-integrated-data-system-vidhan/pull/2) adds attendance and this final delivery on top of the backend branch. They are stacked, not merged. Senior approving reviews are still required. Phase 2 [PR #3](https://github.com/data-culture-goalkeep/kc2-integrated-data-system-vidhan/pull/3) is a separate synthetic-only frontend; no further frontend work or live activation occurs in this task.
'''
    (ROOT/'README.md').write_text(readme)
    print('Wrote handover, senior checklist, recovery increment report and README from verified aggregates.')


if __name__=='__main__':main()
