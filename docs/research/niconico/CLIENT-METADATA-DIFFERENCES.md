# Web・iOS・Androidの投稿者情報：保持できる値と確定できない値

2026-09-20、R09。今回はownerモデルだけを比較した。**投稿者IDがあること、ユーザー／チャンネルの種類が分かること、表示名が利用できることは別の状態として扱う。** ニコニコへの新規通信0、本体変更0。過去の集計資料を再集計し、公開OSSの対象ファイルを固定commitで確認した。

## 結論と証拠の範囲

| 対象 | 根拠・時点 | 確認したこと | 確認していないこと |
|---|---|---|---|
| Web検索ページJSON | 2026-09-13の項目限定抽出を再集計 | 14応答・延べ448動画、hidden101件は全てtype=user、IDあり、visibility=hidden、name/iconUrl=null | 現在の再通信、匿名条件、異なる動画・投稿者の実数 |
| Web関連検索nvapi | 同じ記録の別5応答 | 延べ10動画のhidden2件も同じ形。各応答2件 | 検索本体32件との混同、全件網羅 |
| iOS検索 | 2026-09-12の項目限定抽出を再集計 | 30応答・延べ685動画全てIDあり。hidden387件は全てtype=user、visibility=hidden、name/iconUrl=null | この通信とIPA版の一対一の対応、現在の再現、Webと同一動画の比較 |
| iOS OwnerInfo | IPA 12.37 (276)の既存シンボル抽出 | ownerType/type/visibilityを分離。id/name/iconUrlは任意文字列型 | 復号・実行・サーバーの現在の応答 |
| Android NvOwner | 9.14.0 (471)、classes6.dexの既存命令参照 | Lfd/b;->aはownerType/id/name/iconUrlを参照。type/visibilityはこの参照一覧にない | 上位層の型判定、元JSON全項目、Android実通信 |

「Web101＋iOS387」は延べ観測数であり、488人・488本の独立標本ではない。クライアント間で同一動画・同一時刻・同一会員条件をそろえた実験ではないため、サーバー応答のクライアント差を証明したとは呼ばない。

Android列挙値にはuser/channel/hiddenがあり、ID等は別フィールドとして渡される。ただし残っているのはシンボルと命令参照の抽出で、全制御フローの証明ではない。**「hiddenだからIDを必ず捨てる」とする根拠はない一方、「Androidのhiddenは必ずuser」とする根拠もこのモデルだけでは足りない。** 未取得のtypeを数値IDから補わない。

## endpointと返却項目

```yaml
checked_at: 2026-09-20
verification: historical-capture-reanalysis
new_niconico_requests: 0
endpoints:
  - url: https://www.nicovideo.jp/tag/{query}
    method: GET
    client: web
    query: [responseType=json, page, sort, order]
    items_path: data.response.$getSearchVideoV2.data.items
    authentication: Cookie present in historical samples; necessity untested
    observed_page_item_count: 32
  - url: https://nvapi.nicovideo.jp/v2/search/video
    method: GET
    client: [ios-capture, web-related-search]
    query: [tag, page, pageSize, searchByUser, sortKey, sortOrder]
    items_path: data.items
    authentication: Cookie present in historical samples; necessity untested
    observed_ios_page_sizes: [10, 15, 25]
    observed_web_related_item_count: 2
fields: [owner.ownerType, owner.type, owner.visibility, owner.id, owner.name, owner.iconUrl]
batch:
  supported: search-result-page
  arbitrary_video_ids: unconfirmed-for-these-routes
```

queryは観測名の主要部分で、全部が常時必須という意味ではない。iOS記録にはallowFutureContents、channelVideoListingStatus、lockTag、nicoadFrames、selectContentType、sensitiveContentsもある。検索語そのものやCookie値は保存しない。追加headerの完全な一覧・必須性はこの項目限定抽出から確定できない。GETなのでrequest bodyは不要という前提の再現案であり、今回生リクエストを再読して確認したものではない。

成功の判定はHTTP200だけでなく、itemsの存在、各動画IDとの対応、owner各項目の型を確認すること。既取得の同じ検索ページのownerを使えば追加通信0の候補になるが、NG本体での削減実測ではない。任意の100動画を必ず検索1回で取得できるという意味でもない。上限、応答サイズ・時間、rate limit、キャッシュ寿命は今回測定していない。

Webの448件・関連10件に動画ごとのtag/tagsはなかった。検索条件のtagやadditionalsの候補タグは、各動画のタグ集合の代わりにはならない。ownerだけでタグ・ロック情報・説明文を取得済みにしない。

## 公開OSSとの照合

確認：2026-09-20 JST。今回のGitHub取得は認証なし。対象commitは前回R03と同一で、版の差分調査は不要だった。新たにowner宣言を照合した。ライブラリは導入・実行していない。

| 作者・参照先 | 固定revision | 今回読んだ箇所 | 得られた情報 |
|---|---|---|---|
| niconicolibs / [niconico.py](https://github.com/niconicolibs/niconico.py/blob/9d9c62f61f88ce640b4914007a25ddbb5d756582/niconico/objects/video/__init__.py#L32) | 9d9c62f61f88ce640b4914007a25ddbb5d756582 | Owner、32–40行 | ownerType/type/visibilityは別。typeにunknownを含む。id/name/iconUrlはnull許容 |
| kongyo2 / [niconicojs](https://github.com/kongyo2/niconicojs/blob/e15fc91920567804685a6c45ebc08c2a8639f52e/src/types.ts#L19) | e15fc91920567804685a6c45ebc08c2a8639f52e | Owner、19–27行 | id/name/iconUrlをstringと宣言。過去hidden応答のname/iconUrl=nullをこの型宣言だけでは表現していない |

後者は**型宣言と観測値の不一致**であり、ライブラリがクラッシュすることを実行確認した結果ではない。コンパイラ設定・デコード処理・呼び出し側の扱いは未検証。公開型をそのまま現行APIの必須項目・非null保証にしない。niconico.pyがnullを許容することも、現在の全応答を検証した保証ではない。

## NG開発担当へ渡す解釈条件

以下は解析結果からの設計上の提案であり、新たなAPI仕様や本体実装ではない。IDは文字列として保持する選択ができ、数値化する場合は精度と形式を検査する。

| 入力条件 | 保持・判定の考え方 | 根拠区分 |
|---|---|---|
| ownerType=hidden、type=user、有効ID、name=null | IDとuser種別を保持。表示名は利用不可。名前の空文字とは区別する | 過去Web/iOSで観測 |
| ownerType=hidden、有効ID、type未取得 | IDの証拠を保持しても種別は未確定。ユーザーNGへ自動投入しない | Androidの限定モデルからの保守的提案 |
| ownerType=hidden、type=channel | 型が矛盾しないか情報源ごとに確認。今回の標本にこの組み合わせはない | 未確認の条件 |
| ownerType=user、type=channelなど種別が矛盾 | 情報源の矛盾として保留。片方を無条件に優先しない | 設計提案、実応答未観測 |
| ownerがnull／ID欠落／動画が非公開 | 投稿者の不存在・退会とは断定しない。判定材料不足を保持する | 欠落理由の未確定 |
| userとchannelで同じ数字のID | 種別込みで比較する | 名前空間の混同防止 |

hiddenの名前がnullであることから、「名前は空文字」「名前NGに一致しない」「退会している」へ飛躍しない。名前条件を評価できない状態を残す。正のIDがあるだけでも、その値が対象動画に結び付く証拠と種別の確認は別に必要。

## 再検証方法と制約

今回の[集計証拠](evidence/owner-client-review-20260920.json)に、元の項目限定抽出4ファイルのSHA256、日時、版、件数、参照モデル、公開ファイルのSHA256を保存した。元の抽出資料には不要なID等があるため公開セットへコピーしていない。**hashは入力識別用であり、公開集計だけから元の通信を復元・独立再集計できるわけではない。** 生の通信記録は今回読み直していない。

入力資料を持つ担当者がオフラインで再集計する場合：

1. Webのsearchをhostで分離し、itemsを連結する。www側14応答448件、nvapi側5応答10件を別に数える。
2. owner.ownerTypeがhiddenの要素だけ取り、IDの非空文字列、type=user、visibility=hidden、name/iconUrlのnullをそれぞれ集計する。Web側IDは匿名化済みのため、元の数値形式の検証には使わない。
3. iOSはsessions[].searches[]のitem_countとowner_id_countを合計し、hidden[].ownerを集計する。nullは抽出時のname_is_null/iconUrl_is_nullフラグで確認する。
4. アプリは対象ファイルhashと版を照合し、Androidの参照項目・iOSの任意文字列型を確認する。これを実通信の認証条件や特定画面の実行結果へ読み替えない。

Web/iOSとも今回対象の過去GETにはCookieがあった。必要性の比較、匿名条件、一般会員条件、同一動画でのクライアント差、現在のhidden出現は再確認していない。通常のユーザー操作が許可された環境で最小限の再観測をする場合も、閲覧履歴・名前・ID・キーの実値を報告へ持ち込まず同じ集計形式を使う。ブラウザ安全ポリシーによる既存の拒否を回避しない。

## 関連資料と次の解析

[実装への引き渡し](IMPLEMENTATION-HANDOFF.md)、[一括metadata候補](BULK-METADATA-CANDIDATES.md)、[初期データ再利用](BROWSER-DATA-REUSE.md)。本体の制作は別work。このworkでは解析とまとめだけを続ける。

次はR11の広告一括APIについて、保存済みの80件全返却・100指定62返却・600/700報告を原根拠の有無で整理する。大量の再通信は行わず、返却フィールドがタグ／投稿者補完に使えるかを既存証拠から評価する。

## 資料検査

11 findings / 12 sourcesの形式・参照hash、52収録ファイルのZIP manifest、相対リンク、公開対象・差分の秘密値/個人パス候補を検査した。公開資料を対象にした独立レビューでは重大・重要な指摘なし。READMEの収録件数の更新漏れを修正した。レビュー担当は非公開の元集計を再計算していない。今回診断・本体コードは変更せず、実通信試験や既存コードテストを繰り返していない。
