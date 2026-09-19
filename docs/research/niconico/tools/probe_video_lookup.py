"""Compare CSV and repeated watchIds; no authentication, raw payloads or owner IDs saved.

Checked 2026-09-20. Default is offline: prints planned URLs only.
Run: python tools/probe_video_lookup.py --live --output <new-summary.json>
Exactly 3 GETs maximum, 1 second apart, 20 second timeout, no retries/redirects.
--mode control instead sends single A, single B, repeated A/B (3 GETs maximum).
The 2 default IDs are public research samples, not browsing history.
HTTP/transport/schema failure stops the run. General-member behavior is not tested.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = 'https://nvapi.nicovideo.jp/v1/videos'
HEADERS = {'User-Agent': 'NicoNGResearch/20260920', 'Accept': 'application/json',
           'Accept-Encoding': 'identity', 'X-Frontend-Id': '6', 'X-Frontend-Version': '0',
           'Origin': 'https://www.nicovideo.jp', 'Referer': 'https://www.nicovideo.jp/'}
DEFAULT_IDS = ['sm15630734', 'sm1097445']


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def cases(ids, mode='encoding'):
    if mode == 'control':
        return [('single_a', [('watchIds', ids[0])]),
                ('single_b', [('watchIds', ids[1])]),
                ('repeated_forward', [('watchIds', value) for value in ids])]
    return [('csv', [('watchIds', ','.join(ids))]),
            ('repeated_forward', [('watchIds', value) for value in ids]),
            ('repeated_reverse', [('watchIds', value) for value in reversed(ids)])]


def summarize(payload, ids):
    items = payload.get('data', {}).get('items')
    if not isinstance(items, list):
        return {'schema_valid': False}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get('watchId'), str) or not item['watchId']:
            return {'schema_valid': False}
        video = item.get('video')
        if video is not None and (not isinstance(video, dict) or
                                  not isinstance(video.get('id'), str) or not video['id']):
            return {'schema_valid': False}
    rows = [x for x in items if isinstance(x, dict)]
    videos = [x['video'] for x in rows if isinstance(x.get('video'), dict)]
    owners = [x['owner'] for x in videos if isinstance(x.get('owner'), dict)]
    idset = set(ids)
    known = {'type', 'id', 'title', 'registeredAt', 'owner', 'count', 'thumbnail',
             'duration', 'isChannelVideo', 'tag', 'tags', 'contentType'}
    return {'schema_valid': len(rows) == len(items), 'returned_items': len(items),
            'matched_watch_ids': len({x.get('watchId') for x in rows} & idset),
            'matched_video_ids': len({x.get('id') for x in videos} & idset),
            'returned_requested_positions': [i for i, vid in enumerate(ids) if any(x.get('watchId') == vid for x in rows)],
            'unexpected_watch_ids': sum(x.get('watchId') not in idset for x in rows),
            'watch_video_id_disagreement': sum(x.get('watchId') != x['video'].get('id') for x in rows if isinstance(x.get('video'), dict)),
            'video_null_or_missing': len(rows) - len(videos),
            'owner_id_present': sum(x.get('id') is not None for x in owners),
            'owner_id_types': dict(Counter(type(x.get('id')).__name__ for x in owners)),
            'owner_type': dict(Counter(x.get('ownerType') if x.get('ownerType') in ('user', 'channel', 'hidden') else 'other_or_missing' for x in owners)),
            'tag_key_present': sum('tag' in x for x in videos),
            'tags_key_present': sum('tags' in x for x in videos),
            'known_video_fields_present': sorted(set().union(*(set(x) & known for x in videos)))}


def fetch(url, ids):
    started = datetime.now(timezone.utc).isoformat()
    before = time.perf_counter()
    info = {'started_at': started, 'url_ascii_bytes': len(url.encode('ascii'))}
    try:
        opener = urllib.request.build_opener(NoRedirect())
        try:
            response = opener.open(urllib.request.Request(url, headers=HEADERS), timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read(2_000_001)
            info['http_status'] = response.code
            info['cache_control'] = response.headers.get('Cache-Control')
        info.update(elapsed_ms=round((time.perf_counter()-before)*1000, 2), response_body_bytes=len(raw))
        if len(raw) > 2_000_000:
            info['failure'] = 'response_size_guard';return info, None
        info['response_sha256'] = hashlib.sha256(raw).hexdigest()
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            info['failure'] = 'unexpected_payload';return info, None
        status = payload.get('meta', {}).get('status')
        info['body_status'] = status if isinstance(status, int) else None
        if response.code != 200:
            code = payload.get('meta', {}).get('errorCode')
            if code in {'INVALID_PARAMETER', 'BAD_REQUEST', 'NOT_FOUND', 'FORBIDDEN', 'UNAUTHORIZED'}:
                info['error_code'] = code
            info['failure'] = 'http_error';return info, None
        info.update(summarize(payload, ids))
        return info, payload
    except (urllib.error.URLError, TimeoutError, OSError):
        info.update(http_status=None, failure='transport_error');return info, None
    except (ValueError, TypeError, AttributeError):
        info['failure'] = 'parse_or_schema_error';return info, None


def run(ids, mode='encoding'):
    result = {'schema_version': 1, 'checked_at': datetime.now(timezone.utc).isoformat(),
              'endpoint': ENDPOINT, 'method': 'GET', 'headers': HEADERS,
              'authentication': 'none; no Cookie or login session', 'general_member_session_tested': False,
              'public_research_video_ids': ids, 'mode': mode, 'automatic_retries': 0, 'requests': [], 'stopped_reason': None}
    baseline = {}
    planned = cases(ids, mode)
    for label, query in planned:
        url = ENDPOINT + '?' + urllib.parse.urlencode(query)
        info, payload = fetch(url, ids)
        info['case'] = label
        result['requests'].append(info)
        if info.get('http_status') != 200 or info.get('body_status') != 200 or not info.get('schema_valid'):
            result['stopped_reason'] = label + ': invalid HTTP/body/schema or transport failure';break
        for row in payload['data']['items']:
            video = row.get('video')
            if isinstance(video, dict) and row.get('watchId') in ids:
                owner = video.get('owner')
                if label == 'csv' or label.startswith('single_'):baseline[row['watchId']] = owner
                else:
                    origin = 'single' if mode == 'control' else 'csv'
                    field = 'owner_equal_to_'+origin if row['watchId'] in baseline and owner == baseline[row['watchId']] else 'owner_not_equal_or_baseline_missing'
                    info[field] = info.get(field, 0) + 1
        if label != planned[-1][0]:time.sleep(1)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true');parser.add_argument('--output', type=Path)
    parser.add_argument('--ids', nargs=2, default=DEFAULT_IDS)
    parser.add_argument('--mode', choices=['encoding', 'control'], default='encoding')
    args = parser.parse_args()
    if len(set(args.ids)) != 2 or not all(re.fullmatch(r'(sm|so|nm)\d+', x) for x in args.ids):
        parser.error('exactly two different public video IDs are required')
    if not args.live:
        print(json.dumps({'live': False, 'max_requests': 3, 'urls': [ENDPOINT+'?'+urllib.parse.urlencode(q) for _, q in cases(args.ids, args.mode)]}, indent=2));return
    if args.output is None or args.output.exists():parser.error('choose a new output path')
    result = run(args.ids, args.mode)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        output.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':main()
