# ニコニコ互換性の追加知見 — 2026-10-01

Task153〜157の証拠を再利用し、既知事項と未確認事項を分けた共有用追補。
生HAR、Cookie、認証キー、署名付き配信URLは含めない。GitHub未公開。

## 大百科の一括取得（Task157 / runtime）
- www.nicovideo.jp/watch/sm9上の検証ブラウザから通常のfetchで確認。
- GET https://api.dic.nicovideo.jp/v1/articles/article
- クエリは titles[]=音楽&titles[]=ゲーム のように同名パラメータを反復。URLSearchParamsでエンコード。
- credentials: omitで200、CORS経由でJSON本文の読取り成功。ログイン不要の試験。
- 10指定: 音楽、ゲーム、陰陽師、初音ミク、東方、VOCALOID、ニコニコ動画、Bad Apple!!、C++、zenza_no_article_20261001。
- 1 GETで9記事を返却、最後の不存在名は返却なし。配列の各要素にid/title/view_title/category/summary/url/request_title。
- VOCALOID→title=vocaloid、Bad Apple!!→bad apple!!、C++→c++。request_titleはそれぞれ入力表記を保持。配列の位置や正規化済titleで照合しない。
- 不存在だけの応答や10件超のサーバー上限は未確認。10は製品の安全な分割単位であり、サーバー上限の断定ではない。
- /v1/articles?titles[]=... は400（ids is missing, ids is empty）。/v1/articles/articleとの違いを混同しない。
- 旧dic.nicovideo.jp/api/e/...は今回404。正式廃止とは断定しない。
- 個別記事APIは公式配信root-C4Hqoj7f.jsに/v1/articles/{category}/{title}とcredentials omitを静的確認。一括APIは上記の実通信を根拠とする。
- クライアントは通信失敗・不正JSONを記事なし扱いせず、キャッシュしない。旧HEADキャッシュと新キャッシュを区別する。

## watch v4応答（Task153 / 既存実測の再整理）
- 単純なURLのv3→v4置換ではなく、視聴JSONの$watchV4.data構造への対応が必要。
- media.contents、コメントthreads.isPostTargetとlayers.componentsを既存モデルへ変換した。
- 投稿者・シリーズのlazy取得は要求対象watchIdに対応するキーを使用する。キー自体は共有しない。
- sm9/1398430036の情報取得、sm1削除エラー、既存v1 HLSセッション作成201はTask153で確認済み。
- 有料・会員限定・投稿・タグ編集は未検証。新応答に無いクリエイターズツリー存在フラグを事実上の不存在と一般化しない。
- 証拠: commit a0832fa、docs/design-pack/162_TASK_153_WATCH_V4_RESPONSE.md、WatchV4ResponseTest.js。

## サムネイル（Task154 / 既存実測の再整理）
- v4でnormal/middle/largeの画像URLを使用。旧thumbnail.urlだけを参照するコードでは欠落する。
- MediaMetadataのartworkへ未定義srcを渡すと再生開始前に例外となった。OS向け画像情報の欠落で動画再生を止めない。
- 証拠: commit 8449bb1、163_TASK_154_WATCH_V4_THUMBNAIL.md、WatchV4ThumbnailStartupTest.js。sm46867460で利用者と同じ例外を検証ブラウザで再現。

## HLS再生開始（Task155 / runtimeとユーザー報告）
- canPlayTypeが対応を返しても、検証Chromeの標準HLSはDomand再生開始時にMediaError4となった。全Chrome・全動画共通の仕様とは断定しない。
- 標準HLS設定yesのまま開始位置0のエラー3/4からhls.jsへ切替え、sm46867460の1280x720、3.945秒を確認。
- Task156との組合せではsm9の480x360、2.133→3.644秒の進行も確認。
- 2026-10-01ユーザー報告「再生できるようになりました」。ユーザー側の個別動画・ブラウザ版はこの報告では未指定。
- 証拠: commit 2816fa8、164_TASK_155_NATIVE_HLS_FALLBACK.md、NativeHlsStartupFallbackTest.js。

## Pocketの初回要求（Task156 / implementation）
- これはニコニコのAPI変更ではなく製品内の初期化順序の不具合。
- iframeのready通知後にDBをawaitしたため、最初のMessagePort要求が受信登録前に消えた。DB準備→ready通知・受信登録の順へ修正。
- 配布物で初回getthumbinfo要求1回とbusy=falseを確認。ログインしたマイリスト追加・削除は未確認。
- 証拠: commit c765983、165_TASK_156_POCKET_FIRST_REQUEST.md、PocketFirstRequestTest.js。

## 記録の運用
- 正本Knowledge BaseのUPDATE-GUIDEに従い、contributions/に発見ID付きJSON、evidenceにこの匿名化追補、sources.jsonにSHA-256を追加する。
- contributionsは正本担当の取り込み待ち。既存findingsや公開済みAPI一覧を勝手に確定・置換しない。今回追加分だけの共有ZIPを作成する。
- 今後のAPI互換修正でも、実測条件・未確認条件・秘密を除いた証拠・出典ハッシュを同じTask内で保存する。製品固有バグとサーバー仕様を分ける。
