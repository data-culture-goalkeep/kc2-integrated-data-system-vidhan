"""Conservative incremental projection into the existing deployed model.

Pure compiler: no remote transport. Decisions must be explicit, evidence-linked
and separately approved. Absent decisions return no projection, never guesses.
"""
from etl_core import stable_id, required, validate_record, POINTERS


def project(evidence, decision=None):
    if not decision:
        return []
    required(decision.get('approved') is True and bool(decision.get('approval_reference')),
             'Evidence-linked business approval required')
    child = evidence.get('verified_child_id')
    required(child is not None, 'Authoritative identity required')
    required(evidence.get('date_verification') != 'SOURCE_CONFLICT', 'Calendar disagreement unresolved')
    kind = evidence['dataset']
    table = {'daily_attendance':'attendance_observations', 'adl_visit_slots':'adl_visits',
             'support_attendance':'support_observations'}.get(kind)
    required(table is not None, 'Summary/context/activity evidence is not an approved child event')
    required(decision.get('event_kind') == kind, 'Decision scope differs')
    original = evidence['original_value']
    values = {'id':stable_id('historical-operational-v1', evidence['source_record_id'], evidence['source_column'], kind),
              'child_id':child, 'origin_kind':'import', 'review_state':'pending'}
    if kind == 'daily_attendance':
        required(evidence.get('observation_kind') == 'MARK', 'Only literal observations may project')
        required(evidence.get('recovered_date') is not None, 'Attendance requires verified date')
        required(evidence.get('date_verification') == 'ORIGINAL_EVIDENCE', 'Verified original calendar required')
        marks = decision.get('mark_mapping', {})
        required(type(original) is str and original in marks and bool(decision.get('service_code')), 'Unapproved attendance meaning')
        values.update(attendance_date=evidence['recovered_date'], service_code=decision['service_code'], mark_code=marks[original])
    elif kind == 'adl_visit_slots':
        required(original is True and decision.get('true_means_completed_visit') is True, 'ADL event semantics required')
        values.update(visit_flag=True, visit_date=evidence.get('recovered_date'))
    else:
        meanings = decision.get('value_mapping', {})
        required(type(original) is str and original in meanings and bool(decision.get('event_reference')), 'Approved support event/value required')
        values.update(event_reference=decision['event_reference'], event_date=evidence.get('recovered_date'), text_value=meanings[original])
    ref = f"{evidence['source_file']}/{evidence['source_sheet']}/R{evidence['source_row']}"
    record = {'table':table, 'values':values, 'source_refs':[ref]}
    provenance = {'table':'source_provenance', 'values':{
        'id':stable_id('historical-provenance-v1', values['id']), 'source_record_id':evidence['source_record_id'],
        POINTERS[table]:values['id'], 'source_columns':[evidence['source_column']], 'target_fields':list(values),
        'rule_reference':decision['approval_reference'], 'contribution_state':'selected'}, 'source_refs':[ref]}
    validate_record(record)
    validate_record(provenance)
    return [record, provenance]
