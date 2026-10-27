import unittest
from datetime import datetime, timezone
from attendance_execution import PROJECT, IMPORT
from attendance_indexed_execution import packet, window


class IndexedExecutionTests(unittest.TestCase):
    def test_committed_and_out_of_scope_indices_rejected(self):
        for index in [0, 171, 172, 216]:
            with self.assertRaises(ValueError):
                packet(index, {}, {})

    def test_expiry_and_new_manifest_binding(self):
        a = {'issued_at': '2026-10-27T14:00:00Z', 'expires_at': '2026-10-27T18:00:00Z',
             'project_reference': PROJECT, 'original_import_manifest_sha256': IMPORT,
             'indexed_manifest_sha256': 'synthetic-new-manifest'}
        instant = datetime(2026, 10, 27, 15, tzinfo=timezone.utc)
        window(a, 'synthetic-new-manifest', instant)
        for field in ['project_reference', 'original_import_manifest_sha256', 'indexed_manifest_sha256']:
            with self.assertRaises(ValueError):
                window({**a, field: 'changed'}, 'synthetic-new-manifest', instant)
        with self.assertRaises(ValueError):
            window(a, 'synthetic-new-manifest', datetime(2026, 10, 27, 18, tzinfo=timezone.utc))


if __name__ == '__main__':
    unittest.main()
