# 令和のダラさん記録由来の追加知見（2026-10-01）
原資料はユーザー提供HTML/HAR/掲示板テキスト。生HAR・実キー・本人情報・署名付きURL・メディア本体はここへコピーしない。
HTML SHA256: 0dfe3b066eb2195f4f0ae2310117dfdb204e119bae2d410dc009a71c72960f5a
HAR SHA256: ef20c31d71fa16f2394c8a26d4ef83d9b8086704b75b8566ee0a1f5f2154c9ab / 26019138 bytes。
掲示板テキスト SHA256: 49e45c73f3c7a7f70799ecfe289ddd16a20f39913956eb9e466e1e5d1e8f845b
HAR全体は末尾文字列が閉じずJSON不成立。log.entries先頭から完全オブジェクトだけを解析した201件（index 0〜200）を使用。途中のindex201以降は補完・再生・推測しない。
HTML serverTime 2026-10-01T14:48:31+09:00、HAR index1のHTMLは14:49:18+09:00。双方so46839011でdata.response.media.domandの旧形式、$watchV4なし、hasContentTree=true、billingType=free。全サイト恒久rollbackは未確認。
掲示板#2537（07:59）の一部アニメ失敗と#2539〜2542（13:33〜14:18）のwatchV4欠落は別現象として扱う。第三者報告は公式仕様と同一視しない。
HAR86は公式HLS作成POST201（映像4×音声2の8組）。102master、110/111/120media playlist、112/113/146init、116/118/152鍵、複数映像音声セグメントはいずれも200。鍵は16byteだが値は保存しない。Zenzaの失敗要求は完全部分で特定できない。映像デコードや全尺再生の証明ではない。
HAR0/89/103/104はheartbeat付きHLS POSTの200 ACK。eventはend/start/play/impression。contentUrlは ?accepted=true&actionTrackId=[redacted]&data=[redacted] というquery-only文字列。201の署名付きmaster URLとは別であり、全応答を再生URL扱いしない。
mediaはHLS version6、AES-128、EXT-X-MAP、media sequence1、237セグメント。CODECSはavc1.4d4020/avc1.4d401eとmp4a.40.2、24fps。AES方式やhls.js版差だけをダラさん原因と断定しない。
公式JS PlayerCurrentTime-ivYbzHmw.js（SHA256 1949ceb63c7592a7ad7024aec3857291179846481ace716c08117694892e6e6a）の文字位置54289付近で、PUT /v2/users/me/watch/history/playback-position、Content-Type application/json、content:{videoId:o.video.id,seconds:c?0:s.getCurrentTime()}、withCredentials:!0を確認。
HAR2は同v2ルートのOPTIONS200だけ。完全部分に実PUT成功はない。旧v1廃止とは断定しない。canonical videoIdとcontextWatchIdを区別する。
公式JS dist-CweCUift.js（SHA256 c732a337ecac8c2c80bb545ca592003ea0add827f72b0ea4b9ec433fce3e9ea1）の文字位置7527付近に共通nvapi headersの "X-Niconico-Language":String(n.get().language) がある。
公式JS enum-D-U9K0cq.js（SHA256 241f6b79b8506bb9850c90333bfa3f3c302574bb2d44aa54568ccd4090c18840）の2886付近にGET /v1/comment/keys/post、threadId query、同クライアントe.requestがある。掲示板#2524にも言語header追加案。実APIのheader有無A/B比較は未実施。
公式JS PlayerCurrentTime-ivYbzHmw.jsの10083付近でKEY_EXPIRED時にCt({isLogin:!0,watchId:t.video.id,actionTrackId:t.client.watchTrackId,noSideEffect:!0,skips:[`adult`]})からtag.edit.editKeyを再取得する処理を確認。
Ctの実装元dist-DZ6PTlSG.js（SHA256 4b44906a7effd120baa5659608e1280141f29cf7aef807aa196e1b6c1aad8944）の2062付近には /api/watch/v3/{id} と /api/watch/v3_guest/{id} が残る。キー失効の本番応答は未観測。機械的なv4 URL置換はしない。
公式JS PlayerSeekBar-CGd3RUUk.js（SHA256 1d19d4f81e50f9801077d76407ace9eb97b06cc8cf9bcf00c25fca5c73e7624b）の706201付近に hls.js version 1.6.16。対象Zenza src/_hls.jsは1.7.3固定。版の比較条件でありdowngradeの根拠ではない。
HAR124コメント応答200にdata.voltageZone.heatmapがあり20個の数値。尺度・NG反映・時間対応は未確認。既存のローカルHeatMapと即置換しない。
HAR126 storyboard作成201、155 metadata200。通常会員状態、160x90、10x10、interval10000。画像本文はHARにない。既存Task070の補強であって今回の新実装ではない。
公式mainにgridArea:`[player]`、CSSにも対応selectorが残る。二重再生をselector変更だけで説明しない。
検証: followup-test-results.jsonは2026-10-01T06:03:46.905Z、10件中9成立・D05言語header1未達。実製品関数、通信はstub。既存992件は再実行していない。製品5ファイルは検証前後hash不変。
公開GitHub developを今回照会し321a16a62abca6bb5894afdde1ffa6d1726fb0f7（Task157）、ローカルmainはd4d1f7892d6960b76610aea20b78f0c7a032666c（Task171）。別環境のClaude Code作業状態と導入済みUserscript実版は未確認。
結論: ダラさん固有再生は未解決。旧形式解析の再現試験は通る。新規修正候補はgetPostKey言語header、既存F09/F10へv2契約確認を追加。製品修正・公開・インストールはしていない。
