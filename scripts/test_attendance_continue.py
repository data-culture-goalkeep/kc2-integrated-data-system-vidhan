"""Synthetic tests; no owner artifact, SQL or remote access."""
import unittest
from datetime import datetime, timezone
from attendance_continue import original_index, authorize_window
from attendance_execution import PROJECT, IMPORT


class AttendanceContinuationTests(unittest.TestCase):
    def test_only_remaining_positions_exposed(self):
        self.assertEqual([original_index(i) for i in range(44)], list(range(172, 216)))
        for index in [-1, 44, 171, 172]:
            with self.assertRaises(ValueError):
                original_index(index)

    def test_expiry_and_exact_bindings(self):
        a = {'issued_at': '2026-10-27T14:00:00Z', 'expires_at': '2026-10-27T18:00:00Z',
             'project_reference': PROJECT, 'import_manifest_sha256': IMPORT,
             'continuation_plan_sha256': 'synthetic-plan'}
        now = datetime(2026, 10, 27, 15, tzinfo=timezone.utc)
        authorize_window(a, 'synthetic-plan', now)
        for field in ['project_reference', 'import_manifest_sha256', 'continuation_plan_sha256']:
            with self.assertRaises(ValueError):
                authorize_window({**a, field: 'changed'}, 'synthetic-plan', now)
        with self.assertRaises(ValueError):
            authorize_window(a, 'synthetic-plan', datetime(2026, 10, 27, 18, tzinfo=timezone.utc))


if __name__ == '__main__':
    unittest.main()
