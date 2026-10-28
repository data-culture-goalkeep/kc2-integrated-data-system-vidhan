"""Owner-authorized bounded attendance continuation; no SQL generation or network.

Preserves the stopped journal, reuses unchanged packet/receipt controls, enforces
the four-hour window and binds the owner's exact 20-table resumption plan.
"""
import sys
from datetime import datetime, timezone

import attendance_execution as execution
from etl_core import canonical, required
from recovery import atomic_save, source_integrity

PLAN = 'a77979c4844da64c6aed511c7a56ba64938135a586b7f5caec4a4536bce1fa8a'
OLD = execution.W
execution.W = execution.ROOT / 'work/attendance-resumption'
W = execution.W


def check_window(approval, current=None):
    current = current or datetime.now(timezone.utc)
    issued = datetime.fromisoformat(approval['issued_at'].replace('Z', '+00:00'))
    expires = datetime.fromisoformat(approval['expires_at'].replace('Z', '+00:00'))
    required((expires - issued).total_seconds() == 14400, 'Invalid approval window')
    required(issued <= current < expires, 'Approval not valid or expired')
    required(approval['project_reference'] == execution.PROJECT, 'Wrong approval target')
    required(approval['import_manifest_sha256'] == execution.IMPORT, 'Wrong approved import')
    required(approval['resumption_plan_sha256'] == PLAN, 'Wrong approved resumption plan')


def authorize():
    d, m = execution.manifests()
    p = execution.load(execution.E / 'attendance-resumption-plan.json')
    required(execution.sha(canonical(p).encode()) == PLAN, 'Resumption plan changed')
    required(not execution.journal(), 'Existing continuation journal; no automatic restart')
    required(execution.sha((OLD / 'journal.jsonl').read_bytes()) == p['previous_journal_sha256'], 'Prior journal changed')
    required(source_integrity()['source_snapshot_sha256'] == m['source_snapshot_sha256'] == p['source_snapshot_sha256'], 'Source snapshot changed')
    for batch in m['batches']:
        execution.packet(batch['index'], m)
    meta = execution.load(W / 'project.json')
    required(meta['id'] == execution.PROJECT and meta['region'] == 'ap-northeast-1' and meta['name'] == d['project_name'], 'Project mismatch')
    required(execution.load(W / 'pre-ledger.json') == p['deployed_migration_ledger'], 'Ledger mismatch')
    required(execution.sha(canonical(execution.load(W / 'pre-catalog.json')).encode()) == p['baseline_catalog_sha256'], 'Catalog/security mismatch')
    required(execution.load(W / 'pre-snapshot.json') == p['baseline_existing_table_snapshots'], 'Existing data changed')
    control = execution.load(W / 'pre-control.json')
    required(control['staging_rows'] == control['active_imports'] == 0 and control['database_role'] == 'postgres', 'Unsafe starting checkpoint')
    a = execution.load(W / 'approval-evidence.json')
    check_window(a)
    required(a['owner_approval_quote'] == 'I explicitly approve and authorize the execution of all 216 remaining attendance-import transactions into my existing non-production Supabase project.', 'Missing direct owner evidence')
    atomic_save(W / 'authorization.json', {**a, 'active': True, 'parent_journal_sha256': p['previous_journal_sha256']})
    execution.append({'event': 'authorized', 'import_manifest_sha256': execution.IMPORT, 'resumption_plan_sha256': PLAN, 'issued_at': a['issued_at'], 'expires_at': a['expires_at'], 'parent_journal_sha256': p['previous_journal_sha256']})
    execution.append({'event': 'deployment_verified', 'migration_reapplied': False, 'existing_20_table_catalog_sha256': p['baseline_catalog_sha256']})
    print(canonical({'status': 'preflight_passed', 'transactions': 216, 'records': 43160, 'expires_at': a['expires_at']}))


def main():
    W.mkdir(exist_ok=True, mode=0o700)
    if sys.argv[1] == 'authorize':
        authorize()
        return
    required(sys.argv[1] in {'packet', 'dispatch', 'accept'}, 'Unsupported continuation action')
    a = execution.load(W / 'authorization.json')
    if sys.argv[1] != 'accept':
        check_window(a)
        required(a['active'], 'Inactive authorization')
    execution.main()


if __name__ == '__main__':
    main()
