"""Synthetic tests only; no database or remote executor is available here."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import attendance_execution as execution
from etl_core import canonical


class AttendanceExecutionControls(unittest.TestCase):
    def test_tool_rejection_fails_closed(self):
        self.assertFalse(execution.response_is_acknowledged({'isError': True, 'content': [{'type': 'text', 'text': 'Denied'}]}))

    def test_unknown_empty_or_malformed_ack_fails_closed(self):
        for value in [{}, {'content': []}, {'content': [{'type': 'text', 'text': 'Action completed.'}]}]:
            self.assertFalse(execution.response_is_acknowledged(value))

    def test_database_error_fails_closed(self):
        response = {'content': [{'type': 'text', 'text': json.dumps({'error': {'message': 'synthetic failure'}})}]}
        self.assertFalse(execution.response_is_acknowledged(response))

    def test_structured_query_acknowledgement(self):
        self.assertTrue(execution.response_is_acknowledged({'content': [{'type': 'text', 'text': json.dumps({'result': '<untrusted-data-demo>\n[]\n</untrusted-data-demo>'})}]}))

    def test_durable_metadata_chain_preserves_dispatch_failure(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(execution, 'W', Path(folder)):
            execution.append({'event': 'submitted', 'index': 0, 'request_id': 'synthetic-request'})
            execution.append({'event': 'failed_or_uncertain', 'index': 0})
            events = execution.journal()
            self.assertEqual(events[1]['previous_sha256'], events[0]['sha256'])
            self.assertEqual(sum(e['event'] == 'committed_ack' for e in events), 0)
            for event in events:
                digest = event.pop('sha256')
                self.assertEqual(digest, hashlib.sha256(canonical(event).encode()).hexdigest())


if __name__ == '__main__':
    unittest.main()
