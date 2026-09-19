"""Offline regression: version failures must not silently continue network work."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import probe_snapshot_boundary as probe


class Response:
    def __init__(self, code, value):
        self.code = code
        self.headers = {}
        self.body = json.dumps(value).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class VersionFailureTests(unittest.TestCase):
    def run_probe(self, responses):
        cache = Path(__file__).parent / '__pycache__'
        cache.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=cache) as folder:
            assert Path(folder).resolve().is_relative_to(cache.resolve())
            out = Path(folder) / 'result.json'
            with patch.object(probe, 'build_opener') as factory, \
                 patch.object(probe.time, 'sleep'), \
                 patch('sys.argv', ['probe', '--live', '--output', str(out)]), \
                 contextlib.redirect_stdout(io.StringIO()):
                factory.return_value.open.side_effect = responses
                probe.main()
                count = factory.return_value.open.call_count
            return json.loads(out.read_text(encoding='utf-8')), count

    def test_initial_failure_stops_before_seed_request(self):
        seed_failure = Response(500, {'meta': {'status': 500}})
        for response in (Response(429, {'meta': {'status': 429}}),
                         Response(200, {'last_modified': 'not-a-timestamp'}),
                         TimeoutError()):
            with self.subTest(response=type(response).__name__):
                result, count = self.run_probe([response, seed_failure])
                self.assertEqual(count, 1)
                self.assertIn('version', result['stopped_reason'].lower())

    def test_final_version_failure_is_recorded(self):
        rows = [{'contentId': f'sm{i}', 'tags': 'test', 'userId': 1, 'channelId': None}
                for i in range(1, 102)]
        def ok(data):
            return Response(200, {'meta': {'status': 200}, 'data': data})
        result, count = self.run_probe([
            Response(200, {'last_modified': '2026-09-19T07:07:12+09:00'}),
            ok(rows[:100]), ok(rows[100:]), ok(rows[:100]),
            Response(400, {'meta': {'status': 400, 'errorCode': 'QUERY_PARSE_ERROR'}}),
            ok(rows[:100]), ok(rows[100:]), Response(503, {'meta': {'status': 503}})])
        self.assertEqual(count, 8)
        self.assertIn('version', result.get('stopped_reason', '').lower())


if __name__ == '__main__':
    unittest.main()
