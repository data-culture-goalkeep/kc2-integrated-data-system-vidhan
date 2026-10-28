# Attendance import — verified checkpoint, incomplete

**Historical checkpoint.** A later authorized continuation committed index 172, then index 173 failed with a replay-guard statement timeout. Current state is **173 commits / 34,600 rows**, with 43 batches remaining. See [actual timeout report](43-attendance-continuation-timeout-report.md) and the [locally tested SQL amendment](44-attendance-indexed-guard-amendment.md).

**172 of 216 transactions committed; 34,400 of 43,160 staging records are live.** Execution stopped after an interruption. Do not replay indices 0–171. Original indices **172–215**, comprising **44 transactions / 8,760 records**, remain outstanding. No operational attendance was created.

## Authorization and interruption

The direct owner message “Goalkeep KC-2 — Explicit Owner Authorization for Attendance Import” approved import manifest `911c47968c61fb19a0227e0ab86eae2937dec2e673b9b94c4713ed08bb3ab4ed` and bounded resumption plan `a77979c4844da64c6aed511c7a56ba64938135a586b7f5caec4a4536bce1fa8a`. Approval was first observed by the clock tool at **2026-10-27 14:46:21 UTC**; expiry is **18:46:21 UTC** the same day. The platform did not expose an independent message-receipt timestamp; this earliest tool observation is the recorded timestamp basis. The expiry was never extended.

Fresh preflight verified the exact non-production Tokyo project `hmlbdozsqxlwzvjimjwh`, its deployed 20-table schema/four-entry ledger, empty staging, original full-row fingerprints, source snapshots, code, all packets and private journal. The reviewed SQL/loader and deterministic record IDs were unchanged. No migration was reapplied. This direct authorization was accepted by execution review; the earlier first-attempt rejection is historical evidence in docs 41.

The wait tool later returned `aborted by user`; execution cell 119 was no longer available. The durable journal retained **171 commit acknowledgements** and the submission of index **171** without a journaled acknowledgement. Its request ID is `220a58b344bbaa5617e4b41f88fcf055e89f15d7c8f1788a566a0e730a905e3f`. No request was retried and no subsequent write was submitted after detecting the interruption.

Read-only database comparison confirms the **exact first 172 batches** committed: every expected key and complete payload matches aggregate hashes across all 256 ID buckets, excluding only new database-generated creation/update timestamps. Original source fields and all business payload fields are covered. The journal appends a distinct `commit_verified_readonly` event rather than fabricating the lost acknowledgement. No import remains active; no transaction outcome remains uncertain. The authorization is inactive following the stop condition.

There was also a long acknowledgement gap earlier in this run; no database cause is established. The runtime's in-memory helper store was unavailable after interruption, while private on-disk packets, snapshots and journals remained intact. A filesystem-backed runtime helper now avoids reliance on that store. None of these transport observations justify replaying committed transactions.

## Actual live reconciliation

| Measure | Live / planned |
| --- | ---: |
| Confirmed committed transactions | **172 / 216** |
| Acknowledged / independently verified commits | 171 / 1 |
| Staging records | **34,400 / 43,160** |
| Worksheets represented, potentially partial | 80 / 107 examined |
| Daily roster-context rows | 1,821 / 2,142 |
| Daily literal P/A marks | **20,995 / 24,687** |
| Literal marks, including support participation | 22,567 / 26,259 |
| Formula cells | 189 / 189 |
| Summary values | 2,204 / 2,579 |
| Auxiliary values | 0 / 1 |
| Source contexts | 9,440 / 14,132 |
| Operational attendance | **0** |
| Duplicate coordinates / unexplained prefix losses | **0 / 0** |
| Server-failed / still-uncertain transactions | **0 / 0** |

The **24,960 loaded cell candidates + 9,440 contexts = 34,400 staging records**. Categories overlap only where explicitly stated: daily marks are a subset of literal marks, and contexts are not attendance observations. The remaining 8,760 records are 3,692 daily marks, 375 summaries, one auxiliary value and 4,692 contexts. Their absence is documented outstanding work, not a claimed complete import.

All 34,400 rows are review-pending and code-pending; verified child IDs and parsed dates are NULL. Among the **24,960 cell candidates**, identities are 13,676 provisional, 519 ambiguous and 10,765 unmatched. Date evidence is 20,940 sanitized-untrusted, 383 unresolved-formula headers, 3,628 unparsed and nine missing. Context-only rows have separate classifications in the machine evidence and are not counted as additional missing-date observations.

No source mark/header disagreement, invalid source link or invalid candidate child reference exists. Exact prefix payload agreement includes original sanitized values, coordinates, diagnostics/provenance, flags and candidates. No name-only identity was accepted, missing date fabricated or attendance code interpreted.

## Existing data and security

Before/after aggregate full-row fingerprints and counts are identical for **every original table**: 20,432 source records, 371 children, 716 caregivers, 716 links, 106 questionnaires, 3,286 answers and **28,293 audit events**, plus all other baseline records. Operational attendance/ADL/support, memberships and recovery actions remain zero. No original source/audit record was modified.

The full 20-table catalog, functions, constraints, triggers, RLS, privileges and migration ledger match preflight exactly. Staging RLS remains enabled/forced, without application policies or table grants. Live anon, authenticated and service_role staging reads are denied. No OAuth, application membership, schema change or broad access was activated. The Tokyo pilot exception remains intentional.

Thirteen focused local tests pass (five existing execution controls, six authorization/reconciliation controls, two continuation controls), along with Python/JavaScript syntax, original source/code/packet bindings and Git whitespace checks. Existing isolated PostgreSQL tests are reused for unchanged SQL. Payload serialization was verified against captured live read-only hashes; it preserves zero, false, Unicode and numeric representations. No negative test wrote remote data.

## Exact bounded continuation — not yet authorized

The [continuation plan](evidence/attendance-prefix172-continuation-plan.json) binds the exact destination, original import manifest, 34,400-row committed payload checkpoint, journals, ledger/catalog, original-table fingerprints, source/code hashes and **only unchanged packets 172–215**.

Canonical SHA-256: **`e137a5008ea428acf0e045386f464c5546f6500884f5e282bfa79d55c3ae9a6f`**.

`scripts/attendance_continue.py` is a separate fail-closed mode: it requires fresh captured prefix evidence and a new owner authorization artifact, rejects prior/out-of-scope indices, enforces the approved four-hour window and transaction order, and stops on any rejected/failed/uncertain request. It cannot connect or write by itself. No continuation approval artifact has been created and this mode was **not remotely executed**. A future four-hour window must come from explicit owner approval, not automatic extension.

After separately authorizing these 44 transactions: recheck the exact prefix and original data/security, use a new journal linked to the stopped journal, never resubmit 171, then reconcile all 43,160 keys/payloads, 24,687 daily marks, source links, classifications and security. The prior initial-empty plan is not reused against a nonempty destination.

Evidence: [live checkpoint](evidence/attendance-import-interrupted-checkpoint.json), [continuation hash](evidence/attendance-prefix172-continuation-hash.json). Private source bundles, packets, row hashes, authorization and complete journals remain ignored. PR #2 receives this checkpoint; PRs #1/#2/#3 remain unmerged. This is **partial staging completion**, not business-approved attendance or permission to connect the live frontend.
