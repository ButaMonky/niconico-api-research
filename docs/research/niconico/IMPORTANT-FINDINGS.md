# NG実装へ渡す重要な確認結果

- **snapshotは100動画のタグ・投稿者を1 GETで返した**。最新値の保証とは別：[100件境界](SNAPSHOT-BATCH-BOUNDARY-20260920.md)。
- **/v1/videosの一括候補は試した形式で失敗**。CSV2件は400、反復2件は後方1件のみ。単独は成功するがタグなし。OSS2組の複数取得も各動画へ個別要求：[要求形式と結果](BULK-METADATA-CANDIDATES.md)。
- 提供報告の100指定62返却を全件成功へ読み替えない。hidden/nullから退会と断定しない：[提供報告レビュー](COMMUNITY-CONTRIBUTIONS-REVIEW.md)。

- **新着2動画はsnapshotに0件でも、個別タグ・投稿者は取得可能**。欠落を空タグ/NG非該当としない：[正確性と補完条件](METADATA-ACCURACY.md)。

- **検索初期HTMLの32動画はowner IDを保持、タグ一覧なし**。読み込み後の取得タイミングは未実測：[既取得データ再利用](BROWSER-DATA-REUSE.md)。

- **現行NGの改善箇所を合成入力で特定**：hidden/type userのIDが正規化で落ちる。投稿者だけの複合ルールも詳細完了を待つ。[最優先の開発検討点](IMPLEMENTATION-HANDOFF.md)。

- **IDが既知でも名前や種別が既知とは限らない。** 過去Web/iOSのhiddenは名前・画像がnull。Androidの限定モデルではtypeを保持する根拠が足りず、OSSの非null型も応答保証にならない。[owner比較と解釈条件](CLIENT-METADATA-DIFFERENCES.md)（R09、2026-09-20）。
