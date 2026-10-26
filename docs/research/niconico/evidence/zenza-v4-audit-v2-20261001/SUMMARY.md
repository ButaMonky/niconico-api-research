# 新規知見記録 — ZenzaWatch Watch V4追加監査 v2（2026-10-01）

## 記録の位置づけ
正本UPDATE-GUIDE.mdに従う取り込み待ちcontribution。原監査F01〜F14を18単一主張へ分割し、正常経路6主張を加えた24件。offline-test 23件、static 1件。24個の独立バグではない。
既存NICO-WATCHV4-20261001-ZENZAは公開動画再生の旧実測であり、今回と矛盾しない。削除・置換せずrelated_findingsで関連づけ、supersedesは空とする。

## 原監査の条件
ZenzaWatch 2.7.100-task171 / develop d4d1f7892d6960b76610aea20b78f0c7a032666c。公開用ローカルはTask157 / 321a16a62abca6bb5894afdde1ffa6d1726fb0f7。導入済みUserscript版は未確認。
最終プローブは2026-10-01 14:01:00.224 JST、Windows / Node.js v24.19.0。実製品関数を抽出し、通信・保存先・一部時計を人工環境へ置換した。
既存関連97件は全体992件の内数。原監査で両方成功。追加27ケースは10成立・17期待未達。今回はテストを再実行していない。
実投稿、ログイン状態の公式履歴before/after、再開位置再読込は未実施。公開Watch JSONの試行はERR_TUNNEL_CONNECTION_FAILEDでHTTP応答未観測。経路障害をAPI廃止・作品不存在の根拠にしない。

## 登録一覧
ID共通接頭辞: NICO-ZENZA-20261001-AUDITV2-。P13はPOSITION-FINALの対照条件として保存し、全27ケースを対応づけた。

| ID末尾 | 原監査 | プローブ | 区分 | 内容 |
|---|---|---|---|---|
| TREE-FLAG | F01 | P01 | offline-test | V4変換でツリー不明をfalseへ固定する |
| WATCH-PAGE | F02 | P02 | offline-test | V4メタ情報を視聴ページと判定できない |
| OWNER-FALLBACK | F05 | P03 | offline-test | lazy欠落時に初期channel情報を失う |
| NO-POST-TARGET | F07 | P04 | offline-test | 投稿対象なしで動画情報の解析が例外になる |
| PARTIAL-SERIES | F05 | P05 | offline-test | 部分シリーズでnextVideoが例外になる |
| QUALITY-ORDER | F08 | P06 | offline-test | 真偽値比較が画質候補を降順にしない |
| TREE-BODY | F03 | P07 | offline-test | 不正な親子応答が空の成功に変換される |
| TREE-PARTIAL | F03 | P08 | offline-test | 親取得失敗と子0件を合計0件と表示する |
| TREE-STALE | F04 | P09 | offline-test | 旧動画の親子結果を新動画の追加処理へ渡す |
| POSITION-HTTP | F09 | P10 | offline-test | 再開位置PUTがHTTP403でもresolveする |
| POSITION-FINAL | F10 | P12 | offline-test | 1秒間引きが終端0秒の保存も落とす |
| POST-ACK | F12 | P15 | offline-test | 不完全な成功ACKを成功として扱う |
| POST-BODY-TIMEOUT | F11 | P18 | offline-test | ヘッダー後の本文停止で投稿中が残る |
| POST-KEY | F12 | P24 | offline-test | 投稿キー欠損でもPOSTへ進む |
| ERROR-LOG | F14 | P25 | offline-test | 再生不可エラーログに人工認証値が残る |
| HEATMAP-STALE | F13 | P26 | offline-test | reset後に古いヒートマップ画像を通知する |
| POSITION-API | F09 | P27 | offline-test | 再開位置PUTが本文meta500でもresolveする |
| TAG-KEY-V3 | F06 | 静的 | static | タグ編集キー更新に旧v3専用参照が残る |
| POST-CHAIN | 正常経路 | P16,P21 | offline-test | V4変換から投稿・元動画の履歴保存まで成立する |
| POST-NO-RETRY | 正常経路 | P17,P23 | offline-test | 非トークン失敗2条件で再投稿しない |
| TOKEN-RETRY | 正常経路 | P22 | offline-test | 明示トークン拒否後の限定再試行が成立する |
| INPUT-IMMUTABLE | 正常経路 | P19 | offline-test | V4変換が入力JSONを変更しない |
| POSITION-GUARDS | 正常経路 | P11,P20 | offline-test | 再開位置保存のローカル条件が未送信を守る |
| POST-KEY-403 | 正常経路 | P14 | offline-test | キー取得403では投稿せず投稿中を解除する |

## 再利用の境界

正常投稿の連結経路、明示トークン拒否時の限定再試行、非トークン失敗時の再投稿抑止を修正後も維持する。POST送信後のtimeoutを理由に自動再送しない。サーバー受理・ローカル保存・表示の成功は別状態。

公式の視聴履歴一覧、公式再開位置PUT、Zenza内部の履歴、ブラウザーURL・既読リンクの4層を混同しない。ユーザーの成功報告を否定せず、再開位置のエラー無視と最終保存の間引きは独立問題として扱う。短尺・ID照合・ログイン条件は製品ガードであって公式仕様ではない。

親子の未取得・失敗を0件へ、metadata欠落を不存在へ変換しない。部分series・投稿対象なし等は人工入力で、公式がその形を返すか未確認。ソート・ヒートマップ・間引き等を一律にV4が原因と主張しない。

エラーログには人工authKeyが残る条件を再現しただけで、実キー流出や外部送信の観測ではない。共有資料に実Cookie・実キー・実ユーザー本文を追加しない。

## 証拠の扱い

probe-results.jsonとaudit-probes.mjsは原監査のバイト一致コピー。PROVENANCE.jsonに原本ハッシュを保存する。VALIDATION.mdは原監査の確認記録であり、新規実行結果ではない。STATIC-TAG-KEY.mdは旧v3依存の静的根拠。

**audit-probes.mjsを証拠フォルダ内で実行しない。** 実行すると隣のprobe-results.jsonを上書きするため、再検証は別の使い捨てフォルダへコピーし、repoパスを引数で指定する。

## 統合・公開

contributionsへの記録まで。findings昇格、API-CATALOG更新、全体export、commit/push、製品修正・配布は別作業。標準tools/validate.pyはfindingsだけを検査するため、contributionsを検査した証拠にはならない。

今回は標準検証スクリプトを含む実行要求がツール安全確認で拒否され未実行。設定変更や別経路での実行はしない。追加分自身のJSON・ID重複・出典参照・ハッシュ・既存ファイル保全の確認は保存完了票で区別する。
