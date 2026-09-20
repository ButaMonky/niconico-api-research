# 調査単位ごとの次作業指示文

これは次の担当者へ渡せる指示文。このworkは解析・まとめ専用。本体開発の指示は別workへ渡し、ここでは実行しない。完了状況は[TASKS](TASKS.md)を優先し、完了した通信を繰り返さない。推奨は各タスクに記載。利用者は2026-09-20に今回のAstra高を許可した。GitHub反映の環境上の保留と調査自体の完了は別管理。

## R02完了 → R03（Astra中）

「START-HERE.md、TASKS.mdのR03、COMMUNITY-CONTRIBUTIONS-REVIEW.md、EXTERNAL-SOURCES.mdを読み、Git状態と適用ルールを確認してください。niconicolibs/niconico.pyとkongyo2/niconicojsのcommitを固定し、複数動画IDを扱うAPI・応答モデルを優先して調べてください。既存の/v1/videos・watchIds解析と比較し、新規候補があれば2動画等の最小条件で確認してください。通信回数・tags/owner有無・認証・欠落を分け、コード確認と実通信を混同せずBULK-METADATA-CANDIDATES.mdと台帳へ保存してください。原コード大量転載・認証値・個人パスを公開物へ入れず、差分/出典hash/共有ZIPを検証してください。本体は変更しません。終了時に結果と次の指示文を報告してください。」

## R03完了 → R04/R05（今回Astra高、通常の目安は中）

「Git状態・適用ルール・最新資料を確認し、IMPORTANT-FINDINGS.mdとBULK-METADATA-CANDIDATES.mdを読んでください。NGスクリプトを優先し、まずsnapshotの欠落/鮮度を新しい小標本1条件で照合し、続いて検索かランキング1画面の既取得owner/tagsを調べてください。既実施比較の重複は避け、実通信回数・取得時刻・欠落・タグ集合一致・owner種別を匿名化して保存してください。不明をNG非該当としない条件とフォールバックを実装担当へ渡してください。GitHub反映は最後、コメントや旧APIは後回し、本体機能変更は別作業です。終了単位ごとに次の指示文を示してください。」

## R04完了 → R05（今回Astra高、目安は中）

「METADATA-ACCURACY.mdを読み、検索1画面のHTML/初期データ/DOMにあるvideoIdとowner、tags有無を確認してください。ユーザーの履歴を収集せず公開画面を用い、既存通信記録の調査を重複しないでください。追加通信0で使える情報、欠落時の補完、IDの対応条件をBROWSER-DATA-REUSE.mdへ記録し、NG開発担当へ渡せるようにしてください。GitHub反映は最後にまとめてください。」

## R05完了 → R06（Astra高、許可済み）

「BROWSER-DATA-REUSE.mdと既存SPA資料を読み、取得済みHTMLが参照する公開bridge JSの版を固定して、初期metaの消費・route JSON取得・キャッシュキー・失敗時削除を静的確認してください。ブラウザ実行の安全ポリシー拒否を回避せず、静的コードと実際の遷移観測を区別してください。NGスクリプトが古いページの情報を誤適用しない条件をSPA-DATA-LIFECYCLE.mdへ保存し、実観測ができない点は保留してください。」

## R06完了 → R07の制約整理・R08（Astra高、許可済み）

「SPA-DATA-LIFECYCLE.mdを読み、ブラウザ実行が安全ポリシーで拒否された範囲を回避せず、CORS/拡張機能の未検証条件をBROWSER-REQUEST-CONDITIONS.mdへ保存してください。その後R00〜R06の証拠から、NGスクリプト向けに既取得owner再利用・snapshot一括・必要時単独タグ取得を比較し、通信数、正確性、unknown、キャッシュ、フォールバック、実装前確認事項をIMPLEMENTATION-HANDOFF.mdへまとめてください。本体変更は別作業、GitHub反映は最後です。」

## 別work専用：R08からNG開発への引き渡し（Astra高推奨）

「研究資料のSTART-HERE.md、IMPLEMENTATION-HANDOFF.md、IMPORTANT-FINDINGS.mdと最新Git/AGENTSを確認してください。ニコランNGの別開発branchで、まずOwnerEvidenceのhidden/type user/有効IDを保持できる正規化条件と、投稿者のみのルールが詳細取得完了に依存しない項目別readinessを設計・実装してください。既存のカードID照合・投稿者競合・三値AND/OR/NOTを維持し、owner取得だけでthumbInfoDoneを立てないでください。未知型・型矛盾・無効ID、タグ未取得、snapshot欠落、ロックタグ、SPAの古い応答を検証してください。取得済みownerで不要な通信を省く段階までを最初の単位とし、snapshot一括補完はその後に分けてください。研究branchへ本体変更を混ぜず、通信数は実測と計算を区別してください。ブラウザ安全ポリシー拒否は回避せず未検証範囲を残し、GitHub反映は最後にまとめてください。」

## このworkの次解析：R09完了 → R11（Astra高、今回の設定）

「最新Git/AGENTSとTASKS.md、CLIENT-METADATA-DIFFERENCES.mdを確認してください。このworkでは解析とまとめだけを行い、本体は変更しません。広告一括APIの80件全返却、100指定62返却、600成功/700失敗の報告を、既存資料と原根拠の有無から比較してください。指定数と返却数、タグ・投稿者フィールド、URL長、HTTP失敗とブラウザエラーを分け、大量の再通信や既知結果の重複を避けてADS-BATCH-EVIDENCE.mdへ保存してください。公開資料はniconico-api-research、共有概要は指定outputsへ反映し、最後に結果と次の解析指示文を示してください。」

## 最新：R11・R20完了 → R21（Astra高）

旧R11指示は完了履歴として保持する。次は新しい一括metadata候補を扱う。

「最新Git/AGENTSとTASKS.md、ZENZA-NVAPI-AND-CACHE.mdを読み、R21のPOST /v1/playlist/requestを解析してください。正本のNICO-20260913-PLAYLIST-OWNER、NICO-FOLLOWUP-20260913-PLAYLIST-FORMを利用し、既知のAndroid JSON形式・Webフォーム形式の確認を繰り返さないでください。未解決の副作用・認証条件・任意ID集合への実応答を優先し、安全な一時要求と確認できる場合だけ公開動画2件の少数通信でowner/tags・指定/返却ID対応・欠落を調べてください。用途や状態変更が不明なら送信せず不足根拠を記録してください。既知の/v1/videos失敗・広告600/700試験は繰り返さず、本体は変更しません。解析資料・共有概要・次の解析指示文を更新してください。Astra高。」

## 最新：R21完了 → R22（Astra高）

「最新Git/AGENTSとPLAYLIST-REQUEST-BULK.md、TASKS.mdを読み、R22としてplaylist/requestの少数から中規模の件数条件を調べてください。2動画の匿名成功と投稿者一致を繰り返さず、既に正当に取得した公開動画IDを使い、20件から必要な場合だけ100件へ進める最大2回のフォームPOSTを検討してください。初回失敗時は停止し、指定数・異なるID数・返却数・欠落・owner/tag有無・body/responseサイズ・応答時間を記録してください。サーバーの保持・副作用やページ分割は未確認とし、件数成功を上限保証にしないでください。本体は変更せず、資料・共有概要・次の解析指示を更新してください。Astra高。」

## 最新：R22完了 → R23（Astra高）

「最新Git/AGENTSとPLAYLIST-REQUEST-BULK.mdのR22、METADATA-ACCURACY.mdを読み、R23としてplaylist/requestが新着動画の投稿者補完に使えるかを調べてください。今はニコニコ本体の解析に集中し、ZenzaWatch固有コードの解析・制作は行いません。通常100件成功は繰り返さず、公開新着動画の最大3件についてsnapshotの現在の収録状態・playlist/requestのowner・必要時の個別情報を少数通信で比較してください。過去の索引欠落2件を使う場合も同じ欠落が続くと仮定せず、今回は新取得元への適用と現時点の一致を確認する調査だと記録してください。ID/種別の不一致・missing/nullを分け、hiddenやchannelを無理に混ぜず別条件へ回してください。本体を変更せず、解析資料・共有概要・次の指示を更新してください。Astra高。」

## R23→R24→R25の終了と次の解析（Astra高）

R23終了後の指示は「channelを少数混在させ、snapshotとのowner型とID表記を比較する」、R24終了後は「不正ID・重複・欠落を少数条件で分け、全体失敗と部分返却を記録する」。いずれもR25まで実施済み。今後そのまま再実行しない。

### 最新：R25完了 → R12

「最新Git/AGENTS、START-HERE.md、NG-UPDATE-READINESS.md、TASKS.mdを読んでください。R23〜R25の結果を再通信で繰り返さず、R12として現行nvcommentの取得要求・応答を独立資料化してください。既存コメント資料と出典台帳から重複を除き、otya128のGist、yt-dlpのNiconico extractor等の参照revisionを固定して差分と新規項目を確認してください。thread/fork/vposMs/commands/userId/nicoruを整理し、コード確認・外部報告・現在の実通信を分けてください。有効なthreadKey/postKeyやCookie、本文・個人識別値を共有しないでください。既存記録で足りれば再通信せず、必要時だけ少数の読取を検討し、投稿や大量過去ログ取得はしません。Zenza固有コード・NG本体を変更せず、解析資料・指定共有outputs・次の指示文を更新してください。Astra高、GitHub反映は最後。」

## 最新：R12完了 → R13（Astra高）

「Astra高でR13を進めてください。Git状態・適用AGENTS・COMMENTS-READ.md・TASKS.mdを確認し、既存記録とR12で固定した公開コードから、additionals.whenを使う過去ログ取得とthreadKeyの条件を1つに絞って整理してください。niconicojsのゲスト制限メッセージやnndownloadのall-commentsを現行サービス保証としないでください。過去時刻・投稿時刻とvposMsを区別し、重複・停止条件・一般会員の取得範囲を確認してください。必要な根拠が既存資料にあれば再通信せず、新規試験が必要なら正当な取得条件の1動画・少数読取だけに留め、キー実値・Cookie・コメント本文・userIdを保存しないでください。投稿・大量過去ログ取得・本体/Zenza固有コード変更は行いません。資料・指定outputs・次の指示文を更新し、GitHub反映は最後にしてください。」

## 最新：R13完了 → R14（Astra高）

「Astra高でR14のコメント投稿仕様を整理してください。Git/AGENTSとCOMMENTS-READ.md、COMMENTS-HISTORY.md、固定出典を確認し、postKey取得・投稿endpoint・body/vposMs/commands/thread/forkの関係を公開コード中心に調べてください。読取用threadKeyとpostKey、API応答とライブラリ戻り値を区別し、既知コードの再読だけで終わらず認証・対象指定・エラー処理の未整理点を1つ選んで根拠を残してください。今回はコメントを実投稿せず、認証値や本文・userIdの実値を保存しません。本体/Zenza固有コードを変更せず、解析資料・指定outputs・次の指示文を更新し、GitHub反映は最後にしてください。」
