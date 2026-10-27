# Stage 4A — Exception and recovery strategy

Every nonempty row has exactly one primary status in the protected `work/etl/exception-ledger.json`: successfully_transformed, preserved_as_source_only, awaiting_identity_resolution, awaiting_business_rule_approval or rejected_validation. Target entities and zero or more field-level reasons/resolutions are additional metadata. A transformed row can still contain withheld fields or name conflicts; status is not a declaration that every field is approved. `loaded` is recorded only by an actual successful database receipt; Stage 4A has no remote loaded rows.

The machine-readable internal ledger includes source alias, worksheet, original row coordinate, target entity, reason, recommended resolution and status. Immutable source payloads are preserved independently from operational facts. Existing duplicate views remain traceable, and exact target IDs prevent duplicate projected facts. Rejected or unmatched rows never disappear. Loader failures record batch, sanitized SQLSTATE and source references, stop execution and do not count rolled-back receipts. Private diagnostics never contain raw SQL error detail that might echo source values.

## Approved identity behavior

371 child IDs and 716 caregiver IDs are exact, unique business identities in the protected verified dataset. Relationships cover 370 children. All 106 primary questionnaire ID pairs agree with that relationship register; 60 name disagreements remain flags and original sanitized source evidence. Canonical child names are unchanged. Attendance, ADL and support candidates never create accepted FK links without verified identifiers or a separately approved resolution. Across these investigations 2,089 candidate rows are retained for review; a candidate is not a matched event.

For attendance alone, 1,009 of 2,142 rows have one unapproved name/alias candidate, 74 have multiple candidates and 1,059 have none. None are automatically accepted. ADL retains 194 checked visit slots, including four without dates, inside 1,219 roster records. Zero attendance/ADL/support operational rows are planned. Seven unresolved auxiliary literal child-ID occurrences remain source evidence; they do not add children or override the master.

## Recovery

The reusable engine requires exact verified identity, equivalent field meaning, authoritative donor and no contradiction. Recovery overlays copy only sanitized donor cells, retain original missing state, donor/source coordinates, method and validation evidence, and never edit originals. Nonmissing disagreements are suggestions, not overwrites. Chronology-sensitive dates cannot be recovered until date fidelity is approved. Actual safe recoveries in this snapshot: zero. Synthetic tests demonstrate safe recovery, conflict rejection and date blocking; they do not imply real-data corrections were found.

## Goalkeep Google Sheets report

The private report has one tab per source alias S01–S12 and exactly the required columns: Source file, Row reference, Reason for failure. It contains only source aliases, worksheet/row references and allowlisted preparation reason codes/statuses. No names, personal IDs, clinical answers, raw filenames, cell values or credentials are published. The private source manifest lets an authorized analyst resolve aliases. Original files and sharing permissions are unchanged.

[Report verification receipt](evidence/etl-google-failure-log.json) records the destination and full readback. The report contains preparation exceptions and warnings, not remote load failures. Normal source-only retention without other findings is excluded. Source rows with multiple reasons appear once with joined codes: 11,222 report rows versus 28,829 internal reason entries. Do not compare these counts to entity totals. Future Stage 4B should refresh the same report after actual receipts, retaining source tabs and the three required columns. Sharing with a PM or other account needs an authorized destination; the workbook is currently owner-private.

The workbook uses frozen headers, wrapped text and filters. Formatting is configured through native Sheets requests; no rendered visual inspection is claimed. `build_failure_report.py` regenerates protected report payloads without publishing sensitive content. Never send the internal source payload ledger directly to a spreadsheet.

Candidate generation reuses exact identifiers and normalized names/aliases across available sheets. Programme, school/group context and date evidence remain preserved for review; no inferred category equivalence, synthetic chronology or name-only match is used to accept an identity. Context-based adjudication remains a business gate.
