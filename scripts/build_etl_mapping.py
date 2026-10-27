#!/usr/bin/env python3
"""Classify every retained source column and generate a worksheet-level ETL contract."""
import csv
import json
from collections import Counter
from pathlib import Path
from etl_core import ROOT

def main():
    rows=list(csv.DictReader((ROOT/'docs/evidence/final-source-target-coverage.csv').open()))
    profile=json.loads((ROOT/'docs/evidence/data-profile.json').read_text());sheets={(x['source'],x['sheet']):x for x in profile['sheets']}
    result=[]
    for original in rows:
        row=dict(original);source=row['source'];sheet=row['sheet'];col=row['column'];target=row['operational_target'];kind=sheets[(source,sheet)]['kind']
        classification='TECHNICAL';action='preserve_source_only';transform='Retain sanitized cell/header and native source coordinates';gate='No operational interpretation claimed'
        if (source,sheet)==('S03','T01') and target.startswith(('children.','child_private_profiles.')):
            classification='CONFIRMED';action='prepare_pending_literal';transform='Exact-ID child UUID; copy deidentified literal field with explicit type conversion'
            if target.endswith(('_code','_date')):
                classification='PENDING';action='withhold_date' if target.endswith('_date') else 'prepare_inactive_source_lookup';gate='Date fidelity or category meaning approval; never activate/merge values automatically'
            if target.endswith(('assessment_fee','monthly_fee')):
                classification='PENDING';action='preserve_source_only';gate='Sensitive numeric redaction cannot be cast back to a real financial value'
        elif (source,sheet)==('S03','T01') and target.startswith('caregivers.'):
            classification='PENDING';gate='Parent label does not prove a verified caregiver identity';action='preserve_source_only'
        elif (source,sheet)==('S03','T01') and target.startswith('program_changes.'):
            classification='PENDING';action='withhold_date' if target.endswith('_date') else 'prepare_pending_source_slot';gate='Literal source slot only; effective date/category approval needed for historical analytics'
        elif (source,sheet)==('S05','T07'):
            classification='CONFIRMED';action='prepare_verified_registry_or_pair';transform='Exact deidentified IDs; internal UUIDs; no person merge by name';gate='None for observed ID equality; records remain pending import'
        elif (source,sheet)==('S01','T01'):
            if col in ['AZ','BA','A']:
                classification='CONFIRMED';action='verified_pair_or_conflict_evidence';gate='Preserve reported name; never overwrite master'
            elif col in ['D']:
                classification='PENDING';action='withhold_date';gate='Existing synthetic dates do not retain chronology'
            elif col in ['B','C']:
                classification='PENDING';action='prepare_inactive_source_lookup';gate='No source-to-canonical category meanings approved'
            elif target.startswith('questionnaire_answers.') or row['header_projection']:
                classification='CONFIRMED';action='prepare_literal_item_answer';gate='Source numeric/text representation only; scoring, denominator and interpretation remain pending'
                transform='Header-to-item, one explicit answer slot per primary submission; blank stays missing, no zero or score imputation'
            else:
                classification='PENDING';gate='Derived totals/formulas/interpretation not recalculated or asserted'
        elif target or kind in {'daily_attendance','adl_visit_slots','support_attendance','support_event_summary','visit_activity_log','questionnaire_view','questionnaire_subset'}:
            classification='PENDING';gate='Identity, record grain, source authority, dates or value semantics require approval'
        row.update(record_grain=kind,mapping_class=classification,execution_action=action,
            transformation=transform,identifier_rule='Exact verified IDs only; name/context produces candidates',
            validation_requirements='Source hashes, cell/row retention, type/key/FK/lineage checks; pending records not accepted',
            unresolved_business_gate=gate,source_retention='source_records.cell_payload + source_artifacts.worksheet_manifest; private original preserved')
        result.append(row)
    with (ROOT/'docs/evidence/etl-source-target-mapping.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]),lineterminator='\n');w.writeheader();w.writerows(result)
    inventory=[]
    for s in profile['sheets']:
        fields=[r for r in result if (r['source'],r['sheet'])==(s['source'],s['sheet'])]
        inventory.append({'source':s['source'],'sheet':s['sheet'],'native_sheet_id':s['google_sheet_id'],
            'grain':s['kind'],'nonempty_rows':s['nonempty_rows'],'candidate_rows':s['record_rows'],
            'column_positions':len(fields),'classification_counts':dict(Counter(r['mapping_class'] for r in fields)),
            'operational_targets':sorted({r['operational_target'].split('.')[0] for r in fields if r['operational_target']}),
            'retention_targets':['source_artifacts','source_records'],'identifier_rule':'No name-only approved joins'})
    summary={'source_columns':len(result),'worksheets':len(inventory),'classification_counts':dict(Counter(r['mapping_class'] for r in result)),
            'retention_coverage':sum(bool(r['retained_target'] and r['header_retained_target']) for r in result),
            'operational_projection_is_not_full_business_approval':True}
    (ROOT/'docs/evidence/etl-worksheet-contracts.json').write_text(json.dumps(inventory,indent=2)+'\n')
    (ROOT/'docs/evidence/etl-mapping-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
