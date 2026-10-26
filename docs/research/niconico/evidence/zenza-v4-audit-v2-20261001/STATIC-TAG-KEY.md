# F06：タグ編集キー更新の静的根拠

原監査日2026-10-01、develop d4d1f7892d6960b76610aea20b78f0c7a032666c。対象はpackages/lib/src/nico/TagEditApi.js / _refreshEditKey。記録時の再実行・実API観測ではない。

原監査で読んだコードの参照点を抜粋する。連続行の完全コピーではなく、query・例外処理等は省略している。実キーは含まない。

```javascript
const url = `https://www.nicovideo.jp/api/watch/v3/${encodeURIComponent(videoId)}?${query.toString()}`;
const res = await util.fetch(url, {credentials: 'include'});
json = await res.json();
const editKey = json && json.data && json.data.tag && json.data.tag.edit && json.data.tag.edit.editKey;
```

根拠は前の監査の製品ソース読取りとREPORT_V2.mdのF06節。原添付REPORT_V2.mdのSHA-256はa202223e04fcce9c8cd98fcd5cbcdb1b82d124105e949eef8cb44ff910bac1fd。

確認したのは旧v3 URLと旧data.tag.edit.editKeyへの依存だけ。現行HTTP状態・廃止・新しい更新URL・キー寿命は未確認。公式更新要求を観測するまで機械的URL置換や他者動画への試験タグ書込みをしない。
