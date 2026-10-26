# Final recommended Phase 1 model — prepared, not applied

Nineteen tables. Technical recommendation ready for owner review; SQL application and role activation remain prohibited. Supabase-managed auth tables are additional and not counted. Full specification: [final-model.json](evidence/final-model.json).

## Changes from the 17-table draft

| Change | Reason and preservation |
| --- | --- |
| Defer activity_logs (−1) | Event versus planning grain remains unresolved; retain every original cell in source_records and headers in source_artifacts. No event is discarded. |
| Add identity_candidates (+1) | Persist attendance candidate identities, evidence, method and resolution independently from accepted facts. |
| Add recovery_actions (+1) | Persist original/recovered values, donor, method, validation flags and run history without mutating originals. |
| Add record_audit_events (+1) | Retain operational and permission change history; current updated_at alone loses historical changes. |
| children | Unique, literal child_business_id replaces source_admission_number; internal UUID references remain. |
| caregivers / child_caregivers | Authoritative caregiver_business_id belongs to person; relationship stores child/caregiver pair, not a child-scoped copy of the person ID. |
| Security and audit | Private schema, explicit membership, approved controlled values, accountable writes, soft deletion and immutable evidence. No role grants become effective without approved role definitions/memberships. |

## General invariants

All identifier strings retain exact case and leading zeros. Primary keys are UUIDs except one-to-one child profile, composite vocabulary/code, and auth-user membership. FK deletion is RESTRICT; no API permanent deletion is granted. Missing semantic values stay NULL or staged. Evidence tables retain source versions, native sheet key, row, column and mapping rule. Audit fields are server stamped; append-only audit events retain changes. PostgreSQL defaults and exact CHECK expressions are authoritative in the three prepared SQL files.

Review states, origin and technical processing flags are implementation vocabulary, not invented NGO categories. No questionnaire scoring, category seeds, missing visit dates or name-only approved identities are fabricated.

## Complete table specifications

### public.reference_values

Database-controlled source-scoped categories; replaces separate PROGRAM-only lookup. Grain: One approved vocabulary/code.

Required because: Database-controlled source-scoped categories; replaces separate PROGRAM-only lookup.

Primary key: `vocabulary, code`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: Primary/unique keys only. See generated SQL for additional candidate partial indexes.


### public.children

Canonical operational identity/context under RLS; display names remain personal. Grain: One resolved source master identity.

Required because: Canonical operational identity/context under RLS; display names remain personal.

Primary key: `id`. Unique keys: `child_business_id`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| program_vocabulary, current_program_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| program_vocabulary, admitted_program_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| status_vocabulary, child_status_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: program_vocabulary, current_program_code (FK lookup/referential action candidate; benchmark before redundant indexes); program_vocabulary, admitted_program_code (FK lookup/referential action candidate; benchmark before redundant indexes); status_vocabulary, child_status_code (FK lookup/referential action candidate; benchmark before redundant indexes). See generated SQL for additional candidate partial indexes.


### gk_private.child_private_profiles

Separates restricted child/family/health/financial attributes from operational reads. Grain: Zero or one restricted profile per child.

Required because: Separates restricted child/family/health/financial attributes from operational reads.

Primary key: `child_id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| child_id | children(id) | 1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: Primary/unique keys only. See generated SQL for additional candidate partial indexes.


### gk_private.caregivers

Resolved caregiver identity; no global person deduplication by display name. Grain: One caregiver per verified authoritative caregiver business identifier.

Required because: Resolved caregiver identity; no global person deduplication by display name.

Primary key: `id`. Unique keys: `caregiver_business_id`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: Primary/unique keys only. See generated SQL for additional candidate partial indexes.


### public.child_caregivers

Preserves each child/caregiver association independently from person identity. Grain: One child/caregiver association.

Required because: Preserves each child/caregiver association independently from person identity.

Primary key: `id`. Unique keys: `id, child_id`; `child_id, caregiver_id`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| child_id | children(id) | 1 parent per row; RESTRICT |
| caregiver_id | caregivers(id) | 1 parent per row; RESTRICT |
| role_vocabulary, role_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: child_id (FK lookup/referential action candidate; benchmark before redundant indexes); caregiver_id (FK lookup/referential action candidate; benchmark before redundant indexes); role_vocabulary, role_code (FK lookup/referential action candidate; benchmark before redundant indexes). See generated SQL for additional candidate partial indexes.


### public.program_changes

Unpivots promotion slots without inventing interval ends. Grain: One source promotion observation.

Required because: Unpivots promotion slots without inventing interval ends.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| child_id | children(id) | 1 parent per row; RESTRICT |
| program_vocabulary, program_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: program_vocabulary, program_code (FK lookup/referential action candidate; benchmark before redundant indexes); child_id, promotion_date (proposed common entry/report filter). See generated SQL for additional candidate partial indexes.


### public.questionnaire_responses

Submission context; references the validated pair instead of redundant independent IDs. Grain: One approved response row/submission.

Required because: Submission context; references the validated pair instead of redundant independent IDs.

Primary key: `id`. Unique keys: `id, definition_key`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| child_caregiver_id | child_caregivers(id) | 1 parent per row; RESTRICT |
| definition_vocabulary, definition_key | reference_values(vocabulary, code) | 1 parent per row; RESTRICT |
| program_vocabulary, program_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| centre_vocabulary, centre_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: definition_vocabulary, definition_key (FK lookup/referential action candidate; benchmark before redundant indexes); program_vocabulary, program_code (FK lookup/referential action candidate; benchmark before redundant indexes); centre_vocabulary, centre_code (FK lookup/referential action candidate; benchmark before redundant indexes); child_caregiver_id, assessment_date (proposed common entry/report filter). See generated SQL for additional candidate partial indexes.


### public.questionnaire_items

Actual question definitions; one version key without premature questionnaire-framework tables. Grain: One actual question column within an approved definition.

Required because: Actual question definitions; one version key without premature questionnaire-framework tables.

Primary key: `id`. Unique keys: `definition_key, item_key`; `definition_key, ordinal`; `id, definition_key`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| definition_vocabulary, definition_key | reference_values(vocabulary, code) | 1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: definition_vocabulary, definition_key (FK lookup/referential action candidate; benchmark before redundant indexes). See generated SQL for additional candidate partial indexes.


### gk_private.questionnaire_answers

Typed values replace untyped recorded_value; preserves missing answers separately. Grain: One response/item.

Required because: Typed values replace untyped recorded_value; preserves missing answers separately.

Primary key: `id`. Unique keys: `response_id, item_id`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| response_id, definition_key | questionnaire_responses(id, definition_key) | 1 parent per row; RESTRICT |
| item_id, definition_key | questionnaire_items(id, definition_key) | 1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: response_id, definition_key (FK lookup/referential action candidate; benchmark before redundant indexes); item_id, definition_key (FK lookup/referential action candidate; benchmark before redundant indexes). See generated SQL for additional candidate partial indexes.


### public.attendance_observations

Dated source marks kept distinct by service; unresolved names/dates remain staged. Grain: One resolved child/service/source-date observation.

Required because: Dated source marks kept distinct by service; unresolved names/dates remain staged.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| child_id | children(id) | 1 parent per row; RESTRICT |
| service_vocabulary, service_code | reference_values(vocabulary, code) | 1 parent per row; RESTRICT |
| mark_vocabulary, mark_code | reference_values(vocabulary, code) | 1 parent per row; RESTRICT |
| program_vocabulary, program_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: service_vocabulary, service_code (FK lookup/referential action candidate; benchmark before redundant indexes); mark_vocabulary, mark_code (FK lookup/referential action candidate; benchmark before redundant indexes); program_vocabulary, program_code (FK lookup/referential action candidate; benchmark before redundant indexes); child_id, attendance_date (proposed common entry/report filter). See generated SQL for additional candidate partial indexes.


### public.support_observations

Source-cell support observations; not necessarily one person or a daily P/A event. Grain: One approved support matrix cell.

Required because: Source-cell support observations; not necessarily one person or a daily P/A event.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| child_id | children(id) | 1 parent per row; RESTRICT |
| participant_link_id, child_id | child_caregivers(id, child_id) | 0..1 parent per row; RESTRICT |
| program_vocabulary, program_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: child_id (FK lookup/referential action candidate; benchmark before redundant indexes); participant_link_id, child_id (FK lookup/referential action candidate; benchmark before redundant indexes); program_vocabulary, program_code (FK lookup/referential action candidate; benchmark before redundant indexes). See generated SQL for additional candidate partial indexes.


### public.adl_visits

Preserves true visit flags and undated historical exceptions. Grain: One checked visit-slot observation.

Required because: Preserves true visit flags and undated historical exceptions.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| child_id | children(id) | 1 parent per row; RESTRICT |
| program_vocabulary, program_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: program_vocabulary, program_code (FK lookup/referential action candidate; benchmark before redundant indexes); child_id, visit_date (proposed common entry/report filter). See generated SQL for additional candidate partial indexes.


### gk_private.source_artifacts

Immutable snapshot identity and worksheet/column schema. Grain: One authorized source-file version.

Required because: Immutable snapshot identity and worksheet/column schema.

Primary key: `id`. Unique keys: `source_namespace, file_code, version_sha256`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: Primary/unique keys only. See generated SQL for additional candidate partial indexes.


### gk_private.source_records

Restricted staging/reconciliation for every nonempty source row, including unresolved/derived fields. Grain: One artifact/native-sheet/original-row.

Required because: Restricted staging/reconciliation for every nonempty source row, including unresolved/derived fields.

Primary key: `id`. Unique keys: `artifact_id, native_sheet_key, source_row`.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| artifact_id | source_artifacts(id) | 1 parent per row; RESTRICT |

Indexes: processing_state, artifact_id (proposed common entry/report filter). See generated SQL for additional candidate partial indexes.


### gk_private.source_provenance

Many-source-row/cell to one target without unconstrained polymorphic IDs. Grain: One source-column group -> one typed target/field group.

Required because: Many-source-row/cell to one target without unconstrained polymorphic IDs.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| source_record_id | source_records(id) | 1 parent per row; RESTRICT |
| child_id | children(id) | 0..1 parent per row; RESTRICT |
| private_profile_child_id | child_private_profiles(child_id) | 0..1 parent per row; RESTRICT |
| caregiver_id | caregivers(id) | 0..1 parent per row; RESTRICT |
| child_caregiver_id | child_caregivers(id) | 0..1 parent per row; RESTRICT |
| program_change_id | program_changes(id) | 0..1 parent per row; RESTRICT |
| response_id | questionnaire_responses(id) | 0..1 parent per row; RESTRICT |
| item_id | questionnaire_items(id) | 0..1 parent per row; RESTRICT |
| answer_id | questionnaire_answers(id) | 0..1 parent per row; RESTRICT |
| attendance_id | attendance_observations(id) | 0..1 parent per row; RESTRICT |
| support_id | support_observations(id) | 0..1 parent per row; RESTRICT |
| adl_id | adl_visits(id) | 0..1 parent per row; RESTRICT |
| reference_vocabulary, reference_code | reference_values(vocabulary, code) | 0..1 parent per row; RESTRICT |

Indexes: source_record_id (FK lookup/referential action candidate; benchmark before redundant indexes); child_id (FK lookup/referential action candidate; benchmark before redundant indexes); private_profile_child_id (FK lookup/referential action candidate; benchmark before redundant indexes); caregiver_id (FK lookup/referential action candidate; benchmark before redundant indexes); child_caregiver_id (FK lookup/referential action candidate; benchmark before redundant indexes); program_change_id (FK lookup/referential action candidate; benchmark before redundant indexes); response_id (FK lookup/referential action candidate; benchmark before redundant indexes); item_id (FK lookup/referential action candidate; benchmark before redundant indexes); answer_id (FK lookup/referential action candidate; benchmark before redundant indexes); attendance_id (FK lookup/referential action candidate; benchmark before redundant indexes); support_id (FK lookup/referential action candidate; benchmark before redundant indexes); adl_id (FK lookup/referential action candidate; benchmark before redundant indexes); reference_vocabulary, reference_code (FK lookup/referential action candidate; benchmark before redundant indexes). See generated SQL for additional candidate partial indexes.


### gk_private.access_memberships

Application authorization independent of Google sign-in and business caregivers. Grain: One admitted auth user in this dedicated project.

Required because: Application authorization independent of Google sign-in and business caregivers.

Primary key: `user_id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| user_id | auth.users(id) | 1 parent per row; RESTRICT |
| role_vocabulary, role_code | reference_values(vocabulary, code) | 1 parent per row; RESTRICT |
| archived_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: role_vocabulary, role_code (FK lookup/referential action candidate; benchmark before redundant indexes). See generated SQL for additional candidate partial indexes.


### gk_private.identity_candidates

Preserve exact-ID matches and unapproved name/context candidates. Grain: One staged row/candidate identity/method.

Required because: Preserve exact-ID matches and unapproved name/context candidates.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| source_record_id | source_records(id) | 1 parent per row; RESTRICT |
| child_id | children(id) | 0..1 parent per row; RESTRICT |
| caregiver_id | caregivers(id) | 0..1 parent per row; RESTRICT |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: source_record_id (source investigation). See generated SQL for additional candidate partial indexes.


### gk_private.recovery_actions

Append-only original/proposed value, donor, method and validation audit. Grain: One recovery/suggestion per source cell and run.

Required because: Append-only original/proposed value, donor, method and validation audit.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| source_record_id | source_records(id) | 1 parent per row; RESTRICT |
| child_id | children(id) | 0..1 parent per row; RESTRICT |
| caregiver_id | caregivers(id) | 0..1 parent per row; RESTRICT |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| donor_source_record_id | source_records(id) | 0..1 parent per row; RESTRICT |

Indexes: source_record_id (source investigation). See generated SQL for additional candidate partial indexes.


### gk_private.record_audit_events

Append-only operational and access-change history; no API insertion. Grain: One database-generated row change event.

Required because: Append-only operational and access-change history; no API insertion.

Primary key: `id`. Unique keys: primary key only.

| Columns | References | Cardinality / deletion |
| --- | --- | --- |
| created_by | auth.users(id) | 0..1 parent per row; RESTRICT |
| updated_by | auth.users(id) | 0..1 parent per row; RESTRICT |

Indexes: Primary/unique keys only. See generated SQL for additional candidate partial indexes.
