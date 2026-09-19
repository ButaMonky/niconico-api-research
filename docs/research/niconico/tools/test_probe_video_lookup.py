"""Offline tests for the research probe's privacy and request safety."""
import json
import unittest
from unittest.mock import patch
import probe_video_lookup as probe


class ProbeTests(unittest.TestCase):
    def test_response_values_and_unknown_fields_never_leave_summary(self):
        secret = 'private-value-not-for-export'
        body = {'data': {'items': [{'watchId': 'sm9', 'video': {
            'id': 'sm9', 'title': secret, 'tags': [secret],
            'owner': {'id': secret, 'name': secret, 'visibility': secret},
            'unexpected': secret}}]}, 'token': secret}
        result = probe.summarize(body, ['sm9'])
        self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(result['matched_video_ids'], 1)
        self.assertEqual(result['owner_id_present'], 1)
        self.assertEqual(result['tags_key_present'], 1)

    def test_first_transport_failure_stops_remaining_requests(self):
        with patch.object(probe, 'fetch', return_value=({'http_status': None, 'failure': 'transport_error'}, None)) as call:
            result = probe.run(['sm9', 'sm1'])
        self.assertEqual(call.call_count, 1)
        self.assertEqual(len(result['requests']), 1)
        self.assertIsNotNone(result['stopped_reason'])

    def test_malformed_items_stop_before_second_request(self):
        for item in ({}, {'watchId': 1}, {'watchId': 'sm9', 'video': 'broken'},
                     {'watchId': 'sm9', 'video': {}}):
            with self.subTest(item=item):
                payload = {'meta': {'status': 200}, 'data': {'items': [item]}}
                info = {'http_status': 200, 'body_status': 200, **probe.summarize(payload, ['sm9', 'sm1'])}
                with patch.object(probe, 'fetch', return_value=(info, payload)) as call, patch.object(probe.time, 'sleep'):
                    result = probe.run(['sm9', 'sm1'])
                self.assertEqual(call.call_count, 1)
                self.assertIsNotNone(result['stopped_reason'])

    def test_partial_and_null_video_are_not_malformed(self):
        payload = {'data': {'items': [{'watchId': 'sm1', 'video': None}]}}
        result = probe.summarize(payload, ['sm9', 'sm1'])
        self.assertTrue(result['schema_valid'])
        self.assertEqual(result['returned_items'], 1)
        self.assertEqual(result['video_null_or_missing'], 1)
        self.assertEqual(result['matched_video_ids'], 0)


if __name__ == '__main__':
    unittest.main()
