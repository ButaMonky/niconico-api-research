# Public GET probes for uploader playlist pagination (sanitized)

- Provenance: direct public HTTP GET probes performed in the ZenzaWatch investigation on 2026-10-26 JST.
- These results are distinct from the user-uploaded HAR and refer to a different public uploader account.
- User ID and all watch IDs are omitted here. No Cookie, Authorization, or other account credentials are reproduced.
- They are recorded from contemporaneous probe outputs; raw response bodies are not included.
- Observed only on this one public uploader. Do not generalize maximum totalCount or availability.

## v1 playlist/user-uploaded
- Host: `nvapi.nicovideo.jp`; method: GET.
- Path: `/v1/playlist/user-uploaded/{userId}`; `sortOrder=desc&sortKey=registeredAt`.
- Without pageSize/page: meta.status 200; 500 items, totalCount 1082.
- With pageSize=499&page=1: 499 items; totalCount 1082.
- With pageSize=500&page=1/2/3/4: [500, 500, 82, 0] items, totalCount 1082.
- With pageSize=501&page=1: HTTP 400. With pageSize=1000&page=1: HTTP 400.
- Combining pages 1..3 yields 1082 watchId entries and 1082 unique watchIds; no missing content/watchId; registeredAt descending.
- Thus 500 is an observed per-request response limit, **not an intrinsic 500-item limit of the user's uploaded videos**.
- The present ZenzaWatch `PlaylistApiLoader.load` requests only one default page and caches that array for 5 minutes, so a full list is not assembled.

## v3 users/{userId}/videos, same uploader (independent direct GET)
- GET `/v3/users/{userId}/videos?sortKey=registeredAt&sortOrder=desc&pageSize=100&page=1` yielded totalCount 1056.
- Adding `sensitiveContents=mask` yielded totalCount 1082.
- Pages 1..11 with `sensitiveContents=mask`: [100,100,100,100,100,100,100,100,100,100,82].
- All 1082 `essential.id` entries are unique; all match the combined 1082 v1 watchIds **in the same order**; no essential field was missing in these pages.
- This is not proof of the reason for the 26-item difference or of hidden/private media accessibility.
- A client that switches to v3 without retaining `sensitiveContents=mask` can lose items under these observed conditions.

## Remaining unknowns and product-work split
- Limits above 1082 items, extremely old uploads, channel/short-specific listing, login-vs-logged-out parity, and eventual concurrent uploads remain untested.
- An interrupted later page must not be reported as a complete playlist; stable snapshot behavior during pagination is not guaranteed by this probe.
- ZenzaWatch's list model can hold 10000 items, but PlayListSession.MAX_ITEMS=1000 and may trim during reload (code/fixture finding, not Niconico API).
- Product fixes belong to the other chat/task. This evidence is research-only and does not modify ZenzaWatch.
