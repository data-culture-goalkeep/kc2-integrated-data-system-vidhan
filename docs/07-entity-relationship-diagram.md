# Stage 2 — Revised draft ER diagram

**DRAFT, not an implemented database.** Seventeen proposed tables: sixteen core and conditional ACTIVITY_LOGS. AUTH_USERS is Supabase-managed and excluded from that count. Common audit FKs to AUTH_USERS are omitted for readability; full fields/keys are in the model specification. Grouped lookup edges represent separate vocabulary-scoped FKs. Optional target edges in SOURCE_PROVENANCE are mutually exclusive per row, not simultaneous links to every entity. A dotted edge marks the optional activity extension.

```mermaid
erDiagram
    REFERENCE_VALUES {
        text vocabulary PK
        text code PK
        text label
        boolean active
        integer sort_order
    }
    CHILDREN {
        uuid id PK
        text source_namespace
        text source_admission_number
        text display_name
        text current_program_code FK
        text admitted_program_code FK
        text child_status_code FK
        date joining_date
        date dropout_date
    }
    CHILD_PRIVATE_PROFILES {
        uuid child_id PK,FK
        date birth_date
        text gender_reported
        text child_national_id
        text blood_group_reported
        text contact_address
        text sibling_count_reported
        text diagnosis_1
        text diagnosis_2
    }
    CAREGIVERS {
        uuid id PK
        text display_name
        date birth_date
        text contact_phone
        text contact_email
        text national_id
        text employment_reported
        text education_reported
        text origin_kind
    }
    CHILD_CAREGIVERS {
        uuid id PK
        uuid child_id FK
        uuid caregiver_id FK
        text source_namespace
        text source_caregiver_code
        text role_code FK
        text origin_kind
        text review_state
    }
    PROGRAM_CHANGES {
        uuid id PK
        uuid child_id FK
        text program_code FK
        date promotion_date
        integer source_slot
        text origin_kind
        text review_state
    }
    QUESTIONNAIRE_RESPONSES {
        uuid id PK
        uuid child_caregiver_id FK
        text definition_key FK
        date assessment_date
        text program_code FK
        text centre_code FK
        text origin_kind
        text review_state
    }
    QUESTIONNAIRE_ITEMS {
        uuid id PK
        text definition_key FK
        text item_key
        text prompt
        text section_label
        text value_kind
        integer ordinal
        text origin_kind
        text review_state
    }
    QUESTIONNAIRE_ANSWERS {
        uuid id PK
        uuid response_id FK
        uuid item_id FK
        text definition_key FK
        numeric numeric_value
        text text_value
        text answer_state
        text origin_kind
        text review_state
    }
    ATTENDANCE_OBSERVATIONS {
        uuid id PK
        uuid child_id FK
        text service_code FK
        date attendance_date
        text mark_code FK
        text program_code FK
        text batch_reported
        text child_status_reported
        text origin_kind
    }
    SUPPORT_OBSERVATIONS {
        uuid id PK
        uuid child_id FK
        uuid participant_link_id FK
        text event_reference
        date event_date
        text program_code FK
        numeric numeric_value
        text text_value
        text origin_kind
    }
    ADL_VISITS {
        uuid id PK
        uuid child_id FK
        text program_code FK
        boolean visit_flag
        date visit_date
        integer source_slot
        text origin_kind
        text review_state
    }
    ACTIVITY_LOGS {
        uuid id PK
        text activity_description
        date activity_date
        text source_status_reported
        text batch_reported
        text participant_count_reported
        text origin_kind
        text review_state
    }
    SOURCE_ARTIFACTS {
        uuid id PK
        text source_namespace
        text file_code
        text version_sha256
        text source_locator
        jsonb worksheet_manifest
        timestamptz captured_at
    }
    SOURCE_RECORDS {
        uuid id PK
        uuid artifact_id FK
        text native_sheet_key
        integer source_row
        jsonb cell_payload
        text processing_state
        jsonb diagnostics
    }
    SOURCE_PROVENANCE {
        uuid id PK
        uuid source_record_id FK
        text[] source_columns
        text[] target_fields
        text rule_reference
        text contribution_state
        uuid child_id FK
        uuid private_profile_child_id FK
        uuid caregiver_id FK
    }
    ACCESS_MEMBERSHIPS {
        uuid user_id PK,FK
        text approved_email_domain
        text role_code FK
        boolean active
    }
    AUTH_USERS {
        uuid id PK
    }
    REFERENCE_VALUES o|--o{ CHILDREN : scoped_vocabularies
    CHILDREN ||--o| CHILD_PRIVATE_PROFILES : references
    CHILDREN ||--o{ CHILD_CAREGIVERS : references
    CAREGIVERS ||--o{ CHILD_CAREGIVERS : references
    REFERENCE_VALUES o|--o{ CHILD_CAREGIVERS : scoped_vocabularies
    CHILDREN ||--o{ PROGRAM_CHANGES : references
    REFERENCE_VALUES o|--o{ PROGRAM_CHANGES : scoped_vocabularies
    CHILD_CAREGIVERS ||--o{ QUESTIONNAIRE_RESPONSES : references
    REFERENCE_VALUES ||--o{ QUESTIONNAIRE_RESPONSES : scoped_vocabularies
    REFERENCE_VALUES ||--o{ QUESTIONNAIRE_ITEMS : scoped_vocabularies
    QUESTIONNAIRE_RESPONSES ||--o{ QUESTIONNAIRE_ANSWERS : references
    QUESTIONNAIRE_ITEMS ||--o{ QUESTIONNAIRE_ANSWERS : references
    CHILDREN ||--o{ ATTENDANCE_OBSERVATIONS : references
    REFERENCE_VALUES ||--o{ ATTENDANCE_OBSERVATIONS : scoped_vocabularies
    CHILDREN ||--o{ SUPPORT_OBSERVATIONS : references
    CHILD_CAREGIVERS o|--o{ SUPPORT_OBSERVATIONS : references
    REFERENCE_VALUES o|--o{ SUPPORT_OBSERVATIONS : scoped_vocabularies
    CHILDREN ||--o{ ADL_VISITS : references
    REFERENCE_VALUES o|--o{ ADL_VISITS : scoped_vocabularies
    SOURCE_ARTIFACTS ||--o{ SOURCE_RECORDS : references
    SOURCE_RECORDS ||--o{ SOURCE_PROVENANCE : typed_origin
    CHILDREN o|--o{ SOURCE_PROVENANCE : typed_origin
    CHILD_PRIVATE_PROFILES o|--o{ SOURCE_PROVENANCE : typed_origin
    CAREGIVERS o|--o{ SOURCE_PROVENANCE : typed_origin
    CHILD_CAREGIVERS o|--o{ SOURCE_PROVENANCE : typed_origin
    PROGRAM_CHANGES o|--o{ SOURCE_PROVENANCE : typed_origin
    QUESTIONNAIRE_RESPONSES o|--o{ SOURCE_PROVENANCE : typed_origin
    QUESTIONNAIRE_ITEMS o|--o{ SOURCE_PROVENANCE : typed_origin
    QUESTIONNAIRE_ANSWERS o|--o{ SOURCE_PROVENANCE : typed_origin
    ATTENDANCE_OBSERVATIONS o|--o{ SOURCE_PROVENANCE : typed_origin
    SUPPORT_OBSERVATIONS o|--o{ SOURCE_PROVENANCE : typed_origin
    ADL_VISITS o|--o{ SOURCE_PROVENANCE : typed_origin
    ACTIVITY_LOGS o|..o{ SOURCE_PROVENANCE : conditional_typed_origin
    REFERENCE_VALUES o|--o{ SOURCE_PROVENANCE : scoped_vocabularies
    AUTH_USERS ||--o| ACCESS_MEMBERSHIPS : references
    REFERENCE_VALUES ||--o{ ACCESS_MEMBERSHIPS : scoped_vocabularies
```

Curated attendance requires resolved identity/date; unresolved source strings are retained in SOURCE_RECORDS rather than falsely becoming valid FKs. Questionnaire pair and answer-definition relationships are proposed constraints based on observed evidence, still subject to analyst approval. Child-to-caregiver and repeated-response cardinalities describe the proposed capacity, not proof of existing person scope or longitudinal behavior.

For the 16-table variant omit ACTIVITY_LOGS and its SOURCE_PROVENANCE activity pointer/FK/index/target group as one activation unit. See [full optimized model](11-optimized-data-model.md), [comparison](12-data-model-comparison-matrix.md) and [original 12-entity diagram](archive/stage1-er-diagram.md). Diagram syntax/reference checks do not validate business rules or prove rendered layout quality.
