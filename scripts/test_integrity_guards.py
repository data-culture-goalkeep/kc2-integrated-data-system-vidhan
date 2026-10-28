"""Source validation must remain active even when Python optimization is enabled."""
import ast
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]

class IntegrityGuardTests(unittest.TestCase):
    def test_runtime_scripts_do_not_use_removable_assert_guards(self):
        for path in (ROOT/'scripts').glob('*.py'):
            if not path.name.startswith('test_'):
                self.assertFalse(any(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(path.read_text()))),str(path))

    def test_source_guard_still_rejects_under_optimized_python(self):
        code="import sys;sys.path.insert(0,'scripts');from profile_sources import ensure_source_integrity;ensure_source_integrity(False,'Synthetic validation failure')"
        result=subprocess.run([sys.executable,'-O','-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Synthetic validation failure',result.stderr)

if __name__=='__main__':
    unittest.main()
