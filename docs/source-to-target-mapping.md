# Stage 1 — Source-to-target mapping requirements

These are conceptual transformation requirements, not an implemented migration specification. Exact source labels, inferred types, null counts and original column letters are in [field-profiling.csv](evidence/field-profiling.csv). No row has been migrated, excluded from the preserved snapshots, repaired or deduplicated.

| Source range | Candidate conceptual destination | Required transformation / unresolved rule |
| --- | --- | --- |
| S03 T01 A:C | Child identity + lineage | A is source serial, B candidate admission key, C name; retain all original values privately. Do not use the serial/name as a global key |
| S03 T01 D:F,I,AR:AS | Program/status/joining and dropout attributes | Distinguish current/admitted program, status, joining, dropout date/year; approve status meanings and chronology |
| S03 T01 G:H,AE:AK,BK | Restricted health/assessment attributes | Preserve diagnoses, UDID fields, disability/validity/percentage, insurance identifier, assessment date/age and severity; do not infer clinical definitions or enforce an unsupported scale |
| S03 T01 J:N | Child demographics | Preserve DOB, calculated age source, gender, identity field and blood group; DOB missing/chronology issues need review; regenerate age only after reference date approved |
| S03 T01 O:AC | Caregiver/contact attributes | Mother/father identities, contacts, birth dates, employment/education and address require restricted handling; reconcile with caregiver ID links before merge |
| S03 T01 AD | Sibling count | Preserve count. S03 T03 sibling names/details are header-only; no sibling people can be generated from a count |
| S03 T01 AL:AQ | Restricted financial attributes | Income, economic classification, assessment/monthly fees, remarks and concession; keep currency/period/percentage semantics unresolved where not explicit |
| S03 T01 AT:AV | Restricted social/reason attributes | Caste/religion/dropout reason: retain source meaning privately, require access/necessity review before schema exposure |
| S03 T01 AW:BF | Program-change observations | Unpivot five program/date pairs, preserve slot and both cell references; no inferred end dates or automatic event ordering repair |
| S03 T01 BG:BJ | Transition/consent/comments/joining-year attributes | Preserve original fields. Missing consent is unknown, never approval |
| S03 T02/T04–T06/T10/T12 | Fee/child supplement/history/severity reconciliation inputs | Reconcile by evidence; don't union automatically or treat view rows as new people. Historical scope and authority require approval |
| S05 T07 A:D | Caregiver and child-caregiver relation | B unique caregiver ID, C child ID matching master B; preserve A/D names and mismatches separately |
| S01 T01 A:D,AZ:BA | Questionnaire submission context | Child name/program/centre/date and explicit caregiver/child IDs; 60 names disagree with ID-linked master; approval required before choosing authority |
| S01 T01 E:AE | Numeric questionnaire answers | Unpivot 27 actual question headers/values; retain source column, blanks and the observed outlier. Do not clamp to 1–5 yet |
| S01 T01 AF:AI | Text/recommendation answers | Unpivot actual open-text and recommendation fields; sanitize text before AI/test exposure; approve recommendation vocabulary/scoring |
| S01 T01 AJ:AY | Derived score reconciliation inputs | Preserve formulas in original snapshots and compare only after definitions approved. Do not import derived totals as new questionnaire answers |
| S01 T02–T07 | Supporting rubric, summaries and questionnaire views | Retain source guidance and alternate layouts. Owner must designate which submission layout(s) are authoritative; no automatic union |
| S02/S04/S06–S11 monthly grids | Daily attendance observations | Unpivot date columns G:AK with name/program-or-batch/status context. Retain source service/file and cell. Dates may be formula-derived or malformed; 610 marks lack recognized headers. Blank is not A |
| Attendance rosters and annual sheets | Identity/coverage and reconciliation inputs | Repeated child rows across months are expected. Match to master through approved crosswalk, not fuzzy names. Annual summaries remain separate |
| S05 T01–T06 | Support participation observations | Resolve event label/date and caregiver role; numeric counts, M/F variants and Yes differ from P/A. Do not coerce without a legend |
| S05 T08 | Aggregate support event observations | Keep aggregate totals separate from participant records; one date is text/unparsed |
| S07/S08/S09/S10 activity logs | Activity/visit source observations | Content rows include notes/plans; confirm grain, column shifts, participant count and links. Exact duplicate descriptions aren't sufficient to delete events |
| S12 T01–T10 | ADL visit observations | Unpivot five boolean/date pairs. Keep false/blank semantics; four checked flags lack dates. No date or visit may be invented |
| S12 T11–T12 | Annual visit/goals summaries | Reconciliation inputs only until calculation and goal definitions are approved |

Every proposed future target row must carry source file alias/ID, native worksheet ID/name and original row; cell/slot references are needed for unpivoted data. The private map preserves actual filenames and native/exported tab names. A single source row can produce multiple observations; reconciliation must compare both source rows and generated observations at their respective grains, not expect one target row per spreadsheet row.

No uniqueness constraint, controlled enum, required business column, deduplication action or target ID-generation scheme has been approved. Preserve conflicts in staging and produce row-reference issue logs; do not silently select a winning record. The future Google Sheet migration-error log and timestamped SQL files remain Phase 1 implementation obligations after approval.
