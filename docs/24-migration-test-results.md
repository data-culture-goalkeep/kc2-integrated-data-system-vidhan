# Stage 4A — Migration test results

Evidence: [local runtime](evidence/etl-runtime-tests.json), [preparation/reconciliation](evidence/etl-preparation.json), [readiness checks](evidence/etl-readiness.json). Test bundle SHA-256: `7f96ad770c792286a798d588a2a59550c4c0719a802d3ed9884b826d400aa25f`.

The isolated PostgreSQL 17.11 test database applied the exact three deployed migrations, including constraints, audit triggers and deny-by-default security foundations. It used the pinned Docker image, no network or published ports, sanitized pilot data and synthetic negative fixtures. It was removed after testing. This is successful **local database execution**, not remote data loading or a live Google/OAuth test.

First load passed: 137 data batches, 34,077 direct records plus 28,293 generated audit events. Every expected target count matched. Source status finalization passed for all 20,432 retained rows. Replay verified all 34,077 existing payloads, inserted zero records and left all 19 table counts, including audit history, unchanged.

Nine runtime cases passed: invalid FK rolls back the entire batch; prior committed batches survive a later failure; changed existing payloads are rejected; quoted/backslash input round-trips without SQL injection; deferred operational categories remain empty; all 371 canonical child names remain unchanged; imported children have lineage; 86 missing numeric answers remain NULL; no roles, memberships or active reference definitions are created.

All 49 Python unit tests passed. They cover deterministic IDs, exact identifier distinctions, forbidden targets/audit forgery, JSON NULL, numeric validation, duplicate/source-row reconciliation, guarded sanitized recovery. Existing discovery/model/preparation/deployment checks remain required; their final results are recorded in readiness evidence. Prior Stage 3 security tests are historical evidence, not newly executed live positive-role tests.

Remote Stage 4A inspections use read-only project metadata and counts. All 19 remote application tables remain empty; no remote loading, schema change, access activation or denial-insert probe was run. See [remote read-only receipt](evidence/etl-remote-readonly.json).

Final checks passed: original/sanitized hash and privacy verification; archived model comparison; current model/SQL parser and mapping checks; saved live-deployment consistency; ETL readiness; Python compileall; Markdown links; Git whitespace and fsck. [Verification receipt](evidence/etl-verification.json) binds current code hashes. The 46 existing PostgreSQL security cases are prior unchanged-schema evidence and were not rerun in Stage 4A.
