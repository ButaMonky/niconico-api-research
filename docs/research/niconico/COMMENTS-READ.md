# nvcomment：コメント取得の要求・応答構造

R12、確認日2026-09-20 JST。**現行系として保存された100成功要求と、今回revisionを固定したOSSから、1種類の取得経路を整理した。新規ニコニコ通信は0。** 本日の実サイト再現、全件回収、投稿、描画の検証ではない。NG/Zenza本体の変更・Zenza固有解析は行っていない。

## 根拠と今回増えたこと

- [既存記録の安全な再集計](evidence/nvcomment-historical-structure-20260920.json)：2026-09-14の既存集計を使い、100成功（Web76/iOS24）、38,635コメント要素（重複込み）、空コメント応答17を確認。生通信やキー値は今回読んでいない。
- Web76件は`text/plain;charset=UTF-8`、iOS24件は`application/json`。どちらもJSON本文で、全100件に非空threadKeyが記録されている。CookieなしのWeb要求を「キーも認証情報も不要」と読み替えない。
- 応答の`data.voltageZone`という項目名は55/100に存在した。内容・意味・任意性の仕様は未確認。古い一覧のglobalComments/threadsだけで網羅済みとしない。
- [固定OSSの読解](evidence/nvcomment-fixed-sources-20260920.json)：yt-dlpの保存配列、nndownloadの保存JSON、niconicojsの戻り値はそれぞれAPI応答を変換したもの。親thread/forkや件数の意味を引き継がず再利用すると情報を失う。

過去の100成功を新規100通信として数えない。以前のyt-dlp/nndownload参照はmaster未固定だったため、今回の差を「ソフト更新で変わった」と断定するcommit間比較はできない。今回初めて版を固定して読み分けた箇所を記録する。

## 取得経路

1. 視聴情報の`comment.nvComment`から`server`、`params`、`threadKey`を取得する。既存38モデルにこの構造がある。ただしwatchとコメント要求のキー・対象を1対1で照合した記録ではない。
2. `server`を信頼できる視聴情報から受け取り、`/v1/threads`へJSON本文をPOSTする。既存100要求のhostは`public.nvcomment.nicovideo.jp`。yt-dlp/nndownloadもserver値を使う。
3. `meta.status`と返却構造を検査し、`data.threads[]`ごとに親id/forkとcommentsを保持する。空commentsと要求失敗を区別する。

```yaml
endpoint: https://public.nvcomment.nicovideo.jp/v1/threads
method: POST
client: [web, ios, public-client-code]
status: CONFIRMED-LIVE (historical records); CONFIRMED-CODE (pinned sources)
checked_at: 2026-09-20
last_live_evidence_review: 2026-09-14
authentication: threadKey present in all 100 records; current guest login conditions unverified
request:
  body_format: JSON
  fields: [params.targets, params.language, threadKey, additionals]
response:
  fields: [meta.status, data.globalComments, data.threads, data.voltageZone]
batch:
  multiple_targets: supported in recorded request structure and code
  arbitrary_multiple_videos: unverified
  max_targets: unverified
new_niconico_requests: 0
```

この日付は保存証拠を照合した日であり、100要求全ての実行日を本日に置き換えない。過去iOS資料の対象版は12.37。公開Python/TypeScript実装は後述commit、公式アプリの現行バージョンを意味しない。

## 要求の最小構造

```http
POST /v1/threads HTTP/1.1
Host: public.nvcomment.nicovideo.jp
Content-Type: text/plain;charset=UTF-8
X-Frontend-Id: 6
X-Frontend-Version: 0

{
  "params": {
    "targets": [{"id": "<THREAD_ID>", "fork": "main"}],
    "language": "ja-jp"
  },
  "threadKey": "<THREAD_KEY>",
  "additionals": {}
}
```

これは合成した構造例。プレースホルダーのまま送信しない。対象は正当に得たwatch.paramsから引き継ぎ、キーを別動画や別forkへ任意流用しない。R12では送信しない。

| 項目 | 根拠・扱い |
|---|---|
| Content-Type | 過去Webはtext/plain、iOSはapplication/json。JSON本文なのにtext/plainであることだけで誤りと判断しない |
| X-Frontend-Id / Version | yt-dlp/nndownloadは6/0。存在するコードの値であり、全クライアント共通の必須値と検証したわけではない |
| Origin / Referer | yt-dlpはニコニコWebを指定。nndownloadのこの関数には同じ明示指定なし。セッション全体の挙動・ブラウザCORSは未検証 |
| X-Client-Os-Type | 両Python実装のコメントPOSTはothers。過去queryには_clientOsType/pcという名前もあるが、その値や必須性は今回は保存・検証しない |
| Cookie | 過去Web76はなし、iOS24はあり。キー発行元のログイン状態や一般会員条件はこれだけでは分からない |
| threadKey | 秘密の一時キーとして扱い、値・JWT payload・ログを保存しない。postKey、旧flapiキーとは別概念 |
| additionals | 通常例は空。when/res_fromを使う履歴処理はR13へ分離 |

キーを更新するコード上の候補は`GET https://nvapi.nicovideo.jp/v1/comment/keys/thread?videoId=<VIDEO_ID>`、応答`data.threadKey`。nndownload/niconicojsで確認。今回発行しておらず、有効期限・ゲスト条件・一般会員条件・更新上限は未確認。postKeyは読み取り例へ混ぜない。

## 応答・項目の読み方

| 階層・項目 | 再利用上の意味と証拠の限界 |
|---|---|
| meta.status / errorCode | HTTP成功だけでなく本文状態も扱う。100保存要求はHTTP/本文200。エラー分岐はOSSコード確認のみ |
| data.globalComments | スレッド別の件数情報を持つ配列というGist/型定義。nndownload保存版の同名objectと区別 |
| data.threads[].id / fork | 親スレッドと分類。id単独でforkまで表せると仮定しない。main/owner/easyは公開資料・型のラベル |
| commentCount | その応答のcomments.lengthや全回収件数と同一と保証しない |
| comments[].id / no | コメント識別子と番号。型宣言のidはstring。数値に丸めず保持する設計を推奨。実通信の値型分布は既存集計にない |
| vposMs | 表示時点のミリ秒値という公開資料・型。旧vposはセンチ秒という報告なので、変換する場合は×10。ただし由来不明データを推測変換しない |
| postedAt | 投稿時刻。表示時点vposMsと別。単位・timezone・境界処理は入力仕様に従い、過去ページ送りはR13 |
| body / commands | 本文とcommand配列。commandsの型はstring[]。共有資料へ実本文を保存しない |
| userId | コメント投稿者の識別値。動画のowner.idへの変換根拠はない。匿名/実名の判別や人物同定を推測しない |
| isPremium / isMyPost | プレミアム属性・自己投稿を示す名前の項目。現行セッションごとの意味は未検証。isMyPostはOSS型では任意 |
| nicoruCount / nicoruId | 件数と別識別値。nicoruIdのnullable型はコードで確認。自己ニコるとの関係・形式説明はGist報告で、今回の実再現なし |
| score / source | 項目名は過去非空83応答に存在。sourceのtrunk/nicoru/leafの意味はGist報告で、今回値を再集計していない |
| data.voltageZone | 55応答に項目名あり。未解釈の追加フィールドとして保存し、commentsやforkへ混ぜない |

過去非空83応答のcomment項目名集合はbody/commands/id/isMyPost/isPremium/nicoruCount/nicoruId/no/postedAt/score/source/userId/vposMs。これは各コメント全ての型・非null・必須性の保証ではない。応答thread数は3が93件、4が7件。4を任意4動画一括成功とは解釈しない。

親情報が必要な利用では`thread.id`、`thread.fork`、コメントid/noを一緒に保持する。コメントidの全域一意性、fork間のnoの重複許可は未検証なので、独自の一意性を仮定しない。

## OSSの通信と出力を分離する

| 固定実装 | 取得の単位 | 戻り値・保存形式 | 利用時の注意 |
|---|---|---|---|
| yt-dlp `_get_subtitles` | watchのparamsをそのまま渡す1 POST | threads内のcommentsを単一配列にまとめた字幕JSON | 親thread/forkが出力に付け足されない。投稿者コメント等を区別したい場合に配列だけでは不足し得る |
| nndownload `download_video_comments` | targetごとにworker。各POSTのtargetsは1要素、履歴ループあり | 独自globalComments object、threadごとのretrievedCount等を追加 | 保存件数はクライアント集計。APIからそのまま返ったフィールドと扱わない。初回だけでもtarget数分のPOSTになり得る |
| niconicojs `fetchCommentsWithKey` | 指定targetsを1 POSTへまとめる | CommentThread[]を返す | globalComments等の外側は戻り値に含まない。fetchAllCommentsとは返却・通信量が別 |

公開コードの複数target指定は任意動画横断の許可を証明しない。source keyの許可範囲が未確認であり、NGの動画タグ・投稿者一括APIとして転用する根拠もない。

3 targetを渡す場合、yt-dlpの当該関数は通常1 POST、nndownloadの初回は3 POSTという**コード上の計算**。ライブラリ全体のwatch・認証・retry等は別で、今回の性能実測ではない。保存100要求の応答サイズ・時間はこの集計に残っていない。最大件数・rate limit・キャッシュ可能時間は未確定。

## 旧例・失敗・過去ログ・投稿・描画の境界

otya128のGistは本文に2022年の観測を含み、2026年の最終活動日を全文の更新日としない。例のhostは`nvcomment.nicovideo.jp`、targets/languageは直下。現在系の保存記録と固定OSSで確認したparams階層へ、そのまま古い例を混ぜない。旧hostが現在廃止されたとの試験はしていない。`nv-comment.nicovideo.jp`の有効性も今回は確認していない。

nndownloadにはEXPIRED_TOKENでキー更新、INVALID_TOKENで中止、TOO_MANY_REQUESTSで待機する分岐がある。待機60秒・間隔1秒・既定1000件はライブラリ定数で、サービス公式制限ではない。`--all-comments`という名前は完全回収の証明ではない。niconicojsのゲスト過去ログ制限のメッセージも作者側の解釈であり、R13で別途根拠を確認する。

R14候補としてniconicojsに`GET /v1/comment/keys/post?threadId=...`と`POST /v1/threads/{threadId}/comments`がある。コード確認だけで今回送信なし。postKey/body/vposMs/commandsを使う構造は投稿資料で改めて整理する。

R15へ引き継ぐcommand調査項目はue/shita/naka、big/medium/small、色、フォント、改行・衝突・表示時間。R12で確認したのはcommand配列までで、描画効果・公式互換・コメントアート再現は未検証。未知commandを削除する仕様や、未知forkをmainへ丸める一般則を導入しない（niconicojsのnormalizeFork既定値はそのライブラリ実装）。

## 再現条件と安全な引き継ぎ

現在の実通信を行う将来の担当者は、正当に取得した1動画のwatch情報をメモリ内だけで使用し、server/params/threadKeyを組み合わせて1 POSTから始める。公開するのはHTTP/本文状態、フィールド名、thread数、コメント数、時間・bytesと必要な等値結果だけ。キー、Cookie、コメント本文、userId、thread IDの実値を出力しない。レスポンスをそのままdumpする既存ダウンローダーを診断器として無設定で実行しない。

成功条件はHTTP/本文200、data.threads配列、各親情報とcommentsの対応。空commentsでも構造成功になり得る。キー失敗・HTTP失敗では停止し、無期限再試行・大量過去ログ取得をしない。今回この実通信手順を実行したとは記録しない。

## 固定出典

- yt-dlp contributors：[niconico.py](https://github.com/yt-dlp/yt-dlp/blob/c7fb478d21e9e59524befbe23f7801bb267fb880/yt_dlp/extractor/niconico.py#L534)、commit `c7fb478d21e9e59524befbe23f7801bb267fb880`。要求・字幕変換。
- AlexAplin and contributors：[nndownload.py](https://github.com/AlexAplin/nndownload/blob/7a9b6a68980ca5e9558df346468fff1a9a1b663a/nndownload/nndownload.py#L1995)、commit `7a9b6a68980ca5e9558df346468fff1a9a1b663a`。要求・worker・保存形式・キー更新。
- otya128：[nvcomment Gist](https://gist.github.com/otya128/9c7499cf667e75964b43d46c8c567e37/755bb1f4b4a7152ec80518d11d030837d6d6ab85)、revision `755bb1f4b4a7152ec80518d11d030837d6d6ab85`。旧例・項目の意味。APIが返したfile raw revisionは別値なので台帳に両方記録し、このrevision URLを実取得したhashを保存。
- kongyo2 and contributors：[comments.ts](https://github.com/kongyo2/niconicojs/blob/e15fc91920567804685a6c45ebc08c2a8639f52e/src/comments.ts)、commit `e15fc91920567804685a6c45ebc08c2a8639f52e`。R03で固定済みの版を再利用し、最新HEADと主張しない。

全て2026-09-20確認、ファイル別hash/取得時刻/参照行は[台帳証拠](evidence/nvcomment-fixed-sources-20260920.json)。外部コードを実行・製品へ導入せず、共有版には転載しない。既存歴史集計の出典hashも保存し、旧資料を削除しない。

## 終了条件と次

R12は要求・応答・出力変換の区別を整理できたので終了。現在の実通信成功は未確認のまま。次はR13で過去ログのwhen/キー条件を1つ選び、まず既存記録と固定コードから範囲を絞る。投稿・描画・全件回収を同時に進めない。
