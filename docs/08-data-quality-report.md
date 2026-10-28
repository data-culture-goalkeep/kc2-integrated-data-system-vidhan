# Stage 1 — Data-quality report

Status: source issues identified and preserved; no corrections, exclusions, merges or deduplication applied. This is not a migration reconciliation report because no migration occurred.

## Coverage and populations

Twelve authorized spreadsheets, 155 worksheets and 145,785 nonempty cells were profiled. There are 6,521 recognized candidate rows across multiple grains including derived views, summaries and repeated observations. They cannot be interpreted as 6,521 people or approved import rows. The critical populations are 371 child-master rows, 716 caregiver-link rows, 106 primary questionnaire rows, 2,142 daily child-sheet rows and 1,219 monthly ADL child-sheet rows.

## Priority findings

| Priority | Finding | Evidence and calculation | Proposed resolution pending analyst approval |
| --- | --- | --- | --- |
| High | Identity display names disagree with source IDs | 60/106 questionnaire names differ from the name on the same master admission after case/whitespace normalization; all 106 caregiver-child ID pairs match | Preserve conflicting names and identifiers; approve authority before linking or overwriting |
| High | Name-only foreign-key candidates unresolved | Over 4,924 non-master row occurrences, 3,347 unmatched and 20 multiply matched names; 1,557 single candidates. These counts include views | Obtain an approved identity crosswalk; no fuzzy matching or silent orphan deletion |
| High | Attendance date attribution incomplete | 610 P/A marks have no recognized date heading; four candidate headers unresolved; seven static-calendar discrepancies | Retain original row and column; resolve date structure and period metadata before a dated target load |
| High | Birth/joining chronology conflicts | Three master typed DOBs after joining: J165, J270, J302 | Source/analyst review; no date swapping or imputation |
| Review | Questionnaire scale and missingness | 86 missing cells / 2,862 primary numeric answer slots; one primary numeric value is 6, repeated once in an alternate view | Approve scale/applicability; do not clamp or default missing to zero |
| Review | ADL dates incomplete | Four checked slots lack dates out of 194 checked slots; no date-with-unchecked-flag cases found | Keep flag/date separately; obtain correction decision |
| Review | Master data incomplete | DOB missing 3/371; consent missing 191/371; one master admission has no caregiver-link row | Confirm mandatory fields and semantics; do not manufacture values or consent |
| Review | Date representation and placeholders | 217 cells not accepted by conservative date parser; eight ambiguous day/month strings; primary questionnaire date column has 66 text and 40 typed values | Separate placeholders from corrupt dates, approve locale, and document transformations |
| Review | Repeated source rows and names | 23 exact full-row duplicate excess: 1 severity view, 1 roster, 21 activity-log descriptions. Five repeated-name groups in master | Duplicates may be valid repeated content; review grain before any removal. Do not deduplicate people by name |
| Review | Formatting inconsistency | 125 cells with surrounding whitespace; source type/category counts differ across columns | Retain originals and approve canonical mappings |
| Review | Contact/email syntax flags | 642/976 nonblank contact/email cells fail candidate Indian-phone/basic-email syntax heuristics across master/supplement sheets | Dummy placeholders and business exceptions need review; not a claim of 642 invalid contacts or people |
| Technical limitation | Formula results not executed | 66,057 formula cells; 6,907 have no returned cache value. Empty template results and exporter behavior can contribute | Do not claim live calculation validation; preserve raw formulas and approve/recreate metrics in a later increment |
| Source error | Invalid date serial / Excel error | S03 T11 A29; one error cell recorded | Original bytes retained; inspect/correct only with approval |

Issue counts are occurrences, not unique affected people, and can overlap or recur in alternate views. The primary questionnaire's single outlier must not be reported as two distinct problematic submissions simply because it also appears in a view.

## Calculations and indicator evidence

The numeric questionnaire comprises 27 actual item columns E:AE, with source section maxima 30+20+30+20+25+10=135. Source AQ2 sums AJ2:AO2; AR2 references AQ2 and numeric constants 100/135. Source AP2 is a separate recommendation-derived formula using AI2 and constants 0/100. Therefore the observed total formula excludes AP2. This describes the source workbook, not approval that its score design is correct. The exact recommendation rule, missing-answer policy and interpretation thresholds remain review items.

P/A grid cells are counted as literal observations, not assumed scheduled sessions. Blank cells are not absences. ADL booleans are counted separately, with only true flags contributing to the 194 checked-slot count; each retained source slot preserves its original date and coordinate privately. Support participation is not forced into either of these grains.

## Row/cell evidence and reproducibility

[data-profile.json](evidence/data-profile.json) stores source, worksheet, field counts, candidate row lists, categories and issue coordinates. [additional-checks.json](evidence/additional-checks.json) stores ID-pair conflicts, ADL flags/dates, contact-format candidates and calendar discrepancies. No raw record values are included. Native worksheet IDs and public source aliases allow an authorized analyst to locate originals, while private manifests preserve source names.

Scripts inspect immutable source snapshots, calculate statistics programmatically and create separate sanitized copies. The [verification evidence](evidence/verification.json) and [reproduction guide](sanitization-and-reproducibility.md) distinguish passed technical checks from unresolved business correctness. Unknown dates, identity authority and calculation definitions remain open; source data was not changed to make checks pass.

## Readiness

Stage 1 is ready for analyst review with explicit issues and a conceptual model. Approval questions Q01–Q11, especially identity authority, attendance crosswalk/date semantics and questionnaire scoring, must be resolved or explicitly accepted before physical schema implementation. This report does not assert migration readiness or final Phase 1 completion.
