# Attendance source-to-staging — final live reconciliation

**All approved attendance evidence is represented in protected staging.** Exact keys/full payloads and per-sheet counts reconcile to the frozen sanitized bundle. Original spreadsheets and the existing 20,432 source records were not modified or migrated again. Operational attendance remains **zero**.

## Grains and coverage

| Measure | Actual live count |
| --- | ---: |
| Attendance-related worksheets | **107** |
| Distinct referenced source rows / row-context records | **14,132** |
| Daily roster contexts | **2,142** |
| Daily literal P/A marks | **24,687** |
| Support-participation literal marks | **1,572** |
| All literal marks | **26,259** |
| Unresolved formula cells | **189** |
| Summary/aggregate values | **2,579** |
| Auxiliary value | **1** |
| **All cell candidates** | **29,028** |
| **Contexts + cell candidates** | **43,160** |

Daily/support marks are subsets of all literal marks; daily roster rows are not observations. Formulas and summary/alternate views are retained as their own kinds, never converted into daily events. The 43,586 blank roster grid slots remain supported by original rows/column contracts and are not invented absences. The 29,028 cells plus 14,132 contexts account for all expected records; unrelated source-row/entity totals are not compared as evidence of completeness.

The [per-sheet live inventory](evidence/attendance-final-live-sheets.json) records file/sheet aliases, staging/context/cell counts and daily marks for every examined worksheet. Real names/private file details remain protected in the existing source registry and private intake records.

## Pending identity/date/code classifications

| Identity status | Cell candidates (29,028) | All staging rows (43,160) |
| --- | ---: | ---: |
| PROVISIONAL_MATCH | 15,358 | 16,672 |
| AMBIGUOUS | 723 | 804 |
| UNMATCHED | 12,947 | 25,684 |
| VERIFIED | **0** | **0** |

These are source-coordinate records, not unique people. The original daily roster analysis remains 1,009 provisional, 74 ambiguous and 1,059 unmatched across 2,142 rows. Name candidates were never accepted as identities.

| Date evidence | Cell candidates | All staging rows |
| --- | ---: | ---: |
| SANITIZED_UNTRUSTED | 24,562 | 24,562 |
| FORMULA_UNRESOLVED | 452 | 452 |
| UNPARSED | 4,004 | 4,004 |
| MISSING | 10 | 14,142 |
| VERIFIED | **0** | **0** |

The additional missing-date context rows are **not extra attendance observations**. All parsed dates remain NULL; syntactically date-like sanitized headers were not treated as reliable chronology. All **43,160** rows have `code_status=PENDING` and `review_status=pending`. Raw letters/numbers/opaque sanitized literals and formula/header evidence remain intact. No category meanings, formula results, identities or dates were invented.

## Actual reconciliation results

- **43/43 revised tail transactions committed**, adding 8,560 records; all **216** original batch indices are accounted for without replaying the committed prefix.
- **Zero** missing, extra or changed expected keys/payloads across 256 aggregate ID buckets, excluding only newly generated timestamps from the input-payload comparison.
- **Zero** duplicate source coordinates, source-mark/header disagreements, invalid source/artifact coordinates or invalid candidate child references.
- The old **34,600 complete staging rows including timestamps** match their preflight fingerprint exactly.
- Every original table's full-row fingerprint and count is unchanged: children 371; caregivers/links 716 each; questionnaire responses/answers 106/3,286; source records 20,432; audit events 28,293. No audit history or source processing status was rewritten.
- The 20-table catalog, all constraints/indexes/triggers/policies/privileges and four migration entries are unchanged. The current task created **zero indexes or schema objects**.
- Staging remains private and force-RLS protected; all three unapproved roles are denied live reads. Memberships, ADL/support and operational attendance remain zero; no OAuth/live application access was activated.

The earlier index-173 timeout is retained as a failed, rolled-back **historical attempt**. The owner-approved revised attempt succeeded; there are **zero failed/uncertain requests in the revised run**, zero unresolved outcomes and zero remaining approved transactions. [Machine report](evidence/attendance-final-live-reconciliation.json).

## Remaining business work

Authorized reviewers still need reliable identity crosswalks, source-date fidelity/calendar evidence and attendance-code definitions before any operational projection. Unmatched/ambiguous evidence is now structured for review and need not be discarded. The existing synthetic frontend keeps verified attendance and pending review separate; live integration must preserve that boundary and use separately approved backend permissions. Technical staging completeness is not business acceptance or automatic authorization to expose restricted data.
