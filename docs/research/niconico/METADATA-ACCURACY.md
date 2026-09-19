# snapshot欠落とNG判定：新着2動画の対照確認

R04、2026-09-20 04:00:52〜04:00:59 JST。**snapshotが200で0件でも、動画・タグ・投稿者が存在しないとは判断できない。** 今回の新着2動画は検索に現れ、getthumbinfoからタグと投稿者を取得できた。NG判定では未取得状態を維持して補完する必要がある。

## 調査条件と重複を避けた理由

既存の9月14日タグ鮮度差、9月17日検索全体比較は再実施していない。今回は「索引versionより新しい公開動画を検索で選び、同じIDをsnapshotと単独情報へ渡す」という新しい2標本に限定し、欠落した動画でタグ・投稿者の代替取得が成立するかを確認した。

研究者が選んだ公開タグVOCALOIDの新着順2件。個人の検索履歴から選んでいない。証拠には再照合用の公開動画IDと投稿時刻を残し、タグ文字列・投稿者ID・表示名・タイトル・本文は保存しない。[匿名化結果](evidence/metadata-accuracy-new-20260920.json)。

## 要求・認証・再現手順

すべてGET、bodyなし、Cookie/Authorizationなし。Python3.12標準urllib、20秒timeout、1秒間隔、自動再試行0、redirectを追わずHTTP/parse/schema失敗で停止。使用header：User-Agent NicoNGResearch/20260920、Accept-Encoding identity、X-Frontend-Id 6、X-Frontend-Version 0。全headerが必須と検証したわけではない。一般会員としてログインした結果ではない。

1. `https://snapshot.search.nicovideo.jp/api/v2/snapshot/version`のlast_modifiedを読む。
2. `https://nvapi.nicovideo.jp/v2/search/video`へtag=VOCALOID、sortKey=registeredAt、sortOrder=desc、pageSize=2、page=1、sensitiveContents=mask。data.itemsのid/registeredAt/ownerをメモリー内で保持する。
3. `https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search`へq空、targets=title、fields=contentId,tags,userId,channelId,startTime、_sort=-viewCounter、_offset=0、_limit=100、_context=NicoNGResearch。`filters[contentId][0]`と`[1]`に選んだIDをURLエンコードして指定する。HTTPとmeta.statusを確認してdataの指定集合との一致・欠落を数える。
4. 各IDで`https://ext.nicovideo.jp/api/getthumbinfo/{videoId}`を1回ずつ取得。XML nicovideo_thumb_responseのstatus=ok、thumb/video_id一致を確認し、thumb/tags[@domain="jp"]/tagの件数とlock属性、thumb/user_idと検索owner.idの一致を調べる。投稿者種別を確認し、チャンネルIDをuserIdに変換しない。
5. versionをもう一度取得。前後で変われば同じ索引の比較と扱わない。

今回6要求すべてHTTP200、JSON APIの検索meta.statusも200。最初/最後のversionは同じ`2026-09-19T07:07:12+09:00`。約20時間54分前の索引versionだが、この値が全データの正確な更新時刻を保証するとは解釈しない。

## 観測結果

| 項目 | 動画A | 動画B |
|---|---|---|
| registeredAt | 2026-09-20 02:56:13 +09:00 | 2026-09-20 02:48:47 +09:00 |
| 索引versionより後 | はい | はい |
| 検索owner | user、IDあり | user、IDあり |
| 検索video直下tag/tags | なし | なし |
| snapshotの該当行 | なし | なし |
| getthumbinfoタグ件数 | 5（lock=1が5） | 6（lock=1が5） |
| getthumbinfo投稿者 | user_idあり | user_idあり |
| 検索ownerとuser_id | 一致 | 一致 |

snapshotのタグ集合・投稿者一致は**比較不能**であり、不一致や空集合として数えていない。単独情報の成功は現在の視聴ページとの最新タグ一致を保証しない。索引への反映待ちと整合するが、欠落原因や反映される時刻は追跡していない。

| 要求 | 回数 | 合計body bytes | 各応答ms |
|---|---:|---:|---|
| version前後 | 2 | 90 | 309.58 / 492.39 |
| 検索2件 | 1 | 3648 | 225.78 |
| snapshot ID2件 | 1 | 92 | 138.80 |
| getthumbinfo | 2 | 2695 | 371.23 / 335.01 |

6要求・合計6525 bytesは今回の検証負荷で、画面が検索を取得済みなら実装側の追加要求と同じではない。単発値であるため平均速度や100動画時の性能保証へ外挿しない。rate limit未測定、継続監視なし。

## NG実装への引き渡し

- 投稿者判定は検索結果にあるownerを先に使える。タグがないことは動画にタグがない意味ではない。
- snapshotの指定IDと返却IDを必ず突き合わせ、行欠落を`unknown`として残す。HTTP200だけで全件成功と扱わない。
- 行欠落・必要項目null・鮮度要求を満たさない場合だけ単独補完へ回す。今回はgetthumbinfoがタグと投稿者を同時に返す代替候補となった。
- タグNGの厳密な現在値が必要なら、snapshotで非該当だったことだけを最終判定に使わない。索引の古いタグによる誤非該当/誤該当の両方を区別する。
- hidden、channel、削除、非公開は別条件。今回のuser2件の結果をそのまま一般化しない。

R04のこの調査単位は終了。過去の最新タグ差は未解決のまま残す。次はR05で検索1画面の既取得データを確定し、その後R06/R07でSPA対応・呼出条件を絞る。[タスク一覧](TASKS.md)、[一括候補の判定](BULK-METADATA-CANDIDATES.md)。
