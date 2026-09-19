# 100件境界資料の公開前検証

対象：`SNAPSHOT-BATCH-BOUNDARY-20260920.md`と関連findings/evidence/tools。2026-09-20 JST。

- ローカル正本相当：`validate.py`で86 findings / 59 evidence sourcesの形式・参照・SHA256を検証。
- 公開選択版：3 findings / 3 sourcesを検証。sourceのSHA256を作業ファイルだけでなくGitのstage済みblobでも照合し、改行変換後の不一致がないことを確認。
- 匿名化証拠8要求のHTTP状態、100件の全返却・項目一致、101件ページ送り、version一致、queryから再構成したURLサイズをオフライン照合。
- exportのZIP整合性・全収録ファイルのmanifest SHA256・相対リンクを検証。過去の全研究セットを公開版へ混入していない。
- diffと全公開対象をレビュー。ローカル絶対パス、内部URL、メール、JWT、セッション/一時キーの実値、投稿者ID実値等のパターン検査に該当する漏えい候補なし。パターン検査だけで普遍的な秘密情報不在を保証できないため、収録範囲と項目も目視確認した。
- 独立レビュー後、再現コードの初回version取得失敗時の停止と最終version失敗理由を補強。`test_probe_snapshot_boundary.py`の2テスト（初回429・不正時刻・timeout、最終503）について、修正前の4失敗と修正後成功を確認。追加実通信なし。
- 診断コードのデフォルト実行は通信なし。公開版にもオフライン回帰試験を収録する。

## 本体の既存テストについて

研究用branchはGitHub masterの`ae324549449effd9c4c1e15d86b66d9fd11cbaae`を基準とした。`src/`・`scripts/`・`tests/`に変更なし。参考実行した`npm test`は95件中88成功・7失敗。失敗は全て`tests/core.test.mjs`のgenerated系で、次の存在しない生成物を参照するENOENTだった。

`dist/nico-nico-ranking-ng-v14.1-performance-pager-fix (2).user.js`

該当テスト：

- Config complete defaults, keys, sync order and transient setting
- Config restores stored values without writes or change events
- listener order, deduplication, unbind and thrown errors
- Store preserves key, default, write-before-event and silent sync
- ArrayStore normalizes IDs and text, preserves bulk duplicate behavior
- queued mutations survive rejected read and preserve persistence
- Config CSV round trip retains seven types, quoting and numeric IDs

通常の制限付き実行では子プロセス生成がEPERMになったため、権限付き実行で上記の結果を確認した。これは研究診断の回帰試験失敗ではないが、プロジェクト全テスト成功とは報告しない。本体のテスト修正は別開発作業へ残す。試験が変更した生成物は作業コピー内で元へ戻し、公開commitには研究資料だけを含める。
