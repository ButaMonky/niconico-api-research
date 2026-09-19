"""Snapshot batch boundary research, checked 2026-09-20; Python stdlib only.

Default is an offline plan. --live --output <file> sends at most eight GETs,
one second apart, without cookies/login and without automatic retries.
Stores selected public video IDs and aggregate comparisons, never response
bodies, tags, uploader IDs, request IDs, cookies or authentication tokens.
This is a research diagnostic, not production code or a freshness check.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

ENDPOINT = "https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search"
VERSION = "https://snapshot.search.nicovideo.jp/api/v2/snapshot/version"
FIELDS = "contentId,tags,userId,channelId"
HEADERS = {"User-Agent": "NicoNGResearch/20260920", "Accept": "application/json",
           "Accept-Encoding": "identity"}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def query(ids=None, limit=100, offset=0):
    p = {"q": "", "targets": "title", "fields": FIELDS, "_sort": "-viewCounter",
         "_offset": str(offset), "_limit": str(limit), "_context": "NicoNGResearch"}
    if ids is None:
        p["filters[tagsExact][0]"] = "VOCALOID"
    else:
        p.update({f"filters[contentId][{i}]": v for i, v in enumerate(ids)})
    return p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.live:
        print("Offline plan: version; public seed100; seed1 offset100; batch100; "
              "2 IDs with limit101; 101 IDs with limit100 at offsets0/100; version.")
        print("At most 8 GETs. Stop on unexpected failures; no raw data saved.")
        return
    if args.output is None or args.output.exists():
        parser.error("--live requires a new --output path (no overwrite)")
    opener = build_opener(NoRedirect())
    result = {"schema_version": 1, "checked_at": datetime.now(timezone.utc).isoformat(),
              "client": "Python " + platform.python_version(), "authentication": "none",
              "general_member_session_tested": False, "request_headers": HEADERS,
              "automatic_retries": 0, "redirects_followed": False,
              "seed_selection": "public VOCALOID tag index, descending viewCounter",
              "requests": []}

    def get(label, params=None, version=False):
        if result["requests"]:
            time.sleep(1)
        url = VERSION if version else ENDPOINT + "?" + urlencode(params)
        row = {"label": label, "started_at": datetime.now(timezone.utc).isoformat(),
               "method": "GET", "endpoint": VERSION if version else ENDPOINT,
               "query": params, "url_ascii_bytes": len(url.encode("ascii"))}
        result["requests"].append(row)
        started = time.perf_counter()
        try:
            try:
                response = opener.open(Request(url, headers=HEADERS), timeout=20)
            except HTTPError as exc:
                response = exc
            with response:
                body = response.read()
                row.update(http_status=response.code, response_bytes=len(body),
                           response_sha256=hashlib.sha256(body).hexdigest(),
                           response_headers={k: response.headers[k] for k in (
                               "Content-Type", "Content-Encoding", "Cache-Control", "Age",
                               "Access-Control-Allow-Origin", "Retry-After") if k in response.headers})
            row["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
            try:
                parsed = json.loads(body)
            except (ValueError, UnicodeError):
                row["json_decoded"] = False
                return None
            row["json_decoded"] = True
            if not isinstance(parsed, dict):
                row["unexpected_json_shape"] = True
                return None
            if version:
                row["last_modified"] = parsed.get("last_modified")
                return parsed
            meta = parsed.get("meta", {})
            row["meta"] = {k: meta[k] for k in ("status", "totalCount", "errorCode", "errorMessage") if k in meta}
            data = parsed.get("data", [])
            row.update(returned=len(data), distinct_ids=len({d.get("contentId") for d in data}),
                       tags_string_count=sum(isinstance(d.get("tags"), str) for d in data),
                       tags_nonempty_count=sum(bool(d.get("tags")) for d in data),
                       user_id_integer_count=sum(type(d.get("userId")) is int for d in data),
                       channel_id_nonnull_count=sum(d.get("channelId") is not None for d in data))
            return parsed
        except (URLError, TimeoutError, OSError) as exc:
            row["transport_error_type"] = type(exc).__name__  # No local paths/proxy values.
            row["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
            return None

    def successful(value):
        return value is not None and value.get("meta", {}).get("status") == 200

    def valid_version(value):
        if not isinstance(value, dict) or result["requests"][-1].get("http_status") != 200:
            return False
        try:
            return datetime.fromisoformat(value["last_modified"]).tzinfo is not None
        except (KeyError, TypeError, ValueError):
            return False

    def compare(value, ids, reference):
        data = value.get("data", [])
        by_id = {d["contentId"]: d for d in data}
        row = result["requests"][-1]
        row.update(requested_ids=len(ids), requested_distinct_ids=len(set(ids)),
                   missing_count=len(set(ids) - by_id.keys()),
                   unexpected_count=len(by_id.keys() - set(ids)),
                   all_requested_returned=set(ids) == by_id.keys(),
                   fields_equal_to_seed_count=sum(all(d.get(k) == reference[i].get(k)
                       for k in ("tags", "userId", "channelId")) for i, d in by_id.items() if i in reference))

    try:
        if not valid_version(get("version_before", version=True)):
            result["stopped_reason"] = "Initial version request failed or version timestamp invalid"
            return
        seed = get("seed_100", query())
        if not successful(seed) or len(seed.get("data", [])) != 100:
            result["stopped_reason"] = "Seed100 did not return 100 successful rows"
            return
        extra = get("seed_extra_1", query(limit=1, offset=100))
        if not successful(extra) or len(extra.get("data", [])) != 1:
            result["stopped_reason"] = "Extra seed row unavailable"
            return
        data = seed["data"] + extra["data"]
        ids = [d["contentId"] for d in data]
        if len(set(ids)) != 101:
            result["stopped_reason"] = "Seed IDs are not 101 distinct videos"
            return
        reference = {d["contentId"]: d for d in data}
        # IDs are public research targets; uploader identity and tag strings remain in memory only.
        result["public_seed_video_ids"] = ids
        batch = get("batch_100", query(ids[:100]))
        if not successful(batch):
            result["stopped_reason"] = "100-ID request failed; no larger batch attempted"
            return
        compare(batch, ids[:100], reference)
        invalid = get("limit_101_with_2_ids", query(ids[:2], limit=101))
        if result["requests"][-1].get("http_status") not in (200, 400):
            result["stopped_reason"] = "Unexpected boundary response; stop without retries"
            return
        first = get("filter_101_page_1", query(ids))
        if not successful(first):
            result["stopped_reason"] = "101-ID filter failed"
            return
        compare(first, ids, reference)
        last = get("filter_101_page_2", query(ids, limit=100, offset=100))
        if not successful(last):
            result["stopped_reason"] = "Second page failed"
            return
        compare(last, ids, reference)
        page_ids = [d["contentId"] for d in first["data"] + last["data"]]
        result["pagination"] = {"union_count": len(set(page_ids)),
             "duplicate_count": len(page_ids) - len(set(page_ids)),
             "all_101_returned": set(page_ids) == set(ids)}
        if not valid_version(get("version_after", version=True)):
            result["stopped_reason"] = "Final version request failed; index stability not established"
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        print(json.dumps({"requests": len(result["requests"]), "stopped_reason": result.get("stopped_reason"),
                          "pagination": result.get("pagination")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
