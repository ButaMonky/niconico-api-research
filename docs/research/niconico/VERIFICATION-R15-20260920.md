# R15-A検証記録

2026-09-20。固定niconicomments0.4.1 commit d3eb388197b9e40c6e9c592e83a37ecc6ab39fcdを用い、7合成条件のtimeline/座標/境界assertを確認。新規ニコニコ通信・投稿0。schema/command parser、文字計測、pixel描画、main.drawCanvas全体、実ブラウザ、公式比較は未実行。

出典hash・JSON形式・リンク・公開差分・未追跡・秘密値・ZIP manifestを検査し、最終結果を追記する。外部cloneはignore領域のみ、共有物に含めない。

## 最終確認

- 公開27 findings / 27 sourcesの形式・hash、公開111ファイルとZIP111ファイル＋manifest、リンク・秘密値検査を通過。
- 独立レビューで固定ソース11ファイルのhash/サイズ、診断7ケースの全出力と保存証拠の一致を確認。Critical/Importantなし。
- Minor2点を修正：再現コマンドの作業ディレクトリを明示し、固定衝突表の端点・描画範囲端点・naka座標のassertを追加。7ケースを再実行し保存証拠と一致。
- 変更diffと未追跡ファイルは研究資料・診断のみ。cloneと生成ZIPはignore対象で、公開資料へ実認証値・実本文・個人識別値・ローカル絶対パスを追加しない。
- 上記は限定したコードと合成入力の検証。pixel描画・公式互換・文字計測・複数衝突・性能は検証済みと扱わない。
- 公開前のGit blob比較でWindowsのCRLF変換によるhash差を発見。11ファイルのLF正規化後一致を確認し、一次hashはLFのGit blobへ訂正、checkout hashも履歴として保存。診断はCRLF→LFだけ正規化し、CRLF入力とLF入力の両方で7条件・全出力一致を確認。初回のbytes直接一致検査失敗を隠さず、再現性の訂正として記録した。
