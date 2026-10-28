# Stage 4A — ETL pipeline design

Status: tested preparation; remote loading is not authorized. Target remains `hmlbdozsqxlwzvjimjwh`, Tokyo `ap-northeast-1`, the owner-approved non-production exception to Mumbai. The 19-table deployed schema and three applied migrations are unchanged.

## Components and repeatability

1. Reuse frozen discovery profiles, protected originals and sanitized JSONL snapshots. Verify original SHA-256 and each sanitized worksheet digest. Drive metadata verifies the same twelve sources and 155 sheet IDs/order; original snapshots remain unmodified.
2. `build_etl_mapping.py` produces all-coordinate mapping and worksheet contracts. `run_recovery.py` reuses the existing recovery engine and creates independently extracted source references and unapproved identity candidates. Full profiling is not repeated.
3. `prepare_etl.py` extracts every nonempty sanitized row, strengthens sensitive numeric redaction, resolves exact pseudonymous identifiers, projects literal pending facts and produces a protected deterministic plan plus exception ledger. `etl_core.py` checks types, uniqueness, FK coverage, provenance and independent row coverage.
4. `etl_loader.py` compiles whitelist-only typed SQL and executes through an injected executor. It does not open a connection or read credentials. The only supplied execution CLI, `run_etl_tests.py`, creates a network-disabled disposable PostgreSQL container, applies the exact deployed migrations and removes the container. A separately authorized Stage 4B executor must verify the pinned destination before any remote write.
5. Record-level lineage links operational imports and typed provenance atomically. All imported domain records remain pending. Source-scoped reference definitions remain inactive, with empty permissions. No access roles or memberships are seeded. Database audit triggers generate history; ETL cannot supply audit fields or insert history directly.

## Loading and failure behavior

Stable UUID5 keys use source version/coordinate or exact deidentified business identifiers. No case folding, inferred ID repair or name-based canonical merge is used. Original identifiers remain in protected originals and the existing keyed pseudonym mapping; database business identifiers are sanitized tokens. Preserve the key and private snapshots securely to reproduce the same pilot IDs.

Load order: artifacts, source records, inactive reference definitions, children, private profiles, caregivers, child-caregiver pairs, explicit programme slots, questionnaire items, responses, answer slots, unapproved identity candidates, verified recovery evidence if any. Each operational record and its provenance form one atomic unit. Batches contain at most 250 records by default (hard maximum 500); deferred integrity checks run before commit, with bounded lock/statement timeouts. Final source-state transitions use separate bounded transactions.

Replay uses primary-key conflict detection followed by full supplied-business-payload equality. Changed payloads stop the batch instead of overwriting records. No duplicate history is generated on an unchanged replay. Transaction receipts are counted only after successful commit; a failed batch contributes zero inserts. Previously committed batches remain and must be reconciled before retry. Source finalization rejects conflicting existing review states. Do not globally delete, truncate or reset on failure. Source-version changes require a separately reviewed incremental plan; they are not an automatic rerun of this plan.

## Privacy and unresolved semantics

Only sanitized data enters the local test database. Seven additional sensitive numeric cells are masked in-memory; original and existing sanitized snapshots are not edited. All operational dates are withheld: existing synthetic date shifts do not preserve chronology. Sanitized date evidence stays in source payloads, but is not represented as a real event date. Financial numeric fields are withheld. Parent attributes are not assigned to caregiver identities without an exact crosswalk. Sensitive payloads and plans stay owner-only in ignored `work/`; logs and committed evidence contain aliases, coordinates and aggregate counts only.

No scoring formula, canonical category, attendance identity or clinical interpretation is invented. Attendance, ADL and support matrices are retained without operational projection. Unapproved candidates do not become accepted relationships. Recovery needs verified identity, equivalent field meaning, authoritative consistent donor and an auditable sanitized donor value. Date recovery remains blocked by date fidelity policy; actual automatic recoveries are zero.

## Reproduction

Use the pinned preparation environment. Run `build_etl_mapping.py`, `prepare_etl.py`, `build_failure_report.py`, unit tests, `run_etl_tests.py` and `check_etl_readiness.py`. Refresh the targeted recovery cache only when its inputs or investigation logic change. Keep original snapshots, pseudonym key and private bundles outside Git. See docs 23–26 for coverage, exact test evidence and the gated execution plan.
