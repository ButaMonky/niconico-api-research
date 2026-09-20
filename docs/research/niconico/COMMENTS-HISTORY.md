# nvcomment過去ログ：whenの境界と停止条件

R13、2026-09-20 JST。主目的は**同じ投稿時刻がページ境界にある場合に、全件取得を保証できるか**。既存要求のローカル集計と、固定版公開コードの合成実行に限定した。新規ニコニコ通信0、キー発行0、投稿0。本体・Zenza固有コード変更なし。

## 結論

1. 既存の100成功要求はすべて`additionals: {}`。`when`も`res_from`も指定されていなかった。R12の成功記録は過去ログ取得・一般会員全件取得の根拠にはならない。
2. 合成した「whenと同秒のコメントを含める」サーバーでは、固定nndownloadは重複込み4件を保存して終了、固定niconicojsは重複を除いた2件で進展なしと判定し終了。両方とも古い2件へ到達しなかった。
3. 同じデータで「whenと同秒を除外する」条件では両方とも4件に到達した。つまり**境界の含み方を確認せず、件数や停止だけから完全取得と判定できない**。実サーバーの境界・並び順・会員条件は今回未確認。

`all-comments`という機能名や取得件数だけを完全性の根拠にする仮説は支持できない。ニコニコでこの欠落が実際に起きたという主張ではない。

## 既存100要求の適用範囲

[許可項目だけの集計](evidence/comment-history-capture-scope-20260920.json)は、以前の3通信記録をローカルで再読し、`POST public.nvcomment.nicovideo.jp/v1/threads`の要求本文だけから構造と件数を取り出した。再集計理由は、R12の集計にadditionalsの内訳がなく、通常取得と過去ログを区別できなかったため。応答本文・キー内容は解析対象にしない。

| 確認項目 | 結果 |
|---|---:|
| 対象POST / HTTP200 | 100 / 100 |
| additionalsが空object | 100 |
| when指定 / res_from指定 | 0 / 0 |
| 非空threadKeyの存在 | 100（値は保存しない） |

キャプチャ別は76/5/19件。2番目はブラウザというファイル分類でもiOS系User-Agentマーカーが5件含まれる。ファイル名で送信クライアントを決めない。マーカーとContent-Typeの集計は以前のWeb相当76・iOS相当24という内訳と整合するが、ログイン状態・会員種別まで証明しない。生のUser-Agent・Cookie・個人ID・検索語・本文は出力していない。

## 要求・応答とキー条件

取得の基本形は[COMMENTS-READ.md](COMMENTS-READ.md)を参照し、ここでは履歴条件だけを追加する。

```yaml
endpoint: https://public.nvcomment.nicovideo.jp/v1/threads
method: POST
status: CONFIRMED-CODE; SYNTHETIC pagination experiment
checked_at: 2026-09-20
authentication: threadKey required by examined clients; current guest/member history permission unverified
request:
  body: JSON
  fields: [threadKey, params.targets, params.language, additionals.when, additionals.res_from]
  when: Unix seconds (examined code)
  res_from: -1000 (client request value, not a verified server limit)
response:
  fields: [meta.status, meta.errorCode, data.threads[].comments, data.threads[].commentCount]
new_niconico_requests: 0
```

構造例は`{"threadKey":"<THREAD_KEY>","params":{"targets":[{"id":"<THREAD_ID>","fork":"main"}],"language":"ja-jp"},"additionals":{"when":1700000101,"res_from":-1000}}`。時刻とIDは合成例。正当なwatchデータとキーがないまま送信しない。Content-Typeやfrontend headerはR12を継承し、今回必須性を再検証していない。

`when`は投稿時刻の履歴境界で、動画内の表示時点`vposMs`ではない。nndownloadは返却先頭のpostedAtから秒を作り、niconicojsは返却batch内の最小postedAtを使う。先頭が最古という前提、秒境界の含み方、返却順は別の未検証条件である。

| 条件 | コード上の扱い | 今回の根拠の限界 |
|---|---|---|
| ゲスト＋when指定 | niconicojsはINVALID_TOKENかつwhen有り・isLoggedIn=falseならゲスト制限の説明を出す | メッセージ生成条件を確認しただけ。INVALID_TOKENの実原因、一般会員との差を実証しない |
| EXPIRED_TOKEN | nndownloadは`GET /v1/comment/keys/thread?videoId=...`で再取得して継続 | 更新成功、期限、再試行上限、会員条件は未測定 |
| INVALID_TOKEN | nndownloadは例外、niconicojsは状況依存の説明 | 「全部期限切れ」「必ず会員不足」と決めつけない |
| TOO_MANY_REQUESTS | nndownloadは定数60秒待機して再試行 | 公認レート制限・適切な待機時間の根拠ではない |
| 取得範囲 | niconicojsのeasy除外既定、round上限等はクライアント設定 | 設定付き終了を全fork・全履歴取得と呼ばない |

一時キーは不透明な値としてメモリ内だけで扱い、JWTを解読して認可範囲や有効期限を断定しない。旧キャプチャのキーは再送しない。現在の一般会員での範囲・ゲスト履歴の可否は未解決であり、今回不足しているのは現在の正当なキー/会員条件と、少数実測による境界の根拠。

## 固定コードを使った合成確認

入力は4件のみ。番号2/3がT−1秒、番号4/5がT秒。初回when=T+1、仮想ページ上限2件、仮想commentCount=4。対象スレッド1個、返却ページ内は番号昇順。本文・userIdは使用せず、キーはプレースホルダー。

| 固定コード | 仮想when境界 | mock POST数 | 保存行数 | 異なるコメント | 未到達 |
|---|---|---:|---:|---:|---:|
| nndownload | 同秒を含む | 2 | 4 | 2 | 2 |
| niconicojs | 同秒を含む | 2 | 2 | 2 | 2 |
| nndownload | 同秒を除外 | 2 | 4 | 4 | 0 |
| niconicojs | 同秒を除外 | 3 | 4 | 4 | 0 |

含む場合は最初と次のページが同じ2件になる。nndownloadの関数はextendした件数で進捗が合計4に達し、模擬progressが完了となる。重複除去はこの関数にはない。niconicojsは同じキーをMapに上書きしてunique2を保つが、最小noが進まないので、その時点で終了する。while/forの終了を完全性の証明にしてはいけない。

除外の場合に4件へ到達したことも、全データでの保証ではない。特に**同じ秒のコメントがページ上限を超える場合、単純にwhenを1秒戻す修正では、その秒の未取得分を飛ばす可能性がある**。これは境界情報不足からの仮説であり、今回実サービスやその追加fixtureを試験していない。

結果・出典hash・制約は[合成証拠](evidence/comment-history-offline-20260920.json)。Pythonはhash固定のfetch_comments_thread関数だけをAST抽出して実行し、外部module全体をimportしない。Node.jsはhash固定のTypeScriptを型除去し、importを除いたVMへ偽HTTPを渡す。両方とも実ネットワーク・ログイン・動画DL・ライブラリのファイル保存処理は実行しない。

## 再現手順と測定の限界

R12の固定URLからソースを別途用意し、次を実行する。外部ソース自体は本資料集に同梱しない。診断はhashが違う版を拒否する。Python標準ライブラリと、JS側はNode.js24を使用。API認証不要、通信0。

```sh
python tools/probe_comment_history_offline.py <pinned-nndownload.py>
python tools/probe_comment_history_js.py <pinned-comments.ts>
```

成功条件は表の4ケースの件数とカーソル列が合成期待値に一致すること。仮想呼出しは合計9で、ニコニコへの通信回数には数えない。ページ上限2はfixture設定。実レスポンスbytes・応答時間・上限・サービスrate limit・キャッシュ可否は未測定。合成実行時間から性能改善を推定しない。

実装担当へは、要求回数・返却行数・unique件数・重複件数・最古時刻/番号の進展・終了理由を分けて記録する設計を推奨する。停止理由は空ページ、進展なし、上限、認証失敗、利用者中断等を分け、全履歴完全性を別状態にする。これは設計提案で、本体には実装していない。

## 出典・変更履歴・終了判断

作者AlexAplinほか：[nndownload.py](https://github.com/AlexAplin/nndownload/blob/7a9b6a68980ca5e9558df346468fff1a9a1b663a/nndownload/nndownload.py#L2071)、commit `7a9b6a68980ca5e9558df346468fff1a9a1b663a`、2064〜2137行。作者kongyo2ほか：[comments.ts](https://github.com/kongyo2/niconicojs/blob/e15fc91920567804685a6c45ebc08c2a8639f52e/src/comments.ts#L246)、commit `e15fc91920567804685a6c45ebc08c2a8639f52e`、246〜310行。R12の固定ファイルをhash照合して再利用。最新版への追従を主張しない。今回Web表示ツールの固定URL取得はcache missだったが、保存済みソースのhashは一致した。

2026-09-20：R12の「100成功」が過去ログの証拠ではないことを新たに確認し、既存資料を消さず範囲を明記。固定コードの4合成条件を追加。一般会員/ゲストと実サーバー境界は未解決のまま、今回の1単位は終了。次はR14の投稿要求を公開コードから整理する。実投稿や大量過去ログ取得は行わない。
