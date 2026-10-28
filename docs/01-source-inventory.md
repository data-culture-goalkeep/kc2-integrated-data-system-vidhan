# Stage 1 — Source inventory

Status: connected-source discovery completed with unresolved business rules; no schema approved.

## Source coverage and preservation

The owner-supplied Google Drive folder returned 12 native Google Sheets and no subfolders. A separate folder-only search returned no child folders; a document-type search returned no additional document results. All 12 spreadsheets were downloaded as full XLSX snapshots through the authenticated connection. Their 155 worksheet counts and native sheet order were checked against Google Sheets metadata. There were no separate CSV, Word, PDF, interview or discovery-note files among the returned items. Workbook questionnaire guidance and reporting sheets were included in inspection. These bounded connector results describe what was returned and accessible, not a certification that no separately shared or inaccessible project document exists.

The native Drive originals were never edited. Their modified timestamps were unchanged between initial listing and the post-download metadata check. XLSX snapshots are immutable local exports, not byte-for-byte native Google Sheets originals. Each has a SHA-256 checksum; local snapshots are read-only. All worksheets were read, including empty/supporting sheets. Two long native tab titles were shortened in the XLSX export; the restricted worksheet map retains both names, ordinal and native sheet ID.

## Workbooks

| Source | Subject | Worksheets | Recognized candidate rows, including views | Export bytes |
| --- | --- | ---: | ---: | ---: |
| [S01](https://docs.google.com/spreadsheets/d/1L7KYOnESgoevqGbQiiv-a6td6lwvTHtIV9AAc5I55mo/edit?usp=drivesdk) | Parent quality-of-life questionnaire | 7 | 219 | 99,764 |
| [S02](https://docs.google.com/spreadsheets/d/1UMJx4urtxJ3z0-ZlPf4rlNJBln4N8G0tefRxzl1fiKQ/edit?usp=drivesdk) | PT attendance | 14 | 420 | 300,940 |
| [S03](https://docs.google.com/spreadsheets/d/1VeNgkWxBSujQal12bz2UKq8w-HEksZEegNEYmVYuotw/edit?usp=drivesdk) | Child master and supporting registers | 12 | 1,040 | 647,463 |
| [S04](https://docs.google.com/spreadsheets/d/1w-IJ6BMm3XJEyruUsuzQzGq0mY3ubx0q2Vs6lpPckwM/edit?usp=drivesdk) | Speech attendance | 14 | 465 | 294,004 |
| [S05](https://docs.google.com/spreadsheets/d/17XSQjwZGtc_nqfKIkrv3CoUCSz4wH4gvGdaZXZ5yQTA/edit?usp=drivesdk) | Support-group / caregiver records | 8 | 993 | 504,938 |
| [S06](https://docs.google.com/spreadsheets/d/1yWf-6fmLh5RjzWn8wGzJoAhKtdJVKGLN1UjSw5URjyw/edit?usp=drivesdk) | OT fine-motor attendance | 14 | 183 | 103,057 |
| [S07](https://docs.google.com/spreadsheets/d/1jUsFpEzELac5c4slKNPrfH_wrXgks0H8a9353oczcEM/edit?usp=drivesdk) | PVSW attendance and activities | 16 | 444 | 483,909 |
| [S08](https://docs.google.com/spreadsheets/d/1gWCYL8ZKo4oT5hRfLdKIkBK2peZtefnyXSySgipwroA/edit?usp=drivesdk) | EI attendance and activities | 14 | 536 | 304,364 |
| [S09](https://docs.google.com/spreadsheets/d/1KFaS6OtRewhQvdi2dne2AW4jze3_5f1NFY99o99fhl0/edit?usp=drivesdk) | FA attendance and activities | 14 | 331 | 323,443 |
| [S10](https://docs.google.com/spreadsheets/d/1WOJcf_ZbVIhUzZtOSKX_fH-eO4N5-2lPWazzJx5L9HY/edit?usp=drivesdk) | Nursery attendance and activities | 14 | 236 | 288,093 |
| [S11](https://docs.google.com/spreadsheets/d/1QAasVuk9X0AIG-ymPxhnZ1NSwrjH0kzx2iCaF3k69P4/edit?usp=drivesdk) | Vision attendance | 16 | 185 | 317,449 |
| [S12](https://docs.google.com/spreadsheets/d/1gsZ5inu7Hmd-S_bH0EC3onaq7GdR8k4DsHORca-vRCw/edit?usp=drivesdk) | ADL visits and annual summaries | 12 | 1,469 | 212,811 |

Totals: **12 workbooks, 155 worksheets, 145,785 nonempty cells**. The 6,521 recognized candidate rows include rosters, derived views, summaries and repeated observations. They are not a distinct-person count or an import target count. Unclassified/supporting prose sheets have nonempty-row counts, not fabricated business-record counts.

The previously supplied guidelines DOCX and unchanged 35-byte README remain contextual inputs. The complete guidelines, including diagrams/comments, were read in the initial run. Page ranges in the owner request are not independently verified DOCX pagination; requirements cite project-team §3 steps 8–22, §5 and §6. No linked reference implementation was treated as selected-project data.

## Worksheet and cell lineage

See [all worksheets](source-worksheets.md), [complete aggregate profile](evidence/data-profile.json), [column profile](evidence/field-profiling.csv), and [Drive metadata evidence](evidence/drive-sources.json). Public reports use source aliases S01–S12 and sheet aliases T01 onward rather than NGO-specific filenames or tab names. Each worksheet has its actual Google sheet ID in the evidence. Original record row numbers and issue cell coordinates are preserved. A private manifest maps aliases to the original source file/title, exact native/exported worksheet names and local snapshot path. No identifiers, names, contacts, free-text responses or secrets are published in these reports.

## Sanitized working copies

All 155 sheets have separate JSONL working copies in restricted, Git-ignored local storage. They preserve source alias, worksheet alias, row and column positions. Unknown strings, names, contacts, IDs, health/financial categories and NGO-specific details are keyed pseudonyms; approved generic field labels and a small generic category vocabulary are retained. Dates in data cells become synthetic dates. Formula text and workbook metadata/comments/links/pivot caches are absent from these copies. Dates/codes needed for actual profiling were inspected locally in the untouched snapshots; only aggregates and references were exposed to AI. These samples intentionally do not preserve real date chronology or formula execution.

Checksums cover originals and sanitized outputs. Pseudonyms are stable for identical original values within this run; the HMAC key and redaction terms stay outside Git. Exact spelling variants are preserved as different tokens, while separate local normalized comparisons identify whitespace/case issues. The “Dummy Data” filenames were not accepted as proof of sanitization. No sanitized data or re-identification material was committed. See [reproduction and protection](sanitization-and-reproducibility.md).
