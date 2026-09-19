# ブラウザ・拡張機能からの呼出条件：未検証範囲

R07、2026-09-20。**現在の環境では実ブラウザ確認を完了できていない。** R05の公開ニコニコ画面への操作がサイト安全ポリシーに拒否された。ユーザー確認・自動承認審査の前に拒否されており、別ブラウザや間接実行による回避は行っていない。R07はBLOCKEDとして残す。CORSを失敗と判定したのではない。

| 経路 | 確認できたこと | 不足 |
|---|---|---|
| Pythonからsnapshot | R00の100件、R04の欠落を実通信確認 | ブラウザOrigin/CORS/preflightは別条件 |
| Pythonからnvapi /v1/videos | R03の単独成功・CSV失敗・反復部分返却 | ページ内fetchや拡張機能からの可否 |
| Pythonからgetthumbinfo | R04の2動画でタグ/投稿者 | ブラウザでのCORS、管理拡張の権限 |
| 公式検索route loader | 公開コードにcredentials include、mode cors、AbortSignal | 実際の遷移通信、ログイン差、追加通信数 |
| NGのGM.xmlHttpRequest / GM_xmlhttpRequest | 現行ThumbInfoとsnapshotコードに利用経路あり | 対象ブラウザ/管理拡張/版でのruntime検証 |

headerやOriginが必要かをここで一般化しない。通常ページ内fetch、ページ側から観測する応答、userscriptのGM経由は別の呼出経路として試験する必要がある。HTTP200を見ただけではページJSが本文を読めることの確認にならない。独自headerによるpreflightの有無・数は今回測っていない。

許可された検証環境が利用可能になった際の条件：対象ブラウザと管理拡張の版、実行世界、origin、credentials有無、header名、HTTPと本文status、返却ID集合、通常GET/OPTIONSの回数を記録する。Cookie・認証キーの値は保存しない。まず公開動画2件・1経路だけで確認し、無意味な失敗の繰り返しや設定の弱体化は行わない。

現時点の開発引き渡しでは、既に本体が使うGM経路を置き換える根拠は不足している。[実装引き渡し](IMPLEMENTATION-HANDOFF.md)の実装前確認事項として維持する。
