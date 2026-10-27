"""Synthetic authorization and read-only reconciliation tests; no remote calls."""
import copy
import unittest
from datetime import datetime, timezone

from attendance_resume import check_window, PLAN
from attendance_execution import PROJECT, IMPORT
from attendance_reconcile import jsonb_text, expected


class AttendanceResumeTests(unittest.TestCase):
    def setUp(self):
        self.approval = {'issued_at': '2026-10-27T14:46:21Z', 'expires_at': '2026-10-27T18:46:21Z',
                         'project_reference': PROJECT, 'import_manifest_sha256': IMPORT,
                         'resumption_plan_sha256': PLAN}

    def at(self, hour, minute=0, second=0):
        return datetime(2026, 10, 27, hour, minute, second, tzinfo=timezone.utc)

    def test_owner_window_valid(self):
        check_window(self.approval, self.at(15))

    def test_expired_and_not_yet_valid_rejected(self):
        for instant in [self.at(14), self.at(18, 46, 21), self.at(19)]:
            with self.assertRaises(ValueError):
                check_window(self.approval, instant)

    def test_window_cannot_be_extended(self):
        approval = {**self.approval, 'expires_at': '2026-10-27T19:46:21Z'}
        with self.assertRaises(ValueError):
            check_window(approval, self.at(15))

    def test_target_and_manifest_bindings(self):
        for field in ['project_reference', 'import_manifest_sha256', 'resumption_plan_sha256']:
            with self.assertRaises(ValueError):
                check_window({**self.approval, field: 'changed'}, self.at(15))

    def test_jsonb_key_and_number_representation(self):
        self.assertEqual(jsonb_text({'aa': False, 'z': 0, 'b': [None, 0.0000001, -0.0]}),
                         '{"b": [null, 0.0000001, 0.0], "z": 0, "aa": false}')

    def test_payload_and_identifier_changes_detected(self):
        rows = [{'id': 'ab-synthetic-1', 'original_mark': 'P'}, {'id': 'ab-synthetic-2', 'original_mark': None}]
        digest = expected(rows)
        self.assertEqual(digest, expected(list(reversed(rows))))
        changed = copy.deepcopy(rows)
        changed[0]['original_mark'] = 'A'
        self.assertNotEqual(digest, expected(changed))
        changed[0]['id'] = 'ab-other-id'
        self.assertNotEqual(digest, expected(changed))


if __name__ == '__main__':
    unittest.main()
