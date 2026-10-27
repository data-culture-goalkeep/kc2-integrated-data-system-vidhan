import unittest
from attendance_guard_optimization import indexed_query, ORIGINAL, INDEXED


class IndexedGuardTests(unittest.TestCase):
    def test_adds_only_redundant_nonnull_primary_key_probe(self):
        q = 'BEGIN; INSERT INTO example VALUES(1); DO $batch$ BEGIN IF EXISTS(SELECT 1 FROM (SELECT 1 id) x WHERE NOT EXISTS(SELECT 1 FROM example t ' + ORIGINAL + ")) THEN RAISE EXCEPTION 'conflict'; END IF; END $batch$; COMMIT;"
        changed = indexed_query(q)
        self.assertEqual(changed.replace(INDEXED, ORIGINAL), q)
        self.assertEqual(changed.split('DO $batch$')[0], q.split('DO $batch$')[0])

    def test_missing_or_repeated_marker_rejected(self):
        for query in ['SELECT 1', ORIGINAL + ORIGINAL]:
            with self.assertRaises(ValueError):
                indexed_query(query)


if __name__ == '__main__':
    unittest.main()
