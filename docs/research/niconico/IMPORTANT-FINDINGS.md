# NG実装へ渡す重要な確認結果

- **snapshotは100動画のタグ・投稿者を1 GETで返した**。最新値の保証とは別：[100件境界](SNAPSHOT-BATCH-BOUNDARY-20260920.md)。
- **/v1/videosの一括候補は試した形式で失敗**。CSV2件は400、反復2件は後方1件のみ。単独は成功するがタグなし。OSS2組の複数取得も各動画へ個別要求：[要求形式と結果](BULK-METADATA-CANDIDATES.md)。
- 提供報告の100指定62返却を全件成功へ読み替えない。hidden/nullから退会と断定しない：[提供報告レビュー](COMMUNITY-CONTRIBUTIONS-REVIEW.md)。

- **新着2動画はsnapshotに0件でも、個別タグ・投稿者は取得可能**。欠落を空タグ/NG非該当としない：[正確性と補完条件](METADATA-ACCURACY.md)。

- **検索初期HTMLの32動画はowner IDを保持、タグ一覧なし**。読み込み後の取得タイミングは未実測：[既取得データ再利用](BROWSER-DATA-REUSE.md)。

- **現行NGの改善箇所を合成入力で特定**：hidden/type userのIDが正規化で落ちる。投稿者だけの複合ルールも詳細完了を待つ。[最優先の開発検討点](IMPLEMENTATION-HANDOFF.md)。

- **IDが既知でも名前や種別が既知とは限らない。** 過去Web/iOSのhiddenは名前・画像がnull。Androidの限定モデルではtypeを保持する根拠が足りず、OSSの非null型も応答保証にならない。[owner比較と解釈条件](CLIENT-METADATA-DIFFERENCES.md)（R09、2026-09-20）。

## 新規：Zenzaキャッシュの日時をタグ鮮度に使わない（2026-09-20）

[watch-infoのタグ・投稿者保存経路とthumb-infoの期限判定](ZENZA-NVAPI-AND-CACHE.md)を確認。読出しでもupdatedAtが変わり、7日前の内容が24時間以内と判定されるコード経路を合成データで再現。追加0通信の候補だが、最新タグ保証には使えない。実ユーザーDB・実ブラウザは未確認。

[R11広告比較](ADS-BATCH-EVIDENCE.md)：80全返却実測と100→62/600成功/700 fetch失敗報告を分離。decorationの応答項目にタグ・投稿者がないため、metadata一括補完の代用品と扱わない。

## 新規実通信：任意動画IDから投稿者を一括取得（2026-09-20）

[POST playlist/request](PLAYLIST-REQUEST-BULK.md)は匿名で2動画を全返却。投稿者IDとtypeはthumbinfoと2/2一致。タグはない。任意IDの最新側metadata補完候補として優先するが、上限・hidden等・副作用・ブラウザCORSは未確認。100件成功とはまだ書かない。

## 重要：投稿者100件を匿名1 POSTで取得（R22）

[playlist/request追加検証](PLAYLIST-REQUEST-BULK.md)で100指定100返却、全件owner ID/type user/visibility visible。新規2 POSTのみ。タグなし、100件の独立精度照合・特殊動画・CORS・永続副作用・件数上限は未確認。R21の「確認済み2件」から範囲を拡張した。

## R23〜R25：一括ownerを安全に利用する新条件

**200・totalCount=2でも返却は1件だった。** 全返却はID集合で確認する。channel owner.idの`ch`とsnapshot数値ID、重複2行/1動画、不正ID混在で全体400、新着3件補完も確認。[根拠と条件](PLAYLIST-ACCURACY-AND-FAILURES.md)。[ランキングNGの更新着手に必要な解析は揃った](NG-UPDATE-READINESS.md)が、製品・ブラウザ検証は別。

## R12：コメント取得の再利用条件

[コメント取得資料](COMMENTS-READ.md)を追加。params.targets階層を古いGist直下targetsと混ぜない。CookieなしでもthreadKeyが必要な保存記録だった。yt-dlpの平坦化配列やnndownload独自の件数項目をAPI生応答として扱わない。任意複数動画の一括metadata取得を示すものではない。

## R13：全件取得の件数と停止だけでは完全性を保証できない

過去100成功要求は全てadditionals空で、過去ログ成功の根拠ではなかった。固定コードの同秒を含む合成ページでは、保存件数の重複増加または進展なし停止により古い2件へ未到達。[条件と制約](COMMENTS-HISTORY.md)。実サーバーの同じ挙動は未確認。

## R14：投稿の結果不明を自動再送しない

固定niconicojsで、投稿POSTは1回、キーGET・読取POSTは再試行という差を合成確認。HTTP200/meta403と503詳細欠落も区別した。上位層の一律retryによる二重投稿を避ける設計根拠。**実投稿/現行サービス成功ではない**。[投稿仕様と8ケース](COMMENTS-POST.md)。
