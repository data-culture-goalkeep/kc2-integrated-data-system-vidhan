"""Test the proposed amendment on the exact local schema, never a remote URL."""
import gzip
import json
import time
from copy import deepcopy
from attendance_guard_optimization import prepare, W, indexed_query
from attendance_execution import E, PACKETS, ROOT, load, required, sha, canonical
from build_recovery_reference import start_db, snapshot
from etl_loader import load_plan


def main():
    entries = prepare()
    db = start_db('attendance-indexed')
    report = {'scope': 'network=none disposable PostgreSQL; approved sanitized fixtures only; no remote writes', 'tests': {}}
    tests = report['tests']
    try:
        plan = load(ROOT / 'work/etl/plan.json')
        required(load_plan(db, plan)['status'] == 'passed', 'Local baseline failed')
        before = snapshot(db)
        original = load(E / 'attendance-import-manifest.json')
        # Fixture setup uses the exact original INSERT and guards/triggers, but
        # omits only the slow read-back statement. It is never remote SQL.
        for b in original['batches'][:173]:
            q = json.loads(gzip.decompress((PACKETS / b['packet_file']).read_bytes()))['query']
            required(db.sql(q.split('DO $batch$')[0] + 'COMMIT;').returncode == 0, 'Local prefix seed failed')
        count = lambda: int(db.execute('SELECT count(*) FROM gk_private.attendance_import_staging'))
        required(count() == 34600, 'Prefix count differs')
        cutoff = db.execute('SELECT max(created_at)::text FROM gk_private.attendance_import_staging')
        prefix_sql = "SELECT md5(string_agg(md5(to_jsonb(t)::text),'' ORDER BY id)) FROM gk_private.attendance_import_staging t WHERE created_at <= '" + cutoff + "'::timestamptz"
        prefix = db.execute(prefix_sql)
        tests['exact_schema_and_nonempty_34600_row_fixture'] = True
        durations = []
        for b in entries:
            q = json.loads(gzip.decompress((W / b['packet_file']).read_bytes()))['query']
            started = time.monotonic()
            required(db.sql(q).returncode == 0, 'Indexed local import failed')
            durations.append(time.monotonic() - started)
        required(count() == 43160, 'Final count differs')
        tests['all_43_amended_batches_loaded_with_original_60_second_limit'] = True
        for b in [entries[0], entries[-1]]:
            q = json.loads(gzip.decompress((W / b['packet_file']).read_bytes()))['query']
            required(db.sql(q).returncode == 0, 'Replay failed')
        required(count() == 43160, 'Replay duplicated records')
        tests['representative_idempotent_replay'] = True
        first = json.loads(gzip.decompress((W / entries[0]['packet_file']).read_bytes()))['query']
        conflict = first.replace('"review_notes":""', '"review_notes":"CONFLICT"')
        required(conflict != first and db.sql(conflict).returncode != 0, 'Payload conflict accepted')
        tests['conflicting_payload_rejected'] = True
        required(count() == 43160 and db.execute(prefix_sql) == prefix and snapshot(db) == before, 'Existing records/audit changed')
        tests['committed_prefix_timestamps_original_data_and_audit_unchanged'] = True
        for role in ['anon', 'authenticated', 'service_role']:
            required(db.sql('BEGIN; SET LOCAL ROLE ' + role + '; SELECT count(*) FROM gk_private.attendance_import_staging; ROLLBACK;').returncode != 0, 'Role access allowed')
        tests['three_unapproved_roles_still_denied'] = True
        # Compare complete resulting business payloads to the approved rows.
        expected = load(PACKETS / 'records.json')
        from attendance_reconcile import expected as buckets
        q = (ROOT / 'work/attendance-resumption/reconcile-payloads.sql').read_text()
        required(json.loads(db.execute(q)) == buckets(expected), 'Full payload/key reconciliation differs')
        tests['all_43160_keys_and_full_payloads_match_original_approved_records'] = True
        required(db.execute("SELECT count(*) FROM gk_private.attendance_import_staging WHERE parsed_date IS NOT NULL OR verified_child_id IS NOT NULL OR review_status<>'pending' OR code_status<>'PENDING'") == '0', 'Unapproved promotion')
        tests['no_identity_date_code_promotion'] = True
        report.update(status='passed', proposed_transactions=43, final_staging_rows=count(),
                      slowest_amended_batch_seconds=max(durations), total_amended_seconds=sum(durations),
                      unchanged_statement_timeout_seconds=60, expected_new_remote_rows=8560)
    except Exception as exc:
        report.update(status='failed', reason=type(exc).__name__ + ': ' + str(exc)[:160])
    finally:
        report['container_removed'] = db.docker('rm', '-f', db.name).returncode == 0
        (E / 'attendance-indexed-guard-local-tests.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return 0 if report.get('status') == 'passed' and report['container_removed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
