# playlist/request：新着・チャンネル・欠落の検証

確認日：2026-09-20 JST。R23〜R25、匿名Pythonクライアント。既知の100件成功を再試験せず、NG判定で情報を誤用しやすい条件を調べた。本体変更なし。

## 要点と証拠

| 単位 | 実通信で確認したこと | 解釈の限界 |
|---|---|---|
| R23 新着 | snapshotで0件の新着3件をplaylistで3件取得。追加比較で検索とowner ID/typeが3/3一致 | 両比較元はnvapi。同時点の独立した視聴情報との一致は未確認 |
| R24 チャンネル | channel 2件＋user 1件を1 POSTで返却。channelのowner.idは`ch<digits>`、snapshot.channelIdは数値 | 文字列の完全一致は0/2、ch除去後の数字部分一致は2/2。無条件のID正規化は不可 |
| R25 不正ID | `sm9,sm0`と`sm9,not-a-video`は各400 INVALID_PARAMETER | 不正入力で全体が失敗する条件。全ての未存在IDが400になるとはいえない |
| R25 重複 | `sm9,sm9`は200、totalCount=2、items=2、異なるwatchId=1 | totalCountと行数は異なる動画数ではない |
| R25 部分返却 | `sm9,sm1`は200、totalCount=2、items=1、返却sm9、欠落sm1 | HTTP成功とtotalCountは全返却の保証ではない。sm1の欠落理由は不明 |

証拠：[新着](evidence/playlist-new-uploads-20260920.json)、[チャンネル](evidence/playlist-channel-20260920.json)、[失敗・重複・欠落](evidence/playlist-failures-20260920.json)。生応答は保存せず、公開動画ID・項目名・数・等値比較・応答hashのみを記録。実投稿者ID・名前・playlist識別値・キーを除外した。

## 要求と応答

```yaml
endpoint: https://nvapi.nicovideo.jp/v1/playlist/request
method: POST
client: anonymous-python (Web-form request shape)
authentication: none in these observations
status: CONFIRMED-LIVE
first_confirmed: 2026-09-20 # この匿名検証系列。過去の記録は別資料参照
last_confirmed: 2026-09-20
request:
  content_type: application/x-www-form-urlencoded
  title: Metadata research
  watchIds: comma-separated public video IDs
response:
  - data.totalCount
  - data.items[].watchId
  - data.items[].content.id
  - data.items[].content.owner.id
  - data.items[].content.owner.type
  - data.items[].content.owner.visibility
batch:
  supported: true
  max_confirmed: 100 # R22。最大値を意味しない
limitations:
  - no tag/tags/tagList fields in sampled content
  - missing IDs can occur with HTTP 200
  - browser CORS and logged-in general-member behavior unverified
  - server retention and side effects unverified
```

送信header名と今回の値：`Content-Type: application/x-www-form-urlencoded`、`X-Frontend-Id: 6`、`X-Frontend-Version: 0`、`X-Request-With: https://www.nicovideo.jp`、`Origin: https://www.nicovideo.jp`、`User-Agent: NiconicoResearch/20260920`、`Accept: application/json`、`Accept-Encoding: identity`。Cookie/Authorizationなし。これら全てが必須という検証ではない。ログインしていないので、一般会員セッションでの成功とは記録しない。

## R23：新着の範囲と対照失敗

05:56:55〜06:05:36 JST。検索`GET /v2/search/video`の研究用タグVOCALOID・登録日時降順で得た公開3動画（sm46820957、sm46820924、sm46819764）は、登録時刻がそれぞれ05:13:28、04:51:00、04:30:00。snapshot/versionは前後とも前日07:07:12。contentIdフィルタ指定のsnapshot応答0件に対しplaylistは3件返った。これはこの標本での索引欠落補完であり、全新着・遅延時間・最新タグの保証ではない。

最初の取得では、診断コードが個別対照成功後にしかowner比較を記録しなかったため、thumbinfoの406でprimary観測を失った。保存済みの最初の3件返却数を保持し、比較未保存を後から捏造しない。コードを修正し、同じ3動画を検索とplaylistで対にして再取得した理由はこの証拠欠落の補完。再比較は全3件のID/type一致を記録した。

thumbinfoのAcceptをapplication/jsonからapplication/xmlだけに変えた1回の対照も、同じ406・同じbody hashとなった。したがって「Acceptだけを変えれば解消する」という仮説は支持されない。watchページの`?responseType=json`も別1 GETで406。406の原因は未解決で、廃止・一般会員制限・CORS失敗とは断定しない。自動再試行なし、以後の個別対照は停止した。

新着のownerが返ったことと、検索経路との整合性はCONFIRMED-LIVE。独立視聴情報による現在値照合はFAILED/未確認。以前のR21でthumbinfoと2/2一致した結果を新着3件へ一般化しない。

## R24：型付きIDが必要

06:09:25、`filters[channelId][gte]=1`等を含むsnapshot要求は400 QUERY_PARSE_ERROR。要求全体の失敗を記録し、単一parameterの非対応を断定しない。06:10:11、研究用アニメタグの通常検索10件からchannelIdあり2件（so30413239、so23335421）を選び、sm9と混在させた。

playlistは3/3を返し、owner typeはchannel/channel/user、全てvisible、IDあり、tag系項目なし。snapshotのchannelIdとplaylistのowner.idは表記が異なり、型がchannelと確認できた2件についてだけ`ch`付き数字と数値の対応が一致した。user名前空間とchannel名前空間を混同しない。

証拠の`tag_seed_and_batch.success=false`は厳密な文字列一致を成功条件にした診断の結果。検索とPOSTはいずれもHTTP200であり、API呼出し失敗という意味ではない。hidden、公式全種別、数字のみwatch ID等は今回未検証。

## R25：返却集合を必ず照合

06:10:51〜06:11:39、条件ごとの4 POSTのみ。上表の400全体失敗、重複返却、200部分返却を分ける。欠落はowner不明のまま残し、NG非該当・削除済み・空タグへ変換しない。要求前のID検証・重複除去、応答watchId集合の照合が必要。別名watchId/content.idの完全な対応仕様は未確認。

証拠の`success=true`は観測収集が終わったという意味で、全ケースのHTTP成功ではない。sm0とsm1は条件の異なる公開形式IDであり、ゼロIDへの400を全欠落動画へ一般化しない。

## 通信量・性能・再現

R23 10通信、R24 3通信、R25 4通信、合計17（GET10、POST7）。HTTP200は11、400は3、406は3。失敗も数に含めた。大規模再取得なし。時間は単発の壁時計計測で速度保証ではない。

| 要求 | 指定→返却 | 応答bytes | ms |
|---|---|---:|---:|
| R23 最初のplaylist | 3→3 | 4409 | 130.46 |
| R23 owner比較用playlist | 3→3 | 4409 | 408.83 |
| R24 channel混在 | 3→3 | 5084 | 176.90 |
| R25 重複 | 2→2行/1動画 | 3193 | 158.88 |
| R25 欠落 | 2→1 | 1672 | 380.96 |

既知100件の性能は[前回資料](PLAYLIST-REQUEST-BULK.md)を参照。今回rate limit、キャッシュ有効期限、ページ分割、最大件数を測っていない。

```sh
# 通信なしで使用法・条件を確認
python tools/probe_playlist_new_uploads.py --help
python tools/probe_playlist_edge_cases.py --help
# 明示的な再現時のみ実通信。新着は最大8、channel最大2、mixed最大3、availability1通信
python tools/probe_playlist_new_uploads.py --live --output <sanitized-summary.json>
python tools/probe_playlist_edge_cases.py --case channel --live --output <sanitized-summary.json>
python tools/probe_playlist_edge_cases.py --case mixed --live --output <sanitized-summary.json>
python tools/probe_playlist_edge_cases.py --case availability --live --output <sanitized-summary.json>
```

新着は変動するので動画と条件を再確認する。少数でも意図せず繰り返さない。失敗時は停止し、未確認項目をnull/unknownで残す。再現成功条件はHTTPだけでなく対象ID・件数・owner項目・比較可能性を含む。診断コードの合成2テストは「406でも主観測を失わない」「XML Acceptを使う」を検証するもので、実サーバー406の解消を示さない。

最終レビューで第3の合成テストを追加し、検索とplaylistで同じ数字でもuser/channelが違えば成功にしないことを確認。型比較も個別対照より前に保存する。全診断テストは既存分を含め9件成功。

## 終了判断・訂正履歴

2026-09-20：R23は索引欠落補完と同系統整合性まで、独立対照の失敗を残して終了。R24はID表記差、R25は部分返却等を確認して終了。NG実装判断に必要な新条件を得たため、最大件数探索・406反復・hiddenの無作為探索は行わない。[更新着手の判断](NG-UPDATE-READINESS.md)へ引き渡す。タグ鮮度・実ブラウザ・サーバー保持は引き続き未確認。
