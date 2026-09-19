# ZenzaWatchのnvapi利用と既取得metadataの再利用候補

確認：2026-09-20 JST。目的はNG判定に必要なタグ・投稿者を少ない通信で得る**新しい候補**の抽出。製品変更・実ユーザーのキャッシュ読み出しは行っていない。今回ニコニコ通信はタグGETの1回だけ、広告通信0回。

## 新しい発見：キャッシュのupdatedAtはタグ取得日時ではない

**watch-infoにはタグ・投稿者を保存する経路がある。しかし読出しでもupdatedAtが更新されるため、これを最新タグの根拠にしてはいけない。** さらにthumb-infoでは、24時間の期限比較より先にその日時更新を行う経路がある。固定した公開コードを合成データで部分実行すると、7日前の内容が変わらないまま24時間以内のキャッシュと判定された。

証拠はCONFIRMED-CODEとOFFLINE-TEST。実ブラウザでの症状再現、利用者の導入版での動作確認、サーバー上の最新タグとの比較は未実施。現行サービスや全Zenza派生版の不具合を断定する結果ではない。

## 対象版と参照方法

| 作者・対象 | 固定revision | commit日時 | 今回の扱い |
|---|---|---|---|
| [segabito/ZenzaWatch](https://github.com/segabito/ZenzaWatch) | `267bc5cabfa2dda635c28f91b208d9e3093f6fcf` | 2021-07-19 UTC | NVApi.jsを比較した基点。現行実行は未確認 |
| [kphrx/ZenzaWatch](https://github.com/kphrx/ZenzaWatch) | `1dd027d324564f0c0299cc3242073623b633c5fc` | 2026-04-23 UTC | 今回選んだ派生版。利用者の導入版とは未照合 |

作者・ファイル・固定URL・SHA256・確認時刻は[証拠台帳](evidence/zenza-nvapi-cache-20260920.json)に記録。必要ファイルのURL参照後、呼出元を横断するためsparse git cloneを使用した。clone・外部コード全体は共有しない。repoの更新日と個別API経路の現行性は別。

## 保存・読出しの契約

| 項目 | watch-info | thumb-info |
|---|---|---|
| IndexedDB | name `watch-info`、version 2 | name `thumb-info`、version 1 |
| store / primary key | `cache` / `watchId` | `cache` / `watchId` |
| 保存される情報 | `videoInfo`、videoId、ownerId、再生位置・コメント等 | `thumbInfo`、XML、videoId等 |
| 必要なmetadata候補 | `videoInfo.tagList`、`videoInfo.owner`、`videoInfo.videoId/watchId` | パース済みthumbInfoのタグ・投稿者候補。今回その全項目は未精査 |
| 読出し | `get` → `cacheDb.updateTime` | `get` → `cacheDb.updateTime` |
| updatedAt | 読出し・各種putで現在時刻に変わる | 読出し・putで現在時刻に変わる |

呼出経路と重要な条件：

1. `src/NicoVideoPlayerDialog.js`は視聴情報ロード成功後に`WatchInfoCacheDb.put(watchId,{videoInfo})`。`VideoInfoModel.toJSON()`はgetterを列挙し、owner・tagList等を保存する。tagListはname/isLocked等を含むモデル由来で、lock情報を捨てて単なる文字列集合へ早期変換しない。
2. `WatchInfoCacheDb.ownerId`は`videoInfo.owner.linkId`由来。`user/<id>`等になり得るため、数値の投稿者IDとして使わない。`videoInfo.owner.type/id`を分け、channelをuserへ変換しない。
3. 再生位置・視聴回数等のputでも、古いvideoInfoを保持したままupdatedAtを更新する。取得日時の代用品にならない理由は読出しだけではない。
4. `ThumbInfoLoader.js`は24時間のexpireTimeを渡す。`GateAPI.js`は期限を計算してからdb.getを呼ぶが、そのgetがupdatedAtを現在に変えるため、返された日時との比較は古い取得内容を排除できない経路になる。
5. `src/_template.js`は`.nicovideo.jp`ホスト条件で`window.ZenzaWatch.debug.WatchInfoCacheDb`を公開するコードを持つ。他ホストでは同じ公開形を保証しない。userscript隔離・実導入版・ロード順・IndexedDB originを含め、NG側からの可視性は未試験。
6. 通常の視聴開始では`VideoInfoLoader.load`とキャッシュgetを併用している。キャッシュがあることから「Zenza本体は視聴情報通信を省いている」とは推定しない。

参照：[WatchInfoCacheDb](https://github.com/kphrx/ZenzaWatch/blob/1dd027d324564f0c0299cc3242073623b633c5fc/packages/lib/src/nico/WatchInfoCacheDb.js)、[ThumbInfoCacheDb](https://github.com/kphrx/ZenzaWatch/blob/1dd027d324564f0c0299cc3242073623b633c5fc/packages/lib/src/nico/ThumbInfoCacheDb.js)、[GateAPI](https://github.com/kphrx/ZenzaWatch/blob/1dd027d324564f0c0299cc3242073623b633c5fc/packages/lib/src/nico/GateAPI.js)、[IndexedDbStorage](https://github.com/kphrx/ZenzaWatch/blob/1dd027d324564f0c0299cc3242073623b633c5fc/packages/lib/src/infra/IndexedDbStorage.js)、[VideoInfo](https://github.com/kphrx/ZenzaWatch/blob/1dd027d324564f0c0299cc3242073623b633c5fc/src/VideoInfo.js)。

## オフライン再現

[診断](tools/probe_zenza_cache.py)は固定Git blobのSHA256を検証し、updateTimeメソッドと期限条件だけを取り出して合成ストレージ上で実行する。Python・Git・Nodeが必要。通信・ログイン・ブラウザ・ユーザーDBは不要。

```sh
python docs/research/niconico/tools/probe_zenza_cache.py <local-zenza-git-checkout>
```

対象commitがローカルGitに存在することが前提。取得済みコード以外を自動ダウンロードしない。期待値は`before_hit:false`、`after_hit:true`、`tags_unchanged:true`、`writes:1`。欠落レコードはnullのまま。実IndexedDB/worker/GCを再現する試験ではなく、TTL判断のコード上の問題を切り分けるもの。

## NG開発へ渡せる条件

- 現在表示している要求対象videoIdだけを照合し、タグ名・lock・owner type/id・対応するwatchId/videoIdを許可項目として読む設計候補。履歴全件を走査・出力しない。
- videoInfo全体はcsrfTokenや再生関係情報等を含み得る。丸ごと共有・ログ・別AIへ渡さない。既存getには書込副作用があるので「読み取り専用API」と案内しない。
- 再利用による追加0通信は設計上の候補で、ヒット率・速度・利用可能なoriginの実測ではない。100対象中k件を使えれば残り100−k件を補完する計算になるが、タグ鮮度が不明なら最新タグ判定の確定には使えない。
- source、対象ID、項目ごとの状態、確実な取得時刻がある場合のみその時刻を保持する。updatedAtから取得時刻を作らない。古い・欠落・型不明はunknownを維持する。
- 取得済み情報 → 必要ならsnapshot一括 → 索引欠落や最新タグ必須の対象だけ個別確認、が引き渡し候補。キャッシュ再利用だけでfallbackを削除しない。本体への採用は別work。

## nvapi群の把握範囲

`NVApi.js`は汎用fetchラッパーで、endpoint全体の一覧ではない。上記2版の同ファイルhashは同じだった。playlist・タグ・コメントキー等は個別モジュールにも実装されている。以下は**選択版の公開コードで確認した範囲**で、全nvapiや各APIの現在成功を保証しない。

| 機能・module | method / endpoint（基点はnvapi.nicovideo.jp） | 要求と応答のコード上の扱い | 認証・検証状態 |
|---|---|---|---|
| PlaylistApiLoader | GET `/v1/playlist/series/{id}`、`user-uploaded/{id}`、`mylist/{id}`、`watch-later`、`search` | userはsortOrder=desc、他のリスト既定はasc、sortKey=registeredAt。seriesはidのみ。searchは既定desc/registeredAtにoptions。meta.status=200、data.itemsを使用 | credentials include、X-Frontend-Id/Version。独立通信未確認。任意ID配列の一括lookupではない |
| TagEditApi | GET `/v2/videos/{videoId}/tags` | dataを利用。query/bodyなし、X-Tag-Edit-Keyを渡す | include、frontend 6/0、X-Request-With、X-Niconico-Language。今回の匿名・キーなしGETだけ400 |
| TagEditApiの編集系 | POST / DELETE 同tags経路 | tagをqueryへ付加するコード | 編集キーを使用。投稿・削除は実行していない |
| ThreadLoader | GET `/v1/comment/keys/thread`、`post`、`delete`、`nicoru` | threadはvideoId、他はthreadId、deleteにはfork=main | credentials include、frontend。コード確認のみ、キー値は保存しない |

playlistのsessionStorageキャッシュは5分というコード上のTTLを持つ。任意動画ID集合を投入できる証拠はなく、取得されたリストの転用候補に留まる。検索モジュールには別のsnapshot経路もあるため、メソッド定義だけから全画面の実呼出先を決めない。

視聴本体の`VideoInfoLoader`には`www.nicovideo.jp/watch/{id}?responseType=json`がある。nvapiだけを調べれば全情報取得経路を網羅できるわけではない。推薦、HLS access-rights、マイリスト、再生履歴等の追加箇所も見つかったが、今回はendpointと詳細仕様の全件監査を行っていない。コメント・再生関連は後続調査へ回す。

## タグGETの最小実通信と失敗条件

2026-09-20 05:08:17 JST、公開動画`sm15630734`に対してGET `/v2/videos/sm15630734/tags`を1回実行。Cookie / Authorization / X-Tag-Edit-Keyなし。一般会員のログイン条件ではない。

headerはAccept=application/json、Accept-Encoding=identity、X-Frontend-Id=6、X-Frontend-Version=0、X-Request-WithとOriginは`https://www.nicovideo.jp`、X-Niconico-Language=ja-jp、調査用User-Agent。query/bodyなし。完全な非秘密header一覧は証拠JSONにある。

結果はHTTP400、meta.status400、errorCode `INVALID_PARAMETER`、55 bytes、342.62 ms。本文は保存せずhashと項目だけ記録。再試行0。**このheader構成と匿名・キー省略の組合せで失敗**した。編集キーだけが不足原因、ログイン必須、API廃止のいずれも確定しない。ブラウザCORS試験でもない。直ちに認証付き再試験へ拡大せず、匿名で便利な単独タグ取得経路としての採用を保留した。

## 未確認と次候補

実導入版での可視性、キャッシュ被覆率・タグ鮮度・同一動画照合は未確認。ブラウザの安全ポリシーによる制約を迂回して調べない。

次は既存のAndroid/Web静的資料に候補がある`/v1/playlist/request`を優先。method・body・応答モデルをまず固定した公開資料から調べ、任意複数動画IDとowner/tagsを扱えるかを判定する。今回のZenzaでその呼出しを確認したわけではない。状態変更を伴う可能性や用途が不明なら送信せず、既知の`/v1/videos`や大量の広告境界試験を繰り返さない。

2026-09-20追加：R11の比較とともに、利用者の「新しい有用な発見を優先」という指示に沿って上記キャッシュ経路を保存。コード・合成実行・実通信の根拠を分離した。
