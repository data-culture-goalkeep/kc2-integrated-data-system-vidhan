# Original-evidence recovery and completed date increment

Live execution reconciliation passed 28 October 2026, 13:49:50 IST; all 197 approved date transactions completed. Read [final handover](PHASE1-HANDOVER.md) for complete source reconciliation.

Original/sanitized hashes match the frozen 12-file/155-sheet snapshot. Real source dates were obscured by sanitization. The private recovery ledger retains original values, original sheet names, native sheet keys, source IDs/cells, candidate children, dependencies, weekday conflicts and reviewer decisions. Original source payloads and deployed staging are unchanged.

Daily literal P/A marks: 24,687; locally recovered dates: 24,087; conflicts among recovered: 27; unresolved full dates: 600. ADL true slots: 194, dates recovered: 190, missing: four. No newly verified attendance/ADL child crosswalk; zero eligible new operational events. The 110 name-derived support caregiver-ID formulas (102 registry-matching cached IDs; 92 unique lookup names) remain review suggestions. Original formula expressions/cached IDs are private, not discarded.

## Exact approved increment — executed and live-reconciled

- Target: `hmlbdozsqxlwzvjimjwh`, Tokyo non-production.
- Manifest SHA-256: **`a3a4c2478dfc2f4786d253e5c63bbf741d4025940f122d562a5b371585cc1b3e`**.
- 197 atomic transactions: 91 programme `promotion_date` updates and 106 questionnaire `assessment_date` updates, NULL → source-recovered DATE.
- 197 protected recovery-action inserts + 197 typed provenance inserts; **197 actual new trigger audit events**.
- **Actual live totals:** recovery actions 197, provenance 5,969 and audits 28,490; programme dates restored 91, questionnaire dates restored 106.
- All affected records retain pending review status. No source/staging/child/caregiver/answer updates, new operational observations, schema changes or access activation.
- Seven chronology-conflicting date candidates excluded; 30 programme slots lack safe recoverable dates.
- [Exact manifest](evidence/historical-date-increment-manifest.json), [hash](evidence/historical-date-increment-hash.json), [focused tests](evidence/historical-runtime-tests.json).

The manifest binds original/sanitized snapshot, code hashes, private values, per-transaction SQL hashes, exact destination, complete starting-table fingerprints and actual schema/ledger. `historical_execution.py` requires a separate active owner approval; no authorization artifact has been fabricated. It records dispatch before transport, durable official receipts before acknowledgement, and blocks uncertain/out-of-order/repeated requests. No automatic remote execution is implemented by the preparation command.

## Execution outcome and remaining boundaries

Explicit owner approval covered the exact unchanged manifest for 13:09:59–17:09:59 IST on 28 October 2026. One fresh preflight passed; all 197 transactions committed in order without failure, uncertain outcome or retry. One final live reconciliation verified all exact dates, recovery/provenance records, the 197-event audit delta, original before-images and metadata, unchanged pending classifications and unchanged schema/security/ledger. Authorization is consumed/inactive. Preparation manifest bytes remain immutable, including its historical preparation-only authorization flag; actual approval/receipts are archived privately. Do not replay these transactions. Historical attendance/ADL/support business gaps and the separate GitHub review/merge gate remain open.

Execution journal SHA-256: `599a0a4edeffa054d542fc0112842b0e7d584019b29b1ed1f3acb8e8577bceed`. Source records remain **20,432**; attendance staging remains **43,160**; operational attendance/ADL/support and memberships remain **zero**. No schema, source, child, caregiver, answer or staging record changed.
