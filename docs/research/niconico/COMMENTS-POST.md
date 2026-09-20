# コメント投稿：キー・対象・認証・再試行

R14、2026-09-20 JST。固定版公開コードの投稿関数と共通HTTP処理を接続して整理した。**実投稿・キー発行・新規ニコニコ通信はすべて0**。本体・Zenza固有コードは変更しない。対象はniconicojs commit `e15fc91920567804685a6c45ebc08c2a8639f52e`であり、公式クライアントや現在のサービス全体の仕様とは扱わない。

## 結論と新しい確認

- 読取の`threadKey`と投稿の`postKey`は、取得時の対象パラメーターも送信先も異なる。投稿には`threadKey`を送らない。
- 投稿関数は`threadId`と`videoId`を別々に受け取り、`fork`引数を持たない。通常/投稿者/easyの投稿先や権限は、この関数だけでは判定できない。
- **投稿POSTは再試行しないが、キー取得GETとコメント取得POSTは再試行する**。固定HTTP処理まで含む合成実行で確認した。HTTP 200でも`meta.status`が403なら失敗。503では応答内の詳細エラーコードが呼び出し側へ残らない経路がある。

証拠は`CONFIRMED-CODE`と`SYNTHETIC`。`CONFIRMED-LIVE`ではない。「POSTならすべて同じ再試行」「HTTP 200なら投稿成功」「forkを渡せば投稿先が変わる」という扱いは、この固定コードに適用できない。

## キーと対象の区別

| 項目 | 読取 | 投稿 |
|---|---|---|
| キー取得 | GET `nvapi.nicovideo.jp/v1/comment/keys/thread?videoId=...` | GET `nvapi.nicovideo.jp/v1/comment/keys/post?threadId=...` |
| キーフィールド | `data.threadKey` | `data.postKey` |
| 利用先 | POST `/v1/threads`の`threadKey` | POST `/v1/threads/{threadId}/comments`の`postKey` |
| 対象 | `params.targets[]`に`id`と`fork` | URLの`threadId`と本文の`videoId`、forkフィールドなし |
| キー補完 | watch由来または専用GET。R12/R13参照 | `postKey`未指定/nullなら内部GET、指定済みならGET省略 |

`threadId`はString化してURL encode、`videoId`は本文へ渡す。投稿関数はwatchのresolverを呼ばず、thread/videoの対応やキーの紐付けを検証しない。forkを省略しているからmain固定、ownerへ自由投稿可能、easyと互換、といった結論は出せない。読取のmain/owner/easy一覧を、そのまま書込可能な対象一覧に変換しない。

両キー取得関数は応答のキーが`undefined`なら例外を出す。キー型・空文字・期限・権限を完全に検証する仕組みではない。一時キーは不透明な値として扱い、実値を保存しない。一般会員の書込条件は未確認。

## 要求と応答

```yaml
endpoint: https://nvapi.nicovideo.jp/v1/comment/keys/post
method: GET
status: CONFIRMED-CODE
checked_at: 2026-09-20
client: pinned niconicojs; official Web/iOS/Android unverified
authentication: optional session in library; service requirement unverified
request:
  query: [threadId]
response:
  fields: [meta.status, meta.errorCode, data.postKey]
```

```yaml
endpoint: https://public.nvcomment.nicovideo.jp/v1/threads/{threadId}/comments
method: POST
status: CONFIRMED-CODE; SYNTHETIC execution
checked_at: 2026-09-20
authentication: postKey supplied or fetched; login requirement unverified
request:
  content_type: application/json
  body: [videoId, body, commands, vposMs, postKey]
response:
  fields_read: [meta.status, meta.errorCode, data.id, data.no]
  library_return: [id, no]
batch:
  supported_by_examined_wrapper: false
new_niconico_requests: 0
```

本文の構造例（送信しない説明用）：

```json
{"videoId":"<VIDEO_ID>","body":"<SYNTHETIC_COMMENT>","commands":[],"vposMs":1000,"postKey":"<POST_KEY>"}
```

`body`はコメント本文、`vposMs`は動画内の表示時点をミリ秒で渡すフィールド。過去ログ境界`when`や投稿時刻`postedAt`とは別。`commands`は文字列配列を複製し、省略時は空配列。位置・サイズ・色・フォントのcommand許可リストや長さ・座標範囲を投稿関数は検証しない。無効値がサービスに受理されるという意味ではない。server側の上限や正規化は未確認。

ライブラリは`data.id`と`data.no`の存在（undefinedでないこと）を確認し、`{id,no}`だけ返す。API応答全体がこの2項目だけ、あるいは型まで厳格に保証される、とは言えない。追加フィールドを含む合成応答も戻り値では落とすことを確認した。

## 認証とheadersの範囲

既定の共通headersは`User-Agent`、`X-Frontend-Id: 6`、`X-Frontend-Version: 0`、`X-Niconico-Language: ja-jp`、`Referer: https://www.nicovideo.jp/`。投稿は`X-Client-Os-Type: others`と`Content-Type: application/json`を追加する。各headerのサービス必須性は未測定で、値もこのライブラリの既定値である。

`session`を設定した場合に共通HTTP処理がニコニコ系hostへ`Cookie: user_session=<USER_SESSION>`を付加する。投稿関数に事前の`isLoggedIn()`検査はなく、session未指定でも模擬送信まで進む。**これはゲスト投稿成功の証明ではない**。`isLoggedIn()`自体も設定値の存在判定であり、ログイン有効性の照会ではない。既定経路に明示的Authorization/Origin設定はないが、サービスが不要と断定できない。

Node等からCookie headerを構成するコードの観測であり、ブラウザJavaScriptで同じheader設定が可能という保証ではない。Cookie制約・CORS・credentials・一般/プレミアム・所有者権限、Web/iOS/Android差は今回未測定。

## エラーと再試行

8条件は実コードのcomments/http/errorsを組み合わせ、fetchだけを合成応答へ差し替えて実行した。Cookieとキーはプレースホルダー、本文・IDも合成値。出力は値そのものを含まず項目名・有無・件数・エラー分類だけ。

| 合成条件 | 仮想要求数 | 固定コードでの結果 |
|---|---:|---|
| postKey指定、sessionなし、追加fork引数あり | 1 POST | id/noだけ返る。Cookie/fork/threadKey送信なし |
| postKey未指定、合成sessionあり | 1 GET + 1 POST | キーGET後に投稿。両要求にCookie headerあり |
| 投稿HTTP503、詳細metaあり | 1 POST | NiconicoApiError、status503、詳細errorCodeは保持されない |
| 投稿fetchが通信例外 | 1 POST | NiconicoNetworkError、attempts1 |
| 投稿HTTP200、meta.status403/INVALID_TOKEN | 1 POST | NiconicoApiError、status403/errorCode保持。キー再取得なし |
| 投稿HTTP/meta200、dataにid/noなし | 1 POST | NiconicoError。成功応答として返せない |
| postKey取得GETが503→成功 | 2 GET + 1 POST | キー取得だけ再試行して、その後投稿1回 |
| コメント読取POSTが503→成功 | 2 POST | 再試行してthreads配列を返す |

仮想要求合計12、実通信0。`INVALID_TOKEN`はこのケースでは作成した入力であり、実際の投稿APIで観測したエラーではない。

共通HTTPの再試行許可は`idempotent ?? method === GET`。読取`postThreads`は`idempotent: true`を指定し、投稿`postComment`は指定しない。既定retryAttempts=3でも投稿のmaxAttemptsは1になる。HTTP408/429/5xxはJSON解釈より前に一時エラー扱いとなり、最終例外へstatusだけを渡す。今回その経路を503で合成確認し、408/429等はコード確認のみ。

読取の`ThreadKeyRejectedError`やゲスト過去ログ向け説明は、投稿のINVALID_TOKENへ自動適用されない。postKeyの自動更新・再投稿はこの関数にはない。HTTP非成功、JSON不正、meta欠落/エラー、必要項目欠落も区別する。タイムアウト・利用者中断の処理は共通コードにあるが今回の合成8条件には含めない。

固定コードの`COMMENT_RATE_LIMIT_MS=334`、timeout30秒、GET等のretryAttempts3はクライアント設定であり公認rate limitではない。診断では待機を即時化したので、実応答時間・サービス負荷・投稿間隔の実測値はない。

再利用設計への提案：通信断や不完全な成功応答は、サービスが未投稿だったことを証明しない。上位層が汎用再試行を追加すると二重投稿の可能性があるため、「失敗」と「結果不明」を分け、自動再送しない。投稿前の失敗であるキー取得GETとは分離する。これは設計提案で、本体には実装していない。

## 出典と再現方法

作者kongyo2ほか、[niconicojs](https://github.com/kongyo2/niconicojs)、固定commit `e15fc91920567804685a6c45ebc08c2a8639f52e`。確認日は2026-09-20、ファイルごとの取得時刻・SHA256は[固定出典](evidence/comment-post-fixed-sources-20260920.json)。comments.tsはR12の保存済み固定ファイルを再利用し、http/errors/testsは同commitの公開URLから追加取得した。最新HEADの確認や公式仕様追従を主張しない。

- [src/comments.ts](https://github.com/kongyo2/niconicojs/blob/e15fc91920567804685a6c45ebc08c2a8639f52e/src/comments.ts)：PostCommentParams、getThreadKey/getPostKey/postComment、読取postThreadsとの比較。
- [src/http.ts](https://github.com/kongyo2/niconicojs/blob/e15fc91920567804685a6c45ebc08c2a8639f52e/src/http.ts)：baseHeaders、request/getJson/sendJson、parseJsonResponse。
- [src/errors.ts](https://github.com/kongyo2/niconicojs/blob/e15fc91920567804685a6c45ebc08c2a8639f52e/src/errors.ts)：例外型とassertNvapiMeta。
- [test/comments.test.ts](https://github.com/kongyo2/niconicojs/blob/e15fc91920567804685a6c45ebc08c2a8639f52e/test/comments.test.ts)：投稿のmock成功テスト。実投稿試験として数えない。

上記の最初の3ファイルを別途取得し、Python標準ライブラリとNode.js24で実行する。外部ソースは資料ZIPに同梱しない。

```sh
python tools/probe_comment_post_offline.py <pinned-comments.ts> <pinned-http.ts> <pinned-errors.ts>
```

成功条件は8ケースの要求数・項目・エラーと自動assertが一致すること。hashが異なる版は拒否する。TypeScriptの型とimports/exportsを除いたVMで合成fetchを使い、実ネットワークを使うglobal fetchは禁止する。これはライブラリ全体の導入試験ではない。[実行結果](evidence/comment-post-offline-20260920.json)と[検証記録](VERIFICATION-R14-20260920.md)も参照。

## 未確認事項と終了判断

現行ログイン/一般会員条件、キー期限・紐付け、thread/forkの書込先選択、チャンネルや投稿者コメント権限、受理command・文字数・vpos範囲、投稿成功時の全応答構造・エラー一覧、公式クライアント差は未確認。今回実投稿しない方針のため、これらをサービス実証する根拠は不足している。

2026-09-20：R12/R13の読取資料を変更履歴として保持し、R14の投稿契約・HTTP連鎖を新規整理。投稿を読取と同じ認証/エラー/再試行で扱う仮説を固定コードの範囲で否定し、限定完了。次のR15は描画の固定版コードと合成コメントで1条件を調べる。実投稿・Zenza固有コードの調査は引き続き別扱い。
