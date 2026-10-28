# Original-evidence recovery and proposed date increment

Checked 28 October 2026, 11:05 IST; no new remote writes. Read [final handover](PHASE1-HANDOVER.md) for complete source reconciliation.

Original/sanitized hashes match the frozen 12-file/155-sheet snapshot. Real source dates were obscured by sanitization. The private recovery ledger retains original values, original sheet names, native sheet keys, source IDs/cells, candidate children, dependencies, weekday conflicts and reviewer decisions. Original source payloads and deployed staging are unchanged.

Daily literal P/A marks: 24,687; locally recovered dates: 24,087; conflicts among recovered: 27; unresolved full dates: 600. ADL true slots: 194, dates recovered: 190, missing: four. No newly verified attendance/ADL child crosswalk; zero eligible new operational events. The 110 name-derived support caregiver-ID formulas (102 registry-matching cached IDs; 92 unique lookup names) remain review suggestions. Original formula expressions/cached IDs are private, not discarded.

## Exact prepared increment — not executed or authorized

- Target: `hmlbdozsqxlwzvjimjwh`, Tokyo non-production.
- Manifest SHA-256: **`a3a4c2478dfc2f4786d253e5c63bbf741d4025940f122d562a5b371585cc1b3e`**.
- 197 atomic transactions: 91 programme `promotion_date` updates and 106 questionnaire `assessment_date` updates, NULL → source-recovered DATE.
- 197 protected recovery-action inserts + 197 typed provenance inserts; expected 197 new trigger audit events.
- Expected post-execution recovery actions 197, provenance 5,969 and audits 28,490. These are proposed totals, not live counts.
- All affected records retain pending review status. No source/staging/child/caregiver/answer updates, new operational observations, schema changes or access activation.
- Seven chronology-conflicting date candidates excluded; 30 programme slots lack safe recoverable dates.
- [Exact manifest](evidence/historical-date-increment-manifest.json), [hash](evidence/historical-date-increment-hash.json), [focused tests](evidence/historical-runtime-tests.json).

The manifest binds original/sanitized snapshot, code hashes, private values, per-transaction SQL hashes, exact destination, complete starting-table fingerprints and actual schema/ledger. `historical_execution.py` requires a separate active owner approval; no authorization artifact has been fabricated. It records dispatch before transport, durable official receipts before acknowledgement, and blocks uncertain/out-of-order/repeated requests. No automatic remote execution is implemented by the preparation command.

## Required next action

Owner review/approval of the exact manifest, original-date fidelity/disclosure and controlled execution window. Then freshly verify target/source/code/catalog/ledger/fingerprints, execute only this increment through the reviewed connected pathway and reconcile actual dates/evidence/audits. Existing transaction approvals are consumed and confer no permission for this scope. Stop on any failure/uncertainty; read-only diagnosis and separately bounded recovery only. No deletes/resets or blind retries.
