# Stage 1 — Entity relationship diagram

Draft for analyst approval. Solid edges show source ID equality or a proposed unpivot of observed repeated columns; dotted edges are unresolved name-based links. Cardinalities are recommendations, not database constraints. Types are conceptual. Source-record/cell references are derived technical lineage, not invented NGO fields.

```mermaid
erDiagram
    CHILD {
        string admission_number
        string child_name
        string current_program
        string child_status
        date joining_date
        date child_dob
    }
    CAREGIVER {
        string caregiver_id
        string caregiver_name
    }
    CHILD_CAREGIVER {
        string child_id
        string caregiver_id
    }
    PROGRAM {
        string observed_program_value
    }
    PROGRAM_CHANGE {
        string promoted_program
        date promotion_date
        string source_cell_reference
    }
    QUESTIONNAIRE_RESPONSE {
        string source_record_reference
        string child_id
        string caregiver_id
        string program
        string centre
        date assessment_date
    }
    QUESTIONNAIRE_ITEM {
        string source_question_column
        string source_question_label
    }
    QUESTIONNAIRE_ANSWER {
        string source_cell_reference
        string recorded_value
    }
    ATTENDANCE_OBSERVATION {
        string child_name
        string program_or_batch
        string child_status
        date source_date_header
        string recorded_mark
        string source_cell_reference
    }
    SUPPORT_ATTENDANCE {
        string child_name
        string caregiver_name
        string program
        string source_event_label
        string recorded_value
    }
    ADL_VISIT {
        string child_name
        string program
        boolean visit_flag
        date visit_date
        string source_cell_reference
    }
    ACTIVITY_LOG {
        string source_record_reference
        string source_activity_description
        date source_activity_date
        string source_status
    }
    CHILD ||--o{ CHILD_CAREGIVER : observed_child_ID
    CAREGIVER ||--o{ CHILD_CAREGIVER : observed_caregiver_ID
    CHILD ||--o{ QUESTIONNAIRE_RESPONSE : observed_child_ID
    CAREGIVER ||--o{ QUESTIONNAIRE_RESPONSE : observed_caregiver_ID
    QUESTIONNAIRE_RESPONSE ||--o{ QUESTIONNAIRE_ANSWER : proposed_unpivot
    QUESTIONNAIRE_ITEM ||--o{ QUESTIONNAIRE_ANSWER : source_column
    CHILD ||--o{ PROGRAM_CHANGE : repeated_promotion_slots
    PROGRAM ||--o{ PROGRAM_CHANGE : proposed_lookup
    PROGRAM ||--o{ CHILD : current_program
    CHILD o|..o{ ATTENDANCE_OBSERVATION : unresolved_name_link
    CHILD o|..o{ ADL_VISIT : unresolved_name_link
    CAREGIVER o|..o{ SUPPORT_ATTENDANCE : unresolved_name_link
```

See [entities and field evidence](03-entity-discovery.md) and [conceptual model](05-conceptual-data-model.md) for source ranges, key scope and relationship limitations. No physical table or foreign key has been created. The graph includes an unlinked activity-log entity because its participant grain is unresolved.
