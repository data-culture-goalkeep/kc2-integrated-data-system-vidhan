#!/usr/bin/env python3
"""Run migrations on a network-isolated disposable local PostgreSQL with synthetic Auth fixtures.
No database URL, remote credentials, Supabase CLI link or remote execution path is accepted.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'postgres@sha256:858bb5e98eed02eb8cafbcdc007f9a65d1b613972028944a8ec2133ccaf80d27'
DOCKER = ['docker', '--host=unix:///var/run/docker.sock']

class LocalDatabase:
    def __init__(self, name):
        self.name = name
        self.env = {k: v for k, v in os.environ.items() if k not in
                    {'DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH'}}

    def docker(self, *args, **kwargs):
        return subprocess.run(DOCKER + list(args), env=self.env, capture_output=True, text=True,
                              timeout=90, **kwargs)

    def sql(self, query, database='postgres'):
        return self.docker('exec', '-i', self.name, 'psql', '-X', '-qAt', '-v', 'ON_ERROR_STOP=1',
                           '-v', 'VERBOSITY=verbose', '-U', 'postgres', '-d', database, input=query)

    def execute(self, query, database='postgres'):
        result = self.sql(query, database)
        if result.returncode:
            raise AssertionError(result.stderr.strip())  # synthetic-only, never source/secret values
        return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/evidence/postgres-runtime-review.json')
    args = parser.parse_args()
    db = LocalDatabase('gk-kc2-disposable-' + uuid.uuid4().hex[:12])
    result = db.docker('run', '--rm', '-d', '--network', 'none', '--name', db.name,
                       '--label', 'gk.kc2.disposable=true', '--tmpfs', '/var/lib/postgresql/data',
                       '-e', 'POSTGRES_HOST_AUTH_METHOD=trust', IMAGE)
    if result.returncode:
        raise SystemExit('Local Docker startup failed; remote execution is never a fallback.')
    report = {'scope': 'Isolated local PostgreSQL; synthetic Supabase Auth contract, no remote writes',
              'image': IMAGE, 'network': 'none', 'published_ports': [], 'remote_migrations_applied': False,
              'migration_hashes': {}, 'limitations': ['Not the complete Supabase stack or live Google OAuth',
               'JWT claims are simulated via PostgreSQL settings; signature verification is outside these tests']}
    try:
        for _ in range(50):
            if db.sql('SELECT 1').returncode == 0:
                break
            time.sleep(0.2)
        else:
            raise AssertionError('Local PostgreSQL readiness timed out')
        report['postgres_version'] = db.execute('SHOW server_version')
        db.execute((ROOT/'tests/sql/local-auth-bootstrap.sql').read_text())
        for path in sorted((ROOT/'supabase/migrations').glob('*.sql')):
            db.execute(path.read_text())
            report['migration_hashes'][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        spec = importlib.util.spec_from_file_location('postgres_runtime_cases', ROOT/'tests/postgres_runtime_cases.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.DB = db
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        run = unittest.TextTestRunner(verbosity=2).run(suite)
        report.update(status='passed' if run.wasSuccessful() else 'failed', tests_run=run.testsRun,
                      failures=[{'test':str(t),'traceback':trace} for t,trace in run.failures],
                      errors=[{'test':str(t),'traceback':trace} for t,trace in run.errors])
    except Exception as exc:
        report.update(status='failed', setup_error=str(exc))
    finally:
        cleanup = db.docker('rm', '-f', db.name)
        report['container_removed'] = cleanup.returncode == 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'failures','errors'}}, indent=2))
    return 0 if report['status']=='passed' and report['container_removed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
