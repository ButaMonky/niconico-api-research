# フォロー新着のクリック遷移（2026-11-12）

APIではなく公式WebクライアントのイベントとSPAルーターの研究です。提供HAR内のコードとinitiatorを解析しました。新たな実サイト操作はしていません。

## 確認した経路

画像・タイトルのクリック → CommonHeaderルート → 最寄りのa要素 → commonHeader:linkClick（元のnativeEvent付き）→ Layout → PanelのSPAナビゲーター → watch loader。

Layoutはauxclick、Ctrl、Meta、target=_blankを除外しますが、defaultPreventedを確認しません。先にpreventDefaultしても公式ルーターが動きます。通常カードにはdefaultPrevented確認があり、同じ対策では結果が違います。提供記録には公式ルーター由来のfetchとZenza起動由来のfetchがありました。window.openだけを止めてもこの経路は止まりません。

## 修正に使える境界

CommonHeader.default.prototype.onという公開イベント登録口があります。Zenzaが扱う元のEventを識別し、そのイベントの公式遷移への配送だけを止める方式を検証中です。他のスクリプトの名前・内部状態やURL書換えには依存しません。

公式loaderはscriptのtarget loadでインスタンスを作ります。document capture loadで先に登録口を接続できます。既にマウントされた場合、公開APIに個別offがないため既存リスナーを安全に置換できません。その場合は対象ヘッダークリックに限り従来の伝播停止を使います。

## 証拠と限界

[finding](findings/NICO-BROWSER-20261112-HEADER-ROUTING.json)、[匿名化した証拠](evidence/common-header-click-20261112.json)。原本全文・HARは配布せず、ハッシュは照合用です。この資料だけで原本を再計算できません。

抽出した公式コールバックのオフライン再現で取消済みクリックでもルーター呼出しが生じることを確認。製品側の隔離Chromeでは早期・動的読込・遅延接続・通常カード・対象外操作を検証しました。実サービスでのユーザー検証、userscript実行worldと起動順、将来のAPI変更は未確認です。ランキングNGの保存成功を保証する研究ではありません。

製品コードは本研究に複製していません。利用許諾は既存公開ガイドに従い未選定です。
