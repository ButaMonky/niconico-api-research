# 一覧ホバープレビュー引継ぎの検証範囲

2026-09-20 JST。公式と同等の実再生を検証した報告ではない。

- Git開始状態：作業ルートは未追跡の既存研究・共有物がある初期master、remoteなし。研究repoはclean、`codex/research-comment-rendering`。適用AGENTS.mdは確認した祖先・研究配下に見つからなかった。既存worktreeを保持し、R15Bから専用研究worktreeを作成。
- GitHub読取：既存公開先のvisibilityはPUBLICのまま、mainはR15Bより古い。OPEN PR #2〜#10を確認し、#10 headとローカル `352b676325b3559b73eb93f8560e1b76bdbe89a7` が一致。公開先・公開設定・ライセンスは変更しない。
- baseline：既存validatorで28 findings / 28 sourcesを検証。今回追加後は31 findings / 32 sourcesの形式・出典hashを検証する。
- 保存公式JS15ファイルを固定hashで記録。captureのhashは既存資料と一致。既存preview60件の集計と、選択したHLS/commentの等値結果だけを追加。原通信のkey/署名/本文はGitへ保存しない。
- 指定Zenzaのsource関数とdist関数で同じ7合成ケースを実行し、全ケース成功・出力一致。実通信0、DB読取0。モデル全体・実字形・実ブラウザを検証したとはしない。
- 独自実装を追加せず、診断・資料のみを追加。本体/Zenzaの既存変更を保持。無関係な製品テストやR12/R15の既存合成試験は繰り返さない。
- 公開対象は今回の追加・索引差分だけ。生記録、第三者JS全体、提供outerHTML、署名URL、実ID、検索語、個人パス、別タブ情報を含めない。synthetic fixtureは構造だけで再生可能なHTMLではない。
- 共有ZIPは今回の3 findings / 4 sourcesと関連資料・最小診断を選択する。過去の公開セットを丸ごと再配布しない。元のexport.pyの全件出力では今回の厳格な収録範囲を超えるため、今回の許可リストでmanifest/hashを生成する。
- 公開前に相対リンク、JSON、差分の秘密値候補、ZIP manifest、Git index上の出典hash、diff --checkを確認。機械検査は内容の正確性や個人情報が絶対ないことの保証ではなく、目視の対象限定と併用する。

ブラウザはサイト安全ポリシーで拒否されたため、実hover/音量/SPA/画面外/hidden/CORSの現在の動作は未確認。[確認票](HOVER-PREVIEW-OBSERVATION.md)へ明示した。未確認を埋めるための迂回は行わない。

## 実行結果

validatorは31 findings / 32 sourcesでPASS。Git index上の32出典hashが一致し、17 staged filesは研究資料配下だけだった。差分整形検査は成功。今回の15ファイル＋manifestの選択ZIPは3 findings / 4 sourcesで検証でき、ZIP内全hash・相対リンクが一致した。許可した合成ID以外の実動画ID、個人パス、raw blob URL、JWT・署名queryの候補は追加行・選択ZIPで0。対象内容も目視し、既存公開資料全体の再監査結果とはしていない。
