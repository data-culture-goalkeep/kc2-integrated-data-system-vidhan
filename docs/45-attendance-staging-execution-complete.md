# Attendance staging — execution complete and live-verified

**All 216 attendance batches are accounted for; 43,160 pending staging records are live.** The owner-approved revised tail, original indices **173–215**, committed **43/43 transactions**, adding **8,560** records. There were **zero failed/uncertain requests and zero retries in this revised run**. No operational attendance was created.

## Authorization, destination and execution

Exact destination: `kc2-integrated-data-system` / `hmlbdozsqxlwzvjimjwh`, Tokyo `ap-northeast-1`, non-production internal pilot. Tokyo remains the intentional exception to the organisational Mumbai standard.

The direct owner message “Goalkeep KC-2 — Explicit Authorization for Revised Attendance Import” approved revised manifest **`d990a38ee68612363dda031dd036b95e905d81ee40d0e52b5917fe707f474307`**, anchored to original import **`911c47968c61fb19a0227e0ab86eae2937dec2e673b9b94c4713ed08bb3ab4ed`**, and only the redundant primary-key equality described in docs 44. The INSERT bytes and every full-payload comparison remained intact; statement timeout stayed **60 seconds**, with no new index or schema/permission change.

Approval was first observed by the clock tool at **28 October 2026, 00:09:42 IST**, expiring at **04:09:42 IST** (27 October 18:39:42–22:39:42 UTC). An independent platform message-receipt timestamp was unavailable; this earliest clock observation is the recorded basis. Dispatch started **00:12:06 IST**, the final acknowledgement arrived **00:19:36 IST**, and independent live verification passed at **00:21:40 IST**. Every dispatch/acknowledgement was inside the four-hour window; it was never extended.

Fresh preflight verified project/name/region, the exact 34,600-row checkpoint including complete timestamps/payloads, all source/code/packet hashes, original-table fingerprints, the 20-table catalog/security, four-entry migration ledger and absence of active imports. The separate reviewed indexed-tail executor submitted only 173–215 in order. No migration, prior committed batch, source-preservation job, OAuth, membership or frontend connection was run.

## Actual transaction accounting

| Committed original indices | Evidence | Transactions |
| --- | --- | ---: |
| 0–170 | Preserved original acknowledgements | 171 |
| 171 | Exact live prefix verification after lost acknowledgement | 1 |
| 172 | Preserved acknowledgement from the previous continuation | 1 |
| 173–215 | New approved revised SQL acknowledgements and archived raw receipts | 43 |
| **All unique committed indices 0–215** | **215 acknowledgements + one independent commit proof** | **216** |

The previous **failed original-SQL attempt at 173** remains recorded as rolled back with SQLSTATE 57014; it is not counted as a commit. The prior transport interruption/lost acknowledgement and initial execution-review rejection also remain historical evidence. No failure history was deleted or converted into a fabricated acknowledgement. The newly approved revised request IDs/SQL hashes are distinct and bound to the same original batch indices and unchanged data.

The private hash-chained journals and all 43 new raw receipts were checked against their approved request/SQL hashes. The final journal is sealed by `completed_live_verified`; its SHA-256 is recorded in the machine report. The authorization artifact is now **inactive** and no import remains active. Do not rerun any original or amended packet.

## Actual live data and integrity

Live results are **43,160 staging records**, **24,687 daily literal P/A marks**, **107 worksheets**, **2,142 daily roster contexts** and **zero operational attendance**. Every approved key and complete business payload matches across 256 digest buckets, and every worksheet's counts reconcile to the frozen approved bundle. There are zero missing/extra/changed expected records, duplicate source coordinates, source/header disagreements, invalid source links, invalid candidate references or unexplained source losses. [Grain-aware source reconciliation](46-attendance-final-source-reconciliation.md) separates marks, formulas, summaries and contexts.

All prior **34,600 staging rows, including creation/update timestamps**, remain identical. Every original table's complete-row fingerprint and count is unchanged, including **20,432 source records and 28,293 audit events**. The full schema, constraints, triggers, functions, RLS, privileges and migration ledger match preflight exactly. Staging RLS remains enabled/forced, with no application policies or grants; live anon, authenticated and service_role reads are denied. No memberships/OAuth/live-user access were activated.

All 43,160 records remain review- and code-pending; no child identity/date was promoted. Parsed dates and verified child references are NULL. Staging completion preserves evidence for review and does **not** establish attendance semantics, correct calendars, accepted identities or business-approved attendance.

## Verification and next boundary

The unchanged reviewed amendment's eight isolated PostgreSQL checks/four unit tests were reused. New verification executed against live SQL results: exact payload/key and per-sheet coverage, both preserved prefix journals plus the revised journal, all receipts, source versions, original records/timestamps/audits, schema/security/ledger and live role denials. New synthetic journal tests reject changed requests and missing receipts; Python syntax, documentation links, manifest bindings, privacy checks and Git whitespace checks also pass. Local test performance is not substituted for live verification.

Evidence: [final live reconciliation](evidence/attendance-final-live-reconciliation.json), [107-sheet accounting](evidence/attendance-final-live-sheets.json). Sensitive source bundles, detailed row hashes, SQL packets, authorization and raw journals/receipts remain ignored under `work/`. The completion reader is `scripts/report_attendance_final.py` and has no database execution capability.

PR #2 carries this result and remains unmerged; PRs #1/#3 stay separate/unmerged. Remote writes are finished. The next separately requested task may connect the frontend through approved authentication/authorization; this completed import does not activate the draft role matrix, Google OAuth or private application access.
