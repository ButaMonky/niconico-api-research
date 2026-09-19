# 検索初期データをNG判定へ再利用する

R05、2026-09-20 JST。**初期HTMLは32動画の投稿者IDをすでに持っていた。タグ一覧は持っていなかった。** 画面が受け取ったデータを利用できれば、投稿者情報を改めて取りに行く必要を減らせる。ただしuserscriptがそのデータを取り出せる実行時点はまだ実ブラウザで検証していない。

## 確認対象・根拠

認証なしGET `https://www.nicovideo.jp/tag/VOCALOID?sort=f&order=d`。研究用の公開タグであり、個人の履歴を利用しない。Python3.12 urllib/HTMLParserでHTTP応答のHTMLを解析し、ページJavaScriptは実行していない。headerはUser-Agent NicoNGResearch/20260920とAccept-Encoding identity。Cookieなし。最初の構造探索1 GET後、匿名化集計を保存するため1 GETを追加した。計2 HTML要求、追加の動画情報API要求0。

測定は04:04:48 JST、HTTP200、96704 bytes、440.16 ms（単発）。初回探索は96745 bytesであり、2回の本文を同一視しない。公開版のhash付きファイル名はmanifest-baf86e63.js、entry.client-BDJkQFwJ.js、bridge-D5WxNeTE.js。これらの名前は初期HTMLで参照されていた版の識別子で、この段階では全JS本文を検証した意味ではない。[証拠](evidence/browser-initial-data-20260920.json)。

## 情報の場所と利用範囲

HTMLの`meta[name="server-response"]`のcontentをHTML属性としてデコードし、JSONとして読む。HTMLParserやブラウザのgetAttributeは属性のエンティティを復元するため、何度も手動unescapeしない。経路は`data.response.$getSearchVideoV2.data.items`。

| 項目 | 今回の確認 | 再利用の意味 |
|---|---|---|
| items[].id | 32件、異なる32 ID | 表示要素と照合する主キー |
| items[].owner.id | 全32、文字列 | 投稿者NGの候補。数値への無条件変換をしない |
| owner.ownerType | 全32 user | user/channel/hidden/nullを同一視しない |
| items[].tag / tags | 全32でなし | タグNGは別の情報源が必要 |
| 初期HTMLのwatch/userリンク | 今回の抽出条件では0 | HTML本文にリンクがないことと動画情報がないことは別 |
| 読み込み後DOM | 未確認 | ブラウザの画面実行は環境のサイト安全ポリシーで拒否された |

CONFIRMED-LIVEはHTML応答とその構造に限定する。初期HTMLからリンクが0件だった結果は、描画後にもリンクがないという主張ではない。旧9月13日クライアントの解析では初期metaは読み出した後にremoveされるため、遅い時点でmetaが見つからない可能性がある。現在版の寿命はR06で別に扱う。

## 開発担当へ渡す取得契約

1. 初期データを取得できた場合、必要な項目だけを抽出する。meta JSON全体には認証関連データ等が混ざり得るため、全体のログ・保存・他AIへの送信をしない。
2. `videoId → {ownerId, ownerType, source, observedAt, pageKey}`の対応を保持する。ユーザーIDとチャンネルIDを別種として扱い、hiddenでも実在するIDを捨てない。
3. 表示DOMの動画IDと一致した行だけを使う。配列の並びや「何番目のカードか」だけで結び付けない。
4. metaなし・ownerなし・タグなしをNG非該当と解釈しない。必要な項目だけsnapshot/単独情報へ補完する。
5. 情報源ごとの取得時刻を保ち、ページ移動後の古い要求完了から新しいカードへ誤適用しない。SPA時の収集時点と失効条件はR06の範囲。

追加0は、ユーザーが通常表示で受け取った同じ初期データを抽出する場合の**設計上の通信数**。今回の研究では測定のためHTMLを取得しており、実装済み・通信削減率を実測済みという意味ではない。

タグについては[R04](METADATA-ACCURACY.md)のようにsnapshot欠落時の個別補完が必要。タグルールが存在しない場合や、投稿者等の既知項目だけで判定できる場合までタグを要求しない設計を候補にする。OR/ANDなどルールの意味に従い、必要項目がそろった時だけ判定を確定する。

## 制約と終了

現在ページはuserのみ。旧記録のhidden保持やchannelはこの32件で再現したわけではない。ブラウザ起動後のmeta寿命、拡張機能の実行世界、ログイン差、CORS、表示カードとの実結合は未確認。今回のブラウザ操作はサイト安全ポリシーで拒否され、別ブラウザ・間接実行へ切り替えていない。

R05は初期HTMLに限定した結果と実ブラウザ未確認の不足を記録して終了。次は公開JSの静的解析としてR06を進め、実ブラウザの観測が必要な部分は保留する。[タスク一覧](TASKS.md)、[次作業の指示文](NEXT-TASK-PROMPTS.md)。
