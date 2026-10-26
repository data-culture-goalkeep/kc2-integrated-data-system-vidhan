# Stage 1 — Data profiling

Status: NGO record profiling blocked by absent source data. Counts below were computed with `scripts/inspect_sources.py`; no figures were estimated.

## Observed statistics

| Measure | Result | Interpretation |
| --- | ---: | --- |
| Uploaded input files found | 1 | Organisational guidelines only |
| Files in library-files / shared / scratch | 0 / 0 / 0 | Local scan results only |
| Repository context files initially present | 1 | README.md |
| Tabular input candidates | 0 | No NGO spreadsheet or data extract found |
| Worksheets in supplied input | 0 | DOCX, not a workbook |
| Guideline body paragraphs including table cells | 604 | Document structure |
| Guideline tables / table rows | 2 / 14 | Guidance tables, not business records |
| Embedded images / comments | 5 / 2 | Reviewed as guideline context |
| NGO business records | Unknown | No dataset received |

## Checks that cannot yet run

| Requested check | Result | Evidence required |
| --- | --- | --- |
| Column names, source types, sample structure | Not assessable | Authorized source sheets/extracts |
| Missing values and completeness | Not assessable | Records and field requirements |
| Exact and semantic duplicates | Not assessable | Records, grain and identity rules |
| Unique identifiers and candidate keys | Not assessable | Values and cross-file identifier scope |
| Relationships and orphan references | Not assessable | Multiple relevant sources and confirmed keys |
| Inconsistent categories and formats | Not assessable | Actual observed categories and formats |
| Invalid dates, numeric values and identifiers | Not assessable | Values plus locale, ranges and domain rules |
| Contradictory fields and temporal scope | Not assessable | Source data and discovery definitions |

No clean-data finding, duplicate rate, completeness percentage or passed business validation is asserted. Missing input is a discovery blocker, not a source-data defect.

## Recommended profiling increment after intake

1. Preserve originals and checksum them; make sanitized copies locally before AI exposure. Review hidden sheets, comments, formulas, metadata and free text for sensitive content as well as visible cells.
2. Enumerate every worksheet, including hidden ones; distinguish headers, blank rows, totals, merged cells and genuine records. Preserve file, sheet and original row reference; distinguish formula text from cached values.
3. Calculate per-sheet row counts and per-column null/blank counts, inferred type distributions, distinct counts, duplicate groups and invalid-value counts. Report the denominator and parsing method for each metric. Avoid raw sample values in logs.
4. Test candidate keys within and across sources; distinguish exact duplicates from repeated observations. Keep leading-zero identifiers as text. Do not deduplicate or repair ambiguous dates without approved rules.
5. Produce aggregate reports and restricted row-reference issue logs. Reconcile profiled rows with accepted, rejected and explicitly excluded rows. Explain exclusions and multi-row transformations before any migration.

These are technical recommendations for the next Stage 1 increment, not findings about an unseen dataset. Business-validity tests depend on confirmed rules; format-based checks alone cannot establish validity.
