"""Generate read-only aggregate reconciliation SQL and expected payload digests.

All expected values stay private; only hash buckets and aggregate counts leave
the database. No database connection or mutation is implemented here.
"""
import hashlib
import json
from collections import Counter, defaultdict
from decimal import Decimal

from attendance_execution import E, PACKETS, ROOT, load, manifests
from recovery import atomic_save

W = ROOT / 'work/attendance-resumption'


def jsonb_text(value):
    """PostgreSQL jsonb text key ordering, whitespace and numeric expansion."""
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        numeric = Decimal(str(value))
        return format(abs(numeric) if numeric.is_zero() else numeric, 'f')
    if isinstance(value, list):
        return '[' + ', '.join(jsonb_text(v) for v in value) + ']'
    if isinstance(value, dict):
        keys = sorted(value, key=lambda k: (len(k.encode('utf-8')), k.encode('utf-8')))
        return '{' + ', '.join(jsonb_text(k) + ': ' + jsonb_text(value[k]) for k in keys) + '}'
    raise TypeError('Unsupported value')


def expected(rows):
    buckets = defaultdict(list)
    for row in rows:
        digest = hashlib.md5(jsonb_text(row).encode()).hexdigest()
        buckets[row['id'][:2]].append((row['id'], digest))
    return {b: {'rows': len(values), 'payload_md5': hashlib.md5('\n'.join(k + ':' + v for k, v in sorted(values)).encode()).hexdigest()}
            for b, values in sorted(buckets.items())}


SQL = """BEGIN READ ONLY;
SELECT jsonb_build_object(
 'total', (SELECT count(*) FROM gk_private.attendance_import_staging),
 'sheets', (SELECT count(DISTINCT (source_file, source_sheet)) FROM gk_private.attendance_import_staging),
 'source_rows', (SELECT count(DISTINCT source_record_id) FROM gk_private.attendance_import_staging),
 'daily_rosters', (SELECT count(*) FROM gk_private.attendance_import_staging WHERE observation_kind='SOURCE_CONTEXT' AND provenance->>'sheet_kind'='daily_attendance' AND provenance->>'roster_row'='true'),
 'daily_pa_marks', (SELECT count(*) FROM gk_private.attendance_import_staging WHERE observation_kind='MARK' AND provenance->>'sheet_kind'='daily_attendance' AND original_mark IN ('\"P\"'::jsonb,'\"A\"'::jsonb)),
 'duplicate_coordinates', (SELECT count(*) FROM (SELECT source_record_id,source_column FROM gk_private.attendance_import_staging GROUP BY 1,2 HAVING count(*)>1) d),
 'kinds', (SELECT jsonb_object_agg(k,n) FROM (SELECT observation_kind k,count(*) n FROM gk_private.attendance_import_staging GROUP BY 1) x),
 'identity_all', (SELECT jsonb_object_agg(k,n) FROM (SELECT identity_status k,count(*) n FROM gk_private.attendance_import_staging GROUP BY 1) x),
 'identity_cells', (SELECT jsonb_object_agg(k,n) FROM (SELECT identity_status k,count(*) n FROM gk_private.attendance_import_staging WHERE observation_kind<>'SOURCE_CONTEXT' GROUP BY 1) x),
 'dates_all', (SELECT jsonb_object_agg(k,n) FROM (SELECT date_status k,count(*) n FROM gk_private.attendance_import_staging GROUP BY 1) x),
 'dates_cells', (SELECT jsonb_object_agg(k,n) FROM (SELECT date_status k,count(*) n FROM gk_private.attendance_import_staging WHERE observation_kind<>'SOURCE_CONTEXT' GROUP BY 1) x),
 'codes', (SELECT jsonb_object_agg(k,n) FROM (SELECT code_status k,count(*) n FROM gk_private.attendance_import_staging GROUP BY 1) x),
 'reviews', (SELECT jsonb_object_agg(k,n) FROM (SELECT review_status k,count(*) n FROM gk_private.attendance_import_staging GROUP BY 1) x),
 'parsed_dates', (SELECT count(*) FROM gk_private.attendance_import_staging WHERE parsed_date IS NOT NULL),
 'verified_children', (SELECT count(*) FROM gk_private.attendance_import_staging WHERE verified_child_id IS NOT NULL),
 'invalid_source_links', (SELECT count(*) FROM gk_private.attendance_import_staging t LEFT JOIN gk_private.source_records s ON s.id=t.source_record_id WHERE s.id IS NULL OR s.artifact_id<>t.artifact_id OR s.source_row<>t.source_row OR s.native_sheet_key<>t.native_sheet_key),
 'source_mark_disagreements', (SELECT count(*) FROM gk_private.attendance_import_staging t JOIN gk_private.source_records s ON s.id=t.source_record_id WHERE t.source_column<>'__ROW__' AND t.original_mark IS DISTINCT FROM COALESCE(s.cell_payload->t.source_column,'null'::jsonb)),
 'header_disagreements', (SELECT count(*) FROM gk_private.attendance_import_staging t LEFT JOIN gk_private.source_records h ON h.id=t.header_source_record_id WHERE t.header_source_record_id IS NOT NULL AND (h.id IS NULL OR h.artifact_id<>t.artifact_id OR h.native_sheet_key<>t.native_sheet_key OR t.original_header IS DISTINCT FROM COALESCE(h.cell_payload->t.source_column,'null'::jsonb))),
 'invalid_candidates', (SELECT count(*) FROM gk_private.attendance_import_staging t CROSS JOIN LATERAL unnest(t.candidate_child_ids) x(id) LEFT JOIN public.children c ON c.id=x.id WHERE c.id IS NULL),
 'operational_attendance', (SELECT count(*) FROM public.attendance_observations)
) AS reconciliation;
SELECT jsonb_object_agg(bucket,jsonb_build_object('rows',n,'payload_md5',payload_md5)) AS buckets FROM (
 SELECT left(id::text,2) bucket,count(*) n,md5(string_agg(id::text||':'||md5((to_jsonb(t)-ARRAY['created_at','updated_at'])::text),E'\\n' ORDER BY id)) payload_md5
 FROM gk_private.attendance_import_staging t GROUP BY 1
) b;
COMMIT;
"""


def main():
    manifests()
    records = load(PACKETS / 'records.json')
    atomic_save(W / 'expected-payload-buckets.json', expected(records))
    atomic_save(W / 'expected-distributions.json', {
        'kinds': dict(Counter(r['observation_kind'] for r in records)),
        'identity_all': dict(Counter(r['identity_status'] for r in records)),
        'identity_cells': dict(Counter(r['identity_status'] for r in records if r['observation_kind'] != 'SOURCE_CONTEXT')),
        'dates_all': dict(Counter(r['date_status'] for r in records)),
        'dates_cells': dict(Counter(r['date_status'] for r in records if r['observation_kind'] != 'SOURCE_CONTEXT')),
    })
    (W / 'reconcile.sql').write_text(SQL)
    boundary = SQL.index('SELECT jsonb_object_agg(bucket')
    (W / 'reconcile-counts.sql').write_text(SQL[:boundary] + 'COMMIT;')
    (W / 'reconcile-payloads.sql').write_text('BEGIN READ ONLY;\n' + SQL[boundary:])
    (W / 'reconcile-sheets.sql').write_text("""BEGIN READ ONLY;
SELECT source_file,source_sheet,count(*) AS staged_records,
 count(*) FILTER(WHERE observation_kind='SOURCE_CONTEXT') AS contexts,
 count(*) FILTER(WHERE observation_kind<>'SOURCE_CONTEXT') AS cells,
 count(*) FILTER(WHERE observation_kind='MARK' AND provenance->>'sheet_kind'='daily_attendance') AS daily_marks
FROM gk_private.attendance_import_staging GROUP BY source_file,source_sheet ORDER BY source_file,source_sheet;
COMMIT;""")
    # Read-only codec check includes synthetic edge cases plus representative
    # existing sanitized records. Results contain hashes only, never values.
    cases = [None, {'z': 0, 'aa': False, 'b': [None, '\u0939', 'x\ny', 0.0000001, -0.0]}, records[0], records[-1]]
    from etl_core import sql_text, canonical
    checks = ["SELECT " + str(i) + " AS slot,md5(" + sql_text(canonical(v)) + "::jsonb::text) AS digest" for i, v in enumerate(cases)]
    (W / 'codec-check.sql').write_text('BEGIN READ ONLY; ' + ' UNION ALL '.join(checks) + '; COMMIT;')
    atomic_save(W / 'expected-codec.json', [{'slot': i, 'digest': hashlib.md5(jsonb_text(v).encode()).hexdigest()} for i, v in enumerate(cases)])
    print('Prepared exact-key/full-payload bucket reconciliation and source checks; no database writes')


if __name__ == '__main__':
    main()
