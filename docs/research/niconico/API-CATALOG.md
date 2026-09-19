# API・機能一覧

findings JSONから生成。staticは実通信確認ではありません。

| 発見 | 状態 | 対象 | 要点 |
|---|---|---|---|
| [広告一括の80実測と100・600・700報告を分離](findings/NICO-ADS-20260920-BATCH-EVIDENCE.json) | reported | Web / research-only | 過去の80異なるID全返却、100指定62返却報告、600指定成功/700 fetch失敗報告は上限比較の同条件試験ではない。装飾応答にtags/ownerはなく、任意100動画のmetadata補完の代用根拠なし。 |
| [検索初期HTMLの32動画にowner ID・タグ一覧なし](findings/NICO-BROWSER-20260920-INITIAL-OWNER.json) | traffic | Web initial HTML fetched without browser execution | 公開検索の初期HTMLを認証なしで取得し、server-response内data.response.$getSearchVideoV2.data.itemsの32動画にowner.idを確認。全32はuser/文字列ID。video直下tag/tagsなし。読み込み後DOMやuserscriptの取得タイミングは未実測。 |
| [現行検索loaderは初期metaを消費し、その後route JSONを要求するコード](findings/NICO-BROWSER-20260920-SEARCH-LOADER.json) | static | official Web client static JavaScript | タグ検索loaderから直接bridge Biへ接続。server-responseはJSON化後remove、読めなければ要求URLにresponseType=jsonを付ける。汎用Promise cache factoryは別であり、この検索loaderにshortsのTTLやpathnameキーを適用する根拠はない。実ブラウザ遷移は環境制約で未確認。 |
| [検索100件・広告部分返却・投稿者欠落の提供報告を条件付き統合](findings/NICO-METADATA-20260920-CONTRIBUTION-REVIEW.json) | reported | Web / public metadata API / supplied report | 5件のmetadata関連contributionを確認し、6観察を報告として保存。検索100件と広告100指定62返却を分離。pageSize100/page50の境界報告から一般的な5000件上限を確定しない。投稿者欠落・404から退会を確定しない。今回の実通信0。 |
| [新着2動画はsnapshot欠落だが単独タグ・投稿者補完は成功](findings/NICO-METADATA-20260920-NEW-INDEX-MISSING.json) | traffic | public search / snapshot / getthumbinfo | 索引version以降に投稿された新着2動画を固定IDで照合。snapshotは200で0件。各getthumbinfoは5/6タグとuser_idを返し、検索owner.idと2/2一致。欠落を空タグ・投稿者なしと扱う仮説は成立しない。 |
| [OSS2組の複数動画関数は各動画への個別要求](findings/NICO-METADATA-20260920-OSS-FANOUT.json) | static | public Python / TypeScript implementations | niconico.pyはループ、niconicojsは既定並列4で単独GETを繰り返す。入力N件の通常経路はN要求で、1要求の一括取得ではない。コードを実行して測った性能値ではない。 |
| [v1/videosのCSV2件は400・反復2件は後方1件のみ返却](findings/NICO-METADATA-20260920-VIDEOS-BULK-FAILED.json) | traffic | public Web API / Python urllib | 公開通常動画2件・認証なしでCSV2件が400。各単独指定は200。反復指定は後方1件のみで、その本文hashとownerが単独取得に一致。4 GETで条件を切り分け。一括取得候補の静的コードを動作保証にしない。 |
| [NG現行コードのhidden正規化と投稿者ルールの詳細取得依存を確認](findings/NICO-NG-20260920-OWNER-INTEGRATION-GAPS.json) | offline-test | local NG script, Node vm synthetic execution | OwnerEvidence.normalizeは合成userを受け入れ、ownerType hidden/type user/idありをnullにする。contributorId一致の複合ルールはthumbInfoDone falseでnull、trueでtrue。この2点は取得済みownerの再利用に必要な開発検討点。実ブラウザでの不具合再現ではない。 |
| [nvapiタグGETの匿名・キーなし条件は400](findings/NICO-NVAPI-20260920-TAGS-KEYLESS.json) | traffic | Web / research-only | GET /v2/videos/sm15630734/tagsをCookie・タグ編集キーなしで1回試験。HTTP400 INVALID_PARAMETER、55bytes。キー省略だけが原因とは確定しない。 |
| [投稿者IDの保持と投稿者種別・表示状態を分離して扱う](findings/NICO-OWNER-20260920-CLIENT-CONTRACT.json) | static | Web / iOS / Android model comparison | 過去検索記録のhiddenはWeb101件・iOS387件ともtype:user、IDあり、name/iconUrl:null。Androidの調査済みパーサー参照項目はownerType/id/name/iconUrlでtype/visibilityがない。ID保持と名前の利用可否・種類の確定は別に扱う。 |
| [タグ・投稿者100動画の指定ID一括取得を確認](findings/NICO-SNAPSHOT-20260920-BATCH100.json) | traffic | public metadata API / Python urllib | 公開索引から選んだ100動画を1 GETで全返却。全件tags非空文字列・userId整数、channelIdはnull。指定IDの欠落・余分0。同じ索引の取得元と3項目全一致。視聴ページの最新値は再照合していない。 |
| [101個のcontentIdフィルターは受理、2ページで101動画取得](findings/NICO-SNAPSHOT-20260920-FILTER101.json) | traffic | public metadata API / Python urllib | 101個の異なるIDを指定して_limit=100でHTTP200/totalCount101、offset0が100件・offset100が1件。和集合101・重複0。IDフィルター個数も最大100という仮説を否定。フィルター数の真の最大値は未確定。 |
| [_limit=101は範囲エラー、100件のページ上限を確認](findings/NICO-SNAPSHOT-20260920-LIMIT100.json) | traffic | public metadata API / Python urllib | 短い2 ID指定で_limit=101はHTTP400/QUERY_PARSE_ERROR、理由は_limit is out of range. 100 < 101。同じセッションの_limit=100による100動画返却と合わせ、ページ返却数の100/101境界を確認。IDフィルター数の上限とは異なる。 |
| [Zenzaの既取得metadataと鮮度日時の落とし穴](findings/NICO-ZENZA-20260920-CACHE-AGE.json) | offline-test | Web / research-only | watch-infoにタグ・投稿者の保存経路。getがupdatedAtを更新し、thumb-infoの期限比較前にも日時が更新される。固定コードの合成再生では7日前の内容が24時間以内と判定された。実ブラウザ未確認。 |
