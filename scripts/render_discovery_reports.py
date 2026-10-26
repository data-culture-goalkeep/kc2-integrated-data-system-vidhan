#!/usr/bin/env python3
"""Render aggregate Stage 1 inventory and profiling tables from verified evidence."""
import collections,csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROLES={'S01':'Parent quality-of-life questionnaire','S02':'PT attendance','S03':'Child master and supporting registers','S04':'Speech attendance','S05':'Support-group / caregiver records','S06':'OT fine-motor attendance','S07':'PVSW attendance and activities','S08':'EI attendance and activities','S09':'FA attendance and activities','S10':'Nursery attendance and activities','S11':'Vision attendance','S12':'ADL visits and annual summaries'}
def main():
 p=json.loads((ROOT/'docs/evidence/data-profile.json').read_text());extra=json.loads((ROOT/'docs/evidence/additional-checks.json').read_text());drive=json.loads((ROOT/'docs/evidence/drive-sources.json').read_text());urls={s['source']:s['url'] for s in drive['sources']}
 summary=p['totals'];counts=collections.Counter()
 for i in p['issues']:counts[i['code']]+=i['count']
 inventory=['# Stage 1 — Source inventory','', 'Status: connected-source discovery completed with unresolved business rules; no schema approved.','',
 '## Source coverage and preservation','',
 'The owner-supplied Google Drive folder returned 12 native Google Sheets and no subfolders. A separate folder-only search returned no child folders; a document-type search returned no additional document results. All 12 spreadsheets were downloaded as full XLSX snapshots through the authenticated connection. Their 155 worksheet counts and native sheet order were checked against Google Sheets metadata. There were no separate CSV, Word, PDF, interview or discovery-note files among the returned items. Workbook questionnaire guidance and reporting sheets were included in inspection. These bounded connector results describe what was returned and accessible, not a certification that no separately shared or inaccessible project document exists.','',
 'The native Drive originals were never edited. Their modified timestamps were unchanged between initial listing and the post-download metadata check. XLSX snapshots are immutable local exports, not byte-for-byte native Google Sheets originals. Each has a SHA-256 checksum; local snapshots are read-only. All worksheets were read, including empty/supporting sheets. Two long native tab titles were shortened in the XLSX export; the restricted worksheet map retains both names, ordinal and native sheet ID.','',
 '## Workbooks','',
 '| Source | Subject | Worksheets | Recognized candidate rows, including views | Export bytes |',
 '| --- | --- | ---: | ---: | ---: |']
 for s in p['sources']:inventory.append(f"| [{s['source']}]({urls[s['source']]}) | {ROLES[s['source']]} | {s['worksheets']} | {s['source_record_rows']:,} | {s['bytes']:,} |")
 inventory += ['',f"Totals: **{summary['files']} workbooks, {summary['worksheets']} worksheets, {summary['nonempty_cells']:,} nonempty cells**. The {summary['record_rows_including_views']:,} recognized candidate rows include rosters, derived views, summaries and repeated observations. They are not a distinct-person count or an import target count. Unclassified/supporting prose sheets have nonempty-row counts, not fabricated business-record counts.",'',
 'The previously supplied guidelines DOCX and unchanged 35-byte README remain contextual inputs. The complete guidelines, including diagrams/comments, were read in the initial run. Page ranges in the owner request are not independently verified DOCX pagination; requirements cite project-team §3 steps 8–22, §5 and §6. No linked reference implementation was treated as selected-project data.','',
 '## Worksheet and cell lineage','',
 'See [all worksheets](source-worksheets.md), [complete aggregate profile](evidence/data-profile.json), [column profile](evidence/field-profiling.csv), and [Drive metadata evidence](evidence/drive-sources.json). Public reports use source aliases S01–S12 and sheet aliases T01 onward rather than NGO-specific filenames or tab names. Each worksheet has its actual Google sheet ID in the evidence. Original record row numbers and issue cell coordinates are preserved. A private manifest maps aliases to the original source file/title, exact native/exported worksheet names and local snapshot path. No identifiers, names, contacts, free-text responses or secrets are published in these reports.','',
 '## Sanitized working copies','',
 'All 155 sheets have separate JSONL working copies in restricted, Git-ignored local storage. They preserve source alias, worksheet alias, row and column positions. Unknown strings, names, contacts, IDs, health/financial categories and NGO-specific details are keyed pseudonyms; approved generic field labels and a small generic category vocabulary are retained. Dates in data cells become synthetic dates. Formula text and workbook metadata/comments/links/pivot caches are absent from these copies. Dates/codes needed for actual profiling were inspected locally in the untouched snapshots; only aggregates and references were exposed to AI. These samples intentionally do not preserve real date chronology or formula execution.','',
 'Checksums cover originals and sanitized outputs. Pseudonyms are stable for identical original values within this run; the HMAC key and redaction terms stay outside Git. Exact spelling variants are preserved as different tokens, while separate local normalized comparisons identify whitespace/case issues. The “Dummy Data” filenames were not accepted as proof of sanitization. No sanitized data or re-identification material was committed. See [reproduction and protection](sanitization-and-reproducibility.md).','']
 (ROOT/'docs/01-source-inventory.md').write_text('\n'.join(inventory))
 sheetdoc=['# Worksheet inventory','', 'Aliases are resolved through the source table and private worksheet map. “Candidate rows” follows the counting method in the profiling report. Zero means no rows detected under that method; it does not assert absence of prose, formula results or unresolved content.','',
 '| Source / tab | Native sheet ID | Classification | Header row | Grid rows × columns | Nonempty rows | Candidate rows | Formula-only rows | State |','| --- | ---: | --- | ---: | --- | ---: | ---: | ---: | --- |']
 for s in p['sheets']:
  sheetdoc.append(f"| {s['source']} / {s['sheet']} | {s['google_sheet_id']} | {s['kind']} | {s['header_row'] or '—'} | {s['max_row']} × {s['max_column']} | {s['nonempty_rows']} | {s['record_rows']} | {s['formula_only_rows']} | {s['state']} |")
 (ROOT/'docs/source-worksheets.md').write_text('\n'.join(sheetdoc)+'\n')
 with (ROOT/'docs/evidence/field-profiling.csv').open('w',newline='') as out:
  w=csv.writer(out,lineterminator='\n');w.writerow(['source','sheet','column','source_field_label','candidate_rows','missing','formula_cells','distinct_literal_values','type_counts','surrounding_whitespace'])
  for s in p['sheets']:
   for f in s['fields']:w.writerow([s['source'],s['sheet'],f['column'],f['label'],f['rows'],f['missing'],f['formulas'],f['distinct_nonformula'],json.dumps(f['types'],sort_keys=True),f['surrounding_whitespace']])
 kinds=summary['kind_record_rows'];att=[s['attendance'] for s in p['sheets'] if 'attendance' in s];master=next(s for s in p['sheets'] if s['kind']=='child_master');q=next(s for s in p['sheets'] if s['kind']=='questionnaire_primary');score=q['questionnaire_scores']
 text=f'''# Stage 1 — Data profiling

Status: profiling completed locally; source issues remain unresolved. All statistics are computed by repository scripts, not estimated.

## Counting method and limits

Every worksheet and nonempty cell was inspected. Grid dimensions often approach 1,000 rows because of formatting and formulas; they are not record counts. For recognized tabular sheets, candidate rows have a nonblank literal value in the detected child/caregiver name column (or first anchor column). Formula-only template rows are counted separately. Activity logs use rows with any literal content in their first seven columns; these can include notes, separators and repeated plans, so their counts are **candidate content rows, not confirmed events**. Formulas are not executed. All original and sanitized rows remain available, including rows outside the candidate set; nothing is discarded.

Record row references, field names, literal/formula/missing types, distinct counts, categorical dictionaries, duplicate groups and issue coordinates are in [data-profile.json](evidence/data-profile.json). The [worksheet inventory](source-worksheets.md) reconciles dimensions, nonempty rows and classified rows; [field-profiling.csv](evidence/field-profiling.csv) gives every profiled column and its denominator. A worksheet without a record header is profiled structurally rather than assigned invented fields.

## Primary counts and grains

| Source / grain | Actual observed count | Interpretation |
| --- | ---: | --- |
| S03 T01 child master | {kinds['child_master']:,} rows | 371 complete, distinct admission numbers; {master['distinct_normalized_child_names']} distinct normalized names |
| S01 T01 questionnaire | {kinds['questionnaire_primary']} rows | 106 distinct child IDs and 106 distinct caregiver IDs |
| S01 T05 / T06 / T07 | 29 / 45 / 39 rows | Subset/alternate layouts; not additional confirmed submissions |
| S05 T07 caregiver links | {kinds['caregiver_link']} rows | 716 unique caregiver IDs covering 370 child IDs |
| Daily attendance sheets | {len(att)} worksheets / {kinds['daily_attendance']:,} child-sheet rows | Repeated child roster observations across periods/services |
| Literal attendance marks | {sum(x['nonempty_marks'] for x in att):,} cells | P: 17,788; A: 6,899; includes marks with unresolved headers |
| Blank date-grid slots | {sum(x['blank_date_slots'] for x in att):,} cells | Unknown/not recorded; never interpreted as absent |
| S12 monthly ADL visit-slot sheets | {kinds['adl_visit_slots']:,} child-sheet rows | 194 checked visit slots; blank/false flags do not become visits |
| S05 support matrices | {kinds['support_attendance']} child-sheet rows | Mixed numeric, role-coded and yes/no encodings |
| S05 support event summary | {kinds['support_event_summary']} content rows | Aggregate event totals; not individual attendance |
| Other visit/activity logs | {kinds['visit_activity_log']} candidate content rows | Requires event-grain review |
| S03 historical visits | {kinds['historical_visits']} rows | Historical roster/visit material; import period unapproved |
| S03 supplemental child sheets | {kinds['child_supplement']} rows | Reconciliation with master unresolved |
| S03 sibling roster | {kinds['sibling_roster']} anchored rows | Header structure exists, no populated sibling records detected |

Other annual, fee and severity summaries remain separately inventoried. The combined {summary['record_rows_including_views']:,} candidate rows across all sources are not additive unique business records.

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
| Primary questionnaire score cells missing | {score['missing']} / {score['slots']:,} | Question-specific missingness differs; sibling questions may be inapplicable |
| Primary questionnaire score outside observed 1–5 numeric range | 1 | A value of 6; also appears once in an alternate view. Scale approval required |
| Questionnaire assessment-date representation | 66 text / 40 typed dates | Retain source formats; resolve locale |
| Date values not parsed by the conservative checker | {counts['unparsed_or_invalid_date']} | Includes placeholders and non-date text; not all are proven corrupt dates |
| Ambiguous numeric day/month strings | {counts['ambiguous_day_month_date']} | Approve locale before conversion |
| Attendance marks without a recognized date header | {counts['mark_without_date_header']} | Preserve source column; cannot assign a date automatically |
| Unresolved candidate date headers | {counts['unresolved_date_header']} | Includes malformed text/formula-cache gaps |
| Static attendance period / date-header disagreements | {sum(x['date_header_period_disagreements'] for x in extra['attendance_calendar'])} columns | 86/92 sheets had usable static period metadata; review the mismatches |
| ADL checked visit without date | {sum(x['checked_without_date'] for x in extra['adl'])} / 194 | Do not invent visit dates |
| Exact full-row duplicate excess | {counts['exact_record_duplicate_excess']} | 1 severity view, 1 roster, 21 activity-log rows; repeated plans may be legitimate |
| Surrounding whitespace | {counts['surrounding_whitespace']} cells | Normalize only with documented policy; keep original |
| Formula cells without a returned cache value | {counts['formula_cache_missing']:,} / {summary['formulas']:,} formulas | Can be intentional blank/template output or export behavior; not necessarily a failed calculation |
| Excel error / invalid date serial | {summary['excel_error_cells']} cell | S03 T11 A29; raw snapshot preserved |
| Contact/email format review flags | {sum(x['candidate_format_review_count'] for x in extra['contacts'])} / {sum(x['nonblank'] for x in extra['contacts'])} nonblank cells | Includes dummy placeholders; phone/email syntax heuristics only, not confirmed invalidity |

Counts are cell/row occurrences and can overlap; the same underlying issue may recur in a view. They must not be summed into a count of affected people. Every issue retains source alias, worksheet and row/cell references in the evidence; no record values are logged.

## Categories, rules and formulas

Observed daily attendance literals are P and A. Their operational meanings, treatment of blank/weekend/service-not-scheduled cells and denominator are still unapproved. Master current-program has five distinct values and child-status has three. The complete observed category dictionaries, case/whitespace variants and counts are in the field evidence; values outside a small generic safe vocabulary are pseudonymized, including diagnostic and NGO-specific categories. These tokens preserve distinctions without inventing a clinical taxonomy or treating synonyms as equal.

The primary questionnaire has 27 numeric item columns E:AE, three open-ended response columns AF:AH, recommendation AI and derived columns AJ:AY, plus caregiver ID AZ and child ID BA. Headers expose section maxima (30,20,30,20,25,10). Source formula signatures include a percentage divisor of 135 and a recommendation formula with numeric constants 0 and 100. Their presence is source evidence, not an approved scoring definition; source totals, recommendation inclusion, missing-answer policy and interpretation thresholds need review before recreation. See [additional-checks.json](evidence/additional-checks.json).

Support-group values use numeric counts, M/F variants and Yes-style entries, while ADL flags are booleans. They cannot be forced into the daily attendance P/A vocabulary. No controlled enum, deduplication rule, business range or scoring rule has been silently imposed.

## Verification boundary

The checks confirm file/sheet coverage, checksum integrity, lineage retention, reproducible aggregate counts, candidate links and synthetic privacy/regression behavior. They do not certify business correctness, live Google formula recalculation, source completeness beyond accessible folder results, or schema approval. No Supabase connection, table or migration was created.
'''
 (ROOT/'docs/02-data-profiling.md').write_text(text)
 print('Rendered source inventory, worksheet appendix, column CSV and profiling summary.')

if __name__=='__main__':main()
