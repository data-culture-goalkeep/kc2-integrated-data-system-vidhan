# Stage 4C — Final live migration reconciliation

**Actual live verification passed.** This report supersedes earlier interrupted counts for current state while preserving those historical reports. Exact project `hmlbdozsqxlwzvjimjwh`, Tokyo pilot.

## Actual table inventory

| Schema.table | Live rows |
| --- | ---: |
| gk_private.access_memberships | 0 |
| gk_private.caregivers | 716 |
| gk_private.child_private_profiles | 371 |
| gk_private.identity_candidates | 2,089 |
| gk_private.questionnaire_answers | 3,286 |
| gk_private.record_audit_events | 28,293 |
| gk_private.recovery_actions | 0 |
| gk_private.source_artifacts | 12 |
| gk_private.source_provenance | 5,772 |
| gk_private.source_records | 20,432 |
| public.adl_visits | 0 |
| public.attendance_observations | 0 |
| public.child_caregivers | 716 |
| public.children | 371 |
| public.program_changes | 128 |
| public.questionnaire_items | 31 |
| public.questionnaire_responses | 106 |
| public.reference_values | 47 |
| public.support_observations | 0 |

Direct rows total **34,077**, excluding **28,293** trigger-generated history rows. No manually inserted audit rows, memberships, attendance, ADL or support facts exist. All imported operational projections remain pending, references inactive, dates NULL and identity candidates unapproved.

## Source and audit reconciliation

All **20,432** source rows have one final status: resolved **1,194**, reference_only **15,301**, blocked **3,937**. Planned dispositions remain distinct: transformed **1,194**, source-only **15,301**, identity-pending **3,623**, business-pending **314**. Blocked combines the last two; it is not a data-loss count. The complete protected row-level outcome ledger is `work/stage4c/final-source-execution-outcomes.json`, outside Git.

The source-coordinate digest and every table key/payload/status digest equal the approved plan/reference. No duplicate source coordinates or IDs, silent loss, missing provenance or invalid questionnaire/child-caregiver links were found. **99 modeled FK checks have zero violations.** Literal source-to-target child/caregiver identifiers and canonical names reconcile; questionnaire name disagreements stay source evidence.

Audit history totals **28,293**: the exact planned per-table INSERT history plus **20,432 source-record UPDATE events**. Audit before/after content, operation/key uniqueness, backend actor attribution and original status transitions reconcile. Existing 9,988 rows changed only as permitted: approved source-state and mutable audit fields. Their IDs, original payloads, coordinates, diagnostics and creation metadata, and all 12 complete artifact rows, match the pre-execution immutable anchor.

Full live source/FK checks: [aggregate evidence](evidence/stage4c-final-live-reconciliation.json). Final full payload checkpoint: [digests](evidence/stage4c-final-live-checkpoint.json). Existing prefix preservation: [anchor](evidence/stage4c-final-live-anchor.json). Counts and transaction receipts: [verification](evidence/stage4c-execution-verification.json).

## Security and architecture

No differences from the approved complete catalog: 19 tables, 334 columns, 221 constraints, 72 indexes, 81 user triggers, 40 policies and 15 functions. The existing three migration ledger entries are unchanged. RLS and effective table/function privileges equal the deployed reference. Anonymous reads are denied; an unapproved authenticated SQL session sees zero rows in 18 selectable tables, now including populated registries/profiles/source/audit evidence. Memberships and access-role definitions remain zero. No security policy was weakened to load data. These are live SQL-role checks, not Google OAuth/PostgREST end-to-end validation.

All 179 recovery batches and the earlier 40 are accounted for. Stage 4B is complete **within the authorized preservation/pending-record scope**, not a claim that all NGO observations are ready for analytics or user access.
