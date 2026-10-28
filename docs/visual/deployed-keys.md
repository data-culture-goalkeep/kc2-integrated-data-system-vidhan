# Deployed primary and foreign keys

Verified 27 October 2026, 17:57 IST. PK identifies a row; FK requires a related row to exist. Composite keys must be used together. All 99 deployed FKs are listed below; common actor FKs point to managed auth.users. SVG lines group parallel table pairs. Source provenance targets are mutually exclusive per row; a graph edge is a permitted link, not proof every row uses it.

## gk_private.access_memberships

Primary key: `user_id`.

- `created_by` → `auth.users(id)` — `fk_access_memberships_0`.
- `updated_by` → `auth.users(id)` — `fk_access_memberships_1`.
- `user_id` → `auth.users(id)` — `fk_access_memberships_2`.
- `role_vocabulary, role_code` → `public.reference_values(vocabulary, code)` — `fk_access_memberships_3`.
- `archived_by` → `auth.users(id)` — `fk_access_memberships_4`.

## gk_private.caregivers

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_caregivers_0`.
- `updated_by` → `auth.users(id)` — `fk_caregivers_1`.
- `archived_by` → `auth.users(id)` — `fk_caregivers_2`.

## gk_private.child_private_profiles

Primary key: `child_id`.

- `created_by` → `auth.users(id)` — `fk_child_private_profiles_0`.
- `updated_by` → `auth.users(id)` — `fk_child_private_profiles_1`.
- `child_id` → `public.children(id)` — `fk_child_private_profiles_2`.
- `archived_by` → `auth.users(id)` — `fk_child_private_profiles_3`.

## gk_private.identity_candidates

Primary key: `id`.

- `source_record_id` → `gk_private.source_records(id)` — `fk_identity_candidates_0`.
- `child_id` → `public.children(id)` — `fk_identity_candidates_1`.
- `caregiver_id` → `gk_private.caregivers(id)` — `fk_identity_candidates_2`.
- `created_by` → `auth.users(id)` — `fk_identity_candidates_3`.
- `updated_by` → `auth.users(id)` — `fk_identity_candidates_4`.

## gk_private.questionnaire_answers

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_questionnaire_answers_0`.
- `updated_by` → `auth.users(id)` — `fk_questionnaire_answers_1`.
- `response_id, definition_key` → `public.questionnaire_responses(id, definition_key)` — `fk_questionnaire_answers_2`.
- `item_id, definition_key` → `public.questionnaire_items(id, definition_key)` — `fk_questionnaire_answers_3`.
- `archived_by` → `auth.users(id)` — `fk_questionnaire_answers_4`.

## gk_private.record_audit_events

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_record_audit_events_0`.
- `updated_by` → `auth.users(id)` — `fk_record_audit_events_1`.

## gk_private.recovery_actions

Primary key: `id`.

- `source_record_id` → `gk_private.source_records(id)` — `fk_recovery_actions_0`.
- `child_id` → `public.children(id)` — `fk_recovery_actions_1`.
- `caregiver_id` → `gk_private.caregivers(id)` — `fk_recovery_actions_2`.
- `created_by` → `auth.users(id)` — `fk_recovery_actions_3`.
- `updated_by` → `auth.users(id)` — `fk_recovery_actions_4`.
- `donor_source_record_id` → `gk_private.source_records(id)` — `fk_recovery_actions_5`.

## gk_private.source_artifacts

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_source_artifacts_0`.
- `updated_by` → `auth.users(id)` — `fk_source_artifacts_1`.

## gk_private.source_provenance

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_source_provenance_0`.
- `updated_by` → `auth.users(id)` — `fk_source_provenance_1`.
- `answer_id` → `gk_private.questionnaire_answers(id)` — `fk_source_provenance_10`.
- `attendance_id` → `public.attendance_observations(id)` — `fk_source_provenance_11`.
- `support_id` → `public.support_observations(id)` — `fk_source_provenance_12`.
- `adl_id` → `public.adl_visits(id)` — `fk_source_provenance_13`.
- `reference_vocabulary, reference_code` → `public.reference_values(vocabulary, code)` — `fk_source_provenance_14`.
- `source_record_id` → `gk_private.source_records(id)` — `fk_source_provenance_2`.
- `child_id` → `public.children(id)` — `fk_source_provenance_3`.
- `private_profile_child_id` → `gk_private.child_private_profiles(child_id)` — `fk_source_provenance_4`.
- `caregiver_id` → `gk_private.caregivers(id)` — `fk_source_provenance_5`.
- `child_caregiver_id` → `public.child_caregivers(id)` — `fk_source_provenance_6`.
- `program_change_id` → `public.program_changes(id)` — `fk_source_provenance_7`.
- `response_id` → `public.questionnaire_responses(id)` — `fk_source_provenance_8`.
- `item_id` → `public.questionnaire_items(id)` — `fk_source_provenance_9`.

## gk_private.source_records

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_source_records_0`.
- `updated_by` → `auth.users(id)` — `fk_source_records_1`.
- `artifact_id` → `gk_private.source_artifacts(id)` — `fk_source_records_2`.

## public.adl_visits

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_adl_visits_0`.
- `updated_by` → `auth.users(id)` — `fk_adl_visits_1`.
- `child_id` → `public.children(id)` — `fk_adl_visits_2`.
- `program_vocabulary, program_code` → `public.reference_values(vocabulary, code)` — `fk_adl_visits_3`.
- `archived_by` → `auth.users(id)` — `fk_adl_visits_4`.

## public.attendance_observations

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_attendance_observations_0`.
- `updated_by` → `auth.users(id)` — `fk_attendance_observations_1`.
- `child_id` → `public.children(id)` — `fk_attendance_observations_2`.
- `service_vocabulary, service_code` → `public.reference_values(vocabulary, code)` — `fk_attendance_observations_3`.
- `mark_vocabulary, mark_code` → `public.reference_values(vocabulary, code)` — `fk_attendance_observations_4`.
- `program_vocabulary, program_code` → `public.reference_values(vocabulary, code)` — `fk_attendance_observations_5`.
- `archived_by` → `auth.users(id)` — `fk_attendance_observations_6`.

## public.child_caregivers

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_child_caregivers_0`.
- `updated_by` → `auth.users(id)` — `fk_child_caregivers_1`.
- `child_id` → `public.children(id)` — `fk_child_caregivers_2`.
- `caregiver_id` → `gk_private.caregivers(id)` — `fk_child_caregivers_3`.
- `role_vocabulary, role_code` → `public.reference_values(vocabulary, code)` — `fk_child_caregivers_4`.
- `archived_by` → `auth.users(id)` — `fk_child_caregivers_5`.

## public.children

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_children_0`.
- `updated_by` → `auth.users(id)` — `fk_children_1`.
- `program_vocabulary, current_program_code` → `public.reference_values(vocabulary, code)` — `fk_children_2`.
- `program_vocabulary, admitted_program_code` → `public.reference_values(vocabulary, code)` — `fk_children_3`.
- `status_vocabulary, child_status_code` → `public.reference_values(vocabulary, code)` — `fk_children_4`.
- `archived_by` → `auth.users(id)` — `fk_children_5`.

## public.program_changes

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_program_changes_0`.
- `updated_by` → `auth.users(id)` — `fk_program_changes_1`.
- `child_id` → `public.children(id)` — `fk_program_changes_2`.
- `program_vocabulary, program_code` → `public.reference_values(vocabulary, code)` — `fk_program_changes_3`.
- `archived_by` → `auth.users(id)` — `fk_program_changes_4`.

## public.questionnaire_items

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_questionnaire_items_0`.
- `updated_by` → `auth.users(id)` — `fk_questionnaire_items_1`.
- `definition_vocabulary, definition_key` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_items_2`.
- `archived_by` → `auth.users(id)` — `fk_questionnaire_items_3`.

## public.questionnaire_responses

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_questionnaire_responses_0`.
- `updated_by` → `auth.users(id)` — `fk_questionnaire_responses_1`.
- `child_caregiver_id` → `public.child_caregivers(id)` — `fk_questionnaire_responses_2`.
- `definition_vocabulary, definition_key` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_responses_3`.
- `program_vocabulary, program_code` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_responses_4`.
- `centre_vocabulary, centre_code` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_responses_5`.
- `archived_by` → `auth.users(id)` — `fk_questionnaire_responses_6`.

## public.reference_values

Primary key: `vocabulary, code`.

- `created_by` → `auth.users(id)` — `fk_reference_values_0`.
- `updated_by` → `auth.users(id)` — `fk_reference_values_1`.
- `archived_by` → `auth.users(id)` — `fk_reference_values_2`.

## public.support_observations

Primary key: `id`.

- `created_by` → `auth.users(id)` — `fk_support_observations_0`.
- `updated_by` → `auth.users(id)` — `fk_support_observations_1`.
- `child_id` → `public.children(id)` — `fk_support_observations_2`.
- `participant_link_id, child_id` → `public.child_caregivers(id, child_id)` — `fk_support_observations_3`.
- `program_vocabulary, program_code` → `public.reference_values(vocabulary, code)` — `fk_support_observations_4`.
- `archived_by` → `auth.users(id)` — `fk_support_observations_5`.
