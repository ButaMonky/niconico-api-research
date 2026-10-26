# Commons／Bad Apple!! 親子作品・大量ページ監査

2026-10-01の原本HAR 56,796,533 bytes／2,102件を解析。受信2,517,256 bytesは原本の完全一致する先頭部分。保存ミスと判断しない。

親1件、子の申告総数1060。20枠・with_meta=1のページは19→19→16→18→20件でも続く。offsetを要求枠で進める。全範囲から一意1046件（video996/live38/illust10/commons2）、差14の理由不明。総数へ一意数が届くまで無限取得しない。

with_metaはtitle/thumbnailURL/watchURL/userId/親子件数等を追加するが、duration/tags/count/視聴権限はない。data.nodeの親子件数は軽量照会に使える。treeEditURLは権限の証明ではない。登録書込みは未観測。

現Loaderの人工試験は13ケース中6成立・7期待未達。短ページ停止、後続失敗の同側データ喪失、途中404の総数リセット、重複、欠落IDを確認。現在の100枠・メタなし要求の本番再現とは区別する。各300枠の上限は撤廃せず、部分取得・完了・続き・取消を分ける。

既存F01/F03/F04へ追補し、HLS修正を優先する。製品コード修正、全体テスト、ビルド、API最大値試験、登録・削除、公開は未実施。今回知見11件は取り込み待ちcontribution。標準validator/exportは実行せず、保存時は追加JSON・ID・出典・SHA-256と既存ファイル保全だけを確認する。

| ID末尾 | 区分 | 主張 |
|---|---|---|
| SPARSE-PAGES | traffic | 少ない件数の親子ページの先にもデータが存在する |
| TOTAL-GAP | traffic | Bad Apple!!の総数1060と返却1046は一致しない |
| MIXED-KINDS | traffic | 子作品には動画以外も50件含まれる |
| WITH-META | traffic | 親子一覧はwith_meta=1で表示情報を追加する |
| NODE-COUNTS | traffic | 作品のdata.nodeから親子の件数を取得できる |
| CLIENT-SHORT-STOP | offline-test | 現Loaderは短い人工ページで走査を打ち切る |
| CLIENT-PARTIAL-LOSS | offline-test | 後続ページ失敗で同じ側の取得済み一覧が消える |
| CLIENT-404-RESET | offline-test | 途中404で既知の総数が取得件数へ置き換わる |
| CLIENT-DUPLICATES | offline-test | Loader内で重複したglobalIdが残る |
| CLIENT-MISSING-ID | offline-test | globalId欠落行が動画候補になる |
| CLIENT-CAP | offline-test | 現Loaderは親子各300枠まで取得し再開offsetを返さない |
