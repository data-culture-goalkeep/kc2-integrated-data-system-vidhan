-- Owner/project-dashboard inspection only. READ ONLY; no names, source identifiers, payloads or answer values.
-- This uses the dashboard's existing authorised operator connection; never expose it as a public RPC.
BEGIN READ ONLY;
SELECT 'children' AS preview,count(*) AS rows,count(DISTINCT child_business_id) AS unique_business_ids,
 count(*) FILTER(WHERE review_state='pending') AS pending FROM public.children;
SELECT 'caregivers' AS preview,count(*) AS rows,count(DISTINCT caregiver_business_id) AS unique_business_ids,
 count(*) FILTER(WHERE review_state='pending') AS pending FROM gk_private.caregivers;
SELECT 'child_caregivers' AS preview,count(*) AS links,count(DISTINCT child_id) AS linked_children,
 count(DISTINCT caregiver_id) AS linked_caregivers FROM public.child_caregivers;
SELECT 'questionnaire_responses' AS preview,count(*) AS responses,count(DISTINCT definition_key) AS instrument_versions,
 count(*) FILTER(WHERE assessment_date IS NOT NULL) AS dated_responses FROM public.questionnaire_responses;
SELECT 'questionnaire_answers' AS preview,answer_state,count(*) AS slots
 FROM gk_private.questionnaire_answers GROUP BY answer_state ORDER BY answer_state;
SELECT 'source_records' AS preview,processing_state,diagnostics->>'planned_status' AS planned_disposition,count(*) AS rows
 FROM gk_private.source_records GROUP BY processing_state,diagnostics->>'planned_status' ORDER BY processing_state,planned_disposition;
SELECT 'identity_candidates' AS preview,resolution_status,match_method,count(*) AS candidates
 FROM gk_private.identity_candidates GROUP BY resolution_status,match_method ORDER BY resolution_status,match_method;
SELECT 'data_quality' AS preview,diagnostics->>'planned_status' AS unresolved_kind,count(*) AS source_rows
 FROM gk_private.source_records WHERE processing_state='blocked' GROUP BY diagnostics->>'planned_status';
ROLLBACK;
