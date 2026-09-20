# ニコニコAPI解析資料

ニコニコのAPI・ブラウザ・公式アプリに関する調査結果を、後から別の開発者やAIが再利用・再検証できる形にまとめます。ニコニコ公式の仕様書ではありません。

現在の優先テーマは、**多数の動画のタグ・投稿者IDを、少ない通信で正確に取得する方法**です。ニコランNGやZenzaWatchに役立つ情報を優先し、実通信・公開コード・外部報告・未確認の仮説を区別します。製品のソースコードや生の通信記録は収録しません。

## 読み始める場所

- [調査の入口](docs/research/niconico/START-HERE.md)
- [重要な確認結果](docs/research/niconico/IMPORTANT-FINDINGS.md)
- [API・機能一覧](docs/research/niconico/API-CATALOG.md)
- [NG開発への引き渡し](docs/research/niconico/IMPLEMENTATION-HANDOFF.md)
- [投稿者情報のWeb・iOS・Android比較](docs/research/niconico/CLIENT-METADATA-DIFFERENCES.md)
- [タスク一覧・優先順位・推奨思考レベル](docs/research/niconico/TASKS.md)
- [次の担当者への指示文](docs/research/niconico/NEXT-TASK-PROMPTS.md)
- [外部OSS・記事の出典台帳](docs/research/niconico/EXTERNAL-SOURCES.md)

## 今回の主な結果

確認日：2026-09-20 JST。成功は記載した条件・標本に限ります。

| テーマ | 確認したこと | 主な制約 |
|---|---|---|
| [スナップショット一括取得](docs/research/niconico/SNAPSHOT-BATCH-BOUNDARY-20260920.md) | 指定100動画のタグ・投稿者を認証なし1 GETで取得。101 IDは2ページで取得 | 最新タグとの一致、指定IDの最大数は未確定 |
| [別の一括候補](docs/research/niconico/BULK-METADATA-CANDIDATES.md) | `/v1/videos`の2 ID CSVは400、反復指定は後方1件のみ | 他の指定方法まで否定しない。OSSの複数取得関数も内部通信数を確認 |
| [新着動画の欠落](docs/research/niconico/METADATA-ACCURACY.md) | 新着2動画がsnapshotに未収録。検索と単独取得の投稿者が一致 | 欠落を空タグやNG非該当とみなさない |
| [初期データの再利用](docs/research/niconico/BROWSER-DATA-REUSE.md) | 検索HTMLに32 owner ID、動画タグなし | 実ブラウザでの追加通信削減は未測定 |
| [SPAの取得経路](docs/research/niconico/SPA-DATA-LIFECYCLE.md) | 公式公開JSの初期meta消費と検索loaderを静的確認 | 実際の遷移・戻る操作は未検証 |

NG本体については、取得済みownerを保持する正規化条件と、必要な項目ごとの取得状態の管理を優先候補として整理しました。今回の資料作成で本体を修正したわけではありません。

## 証拠の読み方

`CONFIRMED-LIVE` は実通信、`CONFIRMED-CODE` は参照コード、`REPORTED` は報告、`LEGACY` は過去仕様、`HYPOTHESIS` は仮説、`FAILED` は記載条件での失敗です。値が返ることと、現在の正しい値であることを分けます。hiddenを退会済みとは断定しません。

今回の選択版は21 findings / 21 evidence sources。過去の全研究を収録したものではありません。コメント・過去ログ・アプリ差・旧機種API等は、未確認の調査候補を含みます。[検証記録](docs/research/niconico/VERIFICATION-NG-HANDOFF-20260920.md)と各資料の制約も参照してください。

## 検証と更新

Python標準ライブラリで形式・出典hashを検証できます。次の操作はニコニコへ通信しません。

```sh
python docs/research/niconico/tools/validate.py
python -m unittest discover -s docs/research/niconico/tools -p "test_*.py"
python docs/research/niconico/tools/export.py
```

実通信の診断は各ファイルの説明を読み、明示的に有効化した場合だけ実行します。認証値をコードへ埋め込まないでください。生応答・HAR・Cookie・一時キー・個人情報はIssueやPRにも貼らず、[公開資料ガイド](docs/research/niconico/PUBLICATION-GUIDE.md)と[更新手順](docs/research/niconico/UPDATE-GUIDE.md)に従って集計・匿名化した結果を提出してください。

訂正は確認日・対象版・再現条件を添えてIssueまたはPRへ。外部資料は作者・URL・commit等を残し、大量転載せず要約しています。本リポジトリ独自の文書・診断コードのライセンスは未指定です。公開されていることを包括的な再配布・組み込みの許諾とは扱わず、外部資料は各配布元の条件を確認してください。

追加：[Zenzaのnvapi・キャッシュと鮮度](docs/research/niconico/ZENZA-NVAPI-AND-CACHE.md)、[広告一括APIの根拠比較](docs/research/niconico/ADS-BATCH-EVIDENCE.md)。

新規候補：[匿名で任意2動画の投稿者を一括取得](docs/research/niconico/PLAYLIST-REQUEST-BULK.md)。長期的にはZenza等にも使えるニコニコ全体の仕組みを対象とし、過去成果・外部解析を監査後に段階的に統合します。

R22：[投稿者100件を匿名1 POSTで全取得](docs/research/niconico/PLAYLIST-REQUEST-BULK.md)。[これまでの成果と収録範囲](docs/research/niconico/RESEARCH-COVERAGE.md)も参照してください。

R23〜R25：[新着・チャンネルID・不正ID・部分返却](docs/research/niconico/PLAYLIST-ACCURACY-AND-FAILURES.md)。[ランキングNGの更新着手判断](docs/research/niconico/NG-UPDATE-READINESS.md)を追加しました。本体は変更していません。

R12：[nvcommentの要求・応答とクライアント保存形式](docs/research/niconico/COMMENTS-READ.md)。保存100成功と固定OSSを整理し、今回はニコニコへの再通信をしていません。
