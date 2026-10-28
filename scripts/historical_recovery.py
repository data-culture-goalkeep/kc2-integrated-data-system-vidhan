"""Offline original-evidence recovery. Raw values/dates stay in ignored work/.

Does not connect to a database, rewrite a frozen snapshot, or authorize a write.
Source date fidelity and operational eligibility are deliberately separate gates.
"""
import calendar
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
import hashlib
import json
import re
import warnings

import openpyxl
from openpyxl.utils import column_index_from_string

from etl_core import ROOT, canonical, required, stable_id
from profile_sources import label, norm, present, formula
from recovery import atomic_save, source_integrity

W = ROOT / 'work/historical-recovery'
E = ROOT / 'docs/evidence'
VERSION = 'historical-original-evidence-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def calendar_date(value, year=None, month=None):
    """No locale guessing, Excel serial guessing, rollover or arbitrary year."""
    if isinstance(value, datetime):
        return value.date(), 'ORIGINAL_TYPED_DATE'
    if isinstance(value, date):
        return value, 'ORIGINAL_TYPED_DATE'
    if isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value.strip()):
        try:
            return date.fromisoformat(value.strip()), 'ORIGINAL_ISO_DATE'
        except ValueError:
            return None, 'INVALID_DATE'
    if isinstance(value, str):
        text = value.strip()
        named = re.fullmatch(r'(\d{1,2})\s*[- /]\s*([A-Za-z]+)\s*[- /]\s*(\d{4})', text)
        if named:
            names = {name.lower(): i for i in range(1, 13) for name in (calendar.month_name[i], calendar.month_abbr[i])}
            if named[2].lower() in names:
                try:
                    return date(int(named[3]), names[named[2].lower()], int(named[1])), 'ORIGINAL_NAMED_MONTH_DATE'
                except ValueError:
                    return None, 'INVALID_DATE'
        numeric = re.fullmatch(r'(\d{1,2})\s*[-/]\s*(\d{1,2})\s*[-/]\s*(\d{4})', text)
        if numeric:
            a, b, y = map(int, numeric.groups())
            possible = set()
            for m, d in [(a, b), (b, a)]:
                try:
                    possible.add(date(y, m, d))
                except ValueError:
                    pass
            if len(possible) == 1:
                return possible.pop(), 'UNAMBIGUOUS_NUMERIC_DATE'
            return None, 'AMBIGUOUS_DATE_ORDER' if possible else 'INVALID_DATE'
    if type(value) in (int, float) and value == int(value) and 1 <= value <= 31 and year and month:
        try:
            return date(year, month, int(value)), 'EXPLICIT_MONTH_YEAR_DAY'
        except ValueError:
            return None, 'INVALID_DATE'
    return None, 'MISSING_DATE' if not present(value) else 'UNVERIFIED_DATE'


def verified_identity(child_value, caregiver_value, children, caregivers):
    """Exact typed IDs only; disagreeing authorities fail closed."""
    child = children.get((type(child_value).__name__, str(child_value))) if present(child_value) else None
    linked = caregivers.get((type(caregiver_value).__name__, str(caregiver_value))) if present(caregiver_value) else None
    if child and linked and child != linked:
        return None, 'CONFLICTING_IDENTIFIERS'
    # A supplied unknown ID may not be silently superseded by another identifier.
    if present(child_value) and not child:
        return None, 'UNKNOWN_CHILD_IDENTIFIER'
    if present(caregiver_value) and not linked:
        return None, 'UNKNOWN_CAREGIVER_IDENTIFIER'
    return (child or linked), ('EXACT_CHILD_ID' if child else 'EXACT_CAREGIVER_CHILD_LINK' if linked else 'NO_AUTHORITATIVE_ID')


def resolve_cell(ws, coordinate, seen=None):
    """Bounded, non-executing formula subset: same-sheet reference +/- integer days.

    Cached formula values alone are not trusted; external/volatile/array formulae
    remain pending. Never eval Excel text or infer a spill from an export cache.
    """
    seen = set() if seen is None else set(seen)
    if coordinate in seen or len(seen) > 64:
        return None, 'FORMULA_CYCLE_OR_DEPTH', [coordinate]
    seen.add(coordinate)
    cell = ws[coordinate]
    if not formula(cell):
        d, method = calendar_date(cell.value)
        return d, method, [coordinate]
    if type(cell.value).__name__ == 'ArrayFormula':
        # Exact observed source expression, not a general Excel interpreter.
        expression = re.sub(r'\s+', '', cell.value.text).upper()
        known = '=LET(DT,DATE(B1,MONTH(B2&1),1),IF(LEN(B1),SEQUENCE(1,EOMONTH(DT,0)-DT+1,DT),))'
        if expression == known:
            year, month = ws['B1'].value, ws['B2'].value
            months = {name.lower(): i for i in range(1, 13) for name in (calendar.month_name[i], calendar.month_abbr[i])}
            month = months.get(str(month).strip().lower())
            if type(year) in (int, float) and year == int(year) and 1900 <= year <= 2099 and month:
                return date(int(year), month, 1), 'VERIFIED_SOURCE_LET_CALENDAR', [coordinate, 'B1', 'B2']
    if isinstance(cell.value, str):
        match = re.fullmatch(r'=\s*(\$?[A-Z]{1,3}\$?\d+)\s*(?:([+-])\s*(\d+))?\s*', cell.value)
        if match:
            parent = match[1].replace('$', '')
            d, method, refs = resolve_cell(ws, parent, seen)
            if d:
                delta = int(match[3] or 0) * (-1 if match[2] == '-' else 1)
                try:
                    return d + timedelta(days=delta), 'VERIFIED_REFERENCE_DAY_FORMULA', [coordinate] + refs
                except OverflowError:
                    return None, 'INVALID_DATE', [coordinate] + refs
    return None, 'UNSUPPORTED_FORMULA', [coordinate]


def explicit_month_year(ws, header_row):
    """Day-only recovery needs one explicit month/year pair in title/top labels.

    Only a written month-name/year pair is accepted. No inference from file
    modification date, school year, nearby month, or sanitized cells.
    """
    months = {name.lower(): i for i in range(1, 13) for name in (calendar.month_name[i], calendar.month_abbr[i])}
    pattern = r'\b(' + '|'.join(sorted(months, key=len, reverse=True)) + r')[\s_\-/]+((?:19|20)\d{2})\b'
    values = [ws.title] + [str(c.value) for row in ws.iter_rows(max_row=max(1, header_row - 1)) for c in row if isinstance(c.value, str) and not formula(c)]
    pairs = {(int(y), months[m.lower()]) for text in values for m, y in re.findall(pattern, text, re.I)}
    return next(iter(pairs)) if len(pairs) == 1 else (None, None)


def calendar_grid(ws, header_row):
    """Validate the observed daily grid from independent original date anchors.

    Column position is usable only when explicit year/month and at least two
    original full-date anchors prove the same day-offset relationship. Any
    disagreeing full-date anchor rejects the reconstruction for that sheet.
    """
    year, month = ws['B1'].value, ws['B2'].value
    months={name.lower():i for i in range(1,13) for name in (calendar.month_name[i],calendar.month_abbr[i])}
    month=months.get(str(month).strip().lower())
    if not (type(year) in (int,float) and year==int(year) and 1900<=year<=2099 and month):
        return {}
    year=int(year);anchors=[]
    for col in range(7,38):
        coord=ws.cell(header_row,col).coordinate
        d,method,_=resolve_cell(ws,coord)
        if d:
            if (d.year,d.month,d.day)!=(year,month,col-6):return {}
            anchors.append(coord)
    if len(anchors)<2:return {}
    result={}
    for col in range(7,7+calendar.monthrange(year,month)[1]):
        coord=ws.cell(header_row,col).coordinate
        # Unknown Excel expressions are never silently reinterpreted.
        if formula(ws[coord]):continue
        result[coord]=(date(year,month,col-6),'VERIFIED_REPEATED_CALENDAR_GRID',['B1','B2']+anchors)
    return result


def main():
    integrity = source_integrity()
    warnings.filterwarnings('ignore', category=UserWarning)
    profile = json.loads((E / 'data-profile.json').read_text())
    manifest = json.loads((ROOT / 'work/source-intake/private-manifest.json').read_text())
    books = {f['alias']: openpyxl.load_workbook(f['original_path'], data_only=False) for f in manifest}
    plan = json.loads((ROOT / 'work/etl/plan.json').read_text())
    items = [x for unit in plan['units'] for x in unit]
    artifacts = {x['values']['id']: x['values']['file_code'] for x in items if x['table'] == 'source_artifacts'}
    source_rows = {(artifacts[x['values']['artifact_id']], x['values']['native_sheet_key'], x['values']['source_row']): x['values'] for x in items if x['table'] == 'source_records'}
    master = next(s for s in profile['sheets'] if s['kind'] == 'child_master')
    child_by_source = {x['source_refs'][0]: x['values']['id'] for x in items if x['table'] == 'children'}
    children = {}
    for rn in master['record_row_refs']:
        raw = books['S03'].worksheets[0].cell(rn, 2).value
        ref = f'S03/T01/R{rn}'
        children[(type(raw).__name__, str(raw))] = child_by_source[ref]
    required(len(children) == 371, 'Authoritative child registry changed')
    caregivers = {}
    link_sheet = next(s for s in profile['sheets'] if s['kind'] == 'caregiver_link')
    ws = books[link_sheet['source']].worksheets[int(link_sheet['sheet'][1:])-1]
    for rn in link_sheet['record_row_refs']:
        gid, cid = ws.cell(rn, 2).value, ws.cell(rn, 3).value
        child, reason = verified_identity(cid, None, children, {})
        required(child is not None, 'Authoritative caregiver relationship changed')
        key = (type(gid).__name__, str(gid))
        required(key not in caregivers, 'Conflicting caregiver identifier')
        caregivers[key] = child
    required(len(caregivers) == 716, 'Caregiver scope changed')
    # Inspect identities hidden by formula sanitization. A cached VLOOKUP ID
    # whose only input is a person's name remains a suggestion, not proof.
    cached_support=openpyxl.load_workbook(next(f['original_path'] for f in manifest if f['alias']=='S05'),data_only=True)
    identity_formulas=[];formula_counts=Counter();formula_id_suggestions=[]
    caregiver_names=defaultdict(list)
    for rn in link_sheet['record_row_refs']:
        name=books['S05'].worksheets[6].cell(rn,1).value
        gid=books['S05'].worksheets[6].cell(rn,2).value
        caregiver_names[name].append(gid)
    for s in profile['sheets']:
        if s['kind'] not in {'daily_attendance','adl_visit_slots','support_attendance','historical_visits','visit_activity_log'}:continue
        ws=books[s['source']].worksheets[int(s['sheet'][1:])-1]
        for field in s['fields']:
            if label(field['label']) not in {'childname','childnames','traineename','fullnameofthechild','nameofchild','nameofthechild','childid','admissionno','admissionnumber','caregiverid'}:continue
            for rn in range((s['header_row'] or 1)+1,ws.max_row+1):
                cell=ws[f"{field['column']}{rn}"]
                if not formula(cell):continue
                formula_counts[s['kind']]+=1
                identity_formulas.append({'source':s['source'],'sheet':s['sheet'],'cell':cell.coordinate,'formula':str(cell.value)})
                if (s['source'],s['sheet'],field['column'])==('S05','T06','B'):
                    cached=cached_support.worksheets[5][cell.coordinate].value
                    candidate=caregivers.get((type(cached).__name__,str(cached)))
                    gids=caregiver_names.get(ws[f'C{rn}'].value,[])
                    formula_id_suggestions.append({'source':'S05','sheet':'T06','row':rn,'column':'B','formula':cell.value,
                        'cached_identifier':cached,'cached_registry_child_candidate':candidate,
                        'exact_lookup_name_candidates':[caregivers[(type(g).__name__,str(g))] for g in gids],
                        'lookup_name_unique':len(gids)==1,'verified':False,
                        'required_decision':'NGO confirm caregiver-to-child linkage independently of name-only VLOOKUP'})
    cached_support.close()
    atomic_save(W/'identity-formulas.json',identity_formulas)
    atomic_save(W/'formula-id-suggestions.json',formula_id_suggestions)
    staging = json.loads((ROOT / 'work/attendance/records.json').read_text())
    sheets = {(s['source'], s['sheet']): s for s in profile['sheets']}
    ledger = []
    identity_cache = {}
    grids={}
    candidates_by_source=defaultdict(set)
    for item in items:
        if item['table']=='identity_candidates' and item['values'].get('child_id'):
            candidates_by_source[item['values']['source_record_id']].add(item['values']['child_id'])

    def identity(s, rn):
        key = (s['source'], s['sheet'], rn)
        if key in identity_cache:
            return identity_cache[key]
        fields = {label(f['label']): f['column'] for f in s['fields']}
        ws = books[s['source']].worksheets[int(s['sheet'][1:])-1]
        ccol = next((fields[k] for k in ('childid', 'admissionnumber', 'admissionno') if k in fields), None)
        gcol = fields.get('caregiverid')
        cv = ws[f'{ccol}{rn}'].value if ccol else None
        gv = ws[f'{gcol}{rn}'].value if gcol else None
        verified, method = verified_identity(cv, gv, children, caregivers)
        identity_cache[key] = (verified, method, [f'{c}{rn}' for c in (ccol, gcol) if c])
        return identity_cache[key]

    def event(s, rn, col, kind, date_coord=None, staged=None):
        ws = books[s['source']].worksheets[int(s['sheet'][1:])-1]
        sr = source_rows[(s['source'], str(s['google_sheet_id']), rn)]
        child, identity_method, idrefs = identity(s, rn)
        d, method, deps = resolve_cell(ws, date_coord) if date_coord else (None, 'MISSING_DATE', [])
        if not d and date_coord and not formula(ws[date_coord]):
            year, month = explicit_month_year(ws, s['header_row'] or 1)
            d, method = calendar_date(ws[date_coord].value, year, month)
        if not d and date_coord and s['kind']=='daily_attendance':
            gridkey=(s['source'],s['sheet'])
            if gridkey not in grids:grids[gridkey]=calendar_grid(ws,s['header_row'])
            if date_coord in grids[gridkey]:d,method,deps=grids[gridkey][date_coord]
        weekday_conflicts = []
        context_conflict=False
        if d and s['kind']=='daily_attendance':
            cy,cm=ws['B1'].value,ws['B2'].value
            month_names={name.lower():i for i in range(1,13) for name in (calendar.month_name[i],calendar.month_abbr[i])}
            cm=month_names.get(str(cm).strip().lower())
            if type(cy) in (int,float) and cy==int(cy) and 1900<=cy<=2099 and cm:
                context_conflict=(d.year,d.month)!=(int(cy),cm)
        if d and date_coord:
            dc = ws[date_coord]
            for rr in (dc.row-1, dc.row+1):
                if rr < 1 or rr in s['record_row_refs']:
                    continue
                value = ws.cell(rr, dc.column).value
                if isinstance(value, str) and value.strip().lower() in {x.lower() for x in list(calendar.day_name)+list(calendar.day_abbr)}:
                    if not d.strftime('%A').lower().startswith(value.strip().lower()):
                        weekday_conflicts.append({'cell': ws.cell(rr, dc.column).coordinate, 'original_label': value})
        row = {'id': stable_id(VERSION, sr['id'], col, kind), 'source_record_id': sr['id'],
               'source_file': s['source'], 'source_sheet': s['sheet'], 'source_row': rn, 'source_column': col,
               'native_sheet_key':sr['native_sheet_key'],'artifact_id':sr['artifact_id'],
               'original_sheet_name':ws.title,
               'candidate_child_ids':sorted(candidates_by_source[sr['id']]),
               'dataset': kind, 'original_value': str(ws[f'{col}{rn}'].value) if formula(ws[f'{col}{rn}']) else ws[f'{col}{rn}'].value,
               'verified_child_id': child, 'identity_method': identity_method, 'identifier_cells': idrefs,
               'recovered_date': d.isoformat() if d else None, 'date_method': method,
               'date_source_cell': date_coord, 'date_dependencies': deps, 'derived_weekday': d.strftime('%A') if d else None,
               'original_weekday_disagreements': weekday_conflicts,
               'source_calendar_context_disagreement':context_conflict,
               'date_verification': 'SOURCE_CONFLICT' if weekday_conflicts or context_conflict else 'ORIGINAL_EVIDENCE' if d else 'UNRESOLVED',
               'meaning_verified': False, 'eligible_operational': False, 'review_status': 'pending',
               'source_sha256': next(f['sha256'] for f in manifest if f['alias'] == s['source']),
               'required_decisions': ([identity_method] if not child else []) + (['CALENDAR_CONFLICT'] if weekday_conflicts or context_conflict else [] if d else ['AUTHORITATIVE_EVENT_DATE']) + ['APPROVE_EVENT_GRAIN_AND_VOCABULARY']}
        if staged:
            row.update(staging_id=staged['id'], candidate_child_ids=staged['candidate_child_ids'],
                       original_identity_status=staged['identity_status'], observation_kind=staged['observation_kind'])
        # Original dates are sensitive source values; retain locally, never in aggregate reports.
        ledger.append(row)

    for staged in staging:
        if staged['observation_kind'] == 'SOURCE_CONTEXT':
            continue
        s = sheets[(staged['source_file'], staged['source_sheet'])]
        event(s, staged['source_row'], staged['source_column'], s['kind'],
              f"{staged['source_column']}{s['header_row']}" if s['header_row'] else None, staged)
    for s in profile['sheets']:
        ws = books[s['source']].worksheets[int(s['sheet'][1:])-1]
        fields = {f['column']: f['label'] for f in s['fields']}
        if s['kind'] == 'adl_visit_slots':
            for rn in s['record_row_refs']:
                for col, title in fields.items():
                    if re.fullmatch(r'Visit [1-5]', title) and ws[f'{col}{rn}'].value is True:
                        datecol = openpyxl.utils.get_column_letter(column_index_from_string(col)+1)
                        event(s, rn, col, 'adl_visit_slots', f'{datecol}{rn}')
        elif s['kind'] in {'historical_visits', 'visit_activity_log', 'support_event_summary'}:
            datecol = next((c for c, name in fields.items() if label(name) in {'date', 'dateofvisit', 'dateofparkvisit'}), None)
            anchor = next(iter(fields), 'A')
            for rn in s['record_row_refs']:
                event(s, rn, anchor, s['kind'], f'{datecol}{rn}' if datecol else None)
    # Existing verified-ID projections can receive original dates without
    # inventing new events. Prepare only; an incremental manifest needs approval.
    date_updates = []
    provenance = {x['values'].get('program_change_id'):x['values'] for x in items if x['table']=='source_provenance' and x['values'].get('program_change_id')}
    links = {x['values']['id']:x['values']['child_id'] for x in items if x['table']=='child_caregivers'}
    by_source_id = {v['id']:v for v in source_rows.values()}
    for item in items:
        if item['table'] not in {'program_changes','questionnaire_responses'}:
            continue
        values = item['values'];table=item['table']
        if table=='program_changes':
            prov=provenance[values['id']];sr=by_source_id[prov['source_record_id']]
            col=next(c for c in prov['source_columns'] if c in {'AW','AY','BA','BC','BE'})
            datecol=openpyxl.utils.get_column_letter(column_index_from_string(col)+1)
            a,t='S03','T01';child=values['child_id'];field='promotion_date'
        else:
            ref=item['source_refs'][0];a,t,rref=ref.split('/');rn=int(rref[1:])
            s=sheets[(a,t)];sr=source_rows[(a,str(s['google_sheet_id']),rn)]
            datecol='D';child=links[values['child_caregiver_id']];field='assessment_date'
        ws=books[a].worksheets[int(t[1:])-1];coord=f"{datecol}{sr['source_row']}"
        d,method,deps=resolve_cell(ws,coord)
        if d:
            date_updates.append({'table':table,'id':values['id'],'field':field,'before':None,'after':d.isoformat(),
                'child_id':child,'source_record_id':sr['id'],'source_file':a,'source_sheet':t,'source_row':sr['source_row'],
                'source_column':datecol,'date_source_cell':coord,'method':method,'source_dependencies':deps,
                'source_sha256':next(f['sha256'] for f in manifest if f['alias']==a),
                'expected_target_values':values,'review_state_after':'pending'})
    chronology_blocked = set()
    child_rows={child_by_source[f'S03/T01/R{rn}']:rn for rn in master['record_row_refs']}
    for u in date_updates:
        mr=child_rows[u['child_id']];mw=books['S03'].worksheets[0]
        dob,_=calendar_date(mw.cell(mr,10).value);joined,_=calendar_date(mw.cell(mr,9).value)
        event_date=date.fromisoformat(u['after'])
        if (dob and event_date<dob) or (u['table']=='program_changes' and joined and event_date<joined):
            chronology_blocked.add(u['id'])
    programme_groups=defaultdict(list)
    for u in date_updates:
        if u['table']=='program_changes':programme_groups[u['child_id']].append(u)
    for group in programme_groups.values():
        ordered=sorted(group,key=lambda u:u['expected_target_values']['source_slot'])
        if any(a['after']>b['after'] for a,b in zip(ordered,ordered[1:])):
            chronology_blocked.update(u['id'] for u in ordered)
    atomic_save(W/'date-chronology-conflicts.json',[u for u in date_updates if u['id'] in chronology_blocked])
    date_updates=[u for u in date_updates if u['id'] not in chronology_blocked]
    atomic_save(W/'date-recovery-updates.json',date_updates)
    for b in books.values():
        b.close()
    required(source_integrity() == integrity, 'Sources changed during recovery')
    # json-safe originals are written ONLY to private ignored working storage.
    for row in ledger:
        if isinstance(row['original_value'], (date, datetime)):
            row['original_value'] = row['original_value'].isoformat()
    atomic_save(W / 'evidence-ledger.json', ledger)
    summary = {}
    for kind in sorted({r['dataset'] for r in ledger}):
        records = [r for r in ledger if r['dataset'] == kind]
        summary[kind] = {'evidence_candidates': len(records), 'verified_id_candidates': sum(bool(r['verified_child_id']) for r in records),
            'original_dates_recovered': sum(bool(r['recovered_date']) for r in records),
            'dates_without_detected_weekday_conflicts': sum(r['date_verification']=='ORIGINAL_EVIDENCE' for r in records),
            'weekday_conflict_candidates': sum(bool(r['original_weekday_disagreements']) for r in records),
            'unresolved_dates': sum(not r['recovered_date'] for r in records),
            'identity_methods': dict(Counter(r['identity_method'] for r in records)),
            'date_methods': dict(Counter(r['date_method'] for r in records)), 'eligible_operational': 0}
    result = {'version': VERSION, 'status': 'recovered_original_evidence_not_operational_approval',
        'source_snapshot': integrity, 'original_files':12, 'worksheets':155,
        'datasets':summary, 'private_evidence_rows':len(ledger), 'private_ledger_sha256':sha((W/'evidence-ledger.json').read_bytes()),
        'existing_verified_id_date_update_candidates':dict(Counter(x['table'] for x in date_updates)),
        'date_update_chronology_conflicts_excluded':len(chronology_blocked),
        'date_update_plan_sha256':sha((W/'date-recovery-updates.json').read_bytes()),
        'identity_formula_cells_by_dataset':dict(formula_counts),
        'support_formula_id_review':{'formula_cells':len(formula_id_suggestions),
          'cached_identifiers_in_registry':sum(bool(x['cached_registry_child_candidate']) for x in formula_id_suggestions),
          'unique_exact_lookup_names':sum(x['lookup_name_unique'] for x in formula_id_suggestions),
          'newly_verified_links':0,'reason':'Name-derived VLOOKUP results are not independently verified child identities'},
        'date_values_uploaded':0, 'remote_writes':0, 'staging_replayed':False,
        'eligible_operational':0, 'meaning_rules_approved':False,
        'limitations':['Original literal dates are source evidence, not independent confirmation the event occurred.',
            'No inferred identities from names, serial roster numbers, or row alignment.',
            'Unsupported formula and ambiguous text calendars remain unresolved.',
            'Source-context, formulas, summaries and participation marks are not automatically child attendance events.']}
    (E/'historical-original-recovery.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
