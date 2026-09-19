# 任意動画の一括取得候補：OSSと実通信の照合

確認：2026-09-20 JST、R03。**今回の/v1/videosは通信削減用の一括APIとして採用しない。** 通常公開動画2件を認証なしで試し、CSV2件は400、反復指定2件は後方1件だけだった。単独取得は両方成功。これは今回の指定形式・認証条件の結果であり、API全体の廃止やあらゆる形式の不存在を意味しない。

## 固定した公開コード

| 作者・ソース | commit | 主な参照ファイル | コード上の確認 |
|---|---|---|---|
| [niconicolibs/niconico.py](https://github.com/niconicolibs/niconico.py/tree/9d9c62f61f88ce640b4914007a25ddbb5d756582) contributors | `9d9c62f61f88ce640b4914007a25ddbb5d756582` | niconico/video/__init__.py、objects/nvapi.py、objects/video/__init__.py、niconico.py | get_videosが各IDのget_videoを順に呼ぶ。VideosData.items[].video.ownerをモデル化 |
| [kongyo2/niconicojs](https://github.com/kongyo2/niconicojs/tree/e15fc91920567804685a6c45ebc08c2a8639f52e) contributors | `e15fc91920567804685a6c45ebc08c2a8639f52e` | src/videos.ts、http.ts、types.ts、test/lists-and-videos.test.ts、README.md | getVideosが各IDへgetVideo。既定の並列数4。buildQueryの配列は同名parameterの反復 |

CONFIRMED-CODE。参照時刻と各ファイルhashは[証拠](evidence/bulk-oss-review-20260920.json)。niconicojs READMEの2026-09-08試験結果はREPORTEDとして別記。初めにWeb表示で見たsrc変更commit `8467af5…`ではなく、GitHub APIで確認したmain先端`e15fc91…`へ固定して関連本文を読んだ。リポジトリ全体のclone・実行・導入はしない。

## 要求と実通信

endpoint：`https://nvapi.nicovideo.jp/v1/videos`、GET、bodyなし。今回のheaderはAccept application/json、Accept-Encoding identity、User-Agent NicoNGResearch/20260920、X-Frontend-Id 6、X-Frontend-Version 0、OriginとRefererは通常のwww.nicovideo.jp。Cookie/Authorizationなし。これらすべてが必須かは削減試験していない。一般会員でログインした試験ではない。

A/BはR00の公開研究標本から選択した2動画。IDは診断コードと証拠にあり、利用者の履歴から選んだものではない。

| 要求query | HTTP / body status | 返却 | body bytes | 応答ms（各1回） |
|---|---|---|---:|---:|
| watchIds=A%2CB | 400 / 400 | 一括取得失敗 | 55 | 195.91 |
| watchIds=A | 200 / 200 | Aの1動画 | 1812 | 222.17 |
| watchIds=B | 200 / 200 | Bの1動画 | 1532 | 139.33 |
| watchIds=A&watchIds=B | 200 / 200 | Bの1動画だけ | 1532 | 139.90 |

CONFIRMED-LIVE。03:54:01〜03:54:56 JST。まずCSVで失敗して初期3要求の計画を停止した。その後、endpoint自体の利用可否と入力標本の存在を切り分けるため、別計画で単独2件と反復1件を実施。合計4 GET、自動再試行0。失敗したCSVを再送していない。CSVのerrorCodeは初期診断で保持しておらず、400以上の原因を断定しない。

反復指定の本文SHA256は単独Bと同一で、ownerオブジェクトもメモリー内で一致。応答本体、ownerのID/名前/画像URLは保存しない。[CSVの集計](evidence/video-lookup-encoding-20260920.json)と[対照比較](evidence/video-lookup-control-20260920.json)。順序を逆転した要求は未実施なので「常に最後を採用する」という普遍的保証にはしない。

成功応答は`data.items[].watchId`と`video.id`が一致し、`video.owner.id`は文字列、ownerType=user。video直下のtag/tagsキーは3成功応答とも存在しなかった。投稿者IDが返る事実は確認したが、視聴ページとの現在値照合、hidden/channel/null動画は未確認。既知フィールドだけを集計し、未知の追加情報も応答へ混ざり得ることを否定しない。

Cache-Controlはprivate, no-cache。ページ送りなし。この4要求からrate limitや安定した速度は推定しない。Pythonの成功をブラウザのCORS成功と扱わない。

## 既存候補の訂正と実装上の意味

ローカルのFOLLOWUP-APPS-WEB-20260913.mdには、公式WebラッパーのCSV指定とiOS一覧モデルを根拠に一括候補を記録していた。当時は複数IDの実応答なし。今回の結果で、その候補を「試した形式では一括取得失敗」へ限定する。過去の静的発見を削除しない。

| 100動画を扱う方法 | 通信数 | タグ・投稿者 | NG実装への判断 |
|---|---:|---|---|
| niconico.py get_videos | 通常経路100（コードから計算） | ownerモデル。タグ別経路 | 一括削減にならない |
| niconicojs getVideos | 通常経路100、再試行で増え得る（コードから計算） | ownerモデル。タグ明示なし | 並列化と通信削減を混同しない |
| snapshot指定100 ID | 1（R00実測） | tags/userIdを索引から取得 | 鮮度・欠落を別に扱う候補 |
| 既に表示用に取得した一覧データ | 追加0を目標、R05で確認 | owner候補、tagsの所在要確認 | 先に再利用し、不足だけ補完する |

フォールバック候補は「画面の取得済みowner → 許容する鮮度でsnapshot → 必要な単独情報」。単独/v1/videosはタグ補完を兼ねないため、タグを要する判定へ無条件に使わない。欠落・null・失敗をNG非該当としない。ライブラリの型でname必須でも、既存hidden観測のnullは捨てない。

追加候補：niconico.pyの単独タグ取得は/v2/videos/{videoId}/tagsとX-Tag-Edit-Keyを使う。新しい一括タグ経路ではない。コメント/再生系の派生はここで追わない。

## 再現方法と未確認

`python tools/probe_video_lookup.py`はオフラインで最大3要求のURLだけ表示する。`--live --output <new-summary.json>`でCSV→反復→逆順反復を計画し、失敗で止まる。対照は`--mode control --live --output <another-new-summary.json>`。1秒間隔・20秒timeout、認証なし、既存出力を上書きしない。最初の失敗と匿名化は[オフライン試験](tools/test_probe_video_lookup.py)で検査する。今回の4要求を再現するには2モードを順に使うが、通常作業で無意味に再送しない。

他の配列表現・ログイン・includePrivate・hidden・channelは未確認。今回の2 OSSから、現行の任意動画を1要求で全タグと投稿者まで返す新規経路は確認できなかった。次はR04の索引欠落/鮮度、R05の既取得データ再利用を優先する。
