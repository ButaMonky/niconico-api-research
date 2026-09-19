# 更新・検証・共有

既存のローカル正本形式を継承した公開用研究単位。詳細は[今回の概要](SNAPSHOT-BATCH-BOUNDARY-20260920.md)。

次の調査は[TASKS.md](TASKS.md)から1件ずつ選ぶ。公開向けの記述・匿名化・出典・利用許諾・履歴確認は[PUBLICATION-GUIDE.md](PUBLICATION-GUIDE.md)を適用する。推奨思考レベルが高の場合は、利用者の通常設定を自動的に変更せず、必要な理由を説明してから開始する。

1. 主目的を1つ決め、最新資料と他タスクの成果で重複を確認する。
2. findingsにはschema_version=1、固有id、status、evidence_level、platform、app_version、observed_at、claim、evidence、request、response、authentication、unconfirmed、supersedesを記録する。
3. 生データは公開資料から分離し、共有evidenceには許可項目だけを抽出する。出典はsources.jsonへ相対file・取得方法・SHA256を登録する。外部ソースは作者・URL・固定commitとコード/実通信の別を残す。
4. 訂正時は旧証拠を残す。同じ資料集合に旧findingがある場合はsupersedesを指定する。範囲や条件の追加はclarifiesで区別する。
5. `python docs/research/niconico/tools/validate.py`で形式と証拠ハッシュを検証する。これは内容や秘密情報の検査の代わりにはならない。
6. diff・未追跡ファイル・生成物・個人識別値・絶対パスを点検してから、`python docs/research/niconico/tools/export.py`で一覧と共有ZIPを生成し、ZIP内容も点検する。
7. CHANGELOGへ追記し、解析branchへ対象ファイルだけcommit。remote更新を確認し、pushとPRを行う。本体変更は別PR。既存リポジトリの公開設定を変更しない。

raw/、private/、HAR、CHLZ、exports/はignore対象。ignoreは内容検査の代替ではない。過去の全ローカル研究セットを無検査で公開しない。

2026-09-20追加指示：今回のAstra高は利用者が許可済み。NG開発に役立つ解析を優先し、GitHub push/PRは最後にまとめる。個別調査のローカル保存・検証は継続する。

## 独立リポジトリでの更新

公開先は https://github.com/ButaMonky/niconico-api-research 。codex/で始まる研究branchを作り、内容と秘密情報の検査後にcommit・push・PRを行う。本体の機能変更は製品側で行う。手元の旧研究全体ではなく、監査済み選択版だけを追加する。
