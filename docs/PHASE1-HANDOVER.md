# Goalkeep KC-2 — Phase 1 Technical Handover

Prepared for senior Goalkeep and PM review. Live database evidence checked **28 October 2026, 11:05 IST**. Repository: `data-culture-goalkeep/kc2-integrated-data-system-vidhan`.

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
| S01 | 7 | 219 |
| S02 | 14 | 420 |
| S03 | 12 | 1,040 |
| S04 | 14 | 465 |
| S05 | 8 | 993 |
| S06 | 14 | 183 |
| S07 | 16 | 444 |
| S08 | 14 | 536 |
| S09 | 14 | 331 |
| S10 | 14 | 236 |
| S11 | 16 | 185 |
| S12 | 12 | 1,469 |

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

Sanitization replaced datetime cells with unrelated pseudodates and formulas with markers. The unchanged originals still contain recoverable calendar evidence. Of 24,687 actual daily P/A marks, **24,087** now have locally recovered source dates, including exact observed LET/DATE/SEQUENCE calendar reconstruction and consensus-checked repeated grids. **27** of those dates have calendar/weekday conflicts; **600** marks still lack a reliable full date. Thus **627** daily marks retain unresolved/conflicting date gates. These are local recovery results, not live date updates.

Only explicit source year/month plus original full-date anchors can establish a day-only calendar. Any disagreeing anchor rejects grid reconstruction. Leap years, invalid dates, month boundaries, formula dependencies/cycles and ambiguous numeric formats are tested. Weekdays are derived from recovered dates; disagreeing source labels remain evidence. No arbitrary century, Excel serial or malformed date correction is guessed.

## 12. ADL, support and programme history

ADL: 194 true visit slots across 1,219 roster rows; **190 original dates recovered**, four missing. No independently verified child identifier exists in those slots, so no ADL event is inserted. Nullable dates do not waive identity requirements.

Support: 1,572 participation marks, 1,018 original full-date headers recovered; other headers often specify only an event/month. Event/participant/code meanings remain unapproved. The source contains 110 caregiver-ID formula cells: 102 cached IDs match the registry and 92 lookup names are unique, but the sole lookup input is a person's name. These are prepared source-defined suggestions requiring independent NGO confirmation, not automatic verified mappings. Another 784 attendance identity formulas reference names without independent child IDs. All formula evidence is retained privately.

Programme: 128 source slots already exist pending, all with NULL dates. Of the original date candidates, 91 pass exact-ID/date/chronology gates, seven conflict, and 30 lack a safe full-date recovery. Questionnaire: all 106 existing verified-pair responses have recoverable original assessment dates. Prepared date updates leave every review state pending and do not approve programme categories, questionnaire scoring or events.

## 13. Actual database migration results

| Table | Actual live rows |
|---|---:|
| `public.children` | 371 |
| `public.adl_visits` | 0 |
| `gk_private.caregivers` | 716 |
| `public.program_changes` | 128 |
| `public.child_caregivers` | 716 |
| `public.reference_values` | 47 |
| `gk_private.source_records` | 20,432 |
| `public.questionnaire_items` | 31 |
| `gk_private.recovery_actions` | 0 |
| `gk_private.source_artifacts` | 12 |
| `public.support_observations` | 0 |
| `gk_private.source_provenance` | 5,772 |
| `gk_private.access_memberships` | 0 |
| `gk_private.identity_candidates` | 2,089 |
| `gk_private.record_audit_events` | 28,293 |
| `public.attendance_observations` | 0 |
| `public.questionnaire_responses` | 106 |
| `gk_private.questionnaire_answers` | 3,286 |
| `gk_private.child_private_profiles` | 371 |
| `gk_private.attendance_import_staging` | 43,160 |

The original preservation migration inserted 34,077 direct rows and generated 28,293 audit events; attendance added 43,160 staging rows without modifying existing audits. Those are different grains. This finalization task executed **zero remote writes**. The proposed 197 date transactions would add 197 recovery actions and 197 typed provenance rows and generate 197 new audits if separately approved; these are planning expectations, not live results.

## 14. Data-quality findings

Unknown identity, dates and event meanings remain separate blockers. Precise row/cell evidence, original values, candidate UUIDs, recovered dates, formula dependencies, conflicts and required decisions are stored in ignored `work/historical-recovery/`. The existing private source/staging tables already preserve the corresponding source evidence; no extra staging table is needed. Safe aggregate results are committed in [original recovery evidence](evidence/historical-original-recovery.json).

Do not promote a unique name match, interpret a support participation mark as child presence, convert a summary into an event, treat a formula/context as a literal mark, or compare unrelated source-row and event counts. Duplicate source coordinates are zero; alternate views remain preserved, not falsely certified as distinct events. True cross-view event deduplication is pending verified identity/grain.

## 15. Source reconciliation

| Evidence dataset | Candidate cells/rows/slots | Original dates recovered locally | Dates unresolved | Exact verified ID candidates | Eligible new events |
|---|---:|---:|---:|---:|---:|
| adl_visit_slots | 194 | 190 | 4 | 0 | 0 |
| annual_attendance_summary | 2,564 | 0 | 2,564 | 0 | 0 |
| daily_attendance | 24,876 | 24,087 | 789 | 0 | 0 |
| historical_visits | 155 | 153 | 2 | 0 | 0 |
| support_attendance | 1,572 | 1,018 | 554 | 0 | 0 |
| support_event_summary | 30 | 14 | 16 | 0 | 0 |
| visit_activity_log | 145 | 103 | 42 | 0 | 0 |

These denominators are intentionally dataset-specific. Daily candidates include 24,687 literal marks and 189 formula cells. Annual and support summaries are aggregate evidence, not individual events. Some activity/summary rows also carry preserved auxiliary cells, so this ledger is not a count of distinct business events. Every eligible projection still requires identity, grain and meaning gates; **newly verified operational identity mappings: 0**. Earlier 1,009 provisional / 74 ambiguous / 1,059 unmatched daily roster classifications remain candidates, not approved identities.

## 16. Testing evidence

**11 focused synthetic unit tests** and **9 isolated PostgreSQL checks** passed. Runtime applies the exact four deployed migrations in a digest-pinned network=none throwaway container; the container was removed. Checks cover calendar reconstruction/ambiguity, exact identifiers, nullable ADL/support dates, gated literal attendance, deterministic replay, conflicting updates, foreign keys, lineage, transaction rollback, audit generation, unchanged sources, private-data denial and inactive memberships. Unit tests exercise expiry/hash binding, lost/invalid acknowledgements, ordering and receipt tamper detection.

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
4. Approve the precise original-date fidelity/disclosure scope and incremental manifest **`a3a4c2478dfc2f4786d253e5c63bbf741d4025940f122d562a5b371585cc1b3e`** before its 197 updates and associated evidence/audits are executed.
5. Approve questionnaire scoring/missing-answer/category definitions separately; no formulas have been invented.
6. Approve retention/private access, role matrix, OAuth activation and final PM business acceptance separately. The optional organisational Google Docs context-sync destination remains unspecified; Markdown handover is complete.

## 21. Phase 2 dependencies

No further Phase 2 development in this task. PR #3 remains synthetic-only and unmerged. Before live integration: approve role/private-data matrix and Admin provisioning, configure Google OAuth securely, implement approved backend private-data access, validate actual authenticated HTTP/RLS behavior, and preserve pending-vs-verified separation. Historical identity/meaning decisions block only the corresponding operational features; they do not transform staging into accepted data.

## 22. PM review and acceptance checklist

Use [PM review checklist](PM-REVIEW-CHECKLIST.md). Senior review should examine the combined ancestry of PR #1 (backend → main) and PR #2 (attendance/final delivery → backend), review the original-date manifest and unresolved decisions, then record technical acceptance separately from business/operational acceptance and access activation. PRs #1/#2 have no approving review recorded at preparation; neither is merged. Historical execution evidence is preserved. **Technical delivery is ready for review; full operational/business acceptance remains blocked by the explicit evidence gaps and new execution approval.**
