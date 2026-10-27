# Attendance continuation — stopped on a confirmed timeout

**Live import is incomplete: 173 committed batches, 34,600 pending staging records.** Original batch 172 committed; batch 173 failed and did not commit. No later batch ran, no request was retried and no outcome remains uncertain. Original indices **173–215**, comprising **43 transactions / 8,560 records**, remain outstanding.

## Authorization and actual execution

The owner directly authorized only 172–215 under original import manifest `911c47968c61fb19a0227e0ab86eae2937dec2e673b9b94c4713ed08bb3ab4ed` and continuation plan `e137a5008ea428acf0e045386f464c5546f6500884f5e282bfa79d55c3ae9a6f`. Approval was first observed **27 October 2026, 23:35:56 IST**, expiring **28 October, 03:35:56 IST** (18:05:56–22:05:56 UTC). No independent platform receipt timestamp was exposed; this earliest clock observation is the recorded basis. The window was never extended, and authorization is now inactive following the failure.

Fresh read-only preflight matched the exact Tokyo non-production project `hmlbdozsqxlwzvjimjwh`, all 20 tables, four migration entries, original-table fingerprints, all 34,400 staged payloads, source snapshots/code/packets and no active import. The initial 172 transactions were not replayed and no migration was reapplied.

Index 172 committed, adding **200 rows**. Index 173, request `e3c83fd3b3c3d4b7537108bf2686638e7b9d1cb39de9b6456d6108dc772bcbef`, failed with **PostgreSQL `57014: canceling statement due to statement timeout`**, at the inline replay guard's `IF`. The failure receipt was saved at **23:40:39 IST on 27 October**. The executor immediately stopped. Raw receipts, hash-chained journal and inactive authorization remain private under ignored `work/attendance-prefix172/`.

## Independent live reconciliation

| Measure | Actual live result |
| --- | ---: |
| Commits in this continuation / failed requests | **1 / 1** |
| Total committed batches | **173 / 216** |
| Staging rows | **34,600 / 43,160** |
| Daily literal P/A marks | **21,103 / 24,687** |
| Literal marks including support | 22,675 |
| Formula / summary / context records | 189 / 2,204 / 9,532 |
| Cell candidates / represented sheets | 25,068 / 80 (potentially partial) |
| Verified operational attendance | **0** |
| Duplicates / source-header disagreements / invalid references | **0 / 0 / 0** |
| Active imports, including aborted transactions / uncertain outcomes / retries | **0 / 0 / 0** |

All exact keys and full business payloads match the **first 173 original batches** across 256 hash buckets; there are no extra/missing records within that committed prefix. This independently establishes that failed batch 173 rolled back. The remaining 8,560 records are explicitly unexecuted work, not a claimed complete import.

All live rows remain review- and code-pending. Among 25,068 cell candidates, identity classifications are 13,736 provisional, 519 ambiguous and 10,813 unmatched. Date classifications are 21,048 sanitized-untrusted, 383 unresolved-formula headers, 3,628 unparsed and nine missing. Verified child references and parsed dates are NULL. Context-only rows are counted separately in [machine evidence](evidence/attendance-continuation-timeout-report.json). No identity, business date, code meaning or operational fact was invented.

Every original table's complete-row aggregate fingerprint and count is unchanged, including **20,432 source records and 28,293 audits**. All prior 34,400 staging rows **including creation/update timestamps** are unchanged. The complete schema, constraints, RLS, grants, functions, triggers and ledger match preflight exactly. Live anon/authenticated/service_role reads are denied. Memberships, OAuth, ADL/support and operational attendance remain inactive/empty. No source record or audit event was modified.

## Diagnosed performance defect and safe next step

The failing replay guard correlates incoming rows using `IS NOT DISTINCT FROM` across the full payload. Read-only `EXPLAIN` shows a sequential scan/materialization of the staging table for an anti-join. A proposed redundant primary-key equality changes the plan to probe the **existing primary-key index**, while retaining every original null-safe payload comparison. Estimated plan cost changes from 769,561.04 to 235.30; these are planner estimates, **not execution timings**. The actual error context confirms the timeout was inside this guard.

No fix or timeout increase was applied remotely. A separate proposal was tested locally on the exact schema and sanitized 34,600-row fixture: all 43 amended batches loaded, all 43,160 final keys/payloads reconciled, replay/conflict/privacy guards passed, original data/timestamps/audits remained unchanged and the disposable container was removed. Eight integration checks and four focused unit tests pass. Slowest amended batch: **0.262 seconds locally**, with the original **60-second limit unchanged**. This does not promise the same remote latency.

The original SQL/loader/manifests remain immutable. Because the proposed SQL bytes differ, the existing approvals cannot authorize them. See the [exact indexed-tail proposal and new manifest](44-attendance-indexed-guard-amendment.md). Do not replay 0–172, restart the original load, raise timeouts, change schema/permissions or retry 173 automatically. PR #2 records the partial result and proposed fix; all PRs remain unmerged. Attendance staging migration is **not complete**, and no live frontend integration is authorized.
