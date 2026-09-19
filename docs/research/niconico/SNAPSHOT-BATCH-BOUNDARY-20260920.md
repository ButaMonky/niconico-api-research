# スナップショット100件一括取得と返却数境界

確認日時：2026-09-20 02:54:35〜02:54:43 JST。証拠の`checked_at`・`started_at`はUTC（`+00:00`）、APIが返す`last_modified`はJST（`+09:00`）。主目的は指定動画のタグ・投稿者ID補完の件数境界。ニコランNG本体の変更なし。

## 重要な結論

**公開・索引登録済みの100動画について、タグと投稿者IDを認証なしの1 GETで全件取得した。** `_limit=101` は400 `QUERY_PARSE_ERROR`。ただし**101個のIDフィルター自体は受理**され、`_limit=100`・`_offset=0/100`の2 GETで100件＋1件、重複なしの101件を取得できた。

100はこの条件で確認した「1ページの最大返却数」であり、IDフィルター個数やURL長の最大値ではない。101フィルターが成功したため「指定IDも最大100」という仮説は否定された。100件の全タグ取得は今回の索引データに関する結果で、現在の視聴ページのタグとの一致を保証しない。

証拠：`CONFIRMED-LIVE`。既存JSONの`status=traffic`に対応させ、`evidence_level`を併記した。[匿名化済み集計](evidence/snapshot-boundary-20260920.json)と[診断コード](tools/probe_snapshot_boundary.py)を保存。

[公開前検証](VERIFICATION-20260920.md)：研究用検証は通過。本体の既存テスト7件の失敗は範囲外の制約として記録。

## 重複調査を避けるために確認したもの

- ローカル正本の `SNAPSHOT-BATCH-CONFIRMED-20260914.md`：2/36/3動画取得と、別APIに対してタグ1個分が異なる例を確認済み。今回は未確定だった件数境界を進めるため追加検証した。タグ鮮度の同じ比較は繰り返していない。
- 2026-09-17の提供資料：本家検索とスナップショットの上位100件比較を報告済み。検索結果の比較を今回再実施していない。検索結果100件の取得と、指定した100 IDの補完は別の検証である。
- 2026-09-19の提供資料：提供画面・ギフトが中心で、本主目的に影響する新しい一括タグ検証は見つからなかった。追加contribution全12件の一括統合はしていない。
- 広告decorationの600成功・700失敗は、確認した最新提供資料でも原通信と照合できず、引き続き`REPORTED`。9月17日の「100件成功」の詳細は100 ID指定・62件返却であり、100件全返却とは異なる。[提供資料の受領レビュー](evidence/handoff-review-20260920.json)参照。
- `hidden`を退会と断定しない。一般会員のいいね全件取得は未解決のまま。この2点の新規検証はしていない。

## endpointと要求

| 項目 | 内容 |
|---|---|
| URL | `https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search` |
| method / client | GET / Python 3.12.10、公開検索API（Web/iOS/Androidアプリは実行していない） |
| authentication | なし。Cookie・ログイン・Authorizationを送っていない |
| 一般会員 | 会員セッション自体を使っていない。一般会員ログイン条件での試験とは区別する |
| headers | `User-Agent: NicoNGResearch/20260920`、`Accept: application/json`、`Accept-Encoding: identity` |
| body | なし |
| query | `q=`、`targets=title`、`fields=contentId,tags,userId,channelId`、`_sort=-viewCounter`、`_offset=0`、`_limit=100`、`_context=NicoNGResearch` |
| ID指定 | `filters[contentId][0]=<VIDEO_ID_0>`…の独立パラメータ。角括弧などはURLエンコード |
| 並び順 | 指定IDの順序ではなくsortに従う。`contentId`で対応付ける |
| response | `meta.status`、`meta.totalCount`、`data[].contentId/tags/userId/channelId` |

`tags`は空白区切り文字列。今回101動画では全て非空、`userId`は全て整数、`channelId`は全てnull。チャンネル動画の型・欠損条件は今回測定していない。タグのロック状態はこの応答に含めていない。

## 測定値

| 要求 | 指定ID数 | `_limit` / `_offset` | HTTP | `totalCount` / 返却数 | URL bytes | 応答本文 bytes | ms |
|---|---:|---|---:|---|---:|---:|---:|
| batch_100 | 100 | 100 / 0 | 200 | 100 / 100 | 4374 | 27179 | 367.23 |
| limit_101_with_2_ids | 2 | 101 / 0 | 400 | なし / データなし | 281 | 155 | 230.27 |
| filter_101_page_1 | 101 | 100 / 0 | 200 | 101 / 100 | 4416 | 27179 | 129.51 |
| filter_101_page_2 | 101 | 100 / 100 | 200 | 101 / 1 | 4418 | 328 | 122.38 |

400本文の理由は `_limit is out of range. 100 < 101`。短い2 ID要求で境界を試し、長いURLやID個数による失敗との混同を避けた。エラーを「タグなし」と解釈しない。

公開VOCALOIDタグ検索・再生数降順から100件＋次の1件を選んだ。事前に索引に存在する101件であるため、検索未登録動画の網羅性を試していない。100 ID要求の欠落・余分なIDは0。2ページの和集合は101、重複0。各返却動画のタグ文字列・投稿者・チャンネル値は取得元の索引応答と一致した（最新ページとの照合ではない）。

ニコニコAPI通信は合計8 GET（version前後2、検証用ID選定2、表の検証4）。本番で既知100 IDを補完する想定なら、ID選定2通信は不要。各要求間は1秒、タイムアウト20秒、再試行0、リダイレクト追従なし。HTTP 429はこの8回では観測されず、レート制限が存在しないという意味ではない。

サイズは`Accept-Encoding: identity`で読み取った本文の長さで、TLS・ヘッダー等を含む転送総量ではない。時間は接続開始から本文読み取り完了までの単発値。平均・p95・実画面での改善率は未測定。

## 鮮度とキャッシュ

`GET https://snapshot.search.nicovideo.jp/api/v2/snapshot/version`を前後に取得し、両方とも`last_modified=2026-09-19T07:07:12+09:00`。検証時点で約19時間47分前だった。version応答は`Cache-Control: max-age=60`、検索応答は`max-age=0, must-revalidate, no-cache, no-store, private`。

公式説明は毎朝5時の索引更新と記載するが、今回の返却時刻から完了時刻・公開タイミング・最大遅延を一般化しない。クライアント側で結果を保存するなら取得時刻と索引versionを区別する。versionが同じでもブラウザの最新タグと同じとはいえず、TTLだけで正確性を保証できない。[公式説明](https://site.nicovideo.jp/search-api-docs/snapshot)

## 外部資料との照合

[Javakky/NicoApiClient](https://github.com/Javakky/NicoApiClient/tree/5190ad3b777b83f2f10bea2e1a8b40affebc9d96)の`limit.py`・`request.py`は100件超をページ分割する。ライブラリで大きなlimitを指定できることと1通信で全件返ることを区別する。`simple_filter.py`は添字付きcontentIdの配列を生成する。これらは`CONFIRMED-CODE`、今回サービス側の100/101境界を独立に実測した。ライブラリそのものは実行していない。

[niconicolibs/api](https://github.com/niconicolibs/api/tree/7ee4782f7f4f7c351da4b00145b361291e22544a)の`spec/nvapi/nvapi.yaml`・`EssentialVideo.yaml`も確認。動画概要モデルに`owner`があり、`tags`の定義はない。読んだ仕様ファイルに`/v1/videos?watchIds`定義は見つからなかったが、API自体の不存在を意味しない。これだけを代替の全タグ一括APIの根拠にはできない。詳細は[外部資料台帳](EXTERNAL-SOURCES.md)。外部リポジトリ全体は保存していない。

## 再現手順

プロジェクト直下で実行する。追加ライブラリ・認証情報は不要。

```sh
python docs/research/niconico/tools/probe_snapshot_boundary.py
python docs/research/niconico/tools/probe_snapshot_boundary.py --live --output docs/research/niconico/exports/snapshot-boundary-recheck.json
```

初回は通信しない。`--live`のみ最大8 GET。既存出力を上書きしないため再検証時は別名を指定する。予期しないHTTP/通信失敗では後続試験を止め、成功分と失敗種別を残す。出力は公開検証用動画ID、件数・型・一致判定・時刻・サイズ・本文SHA256に限定。本文全体、タグ実値、投稿者ID、レスポンスの追跡IDや全ヘッダーは保存しない。SHA256は本文の取得同一性を示す参照値であり、本文未保存のため公開集計だけから再計算はできない。

成功条件は、100 ID要求でHTTP/本文statusが200、`all_requested_returned=true`、欠落と余分なIDが0、タグと投稿者の型・件数が100であること。101返却指定は400・範囲エラー、101フィルターの2ページ和集合は101・重複0。ID選定は固定した公開検索なので再実行時に対象が変わり得る。今回の正確なID列・queryは証拠JSONに保存した。

## 別開発タスクへの引き渡し

| 既知100動画のタグ・投稿者を補完する候補 | 通信数 | 正確性・条件 | 状態 |
|---|---:|---|---|
| 既にページが持つ情報を再利用 | 追加0 | 存在するフィールドのみ。タグ一覧の有無は画面別 | 既存解析参照、今回未測定 |
| 動画ごとの情報取得 | 原則100 | APIごとに現在値・欠落・認証条件の確認が必要 | 比較用の想定、現行本体の実測通信数ではない |
| スナップショット100 ID | 1 | 索引登録済み100件でタグ・投稿者を全取得。鮮度に制約 | 今回実測 |
| スナップショット＋必要分だけ個別確認 | 1＋k | k件の現在値照合が必要。厳密な最新タグ判定でkを0にできる根拠なし | 設計候補 |

導入判断は別タスク。新着・欠落・古いタグを「NG非該当」と決めない。返却IDで対応付け、欠落または最新性が必要な動画は個別の視聴情報・単独情報APIへフォールバックする候補。ページ内のowner情報を先に使えば、投稿者補完だけの通信を省ける可能性がある。個別経路のレスポンス形式と認証を選別し、同じ失敗を大量に再試行しない。

この研究は1要求100件を本体の既定値として推奨するものではない。URLは今回4374 bytes、2ページ試験では最大4418 bytesだったが、ブラウザ・プロキシ・ID長により条件が変わる。必要に応じ小さいバッチへ分割できる設計が必要。100件成功以上のURL最大値試験は目的への追加利益が小さいため今回は終了した。

## 未確認・次候補

優先候補は、別タスクの最新検証を再確認したうえで、新着・チャンネル・削除など索引欠落条件と、実ブラウザでのCORS・保持済みowner再利用を調べること。厳密な最新タグNGを保ったまま個別通信を何件省けるかは未解決。101より多いIDフィルターの限界、URL最大長、連続性能、投稿者非表示条件、iOS/Androidの現行差も未確認。コメントAPI・過去ログ・描画は[台帳の独立した次調査枠](EXTERNAL-SOURCES.md)へ残し、今回は深追いしていない。

## 更新履歴

- 2026-09-20：36件から100件へ最大確認済み一括返却数を拡張。`_limit`境界とフィルター数を分離して記録。過去の36件成功・鮮度不一致を取り消さない。
- 2026-09-20 公開前レビュー：再現コードのversion取得失敗時に後続通信を停止・失敗理由を記録するよう補強。オフライン回帰試験で初回429・不正時刻・timeoutと最終503を確認。実測時の両version取得は200であり、測定値の変更・追加実通信なし。回帰試験は`python docs/research/niconico/tools/test_probe_snapshot_boundary.py`。
- GitHub公開branchはremoteの既存`master`を基準とした。ローカル正本の未push本体変更や未精査の全研究履歴を含めず、この研究と検証に必要なファイルだけを選択。PR作成は公開範囲の選択であり、リポジトリの公開/非公開設定は変更しない。
