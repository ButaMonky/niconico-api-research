# 提供されたmetadata関連報告の確認

確認日：2026-09-20 JST。R02。結論は **REPORTED**。提供資料の記載と内部整合を確認したもので、現在のニコニコへの再通信・原通信照合は行っていない（新規通信0）。元資料の`status: traffic`は提供者側の分類として保持し、今回独立確認した意味へ変更しない。

## 対象と出典

ユーザー提供のClaude / ZenzaWatch改良プロジェクトによる9月19日contribution ZIPから、9月16〜17日観測の検索・投稿者・件数に関する5 findingsと参照evidence 2件を確認した。9月19日のギフト等を含む全12件を承認したものではない。9月17日版と同じテーマを含む後続版を使用し、両版を独立した再現回数として数えない。

原ZIPと選択した各メンバーのSHA256、要求・応答・認証条件は[匿名化確認記録](evidence/community-metadata-review-20260920.json)。固定Web build hashは提供資料から確定できず、`nvpc_next 配信JS 2026-09-16時点`という報告上の版を記録した。提供資料は非公開ローカル入力であり、読者が元本文をhashだけから再検証できるわけではない。公開物には自分たちの要約だけを含める。

## 採用・保留の判断

| 報告 | 既知との関係 | 保存する判断 | 未確認・保留 |
|---|---|---|---|
| playlist/searchとv2/search/videoがpageSize100で100件返却 | 以前の32件観測と両立する追加報告 | 検索で選ばれた100動画を返す候補 | 任意100動画IDを指定するAPIとは別。Cookie不要かは当該比較で未確認 |
| pageSize100/page50が200・hasNext=false、page51またはsize101が400 | 上記pageSize未確定点への追加報告 | 未ログイン条件の境界観察として保存 | pageSize変更時のpage制限、会員差、連続50ページ取得は未検証。「普遍的に最大5000件」は採用しない |
| decorationへ100 ID指定、200で62返却 | 既存80全返却の観測と標本が異なる | 指定数100・返却62・差38を分離 | 異なる実在ID数・欠落理由・上限不明。100件全取得成功ではない |
| getthumbinfoのuser項目欠落、watch owner/channel null、nicoadにowner、user APIは404 | 既存hidden/索引userId補完と関連する別標本 | 投稿者補完候補の報告 | ownerの鮮度・正確さ、退会/凍結/非表示理由は不明。hiddenとowner nullは同一状態と扱わない |
| snapshotとnvapiの新着100件が不一致 | 既存索引鮮度差を補足 | 現在検索の代替として同一性を保証できない | 件数差だけでは削除・非公開・検索対象差の原因を特定できない |
| routeとnvapiが9条件で32件のID順・総件数一致 | 条件を揃えた比較の追加報告 | その9条件に限定した一致 | 全検索条件・全セッション・tags一致を意味しない |

元の「広告で補える」という表現は、値が返ったことと正確性を分離した。「最大5000件」は上記の境界観察へ限定した。原本を削除・修正せず、訂正意図をこの表で追跡する。

## 再利用に必要な要求・応答

すべてGET。検索系は`https://nvapi.nicovideo.jp/v1/playlist/search`および`/v2/search/video`、タグ/キーワード、sort、page/pageSize等を指定する。比較報告のheaderは`X-Frontend-Id: 6`、`X-Frontend-Version: 0`。返却一覧にはid/owner等の記載があるが、タグ一括取得の証拠にはならない。page50境界報告ではCookieなし・Frontend-Id 6とされ、別の100件比較ではCookieあり。必要性と実行条件を混同しない。

広告一括は`https://api.nicoad.nicovideo.jp/v1/contents/video/decoration?ids=<VIDEO_ID_CSV>`、100個の10文字ID、生カンマ、URL長1164、credentials omitと報告。62返却は欠落理由が分からないため、欠落を「投稿者なし」やNG非該当へ変換しない。600/700報告の原記録は今回も照合していない。

単独補完は`https://ext.nicovideo.jp/api/getthumbinfo/{videoId}`と`https://api.nicoad.nicovideo.jp/v1/contents/video/{videoId}`。前者のuser_id/user_nickname/user_icon_url欠落、後者のownerId/ownerName/ownerIcon存在を報告。watch JSONとnvapi user照合はCookieありとされる。匿名化のため対象投稿者・動画値はこの要約に含めず、独立再検証時は同条件の公開標本を選び、時刻・型・欠落・一致件数だけを記録する。

route JSONは`/tag/{word}`または`/search/{word}`の`responseType=json`。関連報告にはsort状態が保存される可能性もあるため、ログイン済みrouteへのGETを無副作用と仮定しない。詳しい保存挙動はR05/R06へ保留する。

## 性能・正確性と終了条件

100動画が同じ検索結果ページに含まれる場合は1要求でowner候補を得られるという報告。任意100 IDの網羅や最新タグは保証しない。応答時間・bodyサイズ・連続試験・rate limit・キャッシュは原通信未照合につき未測定。今回のsnapshot100件実測とは証拠水準が違うため、同じ実測比較として並べない。

metadata関連の採否と不足条件を保存しR02を終了する。次はR03で公開OSSの固定revisionから任意ID一括候補を調べる。参照：[タスク一覧](TASKS.md)、[外部資料台帳](EXTERNAL-SOURCES.md)、[既確認のsnapshot100件](SNAPSHOT-BATCH-BOUNDARY-20260920.md)。
