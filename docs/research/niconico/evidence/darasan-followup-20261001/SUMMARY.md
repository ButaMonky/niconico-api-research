# ダラさん・午後のWatch旧形式追補（取り込み待ち）

提供資料とオフライン試験の8主張。ダラさん固有の再生失敗は未確定。製品未修正。

- NICO-WEB-20261001-DARASAN-LEGACY [traffic] 10月1日午後の当該動画は旧Watch形式
- NICO-WEB-20261001-DARASAN-COMPAT [offline-test] 記録由来旧形式を現在のパーサーで読める
- NICO-WEB-20261001-DARASAN-POST-LANGUAGE [offline-test] getPostKeyが渡された言語をHTTPへ渡さない
- NICO-WEB-20261001-DARASAN-RESUME-V2 [static] 公式コードが再開位置v2 JSON契約を使う
- NICO-WEB-20261001-DARASAN-HLS-ACK [traffic] HLS作成応答とheartbeat ACKは別物
- NICO-WEB-20261001-DARASAN-HLS-VERSION [static] 公式bundleとZenza設定にHLS版差がある
- NICO-WEB-20261001-DARASAN-COMMENT-HEATMAP [traffic] コメント応答に数値20件のheatmapがある
- NICO-WEB-20261001-DARASAN-TAG-REFRESH [static] 記録公式コードにwatch v3タグキー更新が残る

CAPTURE_NOTES.mdに記録通信と公式JSの根拠、followup-test-results.jsonに10件中9成立・D05未達を保存。JSON形式だけでなく由来と未確認を区別する。
既存監査v2を置換せず、post-key言語と再開位置v2を追加する。V4-only化、認証値保存、POST結果不明の自動再送、HLS版の無根拠変更をしない。
再現スクリプトは隣のfixture/resultへ書き込むため、必ず使い捨てフォルダのコピーから実行する。生HAR・鍵・映像本体は含めない。
