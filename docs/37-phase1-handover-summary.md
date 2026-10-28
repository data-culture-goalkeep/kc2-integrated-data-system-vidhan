> Historical milestone preserved. Current deployed 20-table model and final results: [Phase 1 handover](PHASE1-HANDOVER.md), [final dictionary](FINAL-DATA-DICTIONARY.md), [actual ER diagram](visual/final-deployed-er.svg).

# Phase 1 — Fast-track handover

Verified 27 October 2026, 17:57 IST. Exact project **kc2-integrated-data-system / hmlbdozsqxlwzvjimjwh**, Tokyo `ap-northeast-1`, PostgreSQL 17.11; owner-designated non-production pilot. Tokyo is the explicit exception to Mumbai. **The deployed backend and approved preservation/pending-record migration are complete. Business-approved operational data and application access are not complete.** No new remote write or migration batch was executed in this handover.

## View the model

- [Full deployed ER diagram](visual/deployed-er.svg): all 19 tables; peach marks restricted entities, blue public entities remain RLS protected. Managed Auth is outside the application count. SVG lines group parallel FKs and bundle common actor links into the Auth note; [exact Mermaid](visual/deployed-er.mmd) and [all primary/foreign keys](visual/deployed-keys.md) preserve all 99 constraints.
- [Simplified business relationships](visual/business-relationships.svg): child → caregiver link → questionnaire → answer; programme slots and unresolved candidates shown separately.
- [Spreadsheet-to-Supabase flow](visual/spreadsheet-to-supabase.svg): originals → sanitized snapshot → source retention → pending projections or preserved exceptions → provenance/audit.
- [Safe inspection and preview guide](visual/data-preview.md), using the existing authenticated Supabase project dashboard; no public preview or RLS change.

## Current live inventory

| Table | Rows | Boundary |
| --- | ---: | --- |
| `gk_private.access_memberships` | 0 | Restricted |
| `gk_private.caregivers` | 716 | Restricted |
| `gk_private.child_private_profiles` | 371 | Restricted |
| `gk_private.identity_candidates` | 2089 | Restricted |
| `gk_private.questionnaire_answers` | 3286 | Restricted |
| `gk_private.record_audit_events` | 28293 | Restricted |
| `gk_private.recovery_actions` | 0 | Restricted |
| `gk_private.source_artifacts` | 12 | Restricted |
| `gk_private.source_provenance` | 5772 | Restricted |
| `gk_private.source_records` | 20432 | Restricted |
| `public.adl_visits` | 0 | RLS protected |
| `public.attendance_observations` | 0 | RLS protected |
| `public.child_caregivers` | 716 | RLS protected |
| `public.children` | 371 | RLS protected |
| `public.program_changes` | 128 | RLS protected |
| `public.questionnaire_items` | 31 | RLS protected |
| `public.questionnaire_responses` | 106 | RLS protected |
| `public.reference_values` | 47 | RLS protected |
| `public.support_observations` | 0 | RLS protected |

Totals: **34,077 direct rows + 28,293 generated audit events**; all 219 original transactions accounted for. All 20,432 source rows retained: resolved 1,194, reference-only 15,301, blocked 3,937 (identity 3,623 + business 314). Resolved means source processing, not business acceptance. Source-only includes headers, summaries and repeated views; never compare these grains to people or observations.

Internal UUIDs are relational keys; child/caregiver business IDs remain unique. Child profiles are one-to-one with children; children and caregivers join through child_caregivers. Responses reference that verified pair, and answer/definition composite FKs prevent mixing form versions. reference_values uses `(vocabulary, code)`. Source artifacts/rows/provenance retain file-sheet-row-column lineage. Audit history is append-only; JSON record keys in audit events are not invented domain FKs.

## Remaining operational imports

**Additional records eligible now: 0 verified, 0 safely pending.** All uncertain rows already exist in restricted source storage, so this is not data loss. The local [gate analysis](evidence/phase1-operational-eligibility.json) independently checked the frozen sanitized snapshot without reopening/reprofiling workbooks. No name-only candidate was promoted.

| Dataset / grain | Available evidence | Additional safe import | Decision or evidence needed |
| --- | --- | ---: | --- |
| Daily attendance roster rows | 2,142: 1,009 single candidate, 74 ambiguous, 1,059 unmatched | 0 | Verified ID crosswalk; trustworthy per-mark calendar; approve service/mark codes. Attendance date is NOT NULL; pending cannot waive it. |
| ADL roster rows / checked slots | 1,219 roster rows; 194 true slots, four without dates; zero verified literal-ID rows | 0 | Approve exact child crosswalk and true-slot semantics. Nullable visit_date permits explicit pending NULL only after identity/grain is verified. |
| Support attendance rows | 262: 249 single candidate, six ambiguous, seven unmatched | 0 | Exact child crosswalk and per-event grain/value mapping. Required child_id/event_reference cannot be invented. |
| Other support/activity/history rows | 15 support summaries + 144 activity rows + 155 historical rows (314 business-pending) | 0 | Approve source grain, identity and actual observation meaning; aggregate counts are not invented child events. |
| Programme source slots | 128 already migrated pending with NULL dates | 0 new | Date-fidelity policy and category/history meaning; no replay, no invented effective dates. |
| Questionnaire primary form | 106 responses / 3,286 literal answer slots already migrated pending | 0 new | Approve scoring, missing-answer policy, form/category meaning and dates. 29 subset rows + 84 view rows are not new submissions. |

A single name candidate is not a verified identity. All attendance/ADL/support typed tables require a child FK; neither pending status nor a NULL date creates identity evidence. The 190 ADL slots with reported dates are not chronologically trusted: sanitized date fidelity remains unapproved. No acceptance is inferred from syntactic date parsing.

**Ready preparation:** a private row-level gate ledger reconciles 4,518 candidate rows across prioritized datasets and related views. It retains source record IDs/coordinates and blockers. Reuse existing `etl_core` validation/UUID/compiler and `Builder.project` typed provenance after gates are resolved; deterministic observation IDs must include source record ID and actual source cell/slot. Validate against existing keys, use bounded transactions and a new destination/scope-bound incremental manifest. Do not reuse the consumed initial-load or recovery authorization, change the schema, or run an import with unresolved facts.

## Security and frontend readiness

The 19-table schema, RLS, privileges and triggers exactly match the deployed reference. Fresh counts, key/source reconciliation, duplicate checks and all 99 FK checks pass; prior 82 Python/isolated recovery/security tests were reused rather than repeated. See [lightweight live evidence](evidence/phase1-handover-live.json). No policy, membership or OAuth configuration changed.

**Ready for frontend scaffolding and contract work**, using synthetic fixtures and existing schema. **Authenticated live-user workflows are not ready to activate:** separately approve the pilot role matrix/private-data permissions and designated Admin provisioning; configure Google OAuth for verified Goalkeep Workspace `goalkeep.net` identity; verify server eligibility/session/membership enforcement and real HTTP/RLS behavior. A domain suffix alone must never grant access. No service-role credentials belong in the browser. Restricted tables need an approved backend/Data API access path; do not expose gk_private broadly.

Before operational data-entry/analytics acceptance, approve each relevant date/vocabulary/event/identity rule; unrelated synthetic UI scaffolding need not wait. Approve scope and credentials through supported secrets, and retain sticky header/collapsible icon sidebar, button-triggered forms and consistent responsive components. No frontend was built here. PR #1 remains subject to required review; no automatic merge.

## Quality limitations and handover gates

Sixty questionnaire source-name conflicts remain evidence, 86 numeric answers are missing, and one known answer outlier is retained for review. Attendance header/calendar issues (610 marks without recognized headers, four malformed headers, seven calendar mismatches), four missing ADL dates and three birth/joining chronology conflicts remain unresolved. Zero dates, scores or missing values were fabricated. Categories are inactive and all imported projections pending.

PM/owner next actions: approve scoped exact identity crosswalks and date policy first; questionnaire interpretation/category meanings separately; role/OAuth activation separately. Google Docs context-sync destination and final PM acceptance remain outstanding organisational handover items. Current Markdown context, model, mappings and private failure report are available; raw sources/private ledgers stay outside Git. Complete execution/reconciliation history is in [34](34-recovery-execution-report.md), [35](35-final-migration-reconciliation.md) and [36](36-post-migration-data-quality.md).
