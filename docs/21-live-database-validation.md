# Stage 3 — Live PostgreSQL validation

Verified 27 October 2026 (Asia/Kolkata), project `hmlbdozsqxlwzvjimjwh` / `kc2-integrated-data-system`, Tokyo `ap-northeast-1`. This is actual live catalog and SQL-role validation, separate from local synthetic tests. The Tokyo pilot exception to Mumbai is intentional.

## Comparison method

A record-free disposable PostgreSQL 17.11 instance applied the exact three approved files, then the same catalog query was run locally and remotely with search_path=pg_catalog. The complete structures are equal, with **zero schema/architecture differences**. Columns include type, nullability, generated/default expressions and collation; constraints include definitions and deferral/validation flags; indexes/triggers/policies/functions and effective privileges are compared in full. The column sets also match final-model.json and the 19-entity application ER model (managed Auth is excluded).

Sources: [approved manifest](evidence/deployment-manifest.json), [reference catalog](evidence/expected-deployment-catalog.json), [live catalog](evidence/live-deployment-catalog.json), [machine verification](evidence/deployment-validation.json) and [differences](evidence/deployment-catalog-differences.json). The reference builder loads no synthetic operational records.

## Actual application inventory

| Schema.table | Columns | PK | FK | Unique constraints | CHECK | Indexes | User triggers | Rows | RLS |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gk_private.access_memberships | 15 | 1 | 5 | 0 | 4 | 2 | 4 | 0 | enabled |
| gk_private.caregivers | 18 | 1 | 3 | 1 | 4 | 2 | 4 | 0 | enabled |
| gk_private.child_private_profiles | 38 | 1 | 4 | 0 | 3 | 1 | 5 | 0 | enabled |
| gk_private.identity_candidates | 12 | 1 | 5 | 0 | 5 | 4 | 3 | 0 | enabled |
| gk_private.questionnaire_answers | 16 | 1 | 5 | 1 | 6 | 4 | 5 | 0 | enabled |
| gk_private.record_audit_events | 12 | 1 | 2 | 0 | 0 | 1 | 2 | 0 | enabled |
| gk_private.recovery_actions | 22 | 1 | 6 | 0 | 4 | 2 | 3 | 0 | enabled |
| gk_private.source_artifacts | 12 | 1 | 2 | 1 | 3 | 2 | 3 | 0 | enabled |
| gk_private.source_provenance | 24 | 1 | 15 | 0 | 5 | 14 | 3 | 0 | enabled |
| gk_private.source_records | 12 | 1 | 3 | 1 | 4 | 3 | 4 | 0 | enabled |
| public.adl_visits | 16 | 1 | 5 | 0 | 6 | 3 | 5 | 0 | enabled |
| public.attendance_observations | 20 | 1 | 7 | 0 | 3 | 5 | 5 | 0 | enabled |
| public.child_caregivers | 14 | 1 | 6 | 2 | 3 | 5 | 5 | 0 | enabled |
| public.children | 19 | 1 | 6 | 1 | 4 | 5 | 6 | 0 | enabled |
| public.program_changes | 15 | 1 | 5 | 0 | 4 | 3 | 5 | 0 | enabled |
| public.questionnaire_items | 17 | 1 | 4 | 3 | 5 | 5 | 5 | 0 | enabled |
| public.questionnaire_responses | 18 | 1 | 7 | 1 | 3 | 6 | 5 | 0 | enabled |
| public.reference_values | 16 | 1 | 3 | 0 | 8 | 1 | 4 | 0 | enabled |
| public.support_observations | 18 | 1 | 6 | 0 | 4 | 4 | 5 | 0 | enabled |

The inventory totals 19 tables / 334 columns / 221 constraints / 72 indexes / 81 user triggers / 40 policies / 15 functions. Constraint totals are 19 primary keys, 99 foreign keys, 11 unique constraints, 78 CHECK constraints and 14 constraint-trigger records. There are 32 unique indexes, including PK/unique-backed and candidate partial indexes. All indexes are valid, all constraints validated and all user triggers enabled. Exact names, key columns, CHECK expressions, default/generated values and function bodies are retained in the linked catalog, rather than abbreviated into this table.

## Security results

All 399 effective table privileges and 45 function privileges match the approved reference. All tables have RLS. No anonymous application-table grant or anonymous application-function EXECUTE exists. No DELETE/TRUNCATE privilege exists for anon, authenticated or service_role. Private-table policies, soft-delete authorization, immutable evidence, typed provenance, definition/identity protections and server audit stamping match the approved function/trigger definitions. The private membership table deliberately has no direct-client policy.

Eleven live checks passed:

| Check | Live result |
| --- | --- |
| anon_read_denied | passed (42501) |
| unapproved_identity_no_capabilities | passed |
| unapproved_operational_read_zero | passed |
| restricted_child_profile_read_zero | passed |
| unapproved_operational_insert_denied | passed (P0001) |
| direct_membership_write_denied | passed (42501) |
| privilege_escalation_rpc_denied | passed (P0001) |
| unapproved_registration_denied | passed (P0001) |
| authenticated_delete_denied | passed (42501) |
| audit_insert_privilege_denied | passed (42501) |
| source_evidence_write_denied | passed (42501) |

Tests used SQL-session role changes and synthetic claims inside BEGIN/ROLLBACK. No Auth users, role definitions or memberships were created. A single rollback-only child-insert attempt was necessary to verify runtime write denial; it was rejected. Audit insertion/source updates and deletion probes either used zero-row statements or were denied before writing. No TRUNCATE statement was executed live. Afterwards, actual COUNT(*) on all 19 tables returned zero, proving no probe, source record, membership or audit event persisted.

The restriction on dummy/live records means positive audit-event capture and approved-role CRUD were not repeated against the live database. Those were covered by **46 local PostgreSQL tests** during the previous review, whose migration hashes still match exactly. Stage 3 additionally rebuilt a fresh record-free local reference and reran **37 Python tests**. Their success is not labeled live OAuth or HTTP API validation. Current live denial evidence is [live-access-validation.json](evidence/live-access-validation.json).

## Advisories and differences

The live advisor reports one INFO for the intentionally policy-free membership table and two WARN findings for authenticated-callable guarded SECURITY DEFINER RPCs. See the [deployment report](20-supabase-deployment-report.md#security-verification-and-advisory-findings) and [full advisor evidence](evidence/live-security-advisors.json) for remediation links and rationale. No access was broadened or policy weakened to remove warnings. Reassess before activating users.

There are **no deployed schema differences**. The sole migration metadata difference is MCP-generated remote ledger IDs:

| Source file prefix | Remote version | Remote name |
| --- | --- | --- |
| 20261026171200 | 20261026210941 | 20261026171200_ids_schema |
| 20261026171201 | 20261026211010 | 20261026171201_ids_security |
| 20261026171202 | 20261026211029 | 20261026171202_ids_integrity |

Do not use CLI db push/reset/repair blindly: the file-prefix/remote-version mapping must be reviewed before changing deployment workflows. No manual ledger repair or original-file rename was performed. All three reviewed files retain the hashes in the deployment manifest.

## Remaining boundaries

The database structure and fail-closed foundation are verified live. Loading NGO records still needs approved semantic mappings, sanitized scope, duplicate/error handling, an idempotent loader, source-to-target reconciliation and explicit load authorization. Draft role activation, initial Admin/private grants and real Google OAuth/provider/REST tests remain separate. No frontend, role activation or NGO migration occurred.
