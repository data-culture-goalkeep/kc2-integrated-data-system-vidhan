# Stage 4C — Authorized recovery execution

**Recovery succeeded within the approved sanitized preservation/pending-record scope.** All 179 remaining transactions are acknowledged and actual live PostgreSQL reconciliation passes. No original data transaction 0–39 was replayed. No schema, permissions, memberships, OAuth or frontend change occurred.

## Authorization and target

Exact destination: kc2-integrated-data-system / `hmlbdozsqxlwzvjimjwh`, Tokyo `ap-northeast-1`, PostgreSQL 17.11. The owner designates this a non-production internal pilot and explicitly retains Tokyo as the exception to Mumbai.

Owner approval: conversation message “Goalkeep KC-2 — Stage 4C: Authorized Migration Recovery Execution”. Approval first observed by the clock tool at **2026-10-27T07:49:56+00:00**, expires **2026-10-27T11:49:56+00:00**; four hours, never extended. The protected artifact binds destination, all four approved hashes, source scope, owner reference and window. Adapter started 2026-10-27T07:51:06.338Z; completed 2026-10-27T08:53:35.982Z, within that window. The authorization is now archived/inactive; credentials and the full journal remain private.

Recovery manifest: `bfbc196c3f718a9bc8de49619031424955fcf8385d2c893a732b5853b995ec92`. Original plan: `7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f`. Original execution manifest: `8cf2df9dd09a74234b26f1a99c61d17ed7f1f733eca2f016a4f0429c869471b4`. Recovery planning: `4fc7f1d0d35443d1d3f80445883924676f6b91563291ff2344717165c6d2022e`.

Before writing, fresh MCP checks verified project/name/region/version, all 19 tables and complete schema/security, ledger, no active import, exact 12-artifact/9,988-staged-row prefix and immutable metadata. Source hashes, all packets/SQL, 40 receipts, code and expiry matched; the failure destination was owner-private. The original initial-load guard was not bypassed.

## Actual execution

Executed original data indices 40–136 (97 transactions), then source-status 0–81 (82). All **179/179** received validated commit receipts; **zero failed or uncertain requests** and zero retries. Earlier 40 commits are preserved, accounting for all 219 original transactions. Additional direct inserts: **24,077**. Final direct rows: **34,077**. Generated audit rows: **28,293**. Source updates: **20,432**. These are verified live results, separate from earlier local simulations.

The reviewed immutable loader/SQL, deterministic IDs, transaction boundaries, compressed SHA-verified packets, constraints and audit triggers were used unchanged. The private hash-chained/fsynced journal binds all request IDs and receipts; SHA-256 `69563a40b2f0030333ae551b255aa42678006c8f4dc73585dcb25e3e7b8fbb83`. No recovery failure required a further approval or corrective database write.

A local reconciliation reader initially retained the MCP `reconciliation` result-column wrapper. Unwrapping that captured result fixed the verification-reader mismatch; the checks then passed without another SQL execution or any data change. This was not a database transaction failure.

Evidence: [execution verification](evidence/stage4c-execution-verification.json), [times](evidence/stage4c-execution-times.json), [live reconciliation](evidence/stage4c-final-live-reconciliation.json), [live security](evidence/stage4c-final-live-security.json), [catalog](evidence/stage4c-final-live-catalog.json), [failure-report receipt](evidence/stage4c-google-recovery-report.json).

All original source rows remain accounted for, but operational/business approval is not complete. See [reconciliation](35-final-migration-reconciliation.md) and [data-quality follow-up](36-post-migration-data-quality.md). Stop here for Phase 1 Final QA; PR #1 remains draft/unmerged.
