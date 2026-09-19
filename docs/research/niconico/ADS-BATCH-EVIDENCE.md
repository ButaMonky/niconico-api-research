# R11：広告一括APIの指定数・返却数・根拠

確認：2026-09-20 JST。今回の広告API通信は0件。本体変更なし。過去記録・提供報告の比較であり、現在の再現確認へ格上げしない。新しい取得経路の探索は[Zenzaのnvapi・キャッシュ](ZENZA-NVAPI-AND-CACHE.md)へ分離した。

## 結論

**80件は過去の全返却実測、100件は一部返却の報告、600件は要求成功の報告。最大取得件数を表す共通の指標ではない。** `decoration` の確認済み応答項目は広告ポイントと装飾で、タグ・投稿者の一括補完には転用できる根拠がない。

| 条件 | 指定・返却 | 原根拠と区分 | 判断できないこと |
|---|---|---|---|
| 2026-09-13 Web記録 | 80個の異なるID → 80件、HTTP200 | 過去通信を項目限定抽出した記録を今回再集計。69成功GET中の最大。今回の新規CONFIRMED-LIVEではない | 上限80、認証不要、現在も同じか |
| 同じ記録 | 14指定 → 12返却、HTTP200 | `4490-meta.json`由来。欠落2件、原本文は非公開 | 欠落原因、広告履歴なしとの同値性 |
| 2026-09-17提供報告 | 100指定 → 62返却、HTTP200との報告 | REPORTED。提供finding `NICO-WEB-20260917-PAGESIZE-100`。R02で入力hash確認、原通信未独立照合 | 指定IDの実在・重複、欠落38件の原因、上限62 |
| 2026-09-12提供報告 | 600指定 → 成功との報告、返却数不明 | REPORTED。別AIの報告・5件のJSON例。原要求、HAR、応答ヘッダーなし | 600実在動画の全取得、サーバー上限 |
| 同じ提供報告 | 700指定 → `Failed to fetch`、HTTP状態不明 | REPORTED。失敗時のネットワーク記録なし | HTTPエラーか、CORS・ネットワーク・URL長等のどれか |

600/700は`sm1`からの連番で非存在動画を含む。80件の実在する異なるIDとは条件が違う。100件報告も実在・重複条件が未照合なので、80件の記録と矛盾すると判断しない。既存の「600成功・700失敗」記述は削除せず、この限定を付けて読む。

## endpoint単位の契約

```yaml
endpoint: https://api.nicoad.nicovideo.jp/v1/contents/video/decoration
method: GET
client: [web]
status: historical-traffic-and-REPORTED
reviewed_at: 2026-09-20
first_confirmed: 2026-09-13 # 保持している独立通信記録の日付
last_confirmed: 2026-09-13 # 今回は原通信の新規取得なし
authentication: unresolved
request:
  query: "ids=<VIDEO_ID_1>,<VIDEO_ID_2>"
  body: none
response:
  items: data.contents
  fields: [id, activePoint, totalPoint, decoration]
batch:
  supported: true
  historical_max_unique_input: 80
  historical_max_returned: 80
  server_limit: null
```

- `nvapi.nicovideo.jp`とは別ホスト。個別の`GET /v1/contents/video/{id}`で報告・確認されたownerId/tagsを、この一括APIにもあると推定しない。
- 過去のGETにはCookieあり。Originは`https://www.nicovideo.jp`、`x-frontend-id`・`x-frontend-version`・`content-type`を観測し、OPTIONSも別途存在。各headerが必須かを除外試験していない。Cookie等の値は保存しない。
- 100件および600/700の`credentials:omit`成功は提供報告。原ヘッダーを確認していないため、今回の認証なし実測や一般会員条件の確認とは異なる。
- `ids[]`形式はHTTP400 / `NICOAD_14_1`との報告のみ。今回再送していない。
- `decoration`はnormal/silver/goldを観測。normalでtotalPointが正の過去記録もあり、normalを広告履歴なしと読み替えない。
- 入力と返却はidで照合し、欠落はunknownとする。返却順の一般保証、ページ分割、レート制限は未確定。

## URL長と性能の評価

以下は公開endpointに合成IDを連結した**通信なしの計算**。成功率や原因を測った表ではない。

| 指定条件 | カンマをそのまま使用 | カンマを%2Cへ符号化 |
|---|---:|---:|
| 36個、各10文字 | 460 bytes | 530 bytes |
| 100個、各10文字 | 1164 bytes | 1362 bytes |
| sm1〜sm600 | 3556 bytes | 4754 bytes |
| sm1〜sm700 | 4156 bytes | 5554 bytes |
| 600個、各10文字 | 6664 bytes | 7862 bytes |

旧レビューの「10文字×36件=456文字」は後続資料で訂正済み。ここでも460を採用し、旧資料の履歴を保持する。ID長・符号化が違えば、件数だけではURL長を比較できない。「4096上限」「500件なら安全」は否定された事実ではなく、**裏付けのない仮説として採用しない**。

広告80件の集計では1 GETで全返却した例があるが、事前OPTIONSの有無でブラウザの実通信本数は変わる。応答時間は[証拠JSON](evidence/ads-batch-review-20260920.json)の選択行に保持し、回線・キャッシュ条件が違うため他方式の速度優位を主張しない。原記録の応答サイズは今回の集計対象にない。観測ヘッダーはno-cache/no-store系で、サーバーの長期キャッシュ保証はない。

100動画のタグ・投稿者取得では、このAPI1回から必要項目を得た証拠がない。既存のsnapshot100件1 GET、取得済みownerの再利用、必要時の単独情報取得という比較を維持する。装飾API失敗時に大きなバッチを再送せず、表示上unknownを保持する候補とする。

## 根拠・終了条件・訂正履歴

[集計証拠](evidence/ads-batch-review-20260920.json)に入力ファイルhash、80件と欠落例の匿名化項目、100件報告の抽出、600/700の不足資料を保存。100件の提供ZIP・member hashは[R02証拠](evidence/community-metadata-review-20260920.json)へリンクして重複を抑えた。原HAR等は配布しない。hashは入力同一性の識別用で、非公開原記録の独立追試を可能にするものではない。

2026-09-20：R11を根拠比較の範囲で終了。最大件数・失敗原因を決めるための原要求/返却集合/HTTP状態が不足。通信削減の主目的に必要なtags/ownerがないため、大量の境界再通信は行わない。新規metadata候補を優先する。
