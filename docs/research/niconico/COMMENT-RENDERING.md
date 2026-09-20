# コメント描画：時刻の丸めと表示・衝突の境界

R15-A、2026-09-20 JST。主条件は「単一・無衝突・既定長のコメントが、vposMsからどの刻みに入り、いつ描画対象から外れるか」。`ue/shita`を主対象、`naka`を同じ寸法の対照にした。投稿・キー発行・ニコニコAPI通信0、本体/Zenza固有コードの解析・変更0。

## 新しく確認したこと

1. 固定版niconicommentsのv1変換は`floor(vposMs / 10)`。10000msと10009msはどちらも1000csになる。描画呼出しの時刻はミリ秒ではなくセンチ秒。元のミリ秒値を上書きして失わず、描画用に別の値を作る設計に使える。
2. `ue/shita`の単一コメントは既定300csをtimelineへ登録するが、衝突表への登録は281刻み。**表示期間と衝突判定期間を同一視しない**。
3. 同じ`long=300`でも`naka`は前後に登録期間があり、画面外判定もある。今回の寸法ではtimeline588刻み、矩形が画面内と判定され描画コールへ進むのは489刻み。longを全位置共通の「画面に見える秒数」と扱う仮説は成立しない。

証拠は固定コード`CONFIRMED-CODE`と隔離実行`SYNTHETIC`。フォント・字形のpixel描画、実ブラウザ、公式プレイヤーとの比較はしていない。「公式互換」は作者の目標・説明であって、今回の確認結果ではない。

## 固定出典と対象版

作者xpadev（xpadev-net）ほか、[niconicomments](https://github.com/xpadev-net/niconicomments)。commit **`d3eb388197b9e40c6e9c592e83a37ecc6ab39fcd`**、commit日時2026-09-14T15:14:55Z、package.jsonのversion **0.4.1**。2026-09-20にdevelopを解決してcommit固定した。release tag・配布bundleとの一致は別途未確認。

[出典台帳](evidence/comment-render-fixed-sources-20260920.json)に作者、URL、確認日時、11ファイルのhashと参照関数を保存。複数ファイルを横断するため浅い部分cloneをローカルのignore領域に保持し、共有ZIPへ含めない。LICENSEはMIT表記を確認したが、今回外部ソースの大量転載や製品への導入は行わない。

| 固定ファイル | 今回の確認点 |
|---|---|
| [src/input/v1.ts](https://github.com/xpadev-net/niconicomments/blob/d3eb388197b9e40c6e9c592e83a37ecc6ab39fcd/src/input/v1.ts) | data.threads相当から内部形式へ変換、vposMsの切捨て、commands→mail |
| [src/utils/comment.ts](https://github.com/xpadev-net/niconicomments/blob/d3eb388197b9e40c6e9c592e83a37ecc6ab39fcd/src/utils/comment.ts) | long既定値、固定/移動timeline、衝突登録、getPosX/Y |
| [src/comments/BaseComment.ts](https://github.com/xpadev-net/niconicomments/blob/d3eb388197b9e40c6e9c592e83a37ecc6ab39fcd/src/comments/BaseComment.ts) | shitaのY反転、画面外矩形の除外、draw呼出し |
| [src/main.ts](https://github.com/xpadev-net/niconicomments/blob/d3eb388197b9e40c6e9c592e83a37ecc6ab39fcd/src/main.ts) | drawCanvasのtimeline検索にMath.floor(vpos)を使う |
| [src/definition/initConfig.ts](https://github.com/xpadev-net/niconicomments/blob/d3eb388197b9e40c6e9c592e83a37ecc6ab39fcd/src/definition/initConfig.ts) | canvas1920x1080、移動範囲1530、padding195等の既定値 |

補助関数の型境界・ユーザー番号割当・配列登録はformat.numeric.ts、xmlDocument.ts、array.tsを使用。テスト用個人コメントや画像は読み込まず、合成入力だけを使う。

## 入出力とAPIとの境界

```yaml
component: niconicomments
revision: d3eb388197b9e40c6e9c592e83a37ecc6ab39fcd
package_version: 0.4.1
status: CONFIRMED-CODE; SYNTHETIC
checked_at: 2026-09-20
endpoint: none (renderer; no API call in this experiment)
authentication: none
client: isolated Node24 timing and geometry functions
input:
  api_field: vposMs
  internal_field: vpos
  conversion: floor(vposMs / 10)
  drawCanvas_unit: centiseconds
  commands: ue/shita/naka (loc supplied directly after conversion in probe)
output: timeline membership and geometry draw coordinates; no pixels
```

API取得・過去ログ・投稿はそれぞれ[取得](COMMENTS-READ.md)、[過去ログ](COMMENTS-HISTORY.md)、[投稿](COMMENTS-POST.md)を参照。このレンダラーは今回の経路でCookie/threadKey/postKeyを使用しない。表示時刻は投稿時刻`postedAt`や履歴境界`when`と別物。

`fromV1`はvposMsを切り捨て、本文をcontent、commandsをmailへ渡す。READMEの描画例も動画の秒を100倍してdrawCanvasへ渡す。今回の診断は変換helperを直接実行し、完全なv1 responseのschema検査は行わない。locは解釈済みとして与えるため、文字列commandのparser受理や優先順位の試験でもない。

時刻単位の1cs（センチ秒）は10ms。この資料の「刻み」は1csごとの整数標本を指す。今回の非負整数ms入力で切捨て誤差は0または9msだった。一般式では0〜9msになるが、負値・小数・不正型への実サービス/公開parserの対応を今回保証しない。描画timeline検索の切捨てはmain.tsのコードで確認し、診断側で同じ検索を行う。main.drawCanvas全体は実行していない。

## 合成条件と結果

毎回別の単一コメント、幅300・高さ60、canvas1920x1080、空の衝突表、位置計算の遅延なし。文字計測を実行せず寸法を直接注入する。NicoScript・逆方向・ban・CA groupは適用しない。既定long300は実コードのnormalizeCommentLong(undefined)から取得。

| 入力vposMs | 内部vpos（cs） | loc | timeline登録（両端の整数を含む） | 衝突登録 | x / y |
|---:|---:|---|---|---|---|
| 9999 | 999 | ue / shita各1件 | 999〜1298（300刻み） | 999〜1279（281刻み） | 810 / 0または1020 |
| 10000 | 1000 | ue / shita各1件 | 1000〜1299（300刻み） | 1000〜1280（281刻み） | 810 / 0または1020 |
| 10009 | 1000 | ue / shita各1件 | 1000〜1299（300刻み） | 1000〜1280（281刻み） | 810 / 0または1020 |

固定位置の境界サンプルは開始−1で対象なし、開始と終了直前で描画コールあり、開始+300で対象なし。開始1000csの場合、1299.9csでもtimeline1299を参照して描画コールがあり、1300csではない。これは丸めた開始時刻からの半開区間[1000,1300)に相当する。`ue`は上端0、`shita`はcanvasHeight−posY−height=1020。xは(canvasWidth−width)/2=810。衝突のない今回の条件に限る。

固定衝突表はj<=max(long−20,0)の条件で登録するため、long300ではj=0〜280の281刻み。表示timelineはj=0〜299。**最後の19刻みの描画が残っていても、新たな衝突登録範囲とは一致しない**。2件目との実際の重なりはまだ試験しておらず、次の候補とする。

`naka`対照は入力10000msを1件だけ使用。同じlong300と幅300でtimeline837〜1424（588刻み）。BaseComment.drawの矩形判定を通って_drawへ到達する整数刻みは858〜1346（489刻み）。1000csでx1271.25、1300csでもx約−90となり、右側部分が画面内に残る。固定コメントと同じ1300csで終了するわけではない。これらは**1csごとの標本**であり、連続時刻の厳密な可視境界や字形の可視時間ではない。画面外の登録を即描画と数えず、寸法・速度設定に依存する。

## 再現手順と制約

固定commitを別途取得し、Python標準ライブラリとNode.js24で次を実行する。作業ディレクトリはリポジトリ内の`docs/research/niconico`、または研究ZIPの展開先直下。ソースcheckoutには絶対パスか、その作業ディレクトリからの相対パスを指定する。取得後の診断はネットワーク不要。

```sh
python tools/probe_render_timing_offline.py <pinned-niconicomments-checkout>
```

6ソースの改行をCRLFからLFへ正規化して固定Git blobのhashを検査し、TypeScriptの型/import/exportを除去してVMに読み込む。numeric/user割当は対象関数だけを抽出し、valibotのschema構築・検証は実行しない。fromV1、期間正規化、固定/移動timeline処理、座標計算、BaseComment.drawを実行する。drawの受け手は合成objectで、文字描画・背景・装飾処理は無作用の記録先に差し替える。実fetchは禁じ、外部renderer/フォント/package依存をinstallしない。

成功条件は7ケースの期間・刻み数・座標・境界assertが一致すること。[保存結果](evidence/comment-render-timing-offline-20260920.json)には入力条件と数値だけを残す。性能・FPS・メモリ・実ブラウザのレンダリング・公式再現性を測定したとは扱わない。[検証記録](VERIFICATION-R15-20260920.md)。

## 将来の利用と次候補

コメントアート生成では、元のvposMs、内部vpos、timeline登録、矩形可視判定、衝突期間を別の値として管理する。時刻だけを合わせてもフォントや幅・高さが違えば位置や移動時間は変わるため、生成側の寸法とレンダラー版・設定を固定して比較する。これは引渡し提案で本体実装はしない。

R15-Aは単一コメントの境界を確認できたため終了。R15全体は限定完了とし、フォント/改行/サイズ/色、Flash/HTML5、owner/layer、重複command、NicoCommentDLは未調査のまま残す。次のR15-Bはue/shitaの2件目を+281cs/+300csに置く条件で、残存描画と衝突回避を比較する価値がある。現段階では重なりの有無はHYPOTHESIS。

2026-09-20：R12のvposとvposMsの単位説明へ、固定レンダラー固有の切捨てと境界条件を追加。旧API一般の変換規則や公式プレイヤー仕様へ一般化せず、既存記録は保持する。

公開前訂正：Windows Gitのcore.autocrlfによりcheckoutがCRLFになっていたため、一次hashをGit blob（LF）基準へ訂正。旧checkout hashも台帳へ保持した。11ソースの差が改行だけと確認し、診断を元CRLFと別途用意したLF双方で実行、7条件の結果一致を確認した。解析結論に変更なし。
