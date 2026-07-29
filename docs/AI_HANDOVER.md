# Buffett Investment Analyzer
# AI 引継ぎ書（Sprint17完了時点）
Version: 7.0
Date: 2026-07-28

---
# プロジェクト概要

本プロジェクトは

**「ウォーレン・バフェットならこの会社に投資するか？」**

をAIで分析するWebアプリ。

フレームワーク

- Streamlit
- Gemini API
- yfinance
- Google News RSS
- newspaper4k
- ReportLab（PDFレポート出力）
- pdfplumber（Sprint17、決算資料PDFのテキスト抽出）

Github

https://github.com/lazymethod97-create/buffett-invest-analyzer

---

# 開発ルール

必ず守ること

①初心者でも分かる説明を行う

②1Sprint = 1機能

③既存コードを壊さない

④リファクタリングする場合は理由を説明

⑤コピペだけで動くコードを書く

⑥完成イメージを最初に見せる

⑦Gitへコミットするタイミングを教える

⑧必ずapp.py全体との整合性を確認する

詳細はPROJECT_RULES.md（Ver4.1）を参照。

---

# ディレクトリ

services/

app.py

ai_analysis.py

data_fetcher.py

news_fetcher.py

scoring_engine.py

report.py

hypothesis.py

pdf_report.py

dcf_analysis.py（Sprint9）

portfolio.py（Sprint13）

watchlist.py（Sprint14）

journal.py（Sprint16）

earnings_material.py（Sprint17）

---

# 完了済みSprint

## Sprint1〜8

Ver3.0のAI_HANDOVER.mdを参照。概要：

- Sprint1: Buffett Score（財務データ取得・100点評価・判定コメント）
- Sprint2: AI定性分析（Gemini）
- Sprint3: Google News RSS・記事本文取得・ニュース要約
- Sprint4: Buffett Checklist
- Sprint5: MOAT分析・ブランド分析・経営者分析・Red Team AI
- Sprint6: 投資仮説管理（HypothesisManager等）
- Sprint7: ニュース確認ポイント自動生成
- Sprint8: PDFレポート出力（ReportLab、pdf_report.py）

---

## Sprint9

テーマ：DCF分析（Discounted Cash Flow）

実装済

内容

・dcf_analysis.py 新規作成（services/配下、他モジュールと同階層）

・calculate_dcf()：フリーキャッシュフロー(free_cashflow)を発行済株式数で割り、
　1株あたりFCFを算出→成長率・割引率(WACC簡易値)・永久成長率を用いて
　5年間のFCFを現在価値に割引き、ターミナルバリュー(Gordon Growth Model)を加算して
　理論株価(intrinsic_value_per_share)を算出

・すべてルールベースの計算のみ。AI（Gemini）は一切使用しない

・成長率未指定時はrevenue_growthを参考に5%〜15%にクリップして自動設定（保守的）

・安全余裕(margin_of_safety_pct)に応じて🟢🟡🟠🔴の4段階で判定

・report.py に create_dcf_display() を追加

・app.py側：3つのスライダー（FCF成長率／割引率／永久成長率）で前提条件を調整可能

完了

---

## Sprint10

テーマ：分析結果のキャッシュ化

実装済

内容

・課題：Streamlitは操作のたびにスクリプト全体を再実行するため、Sprint9のDCFスライダーを
　1回動かすだけで、ニュース取得＋Gemini呼び出し7回（AI定性分析／Checklist／MOAT／
　ブランド／経営者／Red Team／ニュース確認ポイント）がすべて再実行されていた

・対応1：`get_stock_data` と `get_latest_news` を直接編集せず、app.py側で
　`st.cache_data(ttl=3600)` によるラッパー関数（`cached_get_stock_data` /
　`cached_get_latest_news`）を追加し、呼び出し口だけ差し替え。同じ引数なら1時間再取得しない

・対応2：AI分析（ニュース要約／AI定性分析／Checklist／MOAT／ブランド／経営者／
　Red Team／確認ポイント）は「🔍 分析開始」ボタンが押された時（analyze_button）に
　**1回だけ**実行し、結果を辞書にまとめて `st.session_state.analysis_bundle` に保存

・表示ブロックはAI関数を直接呼ばず、`st.session_state.analysis_bundle` から値を読むだけに変更

・これによりDCFスライダーなどの操作では一切Gemini呼び出しが走らなくなった
　（表示内容・順序は一切変更していない）

完了

---

## Sprint11

テーマ：タブレイアウト化

実装済

内容

・PROJECT_RULES.md をVer4.0に改訂し、「UI順序を変更しない」ルールを
　「タブの並び順」＋「タブ内の並び順」の2階層に再定義（先にルール側を更新してから実装）

・st.tabs()で5タブを作成：

　[📊 サマリー] [📈 定量分析] [🧠 定性分析] [📰 ニュース] [📋 仮説・レポート]

・会社情報（企業名・セクター・国・株価・時価総額）のみタブの外、常に画面上部に固定

・サマリータブは新規に「星評価・結論だけを抜き出す」表示にした
　（`_star_line()` / `_moat_rating_label()` という小さなヘルパー関数をapp.pyに追加。
　report.pyの詳細表示関数(create_moat_display等)は変更せず、定性分析タブでそのまま使用）

・DCFはコード上「定量分析タブ」のブロックで計算し、その結果(dcf_result)を
　「サマリータブ」のブロックでも再利用している。Streamlitはタブの見た目の並びと
　コードの実行順が別物なので、コードの記述順が定量分析タブ→サマリータブでも問題なく動く

・投資仮説管理・PDFレポートは「仮説・レポート」タブに集約

完了

---

## Sprint12

テーマ：分析モード選択（クイック／標準／フル）

実装済

内容

・サイドバーにラジオボタンで3モードを追加（デフォルト：フル＝従来と同じ挙動）

　| モード | Gemini呼び出し回数 | 表示される内容 |
　|---|---|---|
　| ⚡ クイック | 0回 | 財務スコア・レーダー・DCFのみ（すべてルールベース） |
　| 📊 標準 | 2回 | クイック＋AI定性分析・Checklist・ニュース要約 |
　| 🔎 フル | 7回 | 標準＋MOAT／ブランド／経営者／Red Team・確認ポイント・投資仮説・PDF |

・「🔍 分析開始」ボタンを押した時点で選択されているモードに応じて、
　`analysis_bundle` に格納する項目を出し分ける（未実行の項目は `None` のまま保存）

・`analysis_bundle["mode"]` にモードを保存し、表示側は `is_standard_plus` / `is_full` の
　フラグで各タブの中身を出し分ける

・未実行の項目は各タブ内で「🔒 この項目は『◯◯』モードで表示されます」という
　案内（`_mode_locked_message()`）に置き換わる。エラーにはならない

・「まず複数銘柄をクイックで比較し、気になった銘柄だけフルで再分析する」という
　使い方を想定。モードを上げて分析し直したい場合は、サイドバーでモードを切り替えて
　再度「🔍 分析開始」を押す（同じティッカーでも、まだ実行していない深さのAI呼び出しが走る）

完了

---

## Sprint13

テーマ：Portfolio（保有銘柄管理）

実装済

内容

・PROJECT_RULES.md をVer5.0に改訂し、タブを5個から6個に変更（末尾に
　「💼 Portfolio」タブを追加）。ユーザーに事前確認済み。既存5タブの
　並び順・タブ内の並び順は一切変更していない

・portfolio.py 新規作成（services/配下、他モジュールと同階層）

　・PortfolioHolding：1保有銘柄（ticker, shares, cost_basis）を表すクラス

　・PortfolioManager：add() / delete() / get_all() / clear()

　・hypothesis.py（投資仮説管理）と同じ設計パターン。このモジュールは
　　データ保持のみ担当し、現在株価取得・スコア計算は行わない

・app.py側：

　・st.session_state.portfolio_manager にPortfolioManagerインスタンスを保持
　　（hypothesis_managerと同じ初期化パターン）

　・「💼 Portfolio」タブを追加し、以下を実装：

　　１．登録フォーム（ティッカー・保有株数・取得単価）

　　２．ポートフォリオ合計（取得金額合計／評価額合計／評価損益）

　　３．保有銘柄一覧（銘柄ごとの現在株価・評価損益・Buffett Score・削除ボタン）

　・各銘柄の現在株価取得・Buffett Score計算は、既存のcached_get_stock_data
　　（Sprint10）とcalculate_buffett_score（既存）をそのまま再利用。
　　新しいGemini呼び出しは一切追加していない（すべてルールベース）

・データ保存方針：ユーザー確認の上、セッション中のみ保持する方針とした。
　JSON保存/読込（投資仮説と同様の機能）は今回実装せず、Sprint14以降で検討する

・Portfolioタブは「現在分析中の1銘柄」の状態（current_data等）とは独立しており、
　ticker_input・analysis_bundle等の既存の状態管理を一切変更していない

完了

---

## Sprint14

テーマ：Watch List（気になる銘柄の管理）

実装済

内容

・PROJECT_RULES.md をVer5.1に改訂。新しいタブは追加していない
　（ユーザー確認済み。既存の「💼 Portfolio」タブの中に、保有銘柄一覧の下へ
　「👀 ウォッチリスト」セクションを追加する形にした）

・watchlist.py 新規作成（services/配下、他モジュールと同階層）

　・WatchListItem：1銘柄（ticker, target_price, memo）を表すクラス

　・WatchListManager：add() / delete() / get_all() / clear()

　・portfolio.py（保有銘柄管理）と同じ設計パターン。データ保持のみ担当し、
　　現在株価取得・スコア計算は行わない

・app.py側：

　・st.session_state.watchlist_manager にWatchListManagerインスタンスを保持
　　（portfolio_managerと同じ初期化パターン）

　・「💼 Portfolio」タブの保有銘柄一覧の下に、以下を追加：

　　１．ウォッチリスト登録フォーム（ティッカー・目標株価（任意）・メモ（任意））

　　２．ウォッチリスト一覧（銘柄ごとの現在株価・Buffett Score・目標株価への
　　　到達状況・削除ボタン）

　・各銘柄の現在株価取得・Buffett Score計算は、既存のcached_get_stock_data /
　　calculate_buffett_scoreをそのまま再利用。新しいGemini呼び出しは一切
　　追加していない（すべてルールベース）

・目標株価：現在株価が目標株価以下になった時点で「🎯 到達」と表示する
　（「この値段まで下がったら買いたい」という使い方を想定）。未設定の場合は
　「目標株価は未設定です」と表示し、エラーにはならない

・データ保存方針：保有銘柄と同様、セッション中のみ保持する方針とした。
　JSON保存/読込は今回実装せず、将来のSprintで検討する

・ウォッチリストのデータ（WatchListItem）は保有銘柄のデータ（PortfolioHolding）
　とは完全に分離しており、既存のPortfolio機能（Sprint13）のコードは
　一切変更していない

完了

---

## Sprint15

テーマ：比較分析（複数銘柄のBuffett Scoreを並べて比較）

実装済

内容

・PROJECT_RULES.md をVer6.0に改訂し、タブを6個から7個に変更（末尾に
　「⚖️ 比較分析」タブを追加）。ユーザーに事前確認済み。既存6タブの
　並び順・タブ内の並び順は一切変更していない

・新規モジュールは作成していない（すべてapp.py内に実装）。
　理由：report.py内の既存の描画関数（create_radar_chart等）は単一銘柄用の設計であり、
　report.pyの内容を確認できない状態で複数銘柄比較用に改修すると、既存コードを
　壊すリスクがあるため。plotly.graph_objectsをapp.py側で直接使い、
　report.pyの既存関数・既存表示は一切変更していない

・app.py側：

　・先頭に `import plotly.graph_objects as go` を追加（サードパーティimport、
　　streamlitの直後に配置）

　・st.session_state.compare_bundle を追加（「⚖️ 比較する」ボタンを押した時だけ
　　計算し、結果を保持する。Sprint10のキャッシュ化と同じ考え方）

　・「⚖️ 比較分析」タブを追加し、以下を実装：

　　１．比較対象銘柄の選択（Portfolio／ウォッチリスト登録済み銘柄からの
　　　複数選択 ＋ 自由入力（カンマ区切り）の両対応）

　　２．スコア比較サマリー（銘柄ごとのBuffett Score・判定）

　　３．総合スコア比較（棒グラフ）

　　４．指標別スコア比較（レーダーチャート、複数銘柄を重ねて表示）

・比較する指標はSprint15時点ではBuffett Scoreのみ。既存のcached_get_stock_data /
　calculate_buffett_scoreをそのまま再利用し、新しいGemini呼び出しは一切
　追加していない（すべてルールベース）

・レーダーチャートは、項目ごとに配点(max_score)が異なるため
　（例：ROEは20点満点、ROAは5点満点）、達成率(%)に正規化してから比較している

・データ取得に失敗した銘柄がある場合はエラーにせず、警告として表示した上で
　取得できた銘柄だけで比較を続行する

・比較分析タブは「現在分析中の1銘柄」の状態（current_data等）や、Portfolio／
　ウォッチリストの既存のデータ・ロジックとは独立しており、それらのコードは
　一切変更していない

完了

---

## Sprint16

テーマ：AI投資日誌（実体は「投資日誌」。手入力のみ）

実装済

内容

・PROJECT_RULES.md をVer6.1に改訂。新しいタブは追加していない
　（ユーザー確認済み。既存の「📋 仮説・レポート」タブの中に、PDFレポート出力の
　下へ「📓 AI投資日誌」セクションを追加する形にした。投資仮説と目的が
　近いため、同じタブ内に置いている）

・journal.py 新規作成（services/配下、他モジュールと同階層）

　・JournalEntry：1件の日誌（date, ticker, decision, reason）を表すクラス

　・JournalManager：add() / delete() / get_all() / clear() に加えて、
　　to_json() / load_from_json() を実装（投資仮説と同様、日誌は長期保存の
　　ニーズが高いと想定し、JSON保存/読込に対応。ユーザー確認済み）

　・hypothesis.py（投資仮説管理）と同じ設計パターン

・app.py側：

　・st.session_state.journal_manager にJournalManagerインスタンスを保持

　・st.session_state.last_loaded_journal_file_id を追加。JSON読込時に
　　同じファイルを繰り返し読み込まないようにする仕組みで、hypothesis.pyの
　　JSON読込で過去に発生した無限ループ不具合（Sprint10〜11の間に修正）と
　　同じ対策を最初から組み込んでいる

　・先頭に `import datetime` を追加（標準ライブラリ、日誌の日付入力用）

　・「📋 仮説・レポート」タブのPDFレポート出力の下に、以下を追加：

　　１．日誌記録フォーム（日付・ティッカー（任意）・売買の判断
　　　（買い／売り／様子見／保有継続）・理由（自由記述））

　　２．JSON保存（ダウンロード）／読込（アップロード）ボタン

　　３．日誌一覧（日付が新しい順に表示。削除ボタン付き）

・「AI投資日誌」という名称だが、Sprint16時点では手入力のみで、
　Gemini呼び出しは一切行わない（ユーザー確認済み。将来、任意でAIコメントを
　追加する機能は別Sprintで検討可能）

・保有銘柄（Portfolio）とは無関係に、自由に日誌を記録できる
　（ユーザー確認済み。銘柄は任意入力の自由記述で、PortfolioHoldingとの
　紐付けは行っていない）

・日誌データ（JournalEntry）は、投資仮説（InvestmentHypothesis）・保有銘柄
　（PortfolioHolding）・ウォッチリスト（WatchListItem）のいずれとも独立した
　データであり、既存の機能・コードは一切変更していない

完了

---

## Sprint17

テーマ：決算資料解析（決算説明資料などのPDFをアップロードして解析）

実装済

内容

・PROJECT_RULES.md をVer7.0に改訂し、タブを7個から8個に変更（末尾に
　「📑 決算資料解析」タブを追加）。ユーザーに事前確認済み。既存7タブの
　並び順・タブ内の並び順は一切変更していない

・新規ライブラリ pdfplumber を追加（requirements.txtへの追加が必要。
　ユーザー合意済み）。PDFからテキストを抽出するために使用する

・earnings_material.py 新規作成（services/配下、他モジュールと同階層）

　・extract_text_from_pdf(file_bytes)：PDFのバイト列からテキストを抽出する
　　唯一の公開関数。ルールベースの処理のみで、AIは使用しない

・ai_analysis.py に以下の2関数を追加（既存の関数・コードは一切変更していない。
　ファイル末尾に追記する形で対応した）

　・generate_earnings_material_analysis(pdf_text, company_name=None)：
　　抽出したテキストをGeminiに渡し、決算サマリー・良かった点・懸念点・
　　経営陣コメントの印象・結論（強気／中立／弱気）を生成する

　・_generate_rule_earnings_material_analysis(pdf_text)：
　　APIキー未設定・APIエラー時のフォールバック。既存の
　　_generate_rule_news_summary等と同じ設計方針（抽出テキストの冒頭を
　　表示し、AI分析が利用できない旨を案内する）

・app.py側：

　・st.session_state.earnings_material_result を追加。「📑 資料を解析する」
　　ボタンを押した時だけPDF抽出・Gemini呼び出しを行い、結果を保持する
　　（Sprint15の比較分析と同じ、ボタン起点でのみ計算する設計）

　・「📑 決算資料解析」タブを追加し、以下を実装：

　　１．PDFアップロード欄＋「📑 資料を解析する」ボタン

　　２．解析結果（Geminiによる要約・ポイント抽出をMarkdownで表示）

　　３．抽出したテキストの確認用expander（元データの冒頭5000文字）

・Gemini呼び出しは、このタブの「📑 資料を解析する」ボタンを押した時だけ発生する。
　Sprint12の分析モード（クイック／標準／フル）による呼び出し回数制御とは
　独立しており、モードに関わらずこのタブは利用できる

・画像だけのPDF等でテキストが抽出できなかった場合はエラーにせず、
　警告メッセージを表示するだけにとどめている

・決算資料解析タブは「現在分析中の1銘柄」の会社名（company_name）を
　Geminiへの参考情報として渡す以外は、current_data等の既存の状態管理とは
　独立しており、既存の機能・コードは一切変更していない

完了

---

## 見つかった不具合の修正（Sprint10〜11の間に対応）

- JSON読込の無限ループ：`st.file_uploader` 読込成功後の `st.rerun()` により、
　同じファイルが残っている限り読込→rerun→読込…を繰り返す可能性があった。
　`st.session_state["last_loaded_hypothesis_file_id"]` に処理済みファイルIDを記録し、
　同じファイルなら再読込しないよう修正

- フッターのデータソース表記：「データソース: Google RSS」はyfinanceも使っているため不正確。
　「データソース: yfinance / Google News RSS」に修正

完了

---

# app.py

最新版

Sprint17対応済

現在の構成（Sprint11でタブ化）

会社情報（タブの外、常に上部固定）
↓
サイドバー：分析モード選択（Sprint12）
↓
タブ：[📊 サマリー] [📈 定量分析] [🧠 定性分析] [📰 ニュース] [📋 仮説・レポート]

各タブ内の並び順はPROJECT_RULES.md（Ver4.1）を参照。

## session_state設計（Sprint10〜12）

- `st.session_state.current_data`：get_stock_dataの結果（企業データ辞書）
- `st.session_state.current_score_result`：calculate_buffett_scoreの結果
- `st.session_state.analysis_bundle`：AI分析結果一式をまとめた辞書。キー：
　`mode`, `news`, `analysis`, `summary`, `confirmation_points`,
　`checklist`, `moat`, `brand`, `mgmt`, `red_team`
　（クイック／標準モードでは一部キーがNoneのまま保存される）
- `st.session_state.hypothesis_manager`：HypothesisManagerインスタンス
- `st.session_state.last_company`：企業切替検知用
- `st.session_state.last_loaded_hypothesis_file_id`：JSON読込の重複防止用（不具合修正）
- `st.session_state.portfolio_manager`：PortfolioManagerインスタンス（Sprint13）。セッション中のみ保持し、現在分析中の1銘柄の状態とは独立している
- `st.session_state.watchlist_manager`：WatchListManagerインスタンス（Sprint14）。保有銘柄（portfolio_manager）とは別データとして、セッション中のみ保持する
- `st.session_state.compare_bundle`：比較分析タブ（Sprint15）で「⚖️ 比較する」ボタンを押した時の結果一覧。ボタンを押すまではNone
- `st.session_state.journal_manager`：JournalManagerインスタンス（Sprint16）。手入力の投資日誌をセッション中保持し、JSON保存/読込にも対応する
- `st.session_state.last_loaded_journal_file_id`：日誌JSON読込の重複防止用（Sprint16。hypothesis.pyの不具合修正と同じ仕組み）
- `st.session_state.earnings_material_result`：決算資料解析タブ（Sprint17）で「📑 資料を解析する」ボタンを押した時の結果（ファイル名・抽出テキスト・Gemini分析結果）。ボタンを押すまではNone

## キャッシュ関数（Sprint10）

- `cached_get_stock_data(ticker)`：`get_stock_data`を`st.cache_data(ttl=3600)`でラップ
- `cached_get_latest_news(company_name)`：`get_latest_news`を同様にラップ
- どちらもdata_fetcher.py／news_fetcher.py自体は無変更

## サマリータブ用ヘルパー（Sprint11）

- `_star_line(stars)`：星の数を`★☆`の文字列に変換
- `_moat_rating_label(rating)`：MOATのrating("wide"/"narrow"/"none")をラベル文字列に変換
- `_mode_locked_message(required_mode_label)`：Sprint12で、未実行モードの項目に表示する案内

---

# hypothesis.py

完成済（Sprint6時点から変更なし）

クラス

InvestmentHypothesis

HypothesisManager

HypothesisStatus

JSON対応済

generate_default_hypotheses はGemini未設定時／APIエラー時のフォールバックとして ai_analysis.py 経由で使用される（app.pyから直接は呼ばない）

Sprint12以降、投資仮説の生成・表示は「フルモード」でのみ実行される（MOAT／ブランド／経営者／Red Teamの結果を使うため）。

---

# ai_analysis.py

Sprint7〜16は変更なし。Sprint17でgenerate_earnings_material_analysisを
ファイル末尾に追記（既存の関数・コードは一切変更していない）

含まれる関数

generate_ai_analysis

generate_news_summary

generate_buffett_checklist

generate_moat_analysis

generate_brand_analysis

generate_management_analysis

generate_red_team_analysis

generate_investment_hypothesis（Sprint6・AI仮説生成）

generate_news_confirmation_points（Sprint7・ニュース確認ポイント）

generate_earnings_material_analysis（Sprint17・決算資料解析）

いずれもGemini APIキー未設定・APIエラー時はルールベース関数へ自動フォールバックする設計で統一されている。

Sprint12により、これらの関数はモードに応じて呼ばれない場合がある（app.py側の分岐であり、関数自体の変更はなし）。

---

# report.py

Sprint9でcreate_dcf_display()を追加済み

create_hypothesis_display()

は未使用（表示はapp.pyで行っている、削除しなくてよい）

Sprint7でcreate_confirmation_points_displayを追加済み

Sprint11で新しい関数は追加していない（既存のcreate_moat_display等をそのまま「定性分析」タブで使用）

---

# dcf_analysis.py

Sprint9で新規追加

calculate_dcf()が唯一の公開関数

すべてルールベースの計算のみで、AIは使用しない

---

# pdf_report.py

Sprint8で新規追加、以降変更なし

PDFBuilderクラスでページ送り・文字折り返しを管理

generate_pdf_report()が唯一の公開関数

Sprint12以降、フルモードでのみ呼び出し可能（app.py側のUI制御）

---

# AI分析

Gemini使用

OpenAIは使用しない

ニュース本文もGeminiへ渡している

Sprint12により、実際の呼び出し回数はモードに応じて 0回／2回／7回 のいずれかになる

Sprint17（決算資料解析）はこのモード分岐とは独立しており、「📑 資料を解析する」
ボタンを押した時だけ、決算資料解析タブ専用のGemini呼び出しが1回発生する

---

# ニュース取得

Google RSS

↓

newspaper4k

↓

記事本文取得

↓

Gemini要約

↓

Gemini確認ポイント生成（Sprint7、フルモードのみ）

---

# 次Sprint

Sprint18

テーマ

有価証券報告書解析（未確定、次回相談）

---

# 将来実装予定

□ Excel出力

□ Owner Earnings

□ Buffett Intrinsic Value（DCF以外の算出方法）

□ 10年財務推移

□ ROIC

□ Insider Ownership

□ SEC EDGAR

□ 有価証券報告書解析

□ 決算説明資料解析

□ AIチャット

□ Portfolio管理（Sprint13予定）

□ WatchList

□ 比較分析

□ AI投資日誌

□ 各セクションの「🔄 この分析だけ再生成」ボタン（中期アイディア、未着手）

□ Gemini呼び出しの統合（Checklist・MOAT・ブランド・経営者を1プロンプト化、中期アイディア、未着手）

□ app.pyの分割（ui_sections.pyへの切り出し、中期アイディア、未着手）

---

# AIへの指示

あなたは

Buffett Investment Analyzer

主任ソフトウェアエンジニア

として開発すること。

必ず

既存コードを壊さず

1Sprintずつ進めること。

app.py全体を確認してから修正すること。

コードは必ず

コピペだけで動く完成版を書くこと。

部分コードではなく

完成コードを書くこと。

新規モジュールを作成する場合は、必ず既存モジュール（report.py等）と同じフォルダに配置するよう指示すること。

PROJECT_RULES.md（Ver4.1）のUIルール（タブの並び順・タブ内の並び順）を守ること。

---

Git Commit

feat: Sprint7 AI news confirmation points

feat: Sprint8 PDF report output via ReportLab

feat: Sprint9 DCF analysis (intrinsic value)

perf: Sprint10 cache AI analysis results in session_state, add st.cache_data wrappers

fix: prevent infinite rerun loop on hypothesis JSON upload

fix: correct footer data source label (yfinance + Google News RSS)

feat: Sprint11 tab layout per PROJECT_RULES Ver4.0

docs: PROJECT_RULES Ver4.0 - redefine UI order rule for tab layout

feat: Sprint12 analysis mode selection (quick/standard/full)

docs: PROJECT_RULES Ver4.1 / AI_HANDOVER Ver4.0 - record Sprint9-12 completion

feat: Sprint13 portfolio management (add/delete holdings, P&L, Buffett Score list)

docs: PROJECT_RULES Ver5.0 / AI_HANDOVER Ver5.0 - add Portfolio tab, record Sprint13 completion

feat: Sprint14 watch list (target price alerts, Buffett Score, inside Portfolio tab)

docs: PROJECT_RULES Ver5.1 / AI_HANDOVER Ver5.1 - add Watch List section, record Sprint14 completion

feat: Sprint15 comparison analysis tab (multi-stock Buffett Score bar/radar chart)

docs: PROJECT_RULES Ver6.0 / AI_HANDOVER Ver6.0 - add comparison analysis tab, record Sprint15 completion

feat: Sprint16 investment journal (manual entries, JSON save/load, no AI calls)

docs: PROJECT_RULES Ver6.1 / AI_HANDOVER Ver6.1 - add investment journal section, record Sprint16 completion

feat: Sprint17 earnings material analysis (PDF upload, pdfplumber extraction, Gemini summary)

docs: PROJECT_RULES Ver7.0 / AI_HANDOVER Ver7.0 - add earnings analysis tab, pdfplumber dependency, record Sprint17 completion

---

現在Version

Ver7.0（AI_HANDOVER.md）／ Ver7.0（PROJECT_RULES.md）

Sprint17完了

次回はSprint18（有価証券報告書解析）から開始する（内容は次回相談）