# 外部資料台帳

確認日：2026-09-20 JST。既存の作者資料台帳はローカル正本の `evidence/community-sources-20260914.json` と `community2-public-sources-20260914.json` に残す。この台帳は取得revisionを固定した追加調査の入口。リポジトリ更新時刻と対象コードの現行動作を同一視しない。

| Source / Author | Revision / checked date | Category / state | 参照箇所・今回の所見 | Current verification |
|---|---|---|---|---|
| [公式スナップショット説明](https://site.nicovideo.jp/search-api-docs/snapshot) / ニコニコ運営 | 2026-09-20、HTML SHA256は証拠JSON | official documentation / REPORTED | endpoint、GET query、`_limit`最大100、`_offset`最大100000、タグ・userId・channelId | 100/101返却境界のみ今回CONFIRMED-LIVE。offset最大や更新周期は再現未検証 |
| [NicoApiClient](https://github.com/Javakky/NicoApiClient/tree/5190ad3b777b83f2f10bea2e1a8b40affebc9d96) / Javakky | `5190ad3b777b83f2f10bea2e1a8b40affebc9d96` / 2026-09-20 | public Python client / CONFIRMED-CODE | `nicovideo_api_client/constants.py`、`api/v2/limit.py`、`request.py`、`simple_filter.py`。添字付きフィルターと100件単位の分割 | コード未実行。独立GETで100/101境界と101 IDのページ送りを確認 |
| [非公式APIドキュメント](https://github.com/niconicolibs/api/tree/7ee4782f7f4f7c351da4b00145b361291e22544a) / niconicolibs contributors | `7ee4782f7f4f7c351da4b00145b361291e22544a` / 2026-09-20 | community specification / CONFIRMED-CODE | `spec/nvapi/nvapi.yaml`、`spec/nvapi/models/EssentialVideo.yaml`、`other/index.html`。動画概要のownerとタグ定義の有無を確認 | 現行全endpointの再現保証なし。otherの過去DMC例は現行domandと混同しない |

詳細と関係するendpoint・header・responseは[調査結果](SNAPSHOT-BATCH-BOUNDARY-20260920.md)と[外部資料照合メモ](evidence/snapshot-boundary-sources-20260920.json)。転載は最小限の項目名と独自の要約のみ。外部リポジトリのclone・ZIP保存・導入なし。

今回の追加検索語：`snapshot.search.nicovideo.jp contentId _limit 100`、`nvapi.nicovideo.jp/v1/videos watchIds`。検索結果から新しい一括全タグendpointを裏付けられる資料は得られなかった。検索の不発はendpoint不存在の証明ではない。既知リスト外のNicoApiClientを取得commit付きで追跡した。

## 次回以降の参照対象（今回の現行確認は未実施）

以下はユーザー指定の調査キュー。作者欄は公開アカウント名に基づく候補であり、コード著者全員を意味しない。2026-09-20にURLを台帳登録したが、この回は内容・revisionの新規確認をしていない。過去資料に記録があっても新しいCONFIRMED-CODE/LIVEへ昇格させない。

| Source / Author | Category / scope | Revision / Verified |
|---|---|---|
| [niconico.py](https://github.com/niconicolibs/niconico.py) / niconicolibs | 現行候補、動画・生放送・複数動画metadata | 今回未取得・未検証 |
| [yt-dlp Niconico extractor](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/niconico.py) / yt-dlp contributors | watch、DMS/domand、HLS、コメント・生放送 | 今回未取得・未検証 |
| [nndownload](https://github.com/AlexAplin/nndownload) / AlexAplin | 動画・マイリスト・シリーズ・ユーザー動画・過去コメント | 今回未取得・未検証 |
| [niconicojs](https://github.com/kongyo2/niconicojs) / kongyo2 | 動画、検索、ランキング、コメント取得・投稿 | 今回未取得・未検証 |
| [nvcomment Gist](https://gist.github.com/otya128/9c7499cf667e75964b43d46c8c567e37) / otya128 | コメント新旧API・thread key・過去ログ | 今回revision未取得・未検証 |
| [NicoCommentDL](https://github.com/abeshinzo78/NicoCommentDL) / abeshinzo78 | ブラウザwatchデータ・HLS・nvComment | 今回未取得・未検証 |
| [niconicomments](https://github.com/xpadev-net/niconicomments) / xpadev-net | コメント描画・コメントアートのレンダラー候補 | 今回未取得・未検証 |
| [nicovideo-api](https://github.com/a1429-lol/nicovideo-api) / a1429-lol | legacy/console候補、Wii U・Nintendo 3DS | 現行Webとは別枠、今回未検証 |
| [node-nicovideo-api](https://github.com/hanakla/node-nicovideo-api) / hanakla | legacy候補、getflv・getthumbinfo・旧ニコ生 | 今回未取得・未検証 |

## コメント研究を独立して進めるための受入項目

今後のコメント資料はmetadataの一括補完と混ぜず、下記の組ごとにendpoint / method / header名 / body構造 / 認証条件 / revision / 実通信日時 / 制約を記録する。これは未調査キューであり、今回発見した仕様ではない。

- **取得・過去ログ・投稿**：`/v1/threads`、`/v1/comment/keys/thread`、`threadKey`・`postKey`の取得方法・用途・形式、有効期間。実値は保存しない。投稿は取得と別の操作であり、将来の試験でも無断でコメントを書き込まない。
- **データ構造**：`vpos`と`vposMs`の単位・変換、`thread`、`fork`、`userId`の意味と匿名化、`nicoru`、旧新レスポンス対応。
- **描画・機械生成**：`commands`、`ue/shita/naka`、`big/medium/small`、色・フォント、改行・衝突回避・表示時間をAPI仕様と分離し、レンダラーの固定revisionで比較する。
- **取得時の探索語**：`nvapi.nicovideo.jp`、`nv-comment.nicovideo.jp`、`nvcomment.nicovideo.jp`、`/api/watch/v3`、`/access-rights/hls`、`media.domand`、`X-Frontend-Id`、`X-Frontend-Version`、`embedded-data`、`data-props`、`live.nicovideo.jp/front/api`。今回これら全てを検索したわけではない。

## 更新履歴

- 2026-09-20：一括取得の境界調査として公式1件・固定commitの公開コード2件を登録。残る初期対象は未検証キューとして明示。

## R03追記：任意動画metadata（2026-09-20）

上記キューのniconico.pyとniconicojsは今回確認を進めた。固定commitはそれぞれ`9d9c62f61f88ce640b4914007a25ddbb5d756582`、`e15fc91920567804685a6c45ebc08c2a8639f52e`。作者、URL、ファイル別hash/時刻、コード確認と作者報告の区別は[OSS確認記録](evidence/bulk-oss-review-20260920.json)。両方とも複数取得の内部は個別GET。今回4 GETの独立試験では単独成功、CSV失敗、反復一部返却。詳細は[候補判定](BULK-METADATA-CANDIDATES.md)。ライブラリ自体は未実行。他の未調査機能を確認済みにはしない。

## R09：owner型の追加照合（2026-09-20）

niconico.py / niconicojsの対象commitはR03から変更なし。Ownerのnullable項目とtype/visibilityを追加確認し、コード宣言と過去通信の違いを[クライアント比較](CLIENT-METADATA-DIFFERENCES.md)へ記録した。参照行・ファイルhash・作者・revisionは同資料と集計証拠。ライブラリの導入や実行はしていない。

## ZenzaWatchの固定ソース（2026-09-20）

作者segabito / kphrx。URLは[本家](https://github.com/segabito/ZenzaWatch)と[派生版](https://github.com/kphrx/ZenzaWatch)。revisionはそれぞれ267bc5cabfa2dda635c28f91b208d9e3093f6fcf / 1dd027d324564f0c0299cc3242073623b633c5fc。NVApi.jsの比較と、派生版のplaylist・タグ・watch/キャッシュ経路を確認。[ファイル単位の台帳](evidence/zenza-nvapi-cache-20260920.json)にURL/hash/確認時刻。[解析結果](ZENZA-NVAPI-AND-CACHE.md)はCONFIRMED-CODE、合成再生、タグ匿名GET失敗を分離。利用者の導入版ではない。横断読解用のsparse cloneはローカルのみで配布しない。

## R21の外部資料確認（2026-09-20）

niconicolibs/apiは既参照commit 7ee4782f7f4f7c351da4b00145b361291e22544aのspec/nvapi/nvapi.yamlにplaylist/request項目なし。API不存在の根拠にはしない。今回の契約は既存の公式Web/Android静的記録と新規実通信から確認。[証拠](evidence/playlist-request-20260920.json)に固定URL/hash・入力findingを記録。GitHubの完全一致公開コード検索も0件だったが、網羅検索とは扱わない。

## R12：コメント取得の固定出典（2026-09-20）

[COMMENTS-READ.mdの固定出典](COMMENTS-READ.md#固定出典)と[機械可読台帳](evidence/nvcomment-fixed-sources-20260920.json)へyt-dlp、nndownload、otya128 Gist、niconicojsを登録。上記「今回未取得」は登録当初の履歴。今回、前3者は参照revisionを新たに固定し、niconicojsは既存固定版のcomments.tsを追加読解。過去masterとの正確な変更差は不明、コード稼働確認なし。外部コードのコピーは共有しない。
