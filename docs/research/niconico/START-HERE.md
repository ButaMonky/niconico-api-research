# ニコニコAPI研究の入口

調査を引き継ぐ場合は[タスク一覧と推奨思考レベル](TASKS.md)を確認し、1件ずつ進める。他のAI・ユーザーへ渡す資料は[公開資料ガイド](PUBLICATION-GUIDE.md)に従う。[公開準備の現状](PUBLICATION-READINESS-20260920.md)に未公開・未監査の範囲を明記した。

まず[スナップショット100件境界の検証](SNAPSHOT-BATCH-BOUNDARY-20260920.md)を読む。指定した100動画のタグ・投稿者を認証なしの1 GETで全取得。_limit=101は400だが101 IDフィルターは2ページで取得できた。索引鮮度と最新タグの正しさは別の問題として扱う。

次に[API-CATALOG](API-CATALOG.md)、必要なfindingsとevidence、[外部資料台帳](EXTERNAL-SOURCES.md)を参照する。[更新手順](UPDATE-GUIDE.md)に従って追加する。

この公開用選択版は2026-09-20の調査単位に限定する。ローカル正本の過去83発見・56証拠を削除したものではなく、過去資料の全公開監査は別途必要。参照元の36件成功・タグ鮮度差・提供資料の報告は今回の概要に条件付きで記録した。

証拠区分：CONFIRMED-LIVE=今回の実通信、CONFIRMED-CODE=参照コード、REPORTED=公式説明/作者記事/提供報告、LEGACY=過去仕様、HYPOTHESIS=仮説、FAILED=今回の条件で再現失敗。既存schemaのstatusはtraffic/static/reported等を保持し、evidence_levelを併記する。失敗応答の確認自体にはCONFIRMED-LIVEを付け得る。

hiddenを退会と断定しない。広告600成功/700失敗は今回原記録未照合。一般会員のいいね全件取得は未解決。製品コードは本研究で変更しない。認証情報・生通信記録・ローカルPC固有のパスは保存しない。

追加：[提供metadata報告の確認](COMMUNITY-CONTRIBUTIONS-REVIEW.md)、[次作業の指示文](NEXT-TASK-PROMPTS.md)。報告はREPORTEDとして統合し、独立実通信とは区別した。

NG実装向けの優先入口：[重要な確認結果](IMPORTANT-FINDINGS.md)。利用者の追加指示により、GitHub反映は最後、当面はZenzaWatch/ニコランNG向け解析とAI間引き継ぎを優先する。

[新着2動画の索引欠落と補完](METADATA-ACCURACY.md)：snapshot0件でもタグ・投稿者は存在した。NG判定に欠落状態が必要。

[検索初期データの再利用](BROWSER-DATA-REUSE.md)：32件のowner確認、追加0の設計候補。実ブラウザは環境制約で未確認。

[検索SPAのデータ寿命](SPA-DATA-LIFECYCLE.md)：現在の公開loaderを静的確認。初期metaは消費後削除、検索にshortsのTTLを流用しない。

**NG開発への最短の入口：[実装引き渡し](IMPLEMENTATION-HANDOFF.md)**。現行コードとの照合、優先修正候補、100動画比較、unknown/lock/SPA条件を整理。R07のCORS実測は[保留理由](BROWSER-REQUEST-CONDITIONS.md)。

## 独立した公開先

本選択版の公開先は[niconico-api-research](https://github.com/ButaMonky/niconico-api-research)。製品リポジトリとは分離した研究資料集で、READMEを入口とする。GitHub Pagesは使用しない。利用許諾の指定は保留し、過去の非公開保存段階の記録も履歴として残す。

[投稿者モデルのWeb/iOS/Android比較](CLIENT-METADATA-DIFFERENCES.md)：hiddenのID、投稿者の種類、名前のnullを分離。過去記録の再集計と公開型宣言の照合で、新規実通信ではない。このworkは解析専用。本体開発は別workへ引き渡す。
