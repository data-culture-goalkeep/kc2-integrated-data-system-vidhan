# Stage 4B — Supabase migration preflight

Verified 27 October 2026, Asia/Kolkata. **Preflight only: no remote data write or schema change was performed.** The scoped, sanitized pending-record import is technically prepared for owner authorization. All counts below are expected first-run values, not verified remote load results.

## Destination, connection and actual database state

- Exact project: `kc2-integrated-data-system`, reference `hmlbdozsqxlwzvjimjwh`, ACTIVE_HEALTHY.
- Region: Tokyo `ap-northeast-1`, intentionally retained for this non-production internal pilot. This is the explicit owner exception to Goalkeep's Mumbai standard, not an unresolved region choice. Non-production is the owner's designation, not an inferred platform tag.
- PostgreSQL: 17.11, platform build `17.11.0.003`, server_version_num 170011.
- Connection: existing authenticated Supabase MCP integration. OAuth credentials stay in the connector; no token/password/service key was copied, requested in chat, added to environment files or committed. Cloud secret bindings are empty; that does not invalidate the connected MCP account.
- Effective database/session role: postgres, not a superuser, with BYPASSRLS and verified schema USAGE plus SELECT/INSERT/UPDATE on all 19 tables. This is a trusted operator migration mechanism, **not an application-user permission**. It is broader than application access; the destination/manifest allowlist, owner authorization and existing database guards constrain its use. No grants, RLS flags, roles or memberships were modified. The connector default transaction mode is read-write; every preflight query was explicitly read-only. This adapter must never be exposed to application users.
- Actual live counts: **zero in every one of the 19 application tables**, including source, audit, reference and membership tables. The complete live catalog equals the approved reference: 334 columns, 221 constraints, 72 indexes, 81 user triggers, 40 policies, 15 functions; zero differences. RLS remains enabled, with no anonymous table grants or application-role DELETE/TRUNCATE privileges.
- Remote migration versions remain 20261026210941 / 20261026211010 / 20261026211029, named 20261026171200_ids_schema / 20261026171201_ids_security / 20261026171202_ids_integrity. Exact deployed source hashes remain unchanged. No db push/reset/repair or schema migration was executed.

Evidence: [live project/role/counts/ledger](evidence/stage4b-live-preflight.json), [catalog](evidence/stage4b-live-catalog.json), [live bridge](evidence/stage4b-live-bridge.json), [Stage 3 deployment](20-supabase-deployment-report.md).

The prior reviewed advisor findings remain relevant: two WARN entries for guarded authenticated-callable security-definer RPCs and one INFO for the deliberately policy-free private membership table. This preflight did not claim a new clean advisor scan or weaken those controls; activation of users remains separate.

## Source snapshot and import boundaries

All twelve authorized Drive source modified timestamps are unchanged. Protected original-export hashes and all 155 sanitized worksheet JSONL hashes match the frozen Stage 4A snapshot. These are frozen export/sanitized hashes plus fresh Drive metadata checks; no new live formula recalculation is claimed. Originals were not modified and full profiling was not repeated.

The identical plan retains 20,432 nonempty source rows and all 5,186 column coordinates: 1,194 transformed, 15,301 source-only, 3,623 identity-pending, 314 business-pending. Candidate rows, repeated views, summaries, source rows and projected observations remain different grains. No row disappears or is silently deduplicated.

Plan SHA-256: `7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f`.

Code/SQL-batch-bound manifest SHA-256: `8cf2df9dd09a74234b26f1a99c61d17ed7f1f733eca2f016a4f0429c869471b4`.

The manifest binds all 219 exact batch request IDs, SQL hashes, byte lengths, phases, record counts, adapter/bridge/compiler/loader hashes and target/scope. The private plan, original identifiers, pseudonym key, full manifest and record-level exception ledger stay in ignored owner-only work directories. Public evidence contains aggregate counts, sanitized headers and source coordinates only. No raw NGO personal data was sent to Supabase during preflight; live probes used catalog/count reads and synthetic SELECT-generated values.

Included scope: sanitized source preservation, exact verified-ID registries/relationships and literal pending projections. There are 371 unique child IDs, 716 unique caregiver IDs, 716 verified pairs covering 370 children, and 106 verified questionnaire pairs. Sixty questionnaire source-name disagreements remain evidence; canonical names are unchanged. Programme rows are 128 explicitly reported master slots with inactive source-scoped codes and NULL dates, **not validated chronological programme events**. All imported domain records remain pending; no clinical meaning or accepted category is asserted.

Excluded operational facts: attendance, ADL and support matrices, unverified identity links, alternate questionnaire views as additional submissions, ambiguous activity/event grains, calculated scores, operational dates, unverified parent/caregiver crosswalks and withheld sensitive numeric values. Source-only evidence remains preserved. All 2,089 identity candidates remain unapproved. Missing numeric answers stay NULL; no dates, identities, marks or scores are invented. Safe real-data recoveries remain zero.

## Expected database writes

| Table | Direct inserts | Trigger-generated inserts | Updates |
| --- | ---: | ---: | ---: |
| public.reference_values | 47 | 0 | 0 |
| public.children | 371 | 0 | 0 |
| gk_private.child_private_profiles | 371 | 0 | 0 |
| gk_private.caregivers | 716 | 0 | 0 |
| public.child_caregivers | 716 | 0 | 0 |
| public.program_changes | 128 | 0 | 0 |
| public.questionnaire_responses | 106 | 0 | 0 |
| public.questionnaire_items | 31 | 0 | 0 |
| gk_private.questionnaire_answers | 3,286 | 0 | 0 |
| public.attendance_observations | 0 | 0 | 0 |
| public.support_observations | 0 | 0 | 0 |
| public.adl_visits | 0 | 0 | 0 |
| gk_private.source_artifacts | 12 | 0 | 0 |
| gk_private.source_records | 20,432 | 0 | 20,432 |
| gk_private.source_provenance | 5,772 | 0 | 0 |
| gk_private.access_memberships | 0 | 0 | 0 |
| gk_private.identity_candidates | 2,089 | 0 | 0 |
| gk_private.recovery_actions | 0 | 0 | 0 |
| gk_private.record_audit_events | 0 | 28,293 | 0 |
| **Total** | **34,077** | **28,293** | **20,432** |

Total expected inserted rows: 62,370. Total expected row mutations including source-state updates: 82,802. Audit events are generated by installed triggers, never directly inserted by ETL. A successful unchanged replay should insert zero, perform no source-state update and generate no additional history; this was verified locally.

## Adapter and transactional execution

`remote_etl.py` reuses `etl_loader.load_plan`, `ordered_batches`, typed SQL compilation and existing source-status transitions. The only compiler extension is optional receipt aggregation; default Stage 4A compilation remains unchanged. Transaction-local receipt accumulation is returned as one final protocol/request-bound SELECT before COMMIT, after deferred constraints are checked. This avoids relying on intermediate result sets that a connector might discard. Receipts are accepted only when the full tool call succeeds and their request ID, table order, cardinality and inserted flags validate. A tool error or uncertain outcome credits no success and stops the run.

`mcp_etl_bridge.mjs` runs inside the existing tools runtime. Its default mode performs live read-only preflight and never starts a writer. A future authorized run additionally needs explicit write-mode selection and an owner-authorization file; neither was activated here. The file must bind project, plan, manifest, scope, approval evidence and a maximum 24-hour validity interval. Do not fabricate an approval to pass this gate. An authorized future Codex task can create that file from the owner's explicit instruction; the analyst is not asked to write code or handle credentials.

The bridge rechecks exact project/region, migration ledger, full catalog, empty target, local source hashes, Drive versions and failure-destination privacy before starting the worker. Every emitted query is checked against the authorized manifest and current code hashes. SQL and tool responses travel through protected files; only batch IDs/statuses are emitted. No arbitrary SQL, alternate project, DDL, deletion, policy activation or access assignment is part of the adapter. These are operator safety controls, not cryptographic signatures or a sandbox against an operator who can edit repository code.

Ordering: artifacts → source rows → inactive reference values/provenance → children/private profiles → caregivers/relationships → source programme slots → questionnaire items/responses/answers → candidate identities → recovery evidence if justified → source-status finalization. Typed provenance travels atomically with its target; FK and deferred integrity checks remain enabled. Default maximum 250 records per data batch; 137 data transactions and 82 status transactions. Lock timeout 5 seconds; statement timeout 60 seconds. No automatic retry is performed. A durable, fsync-backed metadata journal records each request before submission and each validated acknowledgement; interruptions retain an in-flight recovery anchor without logging SQL or source values.

Live non-destructive probes confirmed final-envelope behavior across BEGIN READ ONLY / COMMIT and a 790,283-byte request with 250 synthetic receipts. Actual maximum compiled batch: 787,875 bytes; total SQL text: 60,827,708 bytes. These probes establish connector format/capacity, **not successful live DML or remote migration performance**.

After a future successful run the bridge performs read-only all-table/audit counts and source-state reconciliation (resolved 1,194; reference_only 15,301; blocked 3,937) and saves the protected live receipt. It must not report completion from source counts alone.

## Tests and final verification

- 64 Python unit/contract tests pass, including 15 adapter approval/destination/protocol/failure tests.
- Nine offline bridge scenarios pass: readonly default, chunked Unicode round-trip, exact destination, changed source, report privacy, catalog drift, altered request destination, tool error and unknown network outcome. No real tools/network exist in these mocks.
- A fresh network=none disposable PostgreSQL 17 instance applied the exact deployed migrations and exercised the complete sanitized bundle through the connector-shaped adapter: 34,077 direct inserts, 28,293 generated audit events, exact target reconciliation, zero replay inserts and unchanged all-table/audit counts. All nine existing adversarial database cases pass. Container removed.
- Actual live bridge preflight, catalog/security comparison, empty-table checks and synthetic read-only protocol/capacity probes pass. No remote write test, dummy insert, membership or Auth user was created.
- Source/privacy, model/mapping/SQL, saved deployment, new manifest/preflight, Python syntax, bridge syntax, documentation links and Git checks are recorded in the final verification receipt. Technical tests do not approve business rules or live Google OAuth/HTTP workflows.

During development, tests exposed bridge syntax/polling issues and a local psql-to-MCP fixture envelope mismatch. These were corrected; final unit, bridge and full database tests pass against the current code hashes. They were local/transport defects, not changes to source values, architecture or business rules. Direct changelog retrieval was blocked by the environment's HTTP policy; supported MCP documentation and actual protocol probes were used. No network-policy bypass or credential workaround was attempted.

## Resource impact and failure recovery

The final local first load took 65.072 seconds; local maximum batch 0.629 seconds, p95 0.534 seconds. Local application relations including indexes/TOAST occupy 55,164,928 bytes, of which audit history occupies 31,703,040 bytes. Physical allocation varies; these are **local measurements**, not reserved remote capacity or a completion-time guarantee. Audit rows contain old/new evidence and source-state updates add 20,432 history events; expect significant WAL/storage work beyond base record counts. Keep auditing enabled.

Remote latency, account quota/headroom, WAL and platform timeouts are not fully benchmarked by readonly checks. Approximately 60.8 MB of compiled SQL and chunked local tool transport add orchestration overhead to 219 remote transactions. Execute sequentially, monitor receipts and resources, and stop on timeout/constraint/transport failure. The fixed snapshot is bounded below the tested payload capacity; new data requires a newly reviewed manifest rather than silently increasing limits.

On any failure or lost response: stop further batches, preserve request IDs, source references, committed receipts and failure evidence. A lost tool response may follow a committed transaction. Do not infer rollback, automatically retry, delete prior commits or rerun everything. Read counts, source states and exact existing payloads first. Normal bridge execution refuses any nonempty target; a partial run requires a reviewed recovery plan and explicit recovery authorization. The reusable loader's strict replay was locally tested, but does not itself authorize replay remotely. Changed payloads or conflicting review states are rejected. No destructive down/reset is offered.

The existing private Google Sheets failure workbook remains the intended destination: twelve source tabs, the required Source file / Row reference / Reason for failure columns and 11,222 metadata-only preparation findings. Its permissions and tab/grid layout were rechecked; it remains owner-only. Findings are not remote load failures. Preserve the protected internal exception ledger and update the same report with actual source-level outcomes only after an authorized run. No sharing or report content was changed in preflight.

## Final authorization requirements

The scoped migration is technically ready for owner review. Before the first remote write, the owner must explicitly authorize this exact project, plan/manifest hashes and preservation/pending projection scope, including the literal pending programme slots and acknowledged exclusions. Fresh live/source checks must still pass at execution time. Any changed artifact invalidates the current approval binding.

No further account creation, password/PAT submission or manual cleaning is required for the connected pathway. Unresolved business decisions continue to block their excluded operational categories; they do not authorize guessed values. Role activation, Google OAuth, final analytical acceptance and any wider sharing remain separate approvals. **No remote migration authorization was granted or consumed during this preflight.**

See [machine preflight checks](evidence/stage4b-preflight-verification.json), [batch manifest summary](evidence/stage4b-batch-manifest.json), [adapter runtime](evidence/stage4b-adapter-runtime.json), [bridge tests](evidence/stage4b-bridge-tests.json) and [source checks](evidence/stage4b-source-verification.json).
