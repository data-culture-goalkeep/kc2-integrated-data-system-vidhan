# Stage 4A — Executable source-to-target mapping

This is the final technical mapping for the current preparation snapshot, not approval of pending business semantics. Machine-readable detail: [all source coordinates](evidence/etl-source-target-mapping.csv), [155 worksheet contracts](evidence/etl-worksheet-contracts.json), and [classification counts](evidence/etl-mapping-summary.json). Each entry names source/sheet/native sheet ID, column/header, grain, targets, transformations, identifier rules, validation and approval gates.

Coverage: **5,186/5,186 column positions**, including empty/template columns, across **155 worksheets / 12 files**. Classification: 63 CONFIRMED, 573 TECHNICAL, 4,550 PENDING. These counts classify column positions, not records or approved operational fields. All values receive a sanitized source representation even when their operational projection is pending.

| Dataset | Executable projection | Identity and limits |
| --- | --- | --- |
| S03/T01 child master | children, restricted profiles; explicit programme slot records | 371 exact unique child IDs; no name deduplication; dates/financial numbers withheld |
| S05/T07 caregiver register | caregivers, child_caregivers | 716 unique caregiver IDs, 716 verified pairs covering 370 children |
| S01/T01 primary questionnaire | source-scoped inactive instrument definition, 31 items, 106 responses, 3,286 answer slots | Exact verified child-caregiver pairs; 60 source name disagreements preserved; no canonical name replacement or calculated score |
| Daily attendance sheets | source records, unapproved identity candidates | 2,142 candidate rows; no accepted name-only link; no operational attendance rows |
| ADL sheets | source records, unapproved identity candidates | 1,219 roster rows; 194 checked visit slots, four without dates; no operational ADL rows |
| Support matrices and other views | source records, candidates where supported | Event grain, identity and category semantics pending; no inferred additional facts |
| All headers/summaries/templates/repeated views | artifact worksheet manifest and source payloads | All 20,432 nonempty row coordinates retained once; views are not counted as new people/events |

Source columns without operational targets are explicitly represented in `source_records.cell_payload`; their header/coordinate definitions are in `source_artifacts.worksheet_manifest`. No source field is silently discarded. This preserves sanitized information; it does not reproduce raw personal identifiers or unredacted free text. Protected originals remain the authoritative raw record.

Candidate operational counts (all imported facts pending):

| Target table | Direct ETL rows |
| --- | ---: |
| reference_values | 47 |
| children | 371 |
| child_private_profiles | 371 |
| caregivers | 716 |
| child_caregivers | 716 |
| program_changes | 128 |
| questionnaire_responses | 106 |
| questionnaire_items | 31 |
| questionnaire_answers | 3286 |
| attendance_observations | 0 |
| support_observations | 0 |
| adl_visits | 0 |
| source_artifacts | 12 |
| source_records | 20432 |
| source_provenance | 5772 |
| access_memberships | 0 |
| identity_candidates | 2089 |
| recovery_actions | 0 |
| record_audit_events | 0 |

`record_audit_events` receives **28,293 server-generated** rows in the first local load; its zero above means zero direct ETL inserts. Total direct target inserts: **34,077**. Provenance and answer slots intentionally expand source rows. Restricted answers include 86 missing numeric slots represented as missing/NULL; missing is never zero. The observed S9 value 6 is retained for review, not clamped or interpreted. Other candidate-score anomalies remain source findings until scoring is approved.
