"""Synthetic journal-integrity probes; no source records or database access."""
import json
import tempfile
import unittest
from pathlib import Path

from attendance_execution import canonical, sha
from report_attendance_final import journal


class FinalJournalTests(unittest.TestCase):
    def records(self):
        out = []
        for i in [173, 174]:
            item = {'event': 'committed_ack', 'index': i, 'request_id': 'synthetic-' + str(i),
                    'previous_sha256': out[-1]['sha256'] if out else None}
            item['sha256'] = sha(canonical(item).encode())
            out.append(item)
        return out

    def check(self, items):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'journal.jsonl'
            path.write_text('\n'.join(json.dumps(x) for x in items) + '\n')
            return journal(path)

    def test_valid_receipts_preserved(self):
        self.assertEqual([x['index'] for x in self.check(self.records())], [173, 174])

    def test_changed_request_rejected(self):
        items = self.records()
        items[0]['request_id'] = 'changed'
        with self.assertRaises(ValueError):
            self.check(items)

    def test_missing_receipt_breaks_chain(self):
        with self.assertRaises(ValueError):
            self.check(self.records()[1:])


if __name__ == '__main__':
    unittest.main()
