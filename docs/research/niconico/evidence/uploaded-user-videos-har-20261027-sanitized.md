# Niconico Web・投稿動画一覧HARの匿名化した証拠（2026-10-27記録）

- 分類: user-provided HAR / recorded browser traffic（新規サーバー送信なし）
- 取得日時: 2026-10-26 23:58〜23:59 JST（HARのUTC記録を変換）
- 提供されたHARのSHA-256: `2860b91bfcfc186cd5cfdc82f378ae381e6c6950200d0c566149cc321c5952c0`
- 元HAR: このチャットで提供。約8.1MB、合計171エントリ。研究ディレクトリには原本を置かない
- 注: URLの投稿者ID、動画ID、ページ本文、個人情報、認証・識別子、Cookie、ヘッダー値はこの証拠に複製しない

## NICO-USERVIDEOS-20261027-WEB-PAGES-587
- HTTP GET `https://nvapi.nicovideo.jp/v3/users/{userId}/videos`
- 共通クエリ: `selectContentType=long`、`sortKey=registeredAt`、`sortOrder=desc`、`sensitiveContents=mask`、`pageSize=100`、`page=1..6`
- ページ1〜6: HTTP 200、JSON `meta.status=200`、`data.totalCount=587`（各ページで同じ）
- 各ページの `data.items.length`: `[100,100,100,100,100,87]`
- 合計587件、`items[].essential.id` のユニーク数587、空ID0、`registeredAt` は新しい順
- 項目構造: `data.items[] = { essential, series }`。essential内にid/registeredAt/contentType/count/thumbnail等を確認
- このHARで実測できたのは6ページ・587件。API最大ページ数、匿名時の同一応答、短尺タブ・削除済み・非公開動画の網羅は未確認
- `sensitiveContents=mask` の指定あり。指定なしとの同一HAR対照はなく、この記録だけで効果や隠し動画の全取得を断定しない

## NICO-USERVIDEOS-20261027-SERIES-430
- 上記587件のうち `series !== null` は430件、nullは157件
- `series` は `{id:number,title:string,order:number}` 形式、異なるシリーズIDは6件
- 別API: GET `https://nvapi.nicovideo.jp/v1/users/{userId}/series?page=1&pageSize=100`
- この別APIもHTTP 200 / `meta.status=200` / `data.totalCount=6` / `data.items.length=6`
- `data.items[]` にid/title/itemsCount等があり、投稿動画の6種のseries.idが全て対応
- 投稿動画をシリーズ別に数えた件数 `[258,52,41,38,23,18]` と、別APIの `itemsCount` 6値が一致
- 各シリーズの動画順は `series.order` を参照できる可能性があるが、公式再生順との実機照合はまだない
- 1動画が複数シリーズへ属する仕様、削除動画・非公開動画での差異は未確認

## 同じHARに含まれる周辺通信
- `GET mjk.nicovideo.jp/api/v1/users/{userId}/pinned_achieved_history`（200）
- `GET mjk.nicovideo.jp/api/v1/users/{userId}/achieved_histories`（200）
- `GET nvapi.nicovideo.jp/v1/users/{userId}/creator-support`（200）
- これらは既存研究にも類例があるため「新API発見」とは扱わず、今回の利用確認として記録する

## 既存ZenzaWatchとの関係・所有権
- 現在のZenzaWatch `PlaylistApiLoader` は別の `/v1/playlist/user-uploaded/{userId}` を1回だけ要求し、500件以上のページ送りは未実装（この点は別途コードと公開GETで検証済み）
- 別ユーザーの公開GETによる旧API1,082件/500件の結果と、このHARの587件は異なる対象。混合して検証数を水増ししない
- この記録は仕様研究のみ。別チャット所有の製品コード、修正タスク、予約、worktree、develop、origin、公開版に変更なし
- `sources.json` 等の共有索引は既に未コミット変更があるため編集禁止。新発見JSONはcontributionsとして統合待ち
