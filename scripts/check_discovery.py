#!/usr/bin/env python3
"""Verify Stage 1 evidence against current source bytes; never emit source values."""
import json
import re
import subprocess
from pathlib import Path
from inspect_sources import inspect

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)

def main():
    evidence = json.loads((ROOT / 'docs/evidence/source-inspection.json').read_text())
    guideline_entries = [f for f in evidence['files'] if f['role'] == 'guidelines']
    require(len(guideline_entries) == 1, 'Exactly one guideline input must be identified')
    current = inspect([Path(s['root']) for s in evidence['scan_roots']],
                      Path(guideline_entries[0]['path']), ROOT / evidence['repository_context']['path'])
    # The README path is intentionally portable in the stored evidence.
    current['repository_context']['path'] = evidence['repository_context']['path']
    require(current == evidence, 'Inputs or structural counts changed; regenerate inventory and review reports')
    require(all(s['status'] == 'scanned' for s in evidence['scan_roots']), 'All recorded roots must be scanned')
    require(evidence['summary']['tabular_candidates'] == 0,
            'New tabular sources require privacy review and actual record profiling')
    require(evidence['summary']['business_record_count'] is None, 'Missing records must stay unknown')
    required = ['01-source-inventory.md', '02-data-profiling.md', '03-entity-discovery.md',
                '04-assumptions-and-questions.md', 'project-context.md']
    for name in required:
        p = ROOT / 'docs' / name
        require(p.is_file() and p.stat().st_size > 100, 'Missing or empty required report: ' + name)
    for p in (ROOT / 'docs').glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if '://' not in target and not target.startswith('#'):
                require((p.parent / target.split('#')[0]).is_file(), 'Broken report link: ' + target)
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    require(branch == 'feature/phase1-data-backend', 'Wrong work branch')
    require(not (ROOT / 'supabase/migrations').exists(), 'Unexpected Stage 2 migration output')
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True, capture_output=True)
    # Compile syntax without creating cache files; no third-party dependencies needed.
    for p in (ROOT / 'scripts').glob('*.py'):
        compile(p.read_text(), str(p), 'exec')
    report = {'status': 'passed', 'scope': 'Stage 1 metadata and deliverable integrity only',
              'checks': ['Original source and README hashes unchanged', 'Inventory recomputation matches stored evidence',
                         'All source roots scanned', 'Absent NGO records represented as unknown',
                         'Five required reports present', 'Relative report links resolve',
                         'Required feature branch active', 'No SQL migration directory created',
                         'Git whitespace check passed', 'Python scripts compile'],
              'not_validated': ['NGO record quality, identities or relationships', 'Sanitization of NGO data',
                                'Supabase connectivity, region, schema or migration', 'Remote GitHub access',
                                'Application build, lint or TypeScript checks (no application)',
                                'Google Docs or Sheets access', 'Project-owner acceptance']}
    out = ROOT / 'docs/evidence/verification.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
