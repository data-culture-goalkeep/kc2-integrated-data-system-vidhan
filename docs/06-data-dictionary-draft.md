> Historical milestone preserved. Current deployed 20-table model and final results: [Phase 1 handover](PHASE1-HANDOVER.md), [final dictionary](FINAL-DATA-DICTIONARY.md), [actual ER diagram](visual/final-deployed-er.svg).

# Data dictionary — final recommendation, not deployed

Complete target column types and nullability follow. Source positions and original field labels remain in the [final mapping](evidence/final-source-target-coverage.csv); previous source-oriented dictionary is preserved in [Stage 2 archive](archive/stage2-data-dictionary.md). SQL contains exact defaults, checks, grants and triggers.


## public.reference_values

Database-controlled source-scoped categories; replaces separate PROGRAM-only lookup. Grain: One approved vocabulary/code.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| vocabulary | text | no | PK; vocabulary |
| code | text | no | PK; code |
| label | text | no | label |
| active | boolean | no | active |
| sort_order | integer | yes | sort order |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |
| permissions | jsonb | no | permissions |
| approval_reference | text | yes | approval reference |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |

## public.children

Canonical operational identity/context under RLS; display names remain personal. Grain: One resolved source master identity.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| display_name | text | yes | display name |
| current_program_code | text | yes | FK; current program code |
| admitted_program_code | text | yes | FK; admitted program code |
| child_status_code | text | yes | FK; child status code |
| program_vocabulary | text | no | FK; program vocabulary |
| status_vocabulary | text | no | FK; status vocabulary |
| joining_date | date | yes | joining date |
| dropout_date | date | yes | dropout date |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |
| child_business_id | text | no | candidate uniqueness component; child business id |

## gk_private.child_private_profiles

Separates restricted child/family/health/financial attributes from operational reads. Grain: Zero or one restricted profile per child.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| child_id | uuid | no | PK; FK; child id |
| birth_date | date | yes | birth date |
| gender_reported | text | yes | gender reported |
| child_national_id | text | yes | child national id |
| blood_group_reported | text | yes | blood group reported |
| contact_address | text | yes | contact address |
| sibling_count_reported | text | yes | sibling count reported |
| diagnosis_1 | text | yes | diagnosis 1 |
| diagnosis_2 | text | yes | diagnosis 2 |
| udid_number | text | yes | udid number |
| udid_disability_reported | text | yes | udid disability reported |
| udid_validity_reported | text | yes | udid validity reported |
| udid_percentage_reported | text | yes | udid percentage reported |
| insurance_number | text | yes | insurance number |
| assessment_date | date | yes | assessment date |
| assessment_age_reported | text | yes | assessment age reported |
| family_income_reported | text | yes | family income reported |
| economic_category_reported | text | yes | economic category reported |
| assessment_fee | numeric | yes | assessment fee |
| monthly_fee | numeric | yes | monthly fee |
| monthly_fee_remarks | text | yes | monthly fee remarks |
| concession_reported | text | yes | concession reported |
| social_category_reported | text | yes | social category reported |
| religion_reported | text | yes | religion reported |
| consent_reported | text | yes | consent reported |
| dropout_reason_reported | text | yes | dropout reason reported |
| transition_date | date | yes | transition date |
| comments | text | yes | comments |
| severity_reported | text | yes | severity reported |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## gk_private.caregivers

Resolved caregiver identity; no global person deduplication by display name. Grain: One caregiver per verified authoritative caregiver business identifier.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| display_name | text | yes | display name |
| birth_date | date | yes | birth date |
| contact_phone | text | yes | contact phone |
| contact_email | text | yes | contact email |
| national_id | text | yes | national id |
| employment_reported | text | yes | employment reported |
| education_reported | text | yes | education reported |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |
| caregiver_business_id | text | no | candidate uniqueness component; caregiver business id |

## public.child_caregivers

Preserves each child/caregiver association independently from person identity. Grain: One child/caregiver association.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; candidate uniqueness component; id |
| child_id | uuid | no | FK; candidate uniqueness component; child id |
| caregiver_id | uuid | no | FK; candidate uniqueness component; caregiver id |
| role_code | text | yes | FK; role code |
| role_vocabulary | text | no | FK; role vocabulary |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## public.program_changes

Unpivots promotion slots without inventing interval ends. Grain: One source promotion observation.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| child_id | uuid | no | FK; child id |
| program_code | text | yes | FK; program code |
| program_vocabulary | text | no | FK; program vocabulary |
| promotion_date | date | yes | promotion date |
| source_slot | integer | yes | source slot |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## public.questionnaire_responses

Submission context; references the validated pair instead of redundant independent IDs. Grain: One approved response row/submission.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; candidate uniqueness component; id |
| child_caregiver_id | uuid | no | FK; child caregiver id |
| definition_key | text | no | FK; candidate uniqueness component; definition key |
| definition_vocabulary | text | no | FK; definition vocabulary |
| assessment_date | date | yes | assessment date |
| program_code | text | yes | FK; program code |
| program_vocabulary | text | no | FK; program vocabulary |
| centre_code | text | yes | FK; centre code |
| centre_vocabulary | text | no | FK; centre vocabulary |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## public.questionnaire_items

Actual question definitions; one version key without premature questionnaire-framework tables. Grain: One actual question column within an approved definition.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; candidate uniqueness component; id |
| definition_key | text | no | FK; candidate uniqueness component; definition key |
| definition_vocabulary | text | no | FK; definition vocabulary |
| item_key | text | no | candidate uniqueness component; item key |
| prompt | text | no | prompt |
| section_label | text | yes | section label |
| value_kind | text | no | value kind |
| ordinal | integer | no | candidate uniqueness component; ordinal |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## gk_private.questionnaire_answers

Typed values replace untyped recorded_value; preserves missing answers separately. Grain: One response/item.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| response_id | uuid | no | FK; candidate uniqueness component; response id |
| item_id | uuid | no | FK; candidate uniqueness component; item id |
| definition_key | text | no | FK; definition key |
| numeric_value | numeric | yes | numeric value |
| text_value | text | yes | text value |
| answer_state | text | no | answer state |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## public.attendance_observations

Dated source marks kept distinct by service; unresolved names/dates remain staged. Grain: One resolved child/service/source-date observation.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| child_id | uuid | no | FK; child id |
| service_code | text | no | FK; service code |
| service_vocabulary | text | no | FK; service vocabulary |
| attendance_date | date | no | attendance date |
| mark_code | text | no | FK; mark code |
| mark_vocabulary | text | no | FK; mark vocabulary |
| program_code | text | yes | FK; program code |
| program_vocabulary | text | no | FK; program vocabulary |
| batch_reported | text | yes | batch reported |
| child_status_reported | text | yes | child status reported |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## public.support_observations

Source-cell support observations; not necessarily one person or a daily P/A event. Grain: One approved support matrix cell.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| child_id | uuid | no | FK; child id |
| participant_link_id | uuid | yes | FK; participant link id |
| event_reference | text | no | event reference |
| event_date | date | yes | event date |
| program_code | text | yes | FK; program code |
| program_vocabulary | text | no | FK; program vocabulary |
| numeric_value | numeric | yes | numeric value |
| text_value | text | yes | text value |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## public.adl_visits

Preserves true visit flags and undated historical exceptions. Grain: One checked visit-slot observation.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| child_id | uuid | no | FK; child id |
| program_code | text | yes | FK; program code |
| program_vocabulary | text | no | FK; program vocabulary |
| visit_flag | boolean | no | visit flag |
| visit_date | date | yes | visit date |
| source_slot | integer | yes | source slot |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| origin_kind | text | no | origin kind |
| review_state | text | no | review state |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |

## gk_private.source_artifacts

Immutable snapshot identity and worksheet/column schema. Grain: One authorized source-file version.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| source_namespace | text | no | candidate uniqueness component; source namespace |
| file_code | text | no | candidate uniqueness component; file code |
| version_sha256 | text | no | candidate uniqueness component; version sha256 |
| source_locator | text | yes | source locator |
| worksheet_manifest | jsonb | no | worksheet manifest |
| captured_at | timestamptz | no | captured at |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |

## gk_private.source_records

Restricted staging/reconciliation for every nonempty source row, including unresolved/derived fields. Grain: One artifact/native-sheet/original-row.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| artifact_id | uuid | no | FK; candidate uniqueness component; artifact id |
| native_sheet_key | text | no | candidate uniqueness component; native sheet key |
| source_row | integer | no | candidate uniqueness component; source row |
| cell_payload | jsonb | no | cell payload |
| processing_state | text | no | processing state |
| diagnostics | jsonb | yes | diagnostics |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |

## gk_private.source_provenance

Many-source-row/cell to one target without unconstrained polymorphic IDs. Grain: One source-column group -> one typed target/field group.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| source_record_id | uuid | no | FK; source record id |
| source_columns | text[] | no | source columns |
| target_fields | text[] | no | target fields |
| rule_reference | text | no | rule reference |
| contribution_state | text | no | contribution state |
| child_id | uuid | yes | FK; child id |
| private_profile_child_id | uuid | yes | FK; private profile child id |
| caregiver_id | uuid | yes | FK; caregiver id |
| child_caregiver_id | uuid | yes | FK; child caregiver id |
| program_change_id | uuid | yes | FK; program change id |
| response_id | uuid | yes | FK; response id |
| item_id | uuid | yes | FK; item id |
| answer_id | uuid | yes | FK; answer id |
| attendance_id | uuid | yes | FK; attendance id |
| support_id | uuid | yes | FK; support id |
| adl_id | uuid | yes | FK; adl id |
| reference_vocabulary | text | yes | FK; reference vocabulary |
| reference_code | text | yes | FK; reference code |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |

## gk_private.access_memberships

Application authorization independent of Google sign-in and business caregivers. Grain: One admitted auth user in this dedicated project.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| user_id | uuid | no | PK; FK; user id |
| approved_email_domain | text | no | approved email domain |
| role_code | text | no | FK; role code |
| role_vocabulary | text | no | FK; role vocabulary |
| active | boolean | no | active |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
| archived_at | timestamptz | yes | archived at |
| archived_by | uuid | yes | FK; archived by |
| private_read | boolean | no | private read |
| private_write | boolean | no | private write |
| approval_reference | text | yes | approval reference |

## gk_private.identity_candidates

Preserve exact-ID matches and unapproved name/context candidates. Grain: One staged row/candidate identity/method.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| source_record_id | uuid | no | FK; source record id |
| child_id | uuid | yes | FK; child id |
| caregiver_id | uuid | yes | FK; caregiver id |
| match_method | text | no | match method |
| resolution_status | text | no | resolution status |
| evidence | jsonb | no | evidence |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |

## gk_private.recovery_actions

Append-only original/proposed value, donor, method and validation audit. Grain: One recovery/suggestion per source cell and run.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| source_record_id | uuid | no | FK; source record id |
| donor_source_record_id | uuid | yes | FK; donor source record id |
| child_id | uuid | yes | FK; child id |
| caregiver_id | uuid | yes | FK; caregiver id |
| source_column | text | no | source column |
| field_key | text | no | field key |
| original_value | jsonb | no | original value |
| recovered_value | jsonb | yes | recovered value |
| method | text | no | method |
| validation_status | text | no | validation status |
| identity_verified | boolean | no | identity verified |
| authoritative_source | boolean | no | authoritative source |
| meaning_equivalent | boolean | no | meaning equivalent |
| has_conflict | boolean | no | has conflict |
| evidence | jsonb | no | evidence |
| run_id | uuid | no | run id |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |

## gk_private.record_audit_events

Append-only operational and access-change history; no API insertion. Grain: One database-generated row change event.

| Column | PostgreSQL type | Nullable | Key / purpose |
| --- | --- | --- | --- |
| id | uuid | no | PK; id |
| schema_name | text | no | schema name |
| table_name | text | no | table name |
| record_key | jsonb | no | record key |
| operation | text | no | operation |
| before_value | jsonb | yes | before value |
| after_value | jsonb | yes | after value |
| created_at | timestamptz | no | created at |
| updated_at | timestamptz | no | updated at |
| created_by | uuid | yes | FK; created by |
| updated_by | uuid | yes | FK; updated by |
| actor_ref | text | no | actor ref |
