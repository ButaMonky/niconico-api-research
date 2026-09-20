# 一覧ホバープレビュー：既存資料の到達点と不足

2026-09-20 JST。新規観測の前に照合した資料の整理。研究基点は `352b676325b3559b73eb93f8560e1b76bdbe89a7`（R15B）。GitHubのOPEN PR #2〜#10は積み重なっており、#10のheadとローカル基点が一致した。mainの `0bd9bd6` だけを最新版とはしていない。

| 資料 | 到達点・根拠 | 今回繰り返さないこと | ホバー実装に不足すること |
|---|---|---|---|
| NG-UPDATE-READINESS.md | R25。既取得owner保持・項目別readinessの着手条件 | 100件API再照会 | ホバー映像・音量・コメントの契約 |
| IMPLEMENTATION-HANDOFF.md | 本体固定版の静的確認・合成試験。カードIDとSPA世代照合 | 本体の改修・既存owner試験の反復 | 公式カード保持とNG追加カードの責任分離 |
| IMPORTANT-FINDINGS.md | metadata通信削減・欠落・キャッシュ日時の注意 | 既知の一括API比較 | プレビュー固有の取得・破棄 |
| CLIENT-METADATA-DIFFERENCES.md | 過去Web/iOS集計、Android限定モデル、固定OSS。ID/type/visibility/nameの分離 | hiddenの大量再収集 | 現在の同一動画・同一条件での差。プレビューAPIのowner有無とは別 |
| 共有「ニコニコ解析の概要.md」 | 保存HTMLにプレビュー要素があるという静的確認 | HTMLだけから動作を推定すること | イベント、取得元、寿命、音量状態 |
| 共有「ブラウザ通信記録3の解析結果.md」 | 保存記録：preview 59成功/1失敗、HLS、コメント。配信JSと通信を分離 | 既存全記録の再解析・新規大量通信 | previewから検索カードへの呼出経路。ホバーイベントとの直接対応 |
| 共有「Zenza改良で判明した追加解析・20260917.md」 | 他者によるstoryboard一般会員取得・広告owner補完の報告 | storyboardの再取得 | シーク画像の条件を一覧の動画へ流用できない。導入コードの優先順 |
| COMMENTS-READ.md / 共有R12 | 過去100成功の構造と固定OSS。threadKey、params、出力形式の差 | 全コメント再取得 | ホバーで選ぶtargets、描画・時刻・件数 |
| COMMENT-RENDERING.md / 共有R15A・R15B | niconicomments固定版の合成時間・矩形衝突。2.81秒差の限定重なり | 既存7＋6ケースの再実行 | 公式rendererとの同一性、実字形・pixel、ホバー固有フィルター |
| ZENZA-NVAPI-AND-CACHE.md | kphrx固定派生版の静的確認・合成TTL。updatedAtは取得日時ではない | 実利用者DBの走査 | 利用者指定版との照合、名前・アイコンの補完経路 |
| 今回提供outerHTML | stage/inner/content/video/comment/canvas等の断片 | 元HTML・blob文字列のGit保存 | タグだけではmuted property、開始位置、API、イベント所有者は不明 |

既存資料の固定参照：[研究基点の資料一覧](https://github.com/ButaMonky/niconico-api-research/tree/352b676325b3559b73eb93f8560e1b76bdbe89a7/docs/research/niconico)。共有6資料のhashと保存JSの固定出典は[今回の出典台帳](evidence/hover-preview-fixed-sources-20260920.json)。原記録や資料のhashは同一入力の識別用で、公開集計だけから生記録を復元できるものではない。

今回追加した根拠は、保存済み公式JSの一覧→preview→HLS/コメントの静的接続、保存記録の1組のキー等値照合、指定Zenza版の7件の合成実行。実ブラウザはサイト安全ポリシーにより1回の接続試行を拒否され、別経路への迂回をしていない。[引継ぎ本文](HOVER-PREVIEW-HANDOFF.md)と[閲覧者の確認票](HOVER-PREVIEW-OBSERVATION.md)へ進む。
