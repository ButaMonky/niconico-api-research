# 2026-10-27｜公式投稿者動画一覧HAR・深掘り匿名化証拠

## 出典・対象範囲
- 提供HAR: `投稿動画一覧(1).har`。2026-10-26 23:57:59.755〜23:59:41.777 JSTの171エントリ。サイズ8,123,437バイト。
- 原本SHA-256: `2860b91bfcfc186cd5cfdc82f378ae381e6c6950200d0c566149cc321c5952c0`。
- 先に提供された `投稿動画一覧.har` と今回の `投稿動画一覧(1).har` は、SHA-256・バイト長・内容が完全一致する同一ファイル。
- 参照対象は1投稿者の公式Web投稿動画一覧（公開表示）。実APIへの再要求なし。投稿者ID、動画ID、タイトル、ユーザー名、Cookie、ヘッダー値、署名付きURL、key値は記録しない。
- HARにランキングページ・ランキングAPIを要求したエントリは0件。ランキングHAR／hydrated DOMの別保留2件を検証したことにはならない。

## 初期HTMLと後続APIの同一結果
- 最初のHTML応答: `GET /user/{userId}/video` HTTP 200。
- HTML要素 `#js-initial-userpage-data` の属性 `data-initial-data` をHTML属性アンエスケープ後にJSONとして解析できる。
- `data-initial-data.nvapi[0]` の `method=GET`、`templatePath=/v3/users/{userId}/videos`。
- 埋め込みクエリ: `page=1`, `pageSize=100`, `sortKey=registeredAt`, `sortOrder=desc`, `selectContentType=long`, `sensitiveContents=mask`。補助値は `q=''`, `_language=ja-jp`。
- 埋め込み `body.data.items.length=100`、`body.data.totalCount=587`。
- 後続の実GET `/v3/users/{userId}/videos?pageSize=100&page=1` の100件と、初期HTML埋め込みの100件について、IDと順序だけでなく各 `{series,essential}` オブジェクトが100/100完全一致（JSON構造比較）。
- HTMLの最初の要求からページ1 GET開始まで約10.1秒。再取得理由はHARだけでは確定しないため、通信が必ず冗長とは断定しない。

## シリーズ順序・動画メタデータ
- 6ページ `[100,100,100,100,100,87]`、合計587ユニーク動画、`totalCount=587`、`registeredAt` は降順。HTMLに埋め込まれた最初の100件と重複している。
- `series` は430件、nullは157件。6つのシリーズの動画数は `[258,52,41,38,23,18]`（降順）。
- 別 `GET /v1/users/{userId}/series?page=1&pageSize=100`（HTTP 200）の `itemsCount` 6値と、動画一覧から数えたシリーズ別の件数が全件一致。
- 各シリーズにおける `series.order` は1始まりで連続かつ重複なし（各シリーズ 1..itemsCount）。登録日時降順の動画一覧中ではシリーズ内のorderが降順に並んだ。
- `contentType=long` 587/587。このHARにはshortタブのAPI応答がないため、long/shortの違いや複数シリーズ所属の契約は推定しない。

## サムネイルとHAR保存形式
- `essential.thumbnail` は `url`, `middleUrl`, `largeUrl`, `listingUrl`, `nHdUrl`, `shortUrl` を持つ。587件すべて `listingUrl === middleUrl`。
- 587件すべて `shortUrl=null`。 `nHdUrl` は `img.cdn.nimg.jp` 側の `r640x360l` 変換パスで、署名用 `key` クエリが付く（実値・URL全体は保存しない）。
- HAR内の `nicovideo.cdn.nimg.jp/thumbnails/` への画像GETは107件（異なるURL107）。全107件が動画データの `listingUrl` に一致。`nHdUrl` の画像GETは当該HARに存在しない。
- 107画像GETだけで公式UIが恒久的に107件しか描画しないとは言えない。スクロール範囲やブラウザキャッシュ条件は別途検証。
- 動画一覧6 GETのHAR保存形式: `response.content.encoding=base64` が4件、通常テキストJSONが2件。Base64はHAR内の表現でありAPI暗号化を意味しない。解析時はencodingに応じてデコードする。

## 通信と未確認事項
- 171エントリのうち `GET /v3/users/{userId}/videos` は6回、対応 `OPTIONS` は6回。6 GETはいずれもHTTP 200。ページ2取得開始はページ1より約77秒後（ユーザー操作・事前取得の有無は未検証）。
- ほかにシリーズ、クリエイター支援、ユーザー達成履歴、広告枠等の要求あり。ランキング通信0。3件のstatus=0は広告スクリプト・ヘッダー・ログ画像であり投稿動画APIの失敗ではない。
- 実APIの応答に `Access-Control-Allow-Origin: https://www.nicovideo.jp` と `Access-Control-Allow-Credentials: true` を観測。ブラウザ外の任意のoriginで使えることは意味しない。
- この標本の同一性は2026-10-26の1投稿者・同一HARに限定。HTMLがいつも同形、初期HTMLの100件が再GETと常に一致、シリーズorderが常に連続、thumbnailの署名URLが将来も同形とは断定しない。
- このレコードはユーザー提供記録の匿名化結果。生HARは研究Git/GitHubへ配置していない。
