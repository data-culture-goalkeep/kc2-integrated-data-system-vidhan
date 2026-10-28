#!/usr/bin/env python3
"""Read published PyPI advisories for pinned dependencies; no credentials or package execution."""
import concurrent.futures
import json
from pathlib import Path
import re
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def pins(path):
    result = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith('-r '):
            result.extend(pins(path.parent/line[3:].strip()))
        elif line and not line.startswith('#'):
            match = re.fullmatch(r'([A-Za-z0-9_-]+)==([0-9.]+)', line)
            if not match:
                raise ValueError('Dependency is not pinned to a supported exact version')
            result.append(match.groups())
    return sorted(set(result))

def inspect_package(pin):
    name, version = pin
    record = {'name': name, 'version': version}
    try:
        with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json', timeout=25) as response:
            data = json.load(response)
        record.update(status='checked', advisories=[{'id':v['id'], 'link':v.get('link'),
                      'fixed_in':v.get('fixed_in',[])} for v in data.get('vulnerabilities',[])])
    except (urllib.error.URLError, ValueError, KeyError):
        record.update(status='unavailable', advisories=None)
    return record

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        packages = list(pool.map(inspect_package, pins(ROOT/'requirements-preparation.txt')))
    complete = all(p['status']=='checked' for p in packages)
    advisory_count = sum(len(p.get('advisories') or []) for p in packages)
    report = {'source':'PyPI release JSON vulnerability advisories', 'packages':packages,
              'complete':complete, 'reported_advisories':advisory_count,
              'limitations':['A clean result is not proof that no vulnerability exists; only advisories reported by PyPI were checked',
                             'The pinned Docker image is recorded separately; its OS packages are not covered by this audit']}
    (ROOT/'docs/evidence/dependency-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if complete and advisory_count==0 else 1

if __name__=='__main__':
    raise SystemExit(main())
