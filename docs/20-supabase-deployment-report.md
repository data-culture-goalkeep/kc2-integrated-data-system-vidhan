# Stage 3 — Supabase deployment report

Deployment completed and verified on 27 October 2026 (Asia/Kolkata). The owner explicitly authorized application of the three reviewed migrations to this non-production pilot. No NGO records, role definitions or memberships were loaded, and no OAuth or frontend configuration was performed.

## Target and authorization

- Project: `kc2-integrated-data-system`.
- Reference: `hmlbdozsqxlwzvjimjwh`.
- Region: Tokyo `ap-northeast-1`; intentionally retained by the owner for the internal pilot, overriding the original Mumbai standard. The non-production designation is the owner's designation and repository configuration, not an inferred platform environment tag.
- Reviewed source: PR #1 head `277d4d0236fff9c26ea85cf3bb01b89755cff57a`, feature/phase1-data-backend.
- Integration: authenticated Supabase MCP apply_migration; exact SQL content was passed without editing the migration files.

## Prerequisites verified before the first write

AGENTS.md, project context and the complete current readiness review were read. Project metadata confirmed the exact name/reference/region and healthy PostgreSQL 17.11. Remote migration history, application table inventory and gk_private schema were empty. Git was on the feature branch with the reviewed commit; each file was fetched from that exact PR commit, compared byte for byte and checked against the hashes used by the successful local runtime suite. No critical/high review defect remained unresolved. The deployment integration was available and the owner explicitly authorized this increment.

Each migration was already locally execution-tested with synthetic Auth fixtures. Its table/FK dependencies, RLS, privileges, audit/provenance/recovery/identity structures, once-only ordering and failure recovery were rechecked. Deploying these files seeds no data, approved role definitions or Admin membership, and grants no anonymous application-table access. See [prerequisite manifest](evidence/deployment-manifest.json).

## Applied migrations and immutable source hashes

| Source file | SHA-256 | Remote ledger version | Result |
| --- | --- | --- | --- |
| 20261026171200_ids_schema.sql | `15f862280d9a90fffbf98bdf99b8be774712245a6357ba5c233052b2c3391892` | `20261026210941` | Success; 19 tables and RLS verified before proceeding |
| 20261026171201_ids_security.sql | `996924ab804aac8ba7b9672c941d1b7941fc812150322d45ba9d6e1294879b5c` | `20261026211010` | Success; ledger checked before proceeding |
| 20261026171202_ids_integrity.sql | `5581168a4c6ef61c183552a04474064e44e8bcafdee4bf8e7f1255659cf58abc` | `20261026211029` | Success; final catalog and access validation passed |

MCP generated the remote ledger version IDs. Each remote name retains the original source timestamp, e.g. `20261026171200_ids_schema`. This is a migration metadata difference, not a SQL or architecture change. All three original timestamped files are preserved unchanged. The ordered mapping is in [deployment validation](evidence/deployment-validation.json) and [ledger](evidence/deployed-migration-ledger.json).

**Do not run a plain CLI db push/reset/repair against this project without reviewing this mapping.** CLI version matching would see the original file prefixes and generated remote versions as different. No ledger rows were manually rewritten, no files renamed and no extra migration created. A separately reviewed history-alignment plan is required before switching to a CLI deployment workflow.

## Execution and live results

All three supported migration calls returned success. They ran sequentially; no retry, reset, object drop, dashboard table creation or recovery was needed. No existing application object was overwritten. The final live catalog exactly equals a record-free local reference generated from the approved files on PostgreSQL 17.11.

| Object | Verified live count |
| --- | --- |
| Application tables | 19 |
| Columns | 334 |
| Constraints | 221: 19 PK, 99 FK, 11 unique, 78 CHECK, 14 constraint-trigger records |
| Indexes | 72, including 32 unique indexes |
| User-defined triggers | 81, all enabled |
| RLS policies | 40 |
| Application functions | 15 |
| Effective table-privilege comparisons | 399 |
| Function-execute privilege comparisons | 45 |

All tables have RLS enabled, all constraints are validated and all indexes valid. Source artifacts/records/provenance, candidate identities, recovery actions, restricted child/caregiver/answer data and audit history are present exactly as reviewed. Every application table has zero records after validation, including access_memberships, reference_values and record_audit_events. No source data or approved role was introduced.

See [live database validation](21-live-database-validation.md), [execution results](evidence/deployment-execution.json), [catalog](evidence/live-deployment-catalog.json) and [empty difference report](evidence/deployment-catalog-differences.json).

## Security verification and advisory findings

Eleven live SQL-role denial checks passed, inside an explicit rollback transaction. They cover anonymous reads, absent capabilities for an unapproved identity, restricted-profile protection, operational write rejection, role escalation/registration rejection, direct membership writes, deletion, audit forgery and source-evidence writes. One synthetic child insert was attempted only to verify runtime denial on an otherwise empty database; it was rejected with `Workspace session required`. The transaction rolled back and subsequent counts confirm no record persisted. No synthetic Auth user or application membership was created.

Anonymous roles have zero application-table privileges and no EXECUTE privileges on the 15 application functions. anon, authenticated and service_role have no DELETE/TRUNCATE privilege on any of the 19 tables. The security-definer functions and mutation/truncate/audit/provenance guards match the reviewed definitions; policies were not weakened. Positive authorized-role and audit-event workflows remain separately tested locally; live validation did not create an Admin or activate the draft matrix.

The live security advisor returned one INFO and two WARN findings:

- [0008: RLS enabled without a policy](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy) on gk_private.access_memberships. Deliberate deny-by-default: authenticated clients have no direct table privileges/policies; guarded functions handle the reviewed future workflow.
- [0029: Authenticated-callable SECURITY DEFINER function](https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable), once each for public.gk_register_member and public.gk_manage_membership. Both are intentional reviewed endpoints, with fixed search_path, no anonymous execution, trusted identity/role checks and no current approved roles/memberships. Both denied the unapproved caller live.

These advisories are retained and documented, not described as a clean advisory scan. No policy or function was changed merely to silence them. Reassess the endpoints before enabling actual users. See [advisor evidence](evidence/live-security-advisors.json).

## Failure and rollback procedure

No migration failed. The approved files are transactional and stop on object collision; there is no destructive down/reset. If a future attempt fails, stop writes, inspect both ledger and catalog, determine which earlier transactions committed and preserve evidence. Do not blindly replay the three files or treat a failed tool response as proof that nothing committed. Obtain approval for a concrete recovery before any correction. No such correction was necessary here.

## Readiness and next steps

**The schema is deployed and live-validated; NGO data migration is not yet authorized or fully ready.** Resolve source identity/date/category/scoring decisions, approve the exact source-to-target rules and sanitized loading scope, and prepare/test an idempotent loader, source-level reconciliation and reject log before any data load. Preserve unresolved attendance and questionnaire source conflicts. The organisational per-source Google Sheet failure log remains a later obligation.

Role-matrix activation, initial Admin/private grants and real Google OAuth/provider/HTTP integration tests require a separate increment and approval. No frontend work is included. Before any future schema change, use a new reviewed migration and reverify the exact target; the present authorization does not permit further DDL. PR #1 remains unmerged and its history is preserved.
