# KC2 Phase 1 — Current project context

Updated 27 October 2026, Asia/Kolkata. Stage 3 schema deployed and live-validated; no NGO data or memberships loaded.

The owner subsequently authorized Stage 3 application of only the exact three reviewed SQL migrations. Those migrations are now applied. Migrating NGO records, enabling memberships/broad access/OAuth, further DDL and frontend work remain prohibited without a new authorization. Earlier Stage 1/Stage 2 drafts are preserved in Git and `docs/archive/`; their unresolved identity/location statements are superseded only by the explicit decisions below.

## Confirmed owner decisions and organisational differences

- Exact project: `kc2-integrated-data-system`; Tokyo `ap-northeast-1` intentionally retained for this non-production pilot. This contradicts the original Mumbai technical standard; the latest explicit owner instruction establishes the exception. No alternate project may be used.
- Unique child/caregiver IDs are authoritative business identifiers; internal UUID keys, separate caregiver entities and child/caregiver relationships. Literal local verification confirms 371 unique child IDs, 716 caregiver IDs over 370 child IDs, 106 verified questionnaire pairs. Sixty conflicting questionnaire child names remain source evidence and do not overwrite the master.
- Attendance uses exact verified IDs first; names/aliases/programme are candidate evidence only. Recovery requires verified identity, equivalent field meaning, authoritative donor and no contradiction, with a complete audit trail.
- Google OAuth and verified Goalkeep Workspace `goalkeep.net` identity required for this pilot. Proposed Admin/Member matrix is explicitly draft, not approved for activation. Membership and private access are distinct gates. Future NGO domains require separate approval.
- Guidelines §3/§5/§6 remain organisational requirements; the complete document was read in initial work, but DOCX page rendering was not independently verified. Google Docs context destination, Google Sheet migration-failure log and PM handover remain later obligations. Secure connector/secret bindings override the guideline example of pasting a token into chat.

## Evidence recovered and preserved

12 spreadsheets, 155 sheets, 6,521 candidate rows including views/templates, 145,785 nonempty cells. Full profiling was reused, not repeated. All 12 original and 155 sanitized hashes match frozen evidence. There are 20,432 nonempty rows including headers/formulas/summaries; retention coverage is not an import total. Source coordinates are retained throughout.

The targeted investigation resolved 1,193 explicit child-ID occurrences and 822 caregiver-ID occurrences to the verified registries; seven explicit child-ID occurrences remain unresolved and are privately reported. No conflicting identifier is repaired automatically. Attendance aliases supported by ID-linked sources produce 1,009 one-candidate rows, 74 ambiguous and 1,059 unmatched across 2,142 rows; zero approved name-only links. The prior master-name-only baseline (736/11/1,395) remains valid for its narrower method. No missing values met all safe-recovery conditions, so zero automatic fills occurred. Full protected ledgers and sanitized overlays are in ignored `work/recovery/`.

Known issues remain: 610 attendance marks without recognized date headers; four malformed date headers and seven calendar mismatches; four of 194 checked ADL slots without dates; three DOB/joining conflicts; missing DOB/consent; questionnaire scale/formula uncertainty, 86/2,862 missing numeric answers and one outlier; ambiguous/unparsed dates; activity event grain and category definitions. These are not resolved by technical tests.

## Recommended architecture and prepared artifacts

19 tables, versus the prior 17: defer activity_logs (−1), add identity_candidates, recovery_actions and record_audit_events (+3). Necessary domain entities, scoped reference values, three source-lineage tables and explicit membership remain. Private schema isolates restricted child/caregiver/answer/source/security evidence. Imported targets require typed provenance; questionnaire links validate child/caregiver pairs and definition consistency. Audit history is append-only. No NGO business categories or role definitions are seeded.

Read [final specification](15-final-data-model.md), [dictionary](06-data-dictionary-draft.md), [ER](07-entity-relationship-diagram.md), [recovery design](16-data-recovery-and-reconciliation.md), [connectivity/migrations](17-supabase-connectivity-and-migration-plan.md) and [extensive implementation review](18-implementation-review.md). The complete final mapping retains all 5,186 source-coordinate slots; raw/organized comparisons and previous models remain in docs 09–12/archive.

Prepared migration files cover schema/constraints/indexes, security, and integrity/audit/lineage. At the base-PR review milestone no remote migration or NGO record had been loaded. Stage 3 has since applied the schema only; NGO rows remain absent. Local synthetic tests and live SQL catalog/denial checks now pass; Google OAuth/provider configuration remains unverified.

## Connectivity, verification and next gate

Supabase connectivity is verified through the connected MCP account: exact project kc2-integrated-data-system, reference hmlbdozsqxlwzvjimjwh, Tokyo ap-northeast-1, ACTIVE_HEALTHY, PostgreSQL 17.11. Explicit read-only queries succeeded. The project was empty at preflight; it now has the 19 reviewed tables and three recorded migrations. One accessible organisation/project was returned; no alternate project was selected. Post-deployment advisor findings are documented in docs 20/21, replacing the earlier empty-database scan. No token, password or personal Auth records were retrieved. The secure CLI/API fallback is optional; it writes separate evidence and does not overwrite MCP verification. See docs/evidence/supabase-connectivity.json.

Local preparation checks parse all SQL and PL/pgSQL, compare model/DDL/FKs/mappings/ER and inspect security invariants. Existing discovery/draft-model checks and synthetic regressions remain required. Machine-readable results are in `docs/evidence/preparation-verification.json`, `verification.json`, `model-review-verification.json` and `recovery-preparation.json`. Parser/static/synthetic success is not runtime or business-rule approval.

Repository: `data-culture-goalkeep/kc2-integrated-data-system-vidhan`; branch `feature/phase1-data-backend`. Preserve feature commits, never push to main or merge automatically. Check actual remote status before claiming publication. Stage 3 schema deployment is complete. Next: prepare source mappings/loader/reconciliation for review and obtain separate data-load and role-activation approvals. No further remote application is authorized; real OAuth/REST integration remains unverified.

Permanent standards: Google authentication and server authorization; sticky header/sidebar and collapsed icons; button-triggered Add/Record/Edit forms; supported secret management; extensive first implementation PR review; simplification and preserved raw/organized comparison; reproducible migrations, source reconciliation and automated quality checks. See AGENTS.md and docs 14.

## Publication milestone

GitHub transport recovered through the authorized execution path. Remote main was verified as `5d886cd85a1925d27149f19e5edf8c26bda80e8e`, a common ancestor of the preserved feature history. Preparation commit `403477dad52c5aafc90a49432826f859dba59b5f` was pushed to the new `feature/phase1-data-backend` branch. Draft [PR #1](https://github.com/data-culture-goalkeep/kc2-integrated-data-system-vidhan/pull/1) is open, not merged. The first implementation self-review is in docs 18; independent owner/reviewer approval remains required. At that publication milestone, no database operations or frontend work had occurred. The subsequent review authorized local disposable execution only.

## Base PR review milestone — local runtime verified

Read [current review and readiness](19-base-pr-review-and-readiness.md). The 19-table architecture is retained. Corrected a runtime PL/pgSQL name ambiguity, Member questionnaire-definition writes, excessive service-role grants/TRUNCATE exposure, eligibility-dependent revocation, actor attribution and weak lineage arrays. Hardened duplicate/missing-name handling, independent reconciliation, XML parsing, integrity guards under Python -O and optional fallback evidence. Removed one redundant index. All source evidence remains preserved; no business rule was silently changed.

37 Python tests and 46 PostgreSQL runtime tests pass. Migrations execute on a digest-pinned, network-isolated PostgreSQL 17.11 with synthetic Supabase Auth fixtures; a second fresh replay and transaction rollback tests pass. No real Google login, complete Supabase stack/PostgREST test or NGO load is claimed. Four pinned Python packages show no advisories in queried PyPI metadata. See docs/evidence/postgres-runtime-review.json and dependency-review.json.

At base-PR review the known critical/high defects were fixed and SQL was ready for approval. The owner subsequently authorized Stage 3 and those exact files are now deployed; this does not authorize additional schema changes. The draft role matrix/initial Admin/private grants and real OAuth validation remain separate activation gates. PR #1 remains draft/unmerged; review fixes stay on feature/phase1-data-backend.

## Stage 3 deployment milestone

The exact three reviewed files from PR head 277d4d0 were applied sequentially via Supabase MCP to hmlbdozsqxlwzvjimjwh / Tokyo. Before the first write, remote history/application tables were empty and every file matched PR bytes and local runtime hashes. All three calls succeeded without retries, drops or recovery. Source files are unchanged. See [deployment report](20-supabase-deployment-report.md) and [live validation](21-live-database-validation.md), which supersede earlier preparation-only/empty-database statements.

Live comparison is exact across 19 tables, 334 columns, 221 constraints, 72 indexes, 81 triggers, 40 policies, 15 functions, 399 effective table privileges and 45 function privileges. Eleven live SQL-role denial checks pass. One rollback-only child insert was attempted and rejected; all 19 tables remain empty, including membership/reference/audit evidence. No Auth user, Admin, role definition, NGO record or OAuth/frontend configuration was created. Local 37 Python / 46 PostgreSQL test results remain distinct from live verification.

MCP assigned remote ledger versions 20261026210941 / 20261026211010 / 20261026211029, while ledger names retain the original file timestamps. This metadata difference is fully mapped in deployment-validation.json. It requires a reviewed alignment plan before any CLI db push/reset/repair; no history repair or file renaming was attempted. There is no architecture difference.

The live advisor has one INFO for deliberately policy-free private memberships and two WARN findings for guarded public SECURITY DEFINER RPCs. These are documented reviewed choices, not a claim of a clean advisor scan. Live unapproved callers were denied. Do not add permissive policies merely to remove findings.

Schema implementation is complete and fail-closed. Actual NGO migration is not yet ready/authorized: business mappings and exceptions, sanitized scope, an idempotent loader, rejection log and source-level reconciliation need review and approval. Role-matrix/initial Admin/private grants and Google OAuth/HTTP validation remain separate future gates. Never rerun or edit deployed migration files. PR #1 remains unmerged; preserve the feature history.

The preserved final-model.json and earlier preparation reports are the reviewed source specification/history; their PREPARED status metadata does not supersede actual state in deployment-validation.json and docs 20/21.

## Stage 4A milestone — 27 October 2026

Sanitized ETL preparation is implemented; see docs 22–26. Original snapshots and all 155 sanitized sheet hashes remain intact; connected Drive confirms the same 12 files and worksheet IDs/order. All 5,186 column positions have classified mappings and sanitized retention. The independent original-coordinate ledger reconciles all 20,432 nonempty rows, including headers, summaries, templates and repeated views; 6,521 candidate rows are a different grain.

The protected plan contains 34,077 direct target records, all operational imports pending, plus 28,293 database-generated audit events. Exact IDs establish 371 children, 716 caregivers, 716 child-caregiver pairs covering 370 children and 106 questionnaire pairs. Sixty source name disagreements remain evidence. The 3,286 questionnaire answer slots include 86 missing numeric answers; no score formula is invented. No safe real-data recovery was justified. The 128 programme slots are literal pending reports with NULL dates, not validated chronological events.

Isolated PostgreSQL load/replay passed, nine runtime cases passed, replay inserted zero and changed no audit/table counts. Attendance, ADL and support facts remain unprojected; identity candidates are unapproved. All operational dates are withheld because current synthetic dates do not preserve chronology. Seven additional sensitive numeric cells are masked; sensitive numeric target fields and parent/caregiver crosswalk remain withheld. Full sanitized source rows remain preserved.

Source dispositions: 1,194 transformed; 15,301 source-only; 3,623 awaiting identity; 314 awaiting business rules; zero lost or duplicate dispositions. The owner-private Google workbook has 12 source tabs and 11,222 metadata-only preparation findings, verified by full readback; these are not failed remote loads. Native formatting is configured without a rendered visual review.

Read-only MCP checks reconfirmed the pinned Tokyo project and all 19 remote tables empty. No Stage 4A remote write, access activation or schema change occurred. Docs/evidence/etl-readiness.json and etl-execution-plan.json define the proposed scoped bundle and execution gates. Before Stage 4B: explicit owner authorization and a supported destination-bound executor with fresh source/schema/target checks. Unresolved category, score, date and identity decisions continue to block their operational projections, not preservation. The prior Stage 3 schema milestone remains unchanged.

## Stage 4B preflight — 27 October 2026 (Asia/Kolkata)

The secure remote pathway is prepared, not activated. `remote_etl.py` reuses the existing loader and typed compiler; `mcp_etl_bridge.mjs` uses the active session's authenticated Supabase tools, with no copied tokens or new secrets. Its default live read-only preflight was exercised. Project identity, PostgreSQL 17.11, unchanged three-entry ledger, full catalog/security equality and zero rows in all 19 tables were reconfirmed. The connector executes as privileged postgres (not a superuser); that trusted migration identity has BYPASSRLS, while application privileges/RLS remain unchanged. No application role gains that privilege.

The same twelve Drive versions, protected originals and 155 sanitized hashes match the Stage 4A snapshot; all 20,432 source rows and dispositions are unchanged. The private twelve-tab Google failure destination remains owner-only. Plan SHA remains 7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f. See stage4b-batch-manifest.json for the current code-bound manifest hash and bounded transaction inventory. Expected writes remain planning values, not remote results.

The adapter aggregates receipts in transaction-local settings and returns one bound envelope before COMMIT, avoiding dependence on separate intermediate result sets. A live read-only probe validated the format and a 790,283-byte request/250 synthetic receipt capacity. The actual largest batch is 787,875 bytes; 137 data transactions and 82 state-finalization transactions are prepared. Controlled loading would insert 34,077 direct rows and 28,293 generated audit events and update 20,432 source states; memberships, roles and unresolved operational facts remain excluded.

Execution still needs a new explicit owner authorization bound to exact project, plan, manifest, scope and expiry. No authorization file was created; no write mode was enabled. Failure/unknown commit outcome stops execution; no automatic retry, destructive rollback or reset. An existing partial target blocks normal execution and needs reviewed recovery. Dates, identity decisions, category meanings and questionnaire interpretation retain their exclusions. Doc 27 and the latest preflight evidence distinguish local full-load tests, offline bridge tests and actual live read-only checks.
