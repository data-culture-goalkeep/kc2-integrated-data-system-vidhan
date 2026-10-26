# Stage 2 — Raw versus organized model

**DRAFT — structural comparison, not an approved schema.**

## Model A: actual raw source structure

Twelve spreadsheets contain 155 heterogeneous worksheets, not 155 proven entities or database tables. Counts, schemas, source IDs and row references come from frozen Stage 1 evidence. The raw structure includes 6,521 recognized candidate rows, alternate views, formula templates, reports and supporting prose. It is not a unique-record total.

| Source | Raw shape and important fields | Candidate rows / worksheets | Raw identity / relationship | Repetition and limitations |
| --- | --- | --- | --- | --- |
| S01 | Questionnaire A:D context, E:AI items, AJ:AY derived scores, AZ:BA IDs | 219 / 7 | Explicit child/caregiver IDs match the source link | 27 numeric columns plus text/recommendation; views overlap; 60 names disagree |
| S02 | PT named rosters, monthly P/A date grids, annual reports | 420 / 14 | Names/program, no approved master crosswalk | Dates repeated as columns and same names repeated by month |
| S03 | Child register B/C identity, D:F programs/status, personal fields, five promotion pairs; fee/history/sibling/severity sheets | 1040 / 12 | 371 unique admissions; parent contacts are role-labelled columns | Repeated names; mixed types; sibling header-only; supplements/reports overlap |
| S04 | Speech named rosters and monthly P/A grids | 465 / 14 | Name-based candidates only | Date/header issues and repeated month layouts |
| S05 | Support matrices, explicit caregiver/child link, aggregate event summary | 993 / 8 | 716 unique caregiver codes; 370 child IDs match admissions | Counts/M/F/Yes are not one universal attendance code |
| S06 | OT fine-motor named rosters and monthly grids | 183 / 14 | Name/program only in observations | Blank date slots do not mean absent |
| S07 | PVSW grid, TRAINEE NAME columns, activity notes and annual view | 444 / 16 | Trainee-name population/crosswalk unapproved | 350 rows were absent from prior name-link coverage; now compared separately |
| S08 | EI rosters, monthly date grids and visit/activity tables | 536 / 14 | Name/batch/context, not a global FK | Some observations lack recognized date headings |
| S09 | FA rosters, monthly grids and activity log | 331 / 14 | Name/batch, no approved crosswalk | Formula templates inflate dimensions; activity rows need grain review |
| S10 | Nursery rosters, grids, visit/plan tables and annual view | 236 / 14 | Name/batch, unresolved activity key | 21 repeated description-row excess may be legitimate plans |
| S11 | Vision attendance rosters/grids/annual view and empty sheet | 185 / 16 | Name/program only | Empty tab and formatting rows are source structure, not records |
| S12 | Five Visit flag/date pairs per monthly child row, annual visits/goals | 1469 / 12 | Child name/program, not an approved visit/person key | 194 true slots; four undated; false flags not events |

[Worksheet inventory](source-worksheets.md) gives all 155 tabs and native IDs. [Column profiles](evidence/field-profiling.csv) cover 5,044 statistical field instances; the review adds 142 header-only/coordinate slots to account for every one of the 5,186 source column positions. Eight worksheets have no detected record header; their prose/cells remain source payloads, not invented domain fields. Empty and all-formula rows are retained/reconciled separately.

## Model B: draft organized relational structure

17 proposed tables (16 core plus conditional activity_logs), with no database created. The original 12-entity conceptual model remains available in the archive and Git baseline. Of the 17, 13 are domain/lookup components and four support source versioning, staging, typed provenance and authenticated access membership. Supabase-managed auth.users is external to this count.

| Table | Record grain | Why it exists |
| --- | --- | --- |
| reference_values | One approved vocabulary/code | Database-controlled source-scoped categories; replaces separate PROGRAM-only lookup |
| children | One resolved source master identity | Canonical operational identity/context under RLS; display names remain personal |
| child_private_profiles | Zero or one restricted profile per child | Separates restricted child/family/health/financial attributes from operational reads |
| caregivers | One identified caregiver source identity pending scope review | Resolved caregiver identity; no global person deduplication by display name |
| child_caregivers | One child/caregiver association | Preserves the verified child/caregiver pair and source identifier scope |
| program_changes | One source promotion observation | Unpivots promotion slots without inventing interval ends |
| questionnaire_responses | One approved response row/submission | Submission context; references the validated pair instead of redundant independent IDs |
| questionnaire_items | One actual question column within an approved definition | Actual question definitions; one version key without premature questionnaire-framework tables |
| questionnaire_answers | One response/item | Typed values replace untyped recorded_value; preserves missing answers separately |
| attendance_observations | One resolved child/service/source-date observation | Dated source marks kept distinct by service; unresolved names/dates remain staged |
| support_observations | One approved support matrix cell | Source-cell support observations; not necessarily one person or a daily P/A event |
| adl_visits | One checked visit-slot observation | Preserves true visit flags and undated historical exceptions |
| activity_logs (conditional) | One approved activity event, not each candidate content row | Structured activity records only after row-grain/workflow approval; archive retained regardless |
| source_artifacts | One authorized source-file version | Immutable snapshot identity and worksheet/column schema |
| source_records | One artifact/native-sheet/original-row | Restricted staging/reconciliation for every nonempty source row, including unresolved/derived fields |
| source_provenance | One source-column group -> one typed target/field group | Many-source-row/cell to one target without unconstrained polymorphic IDs |
| access_memberships | One admitted auth user in this dedicated project | Application authorization independent of Google sign-in and business caregivers |

Internal UUIDs decouple database identity from unapproved/reusable source identifiers. Domain FKs use resolved keys; raw source IDs/strings are preserved and never cast directly to UUIDs. Questionnaire responses reference a child-caregiver association, while answers carry definition-consistent response/item FKs. Source-scoped reference values control dropdowns without conflating program, batch, service or role. Imports receive immutable file/row/cell provenance; manual entry uses authenticated audit identity.

## Comparison and information preservation

All raw columns and header coordinates have a declared retention location: source_records.cell_payload plus source_artifacts.worksheet_manifest and the protected immutable export. This does not mean every field has a typed curated destination. The full matrix contains 3,366 conditional named operational projections and 1,820 positions with no named business projection. Those 1,820 positions, including derived scores/views, unused structure, sibling templates, summaries and conditional activities, are explicitly listed; none is silently dropped. Any required application field among them blocks workflow approval until a projection is agreed.

Preserve snapshots before transformation, namespace identifiers, unpivot repeated date/visit/question/promotion columns, and keep distinct observation grains. Do not auto-union source views, deduplicate names, create missing dates, recompute disputed scores, or conflate source retention with approved operational readiness. Technical keys, audit fields and authentication configuration are explicitly proposed system metadata, not new NGO business facts.

See [structural decision/mapping matrix](12-data-model-comparison-matrix.md), [optimized schema specification](11-optimized-data-model.md) and [decision register](13-data-quality-decision-register.md).
