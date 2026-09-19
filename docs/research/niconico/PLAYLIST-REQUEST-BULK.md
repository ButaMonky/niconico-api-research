# 任意動画IDから投稿者を一括取得：playlist/request

確認：2026-09-20 05:31〜05:33 JST、R21。**匿名の1 POSTで指定した2動画の情報・投稿者IDを両方取得できた。別の要求では投稿者IDと種別をgetthumbinfoと比較し、2/2一致した。** タグは返ったcontentオブジェクトにない。任意ID集合の投稿者補完として新しい実通信結果だが、100件対応・最新値の全面保証・実装採用決定ではない。

## 要求と応答

```yaml
endpoint: https://nvapi.nicovideo.jp/v1/playlist/request
method: POST
client: [direct-http, web-form-contract]
authentication: none-in-this-test
status: CONFIRMED-LIVE
first_confirmed: 2026-09-20
last_confirmed: 2026-09-20
request:
  content_type: application/x-www-form-urlencoded
  fields:
    title: "Metadata research"
    watchIds: "sm9,sm15630734"
response:
  items: data.items
  item_fields: [watchId, content]
  owner: data.items[].content.owner
  owner_fields: [ownerType, type, visibility, id, name, iconUrl]
batch:
  supported: true
  max_confirmed: 2
  server_limit: null
limitations:
  - no tags/tag field in examined content objects
  - general-member login and browser CORS not tested
  - no independent proof of server-side non-persistence
  - hidden/channel/deleted/shorts cases untested
```

headerは`Content-Type: application/x-www-form-urlencoded`、`Accept: application/json`、`Accept-Encoding: identity`、`X-Frontend-Id: 6`、`X-Frontend-Version: 0`、`X-Request-With: https://www.nicovideo.jp`、`Origin: https://www.nicovideo.jp`、調査用User-Agent。Cookie、Authorization、一時キーなし。各headerの必要性を個別に除外試験していない。

queryなし。bodyはフォーム符号化されたtitleとwatchIdsのCSV。JSON形式・配列形式・title省略は試していない。URL長にIDを載せるGETとは異なるが、body上限は未確認。

応答は`meta.status=200`、`data`にid/items/meta/totalCount。data.idはオブジェクトで、値は保存していない。data.metaにはownerName/titleがあるが値を転載しない。contentには動画概要、owner、count、thumbnail、duration等がある。名前やサムネイルが返ることと、それを公開資料へ配布する必要があることは別なので、証拠にはキー名・件数・一致だけを保存した。

## 実通信の結果と精度確認

| 試験 | 指定→返却 | 応答 | body bytes / 時間 | 根拠 |
|---|---|---|---|---|
| 初回POST | sm9、sm15630734の2→2 | HTTP/meta 200、両方owner IDあり | 3451 / 205.90 ms | 項目・ID対応を集計 |
| 精度確認POST | 同2件を逆順で2→2 | HTTP/meta 200、逆順指定と同じ順で返却 | 3451 / 373.01 ms | content.id/watchId対応2/2 |
| getthumbinfo制御1 | sm15630734 | HTTP200、status=ok | 2266 / 488.21 ms | 投稿者ID/type一致 |
| getthumbinfo制御2 | sm9 | HTTP200、status=ok | 1497 / 409.85 ms | 投稿者ID/type一致 |

計4通信、再試行0。初回は投稿者値を保持せず存在だけを集計したため、**新取得元の正確性確認**を理由に2回目のPOSTと2制御を同一処理内で比較した。既知の件数境界を再試験したものではない。両動画は公開・古い通常ユーザー動画、owner.type=user。名前の一致・hidden・チャンネル・削除・非公開動画は試していない。一般会員ログイン条件でもない。

getthumbinfoとの同時期一致は、動画視聴ページ等すべての取得元との正しさを証明しない。今回tags/tagフィールドは両contentにない。thumbinfoにはタグがあるが、この一括応答からのタグ取得には成功していない。結果順は今回の2要求での観測に限り、実装ではwatchId/content.idで照合する。

上記は1回ごとのネットワーク条件込みの時間で、速度の統計・優劣の証明ではない。Accept-Encoding=identityで読んだ応答本文サイズ。ブラウザなら独自header等でOPTIONSが増える可能性があり、通信1回の表現は直接HTTPのmetadata POSTについて。pagination・レート制限・キャッシュ保証・最大件数は未確認。

## 副作用と認証の限界

既存の公式Web静的記録では、`request`型の再生リスト取得分岐がtitle/watchIdsをこのPOSTへ渡して応答を返す。Androidにも応答itemsからcontent.ownerを読む経路がある。マイリスト保存操作を呼んだわけではなく、今回はCookie等を付けない少数の情報取得要求として実行した。

ただし、**非永続・完全に副作用なしと実証したわけではない**。data.idの存在だけで保存リスト作成とも断定しない。サーバーの一時保持・記録・リスト寿命は不明。ユーザーのマイリスト等の状態変更を調べるための認証通信は行っていない。大規模利用の前にこの条件を確認する。タイトルを送れるからといって個人情報をbodyへ含めない。

## NG・Zenza向け比較

| 必要な情報 | 確認した方法 | 通信と限界 |
|---|---|---|
| 画面・Zenzaキャッシュに既にあるowner | 既取得データの再利用候補 | 追加0の設計候補。実環境・ID対応・鮮度条件は別 |
| 任意の2動画のowner | 今回のplaylist/request | 1 POST、2件を返却。最新側の補完候補だが上限・特殊動画条件は未確認 |
| 任意100動画のtags/投稿者 | 既存snapshot | 1 GETを確認済み。索引欠落・最新タグとの差あり |
| 必要対象のtags/owner | 個別thumbinfo等 | 対象ごとに通信。欠落する投稿者や現在値の限界は既存資料を参照 |

100動画についてplaylist/requestが1回で完了すると外挿しない。R22で確認する価値がある。タグだけが未知ならこのAPIを追加で呼んでも今回の応答項目では解決しない。既取得ownerを先に保持し、必要項目とソースごとのunknownを分ける。

fallback候補は既取得情報→必要なownerだけplaylist/request→失敗・欠落時はsnapshotまたは個別情報。最新タグが必須なら別の個別確認が必要。欠落をNG非該当にしない。本体実装はこのworkでは行っていない。

## 根拠と再現方法

- [匿名化証拠](evidence/playlist-request-20260920.json)：要求の非秘密項目、応答hash、2回の指定数/返却数、投稿者ID/typeの比較結果。値・生本文・コメント本文・playlist ID実値を配布しない。
- 旧静的根拠：`NICO-20260913-PLAYLIST-OWNER`（Android 9.14.0(471)）と`NICO-FOLLOWUP-20260913-PLAYLIST-FORM`（2026-09-13 Web asset）。元findingを削除せず、入力hashと必要な契約だけ今回の証拠に収録。
- [niconicolibs/apiの固定spec](https://github.com/niconicolibs/api/blob/7ee4782f7f4f7c351da4b00145b361291e22544a/spec/nvapi/nvapi.yaml)にはこのpathがなかった。固定ファイルhashは証拠へ記録。文書にないことを不存在とみなさず、既存静的根拠と今回の実通信を分離した。
- [最小診断](tools/probe_playlist_request.py)は標準では通信なし。`--live`指定で最大3通信（POST1、thumbinfo GET2）、異常時停止、認証・再試行・redirectなし。秘密値・生本文を保存しない。

```sh
python docs/research/niconico/tools/probe_playlist_request.py
# 実通信を意図して再検証するときだけ実行
python docs/research/niconico/tools/probe_playlist_request.py --live --output <summary.json>
```

2026-09-20：少数2件で一括取得と別取得元との一致を確認したためR21を一区切り。副作用・最大件数は未解決として残す。次は20件から必要に応じ100件までの限定した件数試験。既存2動画成功を漫然と繰り返さない。
