# Final deployed data dictionary

Generated from the actual 20-table PostgreSQL catalog; checked 28 October 2026, 11:05 IST. Private schemas remain restricted. Defaults, nullability, primary/foreign keys and constraints below are actual deployed definitions. This replaces draft specifications for current-schema inspection; historical dictionaries remain evidence.

## gk_private.access_memberships

Rows: 0. RLS enabled: True; FORCE RLS: False. Primary key: `user_id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `user_id` | `uuid` | No | `` |
| `approved_email_domain` | `text` | No | `` |
| `role_code` | `text` | No | `` |
| `role_vocabulary` | `text` | No | `'access_role'::text` |
| `active` | `boolean` | No | `false` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |
| `private_read` | `boolean` | No | `false` |
| `private_write` | `boolean` | No | `false` |
| `approval_reference` | `text` | Yes | `` |

Constraints:

- `ck_access_memberships_0`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `ck_access_memberships_1`: `CHECK (approved_email_domain = 'goalkeep.net'::text)`.
- `ck_access_memberships_2`: `CHECK (NOT private_write OR private_read)`.
- `ck_access_memberships_3`: `CHECK (NOT active OR COALESCE(btrim(approval_reference), ''::text) <> ''::text)`.
- `fk_access_memberships_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_access_memberships_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_access_memberships_2`: `FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_access_memberships_3`: `FOREIGN KEY (role_vocabulary, role_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_access_memberships_4`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `pk_access_memberships`: `PRIMARY KEY (user_id)`.

## gk_private.attendance_import_staging

Rows: 43,160. RLS enabled: True; FORCE RLS: True. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `` |
| `source_record_id` | `uuid` | No | `` |
| `header_source_record_id` | `uuid` | Yes | `` |
| `artifact_id` | `uuid` | No | `` |
| `source_file` | `text` | No | `` |
| `source_sheet` | `text` | No | `` |
| `native_sheet_key` | `text` | No | `` |
| `source_row` | `integer` | No | `` |
| `source_column` | `text` | No | `` |
| `source_reference` | `text` | No | `` |
| `observation_kind` | `text` | No | `` |
| `recorded_child_identifier` | `jsonb` | No | `'null'::jsonb` |
| `recorded_child_name` | `jsonb` | No | `'null'::jsonb` |
| `original_mark` | `jsonb` | No | `` |
| `original_header` | `jsonb` | No | `'null'::jsonb` |
| `header_label` | `text` | Yes | `` |
| `program_reported` | `jsonb` | No | `'null'::jsonb` |
| `parsed_date` | `date` | Yes | `` |
| `verified_child_id` | `uuid` | Yes | `` |
| `candidate_child_ids` | `uuid[]` | No | `'{}'::uuid[]` |
| `identity_status` | `text` | No | `` |
| `date_status` | `text` | No | `` |
| `code_status` | `text` | No | `` |
| `review_status` | `text` | No | `'pending'::text` |
| `flags` | `text[]` | No | `` |
| `provenance` | `jsonb` | No | `` |
| `review_notes` | `text` | No | `''::text` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |

Constraints:

- `attendance_import_staging_artifact_id_fkey`: `FOREIGN KEY (artifact_id) REFERENCES gk_private.source_artifacts(id) ON DELETE RESTRICT`.
- `attendance_import_staging_check`: `CHECK ((identity_status = 'VERIFIED'::text) = (verified_child_id IS NOT NULL))`.
- `attendance_import_staging_check1`: `CHECK ((date_status = 'VERIFIED'::text) = (parsed_date IS NOT NULL))`.
- `attendance_import_staging_check2`: `CHECK (identity_status <> 'PROVISIONAL_MATCH'::text OR cardinality(candidate_child_ids) = 1)`.
- `attendance_import_staging_check3`: `CHECK (identity_status <> 'AMBIGUOUS'::text OR cardinality(candidate_child_ids) > 1)`.
- `attendance_import_staging_check4`: `CHECK (identity_status <> 'UNMATCHED'::text OR cardinality(candidate_child_ids) = 0)`.
- `attendance_import_staging_check5`: `CHECK ((observation_kind = 'SOURCE_CONTEXT'::text) = (source_column = '__ROW__'::text))`.
- `attendance_import_staging_code_status_check`: `CHECK (code_status = ANY (ARRAY['VERIFIED'::text, 'PENDING'::text]))`.
- `attendance_import_staging_date_status_check`: `CHECK (date_status = ANY (ARRAY['VERIFIED'::text, 'MISSING'::text, 'FORMULA_UNRESOLVED'::text, 'SANITIZED_UNTRUSTED'::text, 'UNPARSED'::text]))`.
- `attendance_import_staging_header_source_record_id_fkey`: `FOREIGN KEY (header_source_record_id) REFERENCES gk_private.source_records(id) ON DELETE RESTRICT`.
- `attendance_import_staging_identity_status_check`: `CHECK (identity_status = ANY (ARRAY['VERIFIED'::text, 'PROVISIONAL_MATCH'::text, 'AMBIGUOUS'::text, 'UNMATCHED'::text]))`.
- `attendance_import_staging_observation_kind_check`: `CHECK (observation_kind = ANY (ARRAY['MARK'::text, 'FORMULA'::text, 'SUMMARY_VALUE'::text, 'AUXILIARY_VALUE'::text, 'SOURCE_CONTEXT'::text]))`.
- `attendance_import_staging_pkey`: `PRIMARY KEY (id)`.
- `attendance_import_staging_provenance_check`: `CHECK (jsonb_typeof(provenance) = 'object'::text)`.
- `attendance_import_staging_review_status_check`: `CHECK (review_status = ANY (ARRAY['pending'::text, 'reviewed'::text, 'excluded'::text]))`.
- `attendance_import_staging_source_column_check`: `CHECK (source_column ~ '^([A-Z]{1,3}|__ROW__)$'::text)`.
- `attendance_import_staging_source_record_id_fkey`: `FOREIGN KEY (source_record_id) REFERENCES gk_private.source_records(id) ON DELETE RESTRICT`.
- `attendance_import_staging_source_record_id_source_column_key`: `UNIQUE (source_record_id, source_column)`.
- `attendance_import_staging_source_row_check`: `CHECK (source_row > 0)`.
- `attendance_import_staging_verified_child_id_fkey`: `FOREIGN KEY (verified_child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.

## gk_private.caregivers

Rows: 716. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `display_name` | `text` | Yes | `` |
| `birth_date` | `date` | Yes | `` |
| `contact_phone` | `text` | Yes | `` |
| `contact_email` | `text` | Yes | `` |
| `national_id` | `text` | Yes | `` |
| `employment_reported` | `text` | Yes | `` |
| `education_reported` | `text` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |
| `caregiver_business_id` | `text` | No | `` |

Constraints:

- `ck_caregivers_0`: `CHECK (btrim(caregiver_business_id) <> ''::text AND caregiver_business_id = btrim(caregiver_business_id))`.
- `ck_caregivers_1`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_caregivers_2`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_caregivers_3`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `fk_caregivers_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_caregivers_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_caregivers_2`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_caregivers`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_caregivers`: `PRIMARY KEY (id)`.
- `uq_caregivers_0`: `UNIQUE (caregiver_business_id)`.

## gk_private.child_private_profiles

Rows: 371. RLS enabled: True; FORCE RLS: False. Primary key: `child_id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `child_id` | `uuid` | No | `` |
| `birth_date` | `date` | Yes | `` |
| `gender_reported` | `text` | Yes | `` |
| `child_national_id` | `text` | Yes | `` |
| `blood_group_reported` | `text` | Yes | `` |
| `contact_address` | `text` | Yes | `` |
| `sibling_count_reported` | `text` | Yes | `` |
| `diagnosis_1` | `text` | Yes | `` |
| `diagnosis_2` | `text` | Yes | `` |
| `udid_number` | `text` | Yes | `` |
| `udid_disability_reported` | `text` | Yes | `` |
| `udid_validity_reported` | `text` | Yes | `` |
| `udid_percentage_reported` | `text` | Yes | `` |
| `insurance_number` | `text` | Yes | `` |
| `assessment_date` | `date` | Yes | `` |
| `assessment_age_reported` | `text` | Yes | `` |
| `family_income_reported` | `text` | Yes | `` |
| `economic_category_reported` | `text` | Yes | `` |
| `assessment_fee` | `numeric` | Yes | `` |
| `monthly_fee` | `numeric` | Yes | `` |
| `monthly_fee_remarks` | `text` | Yes | `` |
| `concession_reported` | `text` | Yes | `` |
| `social_category_reported` | `text` | Yes | `` |
| `religion_reported` | `text` | Yes | `` |
| `consent_reported` | `text` | Yes | `` |
| `dropout_reason_reported` | `text` | Yes | `` |
| `transition_date` | `date` | Yes | `` |
| `comments` | `text` | Yes | `` |
| `severity_reported` | `text` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `check_profile_dates`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `ck_child_private_profiles_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_child_private_profiles_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_child_private_profiles_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `fk_child_private_profiles_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_child_private_profiles_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_child_private_profiles_2`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_child_private_profiles_3`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_child_private_profiles`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_child_private_profiles`: `PRIMARY KEY (child_id)`.

## gk_private.identity_candidates

Rows: 2,089. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `source_record_id` | `uuid` | No | `` |
| `child_id` | `uuid` | Yes | `` |
| `caregiver_id` | `uuid` | Yes | `` |
| `match_method` | `text` | No | `` |
| `resolution_status` | `text` | No | `` |
| `evidence` | `jsonb` | No | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |

Constraints:

- `ck_identity_candidates_0`: `CHECK (num_nonnulls(child_id, caregiver_id) = 1)`.
- `ck_identity_candidates_1`: `CHECK (match_method = ANY (ARRAY['exact_identifier'::text, 'verified_relationship'::text, 'name_candidate'::text, 'name_context'::text, 'computed_identifier'::text]))`.
- `ck_identity_candidates_2`: `CHECK (resolution_status = ANY (ARRAY['verified'::text, 'candidate'::text, 'rejected'::text]))`.
- `ck_identity_candidates_3`: `CHECK (resolution_status <> 'verified'::text OR (match_method = ANY (ARRAY['exact_identifier'::text, 'verified_relationship'::text])))`.
- `ck_identity_candidates_4`: `CHECK (jsonb_typeof(evidence) = 'object'::text)`.
- `fk_identity_candidates_0`: `FOREIGN KEY (source_record_id) REFERENCES gk_private.source_records(id) ON DELETE RESTRICT`.
- `fk_identity_candidates_1`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_identity_candidates_2`: `FOREIGN KEY (caregiver_id) REFERENCES gk_private.caregivers(id) ON DELETE RESTRICT`.
- `fk_identity_candidates_3`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_identity_candidates_4`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `pk_identity_candidates`: `PRIMARY KEY (id)`.

## gk_private.questionnaire_answers

Rows: 3,286. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `response_id` | `uuid` | No | `` |
| `item_id` | `uuid` | No | `` |
| `definition_key` | `text` | No | `` |
| `numeric_value` | `numeric` | Yes | `` |
| `text_value` | `text` | Yes | `` |
| `answer_state` | `text` | No | `'missing'::text` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_questionnaire_answers_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_questionnaire_answers_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_questionnaire_answers_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `ck_questionnaire_answers_3`: `CHECK (answer_state = ANY (ARRAY['recorded'::text, 'missing'::text, 'needs_review'::text]))`.
- `ck_questionnaire_answers_4`: `CHECK (num_nonnulls(numeric_value, text_value) <= 1)`.
- `ck_questionnaire_answers_5`: `CHECK (answer_state = 'missing'::text AND numeric_value IS NULL AND text_value IS NULL OR answer_state <> 'missing'::text AND num_nonnulls(numeric_value, text_value) = 1)`.
- `fk_questionnaire_answers_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_questionnaire_answers_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_questionnaire_answers_2`: `FOREIGN KEY (response_id, definition_key) REFERENCES public.questionnaire_responses(id, definition_key) ON DELETE RESTRICT`.
- `fk_questionnaire_answers_3`: `FOREIGN KEY (item_id, definition_key) REFERENCES public.questionnaire_items(id, definition_key) ON DELETE RESTRICT`.
- `fk_questionnaire_answers_4`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_questionnaire_answers`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_questionnaire_answers`: `PRIMARY KEY (id)`.
- `uq_questionnaire_answers_0`: `UNIQUE (response_id, item_id)`.

## gk_private.record_audit_events

Rows: 28,293. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `schema_name` | `text` | No | `` |
| `table_name` | `text` | No | `` |
| `record_key` | `jsonb` | No | `'{}'::jsonb` |
| `operation` | `text` | No | `` |
| `before_value` | `jsonb` | Yes | `` |
| `after_value` | `jsonb` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |

Constraints:

- `fk_record_audit_events_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_record_audit_events_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `pk_record_audit_events`: `PRIMARY KEY (id)`.

## gk_private.recovery_actions

Rows: 0. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `source_record_id` | `uuid` | No | `` |
| `donor_source_record_id` | `uuid` | Yes | `` |
| `child_id` | `uuid` | Yes | `` |
| `caregiver_id` | `uuid` | Yes | `` |
| `source_column` | `text` | No | `` |
| `field_key` | `text` | No | `` |
| `original_value` | `jsonb` | No | `` |
| `recovered_value` | `jsonb` | Yes | `` |
| `method` | `text` | No | `` |
| `validation_status` | `text` | No | `` |
| `identity_verified` | `boolean` | No | `false` |
| `authoritative_source` | `boolean` | No | `false` |
| `meaning_equivalent` | `boolean` | No | `false` |
| `has_conflict` | `boolean` | No | `false` |
| `evidence` | `jsonb` | No | `'{}'::jsonb` |
| `run_id` | `uuid` | No | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |

Constraints:

- `ck_recovery_actions_0`: `CHECK (num_nonnulls(child_id, caregiver_id) <= 1)`.
- `ck_recovery_actions_1`: `CHECK (validation_status = ANY (ARRAY['auto_recovered'::text, 'suggested'::text, 'blocked_conflict'::text, 'blocked_untrusted'::text, 'no_recovery'::text]))`.
- `ck_recovery_actions_2`: `CHECK (validation_status <> 'auto_recovered'::text OR identity_verified AND authoritative_source AND meaning_equivalent AND NOT has_conflict AND donor_source_record_id IS NOT NULL AND recovered_value IS NOT NULL AND num_nonnulls(child_id, caregiver_id) = 1)`.
- `ck_recovery_actions_3`: `CHECK (jsonb_typeof(evidence) = 'object'::text)`.
- `fk_recovery_actions_0`: `FOREIGN KEY (source_record_id) REFERENCES gk_private.source_records(id) ON DELETE RESTRICT`.
- `fk_recovery_actions_1`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_recovery_actions_2`: `FOREIGN KEY (caregiver_id) REFERENCES gk_private.caregivers(id) ON DELETE RESTRICT`.
- `fk_recovery_actions_3`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_recovery_actions_4`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_recovery_actions_5`: `FOREIGN KEY (donor_source_record_id) REFERENCES gk_private.source_records(id) ON DELETE RESTRICT`.
- `pk_recovery_actions`: `PRIMARY KEY (id)`.

## gk_private.source_artifacts

Rows: 12. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `source_namespace` | `text` | No | `` |
| `file_code` | `text` | No | `` |
| `version_sha256` | `text` | No | `` |
| `source_locator` | `text` | Yes | `` |
| `worksheet_manifest` | `jsonb` | No | `'{}'::jsonb` |
| `captured_at` | `timestamp with time zone` | No | `now()` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |

Constraints:

- `ck_source_artifacts_0`: `CHECK (version_sha256 ~ '^[a-f0-9]{64}$'::text)`.
- `ck_source_artifacts_1`: `CHECK (jsonb_typeof(worksheet_manifest) = 'object'::text)`.
- `ck_source_artifacts_2`: `CHECK (btrim(source_namespace) <> ''::text AND btrim(file_code) <> ''::text)`.
- `fk_source_artifacts_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_source_artifacts_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `pk_source_artifacts`: `PRIMARY KEY (id)`.
- `uq_source_artifacts_0`: `UNIQUE (source_namespace, file_code, version_sha256)`.

## gk_private.source_provenance

Rows: 5,772. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `source_record_id` | `uuid` | No | `` |
| `source_columns` | `text[]` | No | `` |
| `target_fields` | `text[]` | No | `` |
| `rule_reference` | `text` | No | `` |
| `contribution_state` | `text` | No | `` |
| `child_id` | `uuid` | Yes | `` |
| `private_profile_child_id` | `uuid` | Yes | `` |
| `caregiver_id` | `uuid` | Yes | `` |
| `child_caregiver_id` | `uuid` | Yes | `` |
| `program_change_id` | `uuid` | Yes | `` |
| `response_id` | `uuid` | Yes | `` |
| `item_id` | `uuid` | Yes | `` |
| `answer_id` | `uuid` | Yes | `` |
| `attendance_id` | `uuid` | Yes | `` |
| `support_id` | `uuid` | Yes | `` |
| `adl_id` | `uuid` | Yes | `` |
| `reference_vocabulary` | `text` | Yes | `` |
| `reference_code` | `text` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |

Constraints:

- `ck_source_provenance_0`: `CHECK ((num_nonnulls(child_id, private_profile_child_id, caregiver_id, child_caregiver_id, program_change_id, response_id, item_id, answer_id, attendance_id, support_id, adl_id) +
CASE
    WHEN reference_vocabulary IS NOT NULL AND reference_code IS NOT NULL THEN 1
    ELSE 0
END) = 1)`.
- `ck_source_provenance_1`: `CHECK ((reference_vocabulary IS NULL) = (reference_code IS NULL))`.
- `ck_source_provenance_2`: `CHECK (gk_private.nonempty_text_array(source_columns) AND gk_private.nonempty_text_array(target_fields))`.
- `ck_source_provenance_3`: `CHECK (contribution_state = ANY (ARRAY['selected'::text, 'supporting'::text, 'conflict_evidence'::text]))`.
- `ck_source_provenance_4`: `CHECK (btrim(rule_reference) <> ''::text)`.
- `fk_source_provenance_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_source_provenance_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_source_provenance_10`: `FOREIGN KEY (answer_id) REFERENCES gk_private.questionnaire_answers(id) ON DELETE RESTRICT`.
- `fk_source_provenance_11`: `FOREIGN KEY (attendance_id) REFERENCES public.attendance_observations(id) ON DELETE RESTRICT`.
- `fk_source_provenance_12`: `FOREIGN KEY (support_id) REFERENCES public.support_observations(id) ON DELETE RESTRICT`.
- `fk_source_provenance_13`: `FOREIGN KEY (adl_id) REFERENCES public.adl_visits(id) ON DELETE RESTRICT`.
- `fk_source_provenance_14`: `FOREIGN KEY (reference_vocabulary, reference_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_source_provenance_2`: `FOREIGN KEY (source_record_id) REFERENCES gk_private.source_records(id) ON DELETE RESTRICT`.
- `fk_source_provenance_3`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_source_provenance_4`: `FOREIGN KEY (private_profile_child_id) REFERENCES gk_private.child_private_profiles(child_id) ON DELETE RESTRICT`.
- `fk_source_provenance_5`: `FOREIGN KEY (caregiver_id) REFERENCES gk_private.caregivers(id) ON DELETE RESTRICT`.
- `fk_source_provenance_6`: `FOREIGN KEY (child_caregiver_id) REFERENCES public.child_caregivers(id) ON DELETE RESTRICT`.
- `fk_source_provenance_7`: `FOREIGN KEY (program_change_id) REFERENCES public.program_changes(id) ON DELETE RESTRICT`.
- `fk_source_provenance_8`: `FOREIGN KEY (response_id) REFERENCES public.questionnaire_responses(id) ON DELETE RESTRICT`.
- `fk_source_provenance_9`: `FOREIGN KEY (item_id) REFERENCES public.questionnaire_items(id) ON DELETE RESTRICT`.
- `pk_source_provenance`: `PRIMARY KEY (id)`.

## gk_private.source_records

Rows: 20,432. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `artifact_id` | `uuid` | No | `` |
| `native_sheet_key` | `text` | No | `` |
| `source_row` | `integer` | No | `` |
| `cell_payload` | `jsonb` | No | `'{}'::jsonb` |
| `processing_state` | `text` | No | `'staged'::text` |
| `diagnostics` | `jsonb` | Yes | `'{}'::jsonb` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |

Constraints:

- `ck_source_records_0`: `CHECK (source_row > 0)`.
- `ck_source_records_1`: `CHECK (processing_state = ANY (ARRAY['staged'::text, 'blocked'::text, 'resolved'::text, 'reference_only'::text]))`.
- `ck_source_records_2`: `CHECK (jsonb_typeof(cell_payload) = 'object'::text)`.
- `ck_source_records_3`: `CHECK (btrim(native_sheet_key) <> ''::text)`.
- `fk_source_records_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_source_records_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_source_records_2`: `FOREIGN KEY (artifact_id) REFERENCES gk_private.source_artifacts(id) ON DELETE RESTRICT`.
- `pk_source_records`: `PRIMARY KEY (id)`.
- `uq_source_records_0`: `UNIQUE (artifact_id, native_sheet_key, source_row)`.

## public.adl_visits

Rows: 0. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `child_id` | `uuid` | No | `` |
| `program_code` | `text` | Yes | `` |
| `program_vocabulary` | `text` | No | `'program'::text` |
| `visit_flag` | `boolean` | No | `` |
| `visit_date` | `date` | Yes | `` |
| `source_slot` | `integer` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_adl_visits_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_adl_visits_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_adl_visits_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `ck_adl_visits_3`: `CHECK (visit_flag IS TRUE)`.
- `ck_adl_visits_4`: `CHECK (visit_date IS NOT NULL OR origin_kind = 'import'::text AND review_state <> 'accepted'::text)`.
- `ck_adl_visits_5`: `CHECK (source_slot IS NULL OR source_slot > 0)`.
- `fk_adl_visits_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_adl_visits_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_adl_visits_2`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_adl_visits_3`: `FOREIGN KEY (program_vocabulary, program_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_adl_visits_4`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_adl_visits`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_adl_visits`: `PRIMARY KEY (id)`.

## public.attendance_observations

Rows: 0. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `child_id` | `uuid` | No | `` |
| `service_code` | `text` | No | `` |
| `service_vocabulary` | `text` | No | `'service_context'::text` |
| `attendance_date` | `date` | No | `` |
| `mark_code` | `text` | No | `` |
| `mark_vocabulary` | `text` | No | `'attendance_mark'::text` |
| `program_code` | `text` | Yes | `` |
| `program_vocabulary` | `text` | No | `'program'::text` |
| `batch_reported` | `text` | Yes | `` |
| `child_status_reported` | `text` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_attendance_observations_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_attendance_observations_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_attendance_observations_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `fk_attendance_observations_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_attendance_observations_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_attendance_observations_2`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_attendance_observations_3`: `FOREIGN KEY (service_vocabulary, service_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_attendance_observations_4`: `FOREIGN KEY (mark_vocabulary, mark_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_attendance_observations_5`: `FOREIGN KEY (program_vocabulary, program_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_attendance_observations_6`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_attendance_observations`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_attendance_observations`: `PRIMARY KEY (id)`.

## public.child_caregivers

Rows: 716. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `child_id` | `uuid` | No | `` |
| `caregiver_id` | `uuid` | No | `` |
| `role_code` | `text` | Yes | `` |
| `role_vocabulary` | `text` | No | `'caregiver_role'::text` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_child_caregivers_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_child_caregivers_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_child_caregivers_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `fk_child_caregivers_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_child_caregivers_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_child_caregivers_2`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_child_caregivers_3`: `FOREIGN KEY (caregiver_id) REFERENCES gk_private.caregivers(id) ON DELETE RESTRICT`.
- `fk_child_caregivers_4`: `FOREIGN KEY (role_vocabulary, role_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_child_caregivers_5`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_child_caregivers`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_child_caregivers`: `PRIMARY KEY (id)`.
- `uq_child_caregivers_0`: `UNIQUE (id, child_id)`.
- `uq_child_caregivers_1`: `UNIQUE (child_id, caregiver_id)`.

## public.children

Rows: 371. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `display_name` | `text` | Yes | `` |
| `current_program_code` | `text` | Yes | `` |
| `admitted_program_code` | `text` | Yes | `` |
| `child_status_code` | `text` | Yes | `` |
| `program_vocabulary` | `text` | No | `'program'::text` |
| `status_vocabulary` | `text` | No | `'child_status'::text` |
| `joining_date` | `date` | Yes | `` |
| `dropout_date` | `date` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |
| `child_business_id` | `text` | No | `` |

Constraints:

- `check_child_dates`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `ck_children_0`: `CHECK (btrim(child_business_id) <> ''::text AND child_business_id = btrim(child_business_id))`.
- `ck_children_1`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_children_2`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_children_3`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `fk_children_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_children_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_children_2`: `FOREIGN KEY (program_vocabulary, current_program_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_children_3`: `FOREIGN KEY (program_vocabulary, admitted_program_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_children_4`: `FOREIGN KEY (status_vocabulary, child_status_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_children_5`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_children`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_children`: `PRIMARY KEY (id)`.
- `uq_children_0`: `UNIQUE (child_business_id)`.

## public.program_changes

Rows: 128. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `child_id` | `uuid` | No | `` |
| `program_code` | `text` | Yes | `` |
| `program_vocabulary` | `text` | No | `'program'::text` |
| `promotion_date` | `date` | Yes | `` |
| `source_slot` | `integer` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_program_changes_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_program_changes_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_program_changes_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `ck_program_changes_3`: `CHECK (source_slot IS NULL OR source_slot > 0)`.
- `fk_program_changes_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_program_changes_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_program_changes_2`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_program_changes_3`: `FOREIGN KEY (program_vocabulary, program_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_program_changes_4`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_program_changes`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_program_changes`: `PRIMARY KEY (id)`.

## public.questionnaire_items

Rows: 31. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `definition_key` | `text` | No | `` |
| `definition_vocabulary` | `text` | No | `'questionnaire_definition'::text` |
| `item_key` | `text` | No | `` |
| `prompt` | `text` | No | `` |
| `section_label` | `text` | Yes | `` |
| `value_kind` | `text` | No | `` |
| `ordinal` | `integer` | No | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_questionnaire_items_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_questionnaire_items_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_questionnaire_items_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `ck_questionnaire_items_3`: `CHECK (value_kind = ANY (ARRAY['numeric'::text, 'text'::text, 'recommendation'::text]))`.
- `ck_questionnaire_items_4`: `CHECK (ordinal > 0)`.
- `fk_questionnaire_items_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_questionnaire_items_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_questionnaire_items_2`: `FOREIGN KEY (definition_vocabulary, definition_key) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_questionnaire_items_3`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_questionnaire_items`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_questionnaire_items`: `PRIMARY KEY (id)`.
- `uq_questionnaire_items_0`: `UNIQUE (definition_key, item_key)`.
- `uq_questionnaire_items_1`: `UNIQUE (definition_key, ordinal)`.
- `uq_questionnaire_items_2`: `UNIQUE (id, definition_key)`.

## public.questionnaire_responses

Rows: 106. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `child_caregiver_id` | `uuid` | No | `` |
| `definition_key` | `text` | No | `` |
| `definition_vocabulary` | `text` | No | `'questionnaire_definition'::text` |
| `assessment_date` | `date` | Yes | `` |
| `program_code` | `text` | Yes | `` |
| `program_vocabulary` | `text` | No | `'program'::text` |
| `centre_code` | `text` | Yes | `` |
| `centre_vocabulary` | `text` | No | `'centre'::text` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_questionnaire_responses_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_questionnaire_responses_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_questionnaire_responses_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `fk_questionnaire_responses_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_questionnaire_responses_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_questionnaire_responses_2`: `FOREIGN KEY (child_caregiver_id) REFERENCES public.child_caregivers(id) ON DELETE RESTRICT`.
- `fk_questionnaire_responses_3`: `FOREIGN KEY (definition_vocabulary, definition_key) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_questionnaire_responses_4`: `FOREIGN KEY (program_vocabulary, program_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_questionnaire_responses_5`: `FOREIGN KEY (centre_vocabulary, centre_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_questionnaire_responses_6`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_questionnaire_responses`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_questionnaire_responses`: `PRIMARY KEY (id)`.
- `uq_questionnaire_responses_0`: `UNIQUE (id, definition_key)`.

## public.reference_values

Rows: 47. RLS enabled: True; FORCE RLS: False. Primary key: `vocabulary, code`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `vocabulary` | `text` | No | `` |
| `code` | `text` | No | `` |
| `label` | `text` | No | `` |
| `active` | `boolean` | No | `false` |
| `sort_order` | `integer` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |
| `permissions` | `jsonb` | No | `'{}'::jsonb` |
| `approval_reference` | `text` | Yes | `` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |

Constraints:

- `ck_reference_values_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_reference_values_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_reference_values_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `ck_reference_values_3`: `CHECK (btrim(vocabulary) <> ''::text AND btrim(code) <> ''::text)`.
- `ck_reference_values_4`: `CHECK (jsonb_typeof(permissions) = 'object'::text)`.
- `ck_reference_values_5`: `CHECK (vocabulary = 'access_role'::text OR permissions = '{}'::jsonb)`.
- `ck_reference_values_6`: `CHECK (review_state <> 'accepted'::text OR vocabulary <> 'access_role'::text OR COALESCE(btrim(approval_reference), ''::text) <> ''::text)`.
- `ck_valid_role_permissions`: `CHECK (gk_private.valid_permissions(permissions))`.
- `fk_reference_values_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_reference_values_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_reference_values_2`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_reference_values`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_reference_values`: `PRIMARY KEY (vocabulary, code)`.

## public.support_observations

Rows: 0. RLS enabled: True; FORCE RLS: False. Primary key: `id`.

| Column | PostgreSQL type | Nullable | Default / generation |
|---|---|---|---|
| `id` | `uuid` | No | `gen_random_uuid()` |
| `child_id` | `uuid` | No | `` |
| `participant_link_id` | `uuid` | Yes | `` |
| `event_reference` | `text` | No | `` |
| `event_date` | `date` | Yes | `` |
| `program_code` | `text` | Yes | `` |
| `program_vocabulary` | `text` | No | `'program'::text` |
| `numeric_value` | `numeric` | Yes | `` |
| `text_value` | `text` | Yes | `` |
| `created_at` | `timestamp with time zone` | No | `now()` |
| `updated_at` | `timestamp with time zone` | No | `now()` |
| `created_by` | `uuid` | Yes | `` |
| `updated_by` | `uuid` | Yes | `` |
| `actor_ref` | `text` | No | `('db:'::text  /  /  (CURRENT_USER)::text)` |
| `origin_kind` | `text` | No | `'manual'::text` |
| `review_state` | `text` | No | `'pending'::text` |
| `archived_at` | `timestamp with time zone` | Yes | `` |
| `archived_by` | `uuid` | Yes | `` |

Constraints:

- `ck_support_observations_0`: `CHECK (origin_kind = ANY (ARRAY['manual'::text, 'import'::text]))`.
- `ck_support_observations_1`: `CHECK (review_state = ANY (ARRAY['pending'::text, 'accepted'::text, 'needs_review'::text]))`.
- `ck_support_observations_2`: `CHECK ((archived_at IS NULL) = (archived_by IS NULL))`.
- `ck_support_observations_3`: `CHECK (num_nonnulls(numeric_value, text_value) = 1)`.
- `fk_support_observations_0`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_support_observations_1`: `FOREIGN KEY (updated_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `fk_support_observations_2`: `FOREIGN KEY (child_id) REFERENCES public.children(id) ON DELETE RESTRICT`.
- `fk_support_observations_3`: `FOREIGN KEY (participant_link_id, child_id) REFERENCES public.child_caregivers(id, child_id) ON DELETE RESTRICT`.
- `fk_support_observations_4`: `FOREIGN KEY (program_vocabulary, program_code) REFERENCES public.reference_values(vocabulary, code) ON DELETE RESTRICT`.
- `fk_support_observations_5`: `FOREIGN KEY (archived_by) REFERENCES auth.users(id) ON DELETE RESTRICT`.
- `lineage_support_observations`: `TRIGGER DEFERRABLE INITIALLY DEFERRED`.
- `pk_support_observations`: `PRIMARY KEY (id)`.
