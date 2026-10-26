# Stage 2 — Optimized relational model

**DRAFT — recommendations only; analyst approval required before Supabase implementation.**

## Proposed scope and counts

The full draft has **17 tables**, including **16 core** and **1 conditional** table (`activity_logs`). The original conceptual model had 12 entities and omitted implemented source/access infrastructure. The net additions are one restricted child profile and four provenance/access support tables; PROGRAM is replaced one-for-one with reference_values. No domain was merged merely to lower the count. Auth.users is Supabase-managed and is excluded from the count.

For the 16-table variant, defer activity_logs together with its optional typed provenance column/FK/index/target group. Retain its raw records and metadata. Do not leave an FK referencing an absent optional table. Other possible future tables—sibling people, support events, clinical dictionaries, rich questionnaire lifecycle, audit-event history—are not in this draft and require approved workflows.

## Shared design rules

- UUID PKs are proposed system identities. Source codes remain text in their namespace. A source ID match is not a UUID cast or approval of name authority.
- Server-managed created_at/updated_at are timestamptz. Created_by/updated_by reference auth.users when known; imports may have null historical user with a trusted import actor_ref. Never invent an auth user. Manual writes require the real authenticated actor.
- Mutable domain rows have technical origin_kind and review_state. Unresolved source rows stay in source_records; specific allowed undated imported observations must be marked pending and traceable.
- Required fields shown below are draft database recommendations. Observed completeness does not establish a business mandatory rule. Business requiredness, source-code stability, clinical/financial ranges and canonical categories remain approval gates.
- Dates are date where day-grain is intended; timestamps are timestamptz. Phone numbers, identifiers, codes and leading zeros are text. Money may use a reviewed numeric precision (candidate numeric(14,2)); reported mixed/unknown values remain text or staged. No silent coercion.
- Lookup discriminator columns are fixed/server-generated. MATCH SIMPLE composite vocabulary/code FKs permit an unknown code NULL but cannot link a program field to a role/centre code. Technical enums/check states may be fixed; NGO values use reviewed reference rows, not hardcoded invented enums.
- Questionnaire definition_key is an approved/fingerprinted item-definition namespace, not a source-file export hash and not a new indicator. It is controlled through reference_values without a premature questionnaire-engine table.
- All business and source tables are private by default under RLS/permissions. Children and caregivers still contain personal names. child_private_profiles has a stricter grant/view/RPC boundary; row security alone does not implement field-level protection.
- Source artifacts and source-record payloads are immutable evidence; status/diagnostic updates are separately audited. In this pilot only sanitized authorized payloads may be loaded into any future test project. Original exports remain protected outside Git. No data loading is authorized now.
- Every imported target requires provenance before transaction promotion. The proposed source_provenance table uses bounded typed FK targets, exactly one target group per link, not unconstrained polymorphic entity IDs. This supports multiple source contributions with real FK checks. Server validation enforces source/target field membership. A deferred constraint trigger/import transaction gate is required; a nullable origin string alone is insufficient.
- No cascading deletion of source/person/history evidence. Prefer deactivation/archiving under an approved retention policy; no manual child deletion policy is invented.
- Index candidates below remove identical/prefix duplicates already covered by PK/unique or longer planned indexes. Final query plans/write costs must be checked on the installed PostgreSQL version after approval; no measured performance claim is made.

## Table-by-table specification

### reference_values

Database-controlled source-scoped categories; replaces separate PROGRAM-only lookup. **Grain:** One approved vocabulary/code.

**Primary key:** vocabulary, code.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| vocabulary | text | no |
| code | text | no |
| label | text | no |
| active | boolean | no |
| sort_order | integer | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- Never seed canonical meanings, roles or synonym mappings without analyst approval; preserve source-scoped distinctions

**Index candidates beyond existing keys:** PK/unique coverage is sufficient for the declared initial paths.

### children

Canonical operational identity/context under RLS; display names remain personal. **Grain:** One resolved source master identity.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| source_namespace | text | yes |
| source_admission_number | text | yes |
| display_name | text | yes |
| current_program_code | text | yes |
| admitted_program_code | text | yes |
| child_status_code | text | yes |
| program_vocabulary | text | no |
| status_vocabulary | text | no |
| joining_date | date | yes |
| dropout_date | date | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (program_vocabulary, current_program_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary
- (program_vocabulary, admitted_program_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary
- (status_vocabulary, child_status_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- program_vocabulary is server-generated fixed program discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- program_vocabulary is server-generated fixed program discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- status_vocabulary is server-generated fixed child_status discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- Source admission uniqueness is a proposed partial unique(source_namespace,source_admission_number), gated on Q02; never unique(display_name)
- Birth/joining inequality is not imposed until correction/exception handling approved; original 3 conflicts preserved

**Index candidates beyond existing keys:** (program_vocabulary, current_program_code); (program_vocabulary, admitted_program_code); (status_vocabulary, child_status_code).

### child_private_profiles

Separates restricted child/family/health/financial attributes from operational reads. **Grain:** Zero or one restricted profile per child.

**Primary key:** child_id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| child_id | uuid | no |
| birth_date | date | yes |
| gender_reported | text | yes |
| child_national_id | text | yes |
| blood_group_reported | text | yes |
| contact_address | text | yes |
| sibling_count_reported | text | yes |
| diagnosis_1 | text | yes |
| diagnosis_2 | text | yes |
| udid_number | text | yes |
| udid_disability_reported | text | yes |
| udid_validity_reported | text | yes |
| udid_percentage_reported | text | yes |
| insurance_number | text | yes |
| assessment_date | date | yes |
| assessment_age_reported | text | yes |
| family_income_reported | text | yes |
| economic_category_reported | text | yes |
| assessment_fee | numeric | yes |
| monthly_fee | numeric | yes |
| monthly_fee_remarks | text | yes |
| concession_reported | text | yes |
| social_category_reported | text | yes |
| religion_reported | text | yes |
| consent_reported | text | yes |
| dropout_reason_reported | text | yes |
| transition_date | date | yes |
| comments | text | yes |
| severity_reported | text | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (child_id) → children(id); RESTRICT. draft design; no database exists

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs

**Index candidates beyond existing keys:** PK/unique coverage is sufficient for the declared initial paths.

### caregivers

Resolved caregiver identity; no global person deduplication by display name. **Grain:** One identified caregiver source identity pending scope review.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| display_name | text | yes |
| birth_date | date | yes |
| contact_phone | text | yes |
| contact_email | text | yes |
| national_id | text | yes |
| employment_reported | text | yes |
| education_reported | text | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs

**Index candidates beyond existing keys:** PK/unique coverage is sufficient for the declared initial paths.

### child_caregivers

Preserves the verified child/caregiver pair and source identifier scope. **Grain:** One child/caregiver association.

**Primary key:** id.
**Candidate unique constraints:** (id, child_id); (source_namespace, child_id, source_caregiver_code).

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| child_id | uuid | no |
| caregiver_id | uuid | no |
| source_namespace | text | yes |
| source_caregiver_code | text | yes |
| role_code | text | yes |
| role_vocabulary | text | no |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (child_id) → children(id); RESTRICT. 716/716 source child IDs resolve to 371-key master
- (caregiver_id) → caregivers(id); RESTRICT. caregiver identity scope remains Q02
- (role_vocabulary, role_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- role_vocabulary is server-generated fixed caregiver_role discriminator; MATCH SIMPLE composite FK permits unknown code NULL

**Index candidates beyond existing keys:** (child_id); (caregiver_id); (role_vocabulary, role_code).

### program_changes

Unpivots promotion slots without inventing interval ends. **Grain:** One source promotion observation.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| child_id | uuid | no |
| program_code | text | yes |
| program_vocabulary | text | no |
| promotion_date | date | yes |
| source_slot | integer | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (child_id) → children(id); RESTRICT. draft design; no database exists
- (program_vocabulary, program_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- program_vocabulary is server-generated fixed program discriminator; MATCH SIMPLE composite FK permits unknown code NULL

**Index candidates beyond existing keys:** (program_vocabulary, program_code); (child_id, promotion_date).

### questionnaire_responses

Submission context; references the validated pair instead of redundant independent IDs. **Grain:** One approved response row/submission.

**Primary key:** id.
**Candidate unique constraints:** (id, definition_key).

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| child_caregiver_id | uuid | no |
| definition_key | text | no |
| definition_vocabulary | text | no |
| assessment_date | date | yes |
| program_code | text | yes |
| program_vocabulary | text | no |
| centre_code | text | yes |
| centre_vocabulary | text | no |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (child_caregiver_id) → child_caregivers(id); RESTRICT. 106/106 observed pairs consistent, authority Q01 pending
- (definition_vocabulary, definition_key) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary
- (program_vocabulary, program_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary
- (centre_vocabulary, centre_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- definition_vocabulary is server-generated fixed questionnaire_definition discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- program_vocabulary is server-generated fixed program discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- centre_vocabulary is server-generated fixed centre discriminator; MATCH SIMPLE composite FK permits unknown code NULL

**Index candidates beyond existing keys:** (definition_vocabulary, definition_key); (program_vocabulary, program_code); (centre_vocabulary, centre_code); (child_caregiver_id, assessment_date).

### questionnaire_items

Actual question definitions; one version key without premature questionnaire-framework tables. **Grain:** One actual question column within an approved definition.

**Primary key:** id.
**Candidate unique constraints:** (definition_key, item_key); (definition_key, ordinal); (id, definition_key).

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| definition_key | text | no |
| definition_vocabulary | text | no |
| item_key | text | no |
| prompt | text | no |
| section_label | text | yes |
| value_kind | text | no |
| ordinal | integer | no |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (definition_vocabulary, definition_key) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- definition_vocabulary is server-generated fixed questionnaire_definition discriminator; MATCH SIMPLE composite FK permits unknown code NULL

**Index candidates beyond existing keys:** (definition_vocabulary, definition_key).

### questionnaire_answers

Typed values replace untyped recorded_value; preserves missing answers separately. **Grain:** One response/item.

**Primary key:** id.
**Candidate unique constraints:** (response_id, item_id).

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| response_id | uuid | no |
| item_id | uuid | no |
| definition_key | text | no |
| numeric_value | numeric | yes |
| text_value | text | yes |
| answer_state | text | no |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (response_id, definition_key) → questionnaire_responses(id, definition_key); RESTRICT. draft design; no database exists
- (item_id, definition_key) → questionnaire_items(id, definition_key); RESTRICT. draft design; no database exists

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- At most one numeric_value/text_value; both NULL allowed only for explicit missing answer_state
- Value kind agrees with item definition via constrained server write path; no 1..5 range until Q05

**Index candidates beyond existing keys:** (response_id, definition_key); (item_id, definition_key).

### attendance_observations

Dated source marks kept distinct by service; unresolved names/dates remain staged. **Grain:** One resolved child/service/source-date observation.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| child_id | uuid | no |
| service_code | text | no |
| service_vocabulary | text | no |
| attendance_date | date | no |
| mark_code | text | no |
| mark_vocabulary | text | no |
| program_code | text | yes |
| program_vocabulary | text | no |
| batch_reported | text | yes |
| child_status_reported | text | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (child_id) → children(id); RESTRICT. future curated rows only; unresolved source identities remain source_records
- (service_vocabulary, service_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary
- (mark_vocabulary, mark_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary
- (program_vocabulary, program_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- service_vocabulary is server-generated fixed service_context discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- mark_vocabulary is server-generated fixed attendance_mark discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- program_vocabulary is server-generated fixed program discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- No unique(child_id,date): multiple services and observations can coexist
- Resolved child/date/code required in curated rows; unknowns remain staged, never invented

**Index candidates beyond existing keys:** (service_vocabulary, service_code); (mark_vocabulary, mark_code); (program_vocabulary, program_code); (child_id, attendance_date).

### support_observations

Source-cell support observations; not necessarily one person or a daily P/A event. **Grain:** One approved support matrix cell.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| child_id | uuid | no |
| participant_link_id | uuid | yes |
| event_reference | text | no |
| event_date | date | yes |
| program_code | text | yes |
| program_vocabulary | text | no |
| numeric_value | numeric | yes |
| text_value | text | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (child_id) → children(id); RESTRICT. conditional on approved identity crosswalk
- (participant_link_id, child_id) → child_caregivers(id, child_id); RESTRICT. when a single participant resolves, require the same child
- (program_vocabulary, program_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- program_vocabulary is server-generated fixed program discriminator; MATCH SIMPLE composite FK permits unknown code NULL

**Index candidates beyond existing keys:** (child_id); (participant_link_id, child_id); (program_vocabulary, program_code).

### adl_visits

Preserves true visit flags and undated historical exceptions. **Grain:** One checked visit-slot observation.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| child_id | uuid | no |
| program_code | text | yes |
| program_vocabulary | text | no |
| visit_flag | boolean | no |
| visit_date | date | yes |
| source_slot | integer | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (child_id) → children(id); RESTRICT. conditional on approved identity crosswalk
- (program_vocabulary, program_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- program_vocabulary is server-generated fixed program discriminator; MATCH SIMPLE composite FK permits unknown code NULL
- visit_flag must be true for this fact grain; false/blank source slots retained in source_records
- visit_date may be NULL only for imported pending-date record with provenance; future manual entry requires date

**Index candidates beyond existing keys:** (program_vocabulary, program_code); (child_id, visit_date).

### activity_logs — conditional

Structured activity records only after row-grain/workflow approval; archive retained regardless. **Grain:** One approved activity event, not each candidate content row.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| activity_description | text | yes |
| activity_date | date | yes |
| source_status_reported | text | yes |
| batch_reported | text | yes |
| participant_count_reported | text | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |
| origin_kind | text | no |
| review_state | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs

**Index candidates beyond existing keys:** PK/unique coverage is sufficient for the declared initial paths.

### source_artifacts

Immutable snapshot identity and worksheet/column schema. **Grain:** One authorized source-file version.

**Primary key:** id.
**Candidate unique constraints:** (source_namespace, file_code, version_sha256).

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| source_namespace | text | no |
| file_code | text | no |
| version_sha256 | text | no |
| source_locator | text | yes |
| worksheet_manifest | jsonb | no |
| captured_at | timestamptz | no |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs

**Index candidates beyond existing keys:** PK/unique coverage is sufficient for the declared initial paths.

### source_records

Restricted staging/reconciliation for every nonempty source row, including unresolved/derived fields. **Grain:** One artifact/native-sheet/original-row.

**Primary key:** id.
**Candidate unique constraints:** (artifact_id, native_sheet_key, source_row).

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| artifact_id | uuid | no |
| native_sheet_key | text | no |
| source_row | integer | no |
| cell_payload | jsonb | no |
| processing_state | text | no |
| diagnostics | jsonb | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (artifact_id) → source_artifacts(id); RESTRICT. draft design; no database exists

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs

**Index candidates beyond existing keys:** (processing_state, artifact_id).

### source_provenance

Many-source-row/cell to one target without unconstrained polymorphic IDs. **Grain:** One source-column group -> one typed target/field group.

**Primary key:** id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| id | uuid | no |
| source_record_id | uuid | no |
| source_columns | text[] | no |
| target_fields | text[] | no |
| rule_reference | text | no |
| contribution_state | text | no |
| child_id | uuid | yes |
| private_profile_child_id | uuid | yes |
| caregiver_id | uuid | yes |
| child_caregiver_id | uuid | yes |
| program_change_id | uuid | yes |
| response_id | uuid | yes |
| item_id | uuid | yes |
| answer_id | uuid | yes |
| attendance_id | uuid | yes |
| support_id | uuid | yes |
| adl_id | uuid | yes |
| activity_id [only if activity_logs] | uuid | yes |
| reference_vocabulary | text | yes |
| reference_code | text | yes |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (source_record_id) → source_records(id); RESTRICT. draft design; no database exists
- (child_id) → children(id); RESTRICT. draft design; no database exists
- (private_profile_child_id) → child_private_profiles(child_id); RESTRICT. draft design; no database exists
- (caregiver_id) → caregivers(id); RESTRICT. draft design; no database exists
- (child_caregiver_id) → child_caregivers(id); RESTRICT. draft design; no database exists
- (program_change_id) → program_changes(id); RESTRICT. draft design; no database exists
- (response_id) → questionnaire_responses(id); RESTRICT. draft design; no database exists
- (item_id) → questionnaire_items(id); RESTRICT. draft design; no database exists
- (answer_id) → questionnaire_answers(id); RESTRICT. draft design; no database exists
- (attendance_id) → attendance_observations(id); RESTRICT. draft design; no database exists
- (support_id) → support_observations(id); RESTRICT. draft design; no database exists
- (adl_id) → adl_visits(id); RESTRICT. draft design; no database exists
- (activity_id) → activity_logs(id); RESTRICT. draft design; no database exists [Only if activity_logs enabled.]
- (reference_vocabulary, reference_code) → reference_values(vocabulary, code); RESTRICT. draft design; no database exists

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- Exactly one complete target group, all other target columns NULL; partial reference vocabulary/code pair forbidden
- source_columns and target_fields nonempty; field/column membership checked by bounded mapping validator
- rule_reference identifies approved transformation/mapping version; contribution_state distinguishes selected/supporting/conflict evidence, without treating links as business approval
- Import idempotency must use immutable artifact/sheet/row/column/slot plus target-kind and approved rule identity; repeated exports/business events need approved reconciliation keys, not random UUID deduplication
- Before promotion of imported target rows, deferred constraint trigger or transactional import validator requires >=1 provenance link; update provenance atomically with edits

**Index candidates beyond existing keys:** (source_record_id); (child_id); (private_profile_child_id); (caregiver_id); (child_caregiver_id); (program_change_id); (response_id); (item_id); (answer_id); (attendance_id); (support_id); (adl_id); (activity_id) [conditional]; (reference_vocabulary, reference_code).

### access_memberships

Application authorization independent of Google sign-in and business caregivers. **Grain:** One admitted auth user in this dedicated project.

**Primary key:** user_id.
**Candidate unique constraints:** No additional business uniqueness assumed.

| Field | Recommended type | Nullable |
| --- | --- | --- |
| user_id | uuid | no |
| approved_email_domain | text | no |
| role_code | text | no |
| role_vocabulary | text | no |
| active | boolean | no |
| created_at | timestamptz | no |
| updated_at | timestamptz | no |
| created_by | uuid | yes |
| updated_by | uuid | yes |
| actor_ref | text | no |

**Foreign keys:**

- (created_by) → auth.users(id); RESTRICT. proposed technical audit
- (updated_by) → auth.users(id); RESTRICT. proposed technical audit
- (user_id) → auth.users(id); RESTRICT. Supabase-managed authentication identity, not NGO caregiver identity
- (role_vocabulary, role_code) → reference_values(vocabulary, code); RESTRICT. proposed controlled vocabulary

**Checks / approval dependencies:**

- Audit stamps server-managed; null created_by/updated_by allowed for identified import actor only, never fabricated user IDs
- role_vocabulary is server-generated fixed access_role discriminator; MATCH SIMPLE composite FK permits unknown code NULL

**Index candidates beyond existing keys:** (role_vocabulary, role_code).

## Operational workflow and analytics compatibility

Approved explicit Add/Record/Edit actions can select canonical children, source-scoped categories and current associations. Repeated questionnaires create new responses; existing scores are not overwritten. Separate daily/service, support and ADL grains prevent invalid combined denominators. Submission context is retained historically even if child program changes. Staging/reconciliation shows unresolved rows separately from approved analytic facts. Header-only fields or archived summaries needed by future entry require an approved projection first.

The full machine-readable recommendation is [optimized-model-draft.json](evidence/optimized-model-draft.json); source mappings are [source-target-coverage.csv](evidence/source-target-coverage.csv). The revised ER diagram and per-source dictionary link to this document. No statement here indicates tables, policies, indexes or triggers have actually been created.
