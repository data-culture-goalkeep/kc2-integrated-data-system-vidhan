# Stage 1 — Data profiling

Status: profiling completed locally; source issues remain unresolved. All statistics are computed by repository scripts, not estimated.

## Counting method and limits

Every worksheet and nonempty cell was inspected. Grid dimensions often approach 1,000 rows because of formatting and formulas; they are not record counts. For recognized tabular sheets, candidate rows have a nonblank literal value in the detected child/caregiver name column (or first anchor column). Formula-only template rows are counted separately. Activity logs use rows with any literal content in their first seven columns; these can include notes, separators and repeated plans, so their counts are **candidate content rows, not confirmed events**. Formulas are not executed. All original and sanitized rows remain available, including rows outside the candidate set; nothing is discarded.

Record row references, field names, literal/formula/missing types, distinct counts, categorical dictionaries, duplicate groups and issue coordinates are in [data-profile.json](evidence/data-profile.json). The [worksheet inventory](source-worksheets.md) reconciles dimensions, nonempty rows and classified rows; [field-profiling.csv](evidence/field-profiling.csv) gives every profiled column and its denominator. A worksheet without a record header is profiled structurally rather than assigned invented fields.

## Primary counts and grains

| Source / grain | Actual observed count | Interpretation |
| --- | ---: | --- |
| S03 T01 child master | 371 rows | 371 complete, distinct admission numbers; 366 distinct normalized names |
| S01 T01 questionnaire | 106 rows | 106 distinct child IDs and 106 distinct caregiver IDs |
| S01 T05 / T06 / T07 | 29 / 45 / 39 rows | Subset/alternate layouts; not additional confirmed submissions |
| S05 T07 caregiver links | 716 rows | 716 unique caregiver IDs covering 370 child IDs |
| Daily attendance sheets | 92 worksheets / 2,142 child-sheet rows | Repeated child roster observations across periods/services |
| Literal attendance marks | 24,687 cells | P: 17,788; A: 6,899; includes marks with unresolved headers |
| Blank date-grid slots | 39,630 cells | Unknown/not recorded; never interpreted as absent |
| S12 monthly ADL visit-slot sheets | 1,219 child-sheet rows | 194 checked visit slots; blank/false flags do not become visits |
| S05 support matrices | 262 child-sheet rows | Mixed numeric, role-coded and yes/no encodings |
| S05 support event summary | 15 content rows | Aggregate event totals; not individual attendance |
| Other visit/activity logs | 144 candidate content rows | Requires event-grain review |
| S03 historical visits | 155 rows | Historical roster/visit material; import period unapproved |
| S03 supplemental child sheets | 26 rows | Reconciliation with master unresolved |
| S03 sibling roster | 0 anchored rows | Header structure exists, no populated sibling records detected |

Other annual, fee and severity summaries remain separately inventoried. The combined 6,521 candidate rows across all sources are not additive unique business records.

## Identity and relationship checks

- S03 T01 admission numbers: 371/371 populated and unique. Names: 366 distinct, with five repeated-name groups. Admission-number stability/reuse remains a business question.
- All 716 caregiver-link child IDs match a unique master admission number. One master admission number has no caregiver-link row. Repetition of child IDs in this link sheet is expected for its one-to-many shape, not a duplicate-person defect.
- All 106 primary questionnaire caregiver IDs match unique caregiver-link IDs; all 106 child IDs match unique master admission numbers. All 106 caregiver–child pairs are consistent with the link sheet.
- **60/106 questionnaire names disagree with the name on the same master child ID.** Do not overwrite names or silently choose an identity rule. Dummy-data pseudonym conventions may be the cause, but that is unconfirmed.
- Name-only linkage across non-master sheets was tested on 4,924 row occurrences, including views: 1,557 have one normalized-name master candidate, 20 have multiple candidates and 3,347 have none. These are match diagnostics, not approved person joins or distinct-person counts. No fuzzy matching was applied.

## Data-quality findings

| Finding | Computed result | Meaning / required action |
| --- | ---: | --- |
| Typed birth date after joining date | 3 | S03 T01 J165, J270, J302; review chronology |
| Master child DOB missing | 3 / 371 | No imputation |
| Master consent missing | 191 / 371 | Confirm meaning and whether required; do not default to consent |
| Primary questionnaire score cells missing | 86 / 2,862 | Question-specific missingness differs; sibling questions may be inapplicable |
| Primary questionnaire score outside observed 1–5 numeric range | 1 | A value of 6; also appears once in an alternate view. Scale approval required |
| Questionnaire assessment-date representation | 66 text / 40 typed dates | Retain source formats; resolve locale |
| Date values not parsed by the conservative checker | 217 | Includes placeholders and non-date text; not all are proven corrupt dates |
| Ambiguous numeric day/month strings | 8 | Approve locale before conversion |
| Attendance marks without a recognized date header | 610 | Preserve source column; cannot assign a date automatically |
| Unresolved candidate date headers | 4 | Includes malformed text/formula-cache gaps |
| Static attendance period / date-header disagreements | 7 columns | 86/92 sheets had usable static period metadata; review the mismatches |
| ADL checked visit without date | 4 / 194 | Do not invent visit dates |
| Exact full-row duplicate excess | 23 | 1 severity view, 1 roster, 21 activity-log rows; repeated plans may be legitimate |
| Surrounding whitespace | 125 cells | Normalize only with documented policy; keep original |
| Formula cells without a returned cache value | 6,907 / 66,057 formulas | Can be intentional blank/template output or export behavior; not necessarily a failed calculation |
| Excel error / invalid date serial | 1 cell | S03 T11 A29; raw snapshot preserved |
| Contact/email format review flags | 642 / 976 nonblank cells | Includes dummy placeholders; phone/email syntax heuristics only, not confirmed invalidity |

Counts are cell/row occurrences and can overlap; the same underlying issue may recur in a view. They must not be summed into a count of affected people. Every issue retains source alias, worksheet and row/cell references in the evidence; no record values are logged.

## Categories, rules and formulas

Observed daily attendance literals are P and A. Their operational meanings, treatment of blank/weekend/service-not-scheduled cells and denominator are still unapproved. Master current-program has five distinct values and child-status has three. The complete observed category dictionaries, case/whitespace variants and counts are in the field evidence; values outside a small generic safe vocabulary are pseudonymized, including diagnostic and NGO-specific categories. These tokens preserve distinctions without inventing a clinical taxonomy or treating synonyms as equal.

The primary questionnaire has 27 numeric item columns E:AE, three open-ended response columns AF:AH, recommendation AI and derived columns AJ:AY, plus caregiver ID AZ and child ID BA. Headers expose section maxima (30,20,30,20,25,10). Source formula signatures include a percentage divisor of 135 and a recommendation formula with numeric constants 0 and 100. Their presence is source evidence, not an approved scoring definition; source totals, recommendation inclusion, missing-answer policy and interpretation thresholds need review before recreation. See [additional-checks.json](evidence/additional-checks.json).

Support-group values use numeric counts, M/F variants and Yes-style entries, while ADL flags are booleans. They cannot be forced into the daily attendance P/A vocabulary. No controlled enum, deduplication rule, business range or scoring rule has been silently imposed.

## Verification boundary

The checks confirm file/sheet coverage, checksum integrity, lineage retention, reproducible aggregate counts, candidate links and synthetic privacy/regression behavior. They do not certify business correctness, live Google formula recalculation, source completeness beyond accessible folder results, or schema approval. No Supabase connection, table or migration was created.
