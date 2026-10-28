# Final live table and key inventory

Counts verified 28 October 2026, 13:49:50 IST; project `hmlbdozsqxlwzvjimjwh`, Tokyo non-production. 197 approved date transactions completed; schema/keys unchanged.

| Table | Rows | Primary key | Boundary |
|---|---:|---|---|
| `gk_private.access_memberships` | 0 | `user_id` | Restricted |
| `gk_private.attendance_import_staging` | 43,160 | `id` | Restricted |
| `gk_private.caregivers` | 716 | `id` | Restricted |
| `gk_private.child_private_profiles` | 371 | `child_id` | Restricted |
| `gk_private.identity_candidates` | 2,089 | `id` | Restricted |
| `gk_private.questionnaire_answers` | 3,286 | `id` | Restricted |
| `gk_private.record_audit_events` | 28,490 | `id` | Restricted |
| `gk_private.recovery_actions` | 197 | `id` | Restricted |
| `gk_private.source_artifacts` | 12 | `id` | Restricted |
| `gk_private.source_provenance` | 5,969 | `id` | Restricted |
| `gk_private.source_records` | 20,432 | `id` | Restricted |
| `public.adl_visits` | 0 | `id` | RLS protected |
| `public.attendance_observations` | 0 | `id` | RLS protected |
| `public.child_caregivers` | 716 | `id` | RLS protected |
| `public.children` | 371 | `id` | RLS protected |
| `public.program_changes` | 128 | `id` | RLS protected |
| `public.questionnaire_items` | 31 | `id` | RLS protected |
| `public.questionnaire_responses` | 106 | `id` | RLS protected |
| `public.reference_values` | 47 | `vocabulary, code` | RLS protected |
| `public.support_observations` | 0 | `id` | RLS protected |

## Complete foreign-key reference

- `gk_private.access_memberships(created_by)` → `auth.users(id)` — `fk_access_memberships_0`.
- `gk_private.access_memberships(updated_by)` → `auth.users(id)` — `fk_access_memberships_1`.
- `gk_private.access_memberships(user_id)` → `auth.users(id)` — `fk_access_memberships_2`.
- `gk_private.access_memberships(role_vocabulary, role_code)` → `public.reference_values(vocabulary, code)` — `fk_access_memberships_3`.
- `gk_private.access_memberships(archived_by)` → `auth.users(id)` — `fk_access_memberships_4`.
- `gk_private.attendance_import_staging(artifact_id)` → `gk_private.source_artifacts(id)` — `attendance_import_staging_artifact_id_fkey`.
- `gk_private.attendance_import_staging(header_source_record_id)` → `gk_private.source_records(id)` — `attendance_import_staging_header_source_record_id_fkey`.
- `gk_private.attendance_import_staging(source_record_id)` → `gk_private.source_records(id)` — `attendance_import_staging_source_record_id_fkey`.
- `gk_private.attendance_import_staging(verified_child_id)` → `public.children(id)` — `attendance_import_staging_verified_child_id_fkey`.
- `gk_private.caregivers(created_by)` → `auth.users(id)` — `fk_caregivers_0`.
- `gk_private.caregivers(updated_by)` → `auth.users(id)` — `fk_caregivers_1`.
- `gk_private.caregivers(archived_by)` → `auth.users(id)` — `fk_caregivers_2`.
- `gk_private.child_private_profiles(created_by)` → `auth.users(id)` — `fk_child_private_profiles_0`.
- `gk_private.child_private_profiles(updated_by)` → `auth.users(id)` — `fk_child_private_profiles_1`.
- `gk_private.child_private_profiles(child_id)` → `public.children(id)` — `fk_child_private_profiles_2`.
- `gk_private.child_private_profiles(archived_by)` → `auth.users(id)` — `fk_child_private_profiles_3`.
- `gk_private.identity_candidates(source_record_id)` → `gk_private.source_records(id)` — `fk_identity_candidates_0`.
- `gk_private.identity_candidates(child_id)` → `public.children(id)` — `fk_identity_candidates_1`.
- `gk_private.identity_candidates(caregiver_id)` → `gk_private.caregivers(id)` — `fk_identity_candidates_2`.
- `gk_private.identity_candidates(created_by)` → `auth.users(id)` — `fk_identity_candidates_3`.
- `gk_private.identity_candidates(updated_by)` → `auth.users(id)` — `fk_identity_candidates_4`.
- `gk_private.questionnaire_answers(created_by)` → `auth.users(id)` — `fk_questionnaire_answers_0`.
- `gk_private.questionnaire_answers(updated_by)` → `auth.users(id)` — `fk_questionnaire_answers_1`.
- `gk_private.questionnaire_answers(response_id, definition_key)` → `public.questionnaire_responses(id, definition_key)` — `fk_questionnaire_answers_2`.
- `gk_private.questionnaire_answers(item_id, definition_key)` → `public.questionnaire_items(id, definition_key)` — `fk_questionnaire_answers_3`.
- `gk_private.questionnaire_answers(archived_by)` → `auth.users(id)` — `fk_questionnaire_answers_4`.
- `gk_private.record_audit_events(created_by)` → `auth.users(id)` — `fk_record_audit_events_0`.
- `gk_private.record_audit_events(updated_by)` → `auth.users(id)` — `fk_record_audit_events_1`.
- `gk_private.recovery_actions(source_record_id)` → `gk_private.source_records(id)` — `fk_recovery_actions_0`.
- `gk_private.recovery_actions(child_id)` → `public.children(id)` — `fk_recovery_actions_1`.
- `gk_private.recovery_actions(caregiver_id)` → `gk_private.caregivers(id)` — `fk_recovery_actions_2`.
- `gk_private.recovery_actions(created_by)` → `auth.users(id)` — `fk_recovery_actions_3`.
- `gk_private.recovery_actions(updated_by)` → `auth.users(id)` — `fk_recovery_actions_4`.
- `gk_private.recovery_actions(donor_source_record_id)` → `gk_private.source_records(id)` — `fk_recovery_actions_5`.
- `gk_private.source_artifacts(created_by)` → `auth.users(id)` — `fk_source_artifacts_0`.
- `gk_private.source_artifacts(updated_by)` → `auth.users(id)` — `fk_source_artifacts_1`.
- `gk_private.source_provenance(created_by)` → `auth.users(id)` — `fk_source_provenance_0`.
- `gk_private.source_provenance(updated_by)` → `auth.users(id)` — `fk_source_provenance_1`.
- `gk_private.source_provenance(answer_id)` → `gk_private.questionnaire_answers(id)` — `fk_source_provenance_10`.
- `gk_private.source_provenance(attendance_id)` → `public.attendance_observations(id)` — `fk_source_provenance_11`.
- `gk_private.source_provenance(support_id)` → `public.support_observations(id)` — `fk_source_provenance_12`.
- `gk_private.source_provenance(adl_id)` → `public.adl_visits(id)` — `fk_source_provenance_13`.
- `gk_private.source_provenance(reference_vocabulary, reference_code)` → `public.reference_values(vocabulary, code)` — `fk_source_provenance_14`.
- `gk_private.source_provenance(source_record_id)` → `gk_private.source_records(id)` — `fk_source_provenance_2`.
- `gk_private.source_provenance(child_id)` → `public.children(id)` — `fk_source_provenance_3`.
- `gk_private.source_provenance(private_profile_child_id)` → `gk_private.child_private_profiles(child_id)` — `fk_source_provenance_4`.
- `gk_private.source_provenance(caregiver_id)` → `gk_private.caregivers(id)` — `fk_source_provenance_5`.
- `gk_private.source_provenance(child_caregiver_id)` → `public.child_caregivers(id)` — `fk_source_provenance_6`.
- `gk_private.source_provenance(program_change_id)` → `public.program_changes(id)` — `fk_source_provenance_7`.
- `gk_private.source_provenance(response_id)` → `public.questionnaire_responses(id)` — `fk_source_provenance_8`.
- `gk_private.source_provenance(item_id)` → `public.questionnaire_items(id)` — `fk_source_provenance_9`.
- `gk_private.source_records(created_by)` → `auth.users(id)` — `fk_source_records_0`.
- `gk_private.source_records(updated_by)` → `auth.users(id)` — `fk_source_records_1`.
- `gk_private.source_records(artifact_id)` → `gk_private.source_artifacts(id)` — `fk_source_records_2`.
- `public.adl_visits(created_by)` → `auth.users(id)` — `fk_adl_visits_0`.
- `public.adl_visits(updated_by)` → `auth.users(id)` — `fk_adl_visits_1`.
- `public.adl_visits(child_id)` → `public.children(id)` — `fk_adl_visits_2`.
- `public.adl_visits(program_vocabulary, program_code)` → `public.reference_values(vocabulary, code)` — `fk_adl_visits_3`.
- `public.adl_visits(archived_by)` → `auth.users(id)` — `fk_adl_visits_4`.
- `public.attendance_observations(created_by)` → `auth.users(id)` — `fk_attendance_observations_0`.
- `public.attendance_observations(updated_by)` → `auth.users(id)` — `fk_attendance_observations_1`.
- `public.attendance_observations(child_id)` → `public.children(id)` — `fk_attendance_observations_2`.
- `public.attendance_observations(service_vocabulary, service_code)` → `public.reference_values(vocabulary, code)` — `fk_attendance_observations_3`.
- `public.attendance_observations(mark_vocabulary, mark_code)` → `public.reference_values(vocabulary, code)` — `fk_attendance_observations_4`.
- `public.attendance_observations(program_vocabulary, program_code)` → `public.reference_values(vocabulary, code)` — `fk_attendance_observations_5`.
- `public.attendance_observations(archived_by)` → `auth.users(id)` — `fk_attendance_observations_6`.
- `public.child_caregivers(created_by)` → `auth.users(id)` — `fk_child_caregivers_0`.
- `public.child_caregivers(updated_by)` → `auth.users(id)` — `fk_child_caregivers_1`.
- `public.child_caregivers(child_id)` → `public.children(id)` — `fk_child_caregivers_2`.
- `public.child_caregivers(caregiver_id)` → `gk_private.caregivers(id)` — `fk_child_caregivers_3`.
- `public.child_caregivers(role_vocabulary, role_code)` → `public.reference_values(vocabulary, code)` — `fk_child_caregivers_4`.
- `public.child_caregivers(archived_by)` → `auth.users(id)` — `fk_child_caregivers_5`.
- `public.children(created_by)` → `auth.users(id)` — `fk_children_0`.
- `public.children(updated_by)` → `auth.users(id)` — `fk_children_1`.
- `public.children(program_vocabulary, current_program_code)` → `public.reference_values(vocabulary, code)` — `fk_children_2`.
- `public.children(program_vocabulary, admitted_program_code)` → `public.reference_values(vocabulary, code)` — `fk_children_3`.
- `public.children(status_vocabulary, child_status_code)` → `public.reference_values(vocabulary, code)` — `fk_children_4`.
- `public.children(archived_by)` → `auth.users(id)` — `fk_children_5`.
- `public.program_changes(created_by)` → `auth.users(id)` — `fk_program_changes_0`.
- `public.program_changes(updated_by)` → `auth.users(id)` — `fk_program_changes_1`.
- `public.program_changes(child_id)` → `public.children(id)` — `fk_program_changes_2`.
- `public.program_changes(program_vocabulary, program_code)` → `public.reference_values(vocabulary, code)` — `fk_program_changes_3`.
- `public.program_changes(archived_by)` → `auth.users(id)` — `fk_program_changes_4`.
- `public.questionnaire_items(created_by)` → `auth.users(id)` — `fk_questionnaire_items_0`.
- `public.questionnaire_items(updated_by)` → `auth.users(id)` — `fk_questionnaire_items_1`.
- `public.questionnaire_items(definition_vocabulary, definition_key)` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_items_2`.
- `public.questionnaire_items(archived_by)` → `auth.users(id)` — `fk_questionnaire_items_3`.
- `public.questionnaire_responses(created_by)` → `auth.users(id)` — `fk_questionnaire_responses_0`.
- `public.questionnaire_responses(updated_by)` → `auth.users(id)` — `fk_questionnaire_responses_1`.
- `public.questionnaire_responses(child_caregiver_id)` → `public.child_caregivers(id)` — `fk_questionnaire_responses_2`.
- `public.questionnaire_responses(definition_vocabulary, definition_key)` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_responses_3`.
- `public.questionnaire_responses(program_vocabulary, program_code)` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_responses_4`.
- `public.questionnaire_responses(centre_vocabulary, centre_code)` → `public.reference_values(vocabulary, code)` — `fk_questionnaire_responses_5`.
- `public.questionnaire_responses(archived_by)` → `auth.users(id)` — `fk_questionnaire_responses_6`.
- `public.reference_values(created_by)` → `auth.users(id)` — `fk_reference_values_0`.
- `public.reference_values(updated_by)` → `auth.users(id)` — `fk_reference_values_1`.
- `public.reference_values(archived_by)` → `auth.users(id)` — `fk_reference_values_2`.
- `public.support_observations(created_by)` → `auth.users(id)` — `fk_support_observations_0`.
- `public.support_observations(updated_by)` → `auth.users(id)` — `fk_support_observations_1`.
- `public.support_observations(child_id)` → `public.children(id)` — `fk_support_observations_2`.
- `public.support_observations(participant_link_id, child_id)` → `public.child_caregivers(id, child_id)` — `fk_support_observations_3`.
- `public.support_observations(program_vocabulary, program_code)` → `public.reference_values(vocabulary, code)` — `fk_support_observations_4`.
- `public.support_observations(archived_by)` → `auth.users(id)` — `fk_support_observations_5`.
