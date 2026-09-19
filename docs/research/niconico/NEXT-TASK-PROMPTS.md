# 調査単位ごとの次作業指示文

これは次の担当者へ渡せる指示文。完了状況は[TASKS](TASKS.md)を優先し、完了した通信を繰り返さない。推奨は各タスクに記載。利用者は2026-09-20に今回のAstra高を許可した。GitHub反映の環境上の保留と調査自体の完了は別管理。

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

## R08完了 → NG開発への引き渡し（Astra高推奨）

「研究資料のSTART-HERE.md、IMPLEMENTATION-HANDOFF.md、IMPORTANT-FINDINGS.mdと最新Git/AGENTSを確認してください。ニコランNGの別開発branchで、まずOwnerEvidenceのhidden/type user/有効IDを保持できる正規化条件と、投稿者のみのルールが詳細取得完了に依存しない項目別readinessを設計・実装してください。既存のカードID照合・投稿者競合・三値AND/OR/NOTを維持し、owner取得だけでthumbInfoDoneを立てないでください。未知型・型矛盾・無効ID、タグ未取得、snapshot欠落、ロックタグ、SPAの古い応答を検証してください。取得済みownerで不要な通信を省く段階までを最初の単位とし、snapshot一括補完はその後に分けてください。研究branchへ本体変更を混ぜず、通信数は実測と計算を区別してください。ブラウザ安全ポリシー拒否は回避せず未検証範囲を残し、GitHub反映は最後にまとめてください。」
