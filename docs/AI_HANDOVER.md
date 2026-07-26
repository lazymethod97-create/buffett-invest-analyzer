# Buffett Investment Analyzer
# AI 引継ぎ書（Sprint11完了時点）
Version: 4.0
Date: 2026-07-26

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

※UIルールはPROJECT_RULES.md Ver4.0で「タブの並び順」「タブ内の並び順」の2階層に改訂済み（Sprint11対応）。

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

dcf_analysis.py（Sprint9で追加）

---

# 完了済みSprint

## Sprint1〜Sprint8

Ver3.0時点までに完了済み（Buffett Score／AI定性分析／ニュース取得＋要約／Checklist／MOAT・ブランド・経営者・Red Team分析／投資仮説管理／ニュース確認ポイント／PDFレポート出力）。詳細はVer3.0の引継ぎ書を参照。

---

## Sprint9

DCF分析（Discounted Cash Flow）

完了

内容

・`dcf_analysis.py` 新規作成（services/配下、他モジュールと同階層）

・`calculate_dcf()` が唯一の公開関数。ルールベースの数式計算のみで、AIは使用しない

・将来FCF予測（デフォルト5年）→ 現在価値へ割引 → ターミナルバリュー（Gordon Growth Model）を加算し、理論株価（intrinsic_value_per_share）を算出

・現在株価との差から安全余裕（margin_of_safety_pct）と判定（verdict）を算出

・app.py側：FCF成長率／割引率（WACC簡易値）／永久成長率の3スライダーをUIに追加し、`create_dcf_display()`（report.py）で表示

・データ不足時（FCFマイナス等）は `success: False` を返し、エラーメッセージを表示する設計

完了

---

## Sprint10

分析結果のキャッシュ化

完了

内容

・課題：DCFスライダーを1回動かすだけで、Streamlitがスクリプト全体を再実行し、Gemini呼び出し（AI定性分析／ニュース要約／ニュース確認ポイント／Checklist／MOAT／ブランド／経営者／Red Teamの計7回）が毎回再実行されてしまっていた

・対策1：AI分析はすべて「🔍 分析開始」ボタン押下時（分析実行ブロック）に1回だけ実行し、結果を `st.session_state.analysis_bundle`（辞書）にまとめて保存

・対策2：結果表示ブロックは `analysis_bundle` から値を読むだけにし、AI関数を直接呼ばないよう変更

・対策3：`data_fetcher.py` / `news_fetcher.py` は変更せず、app.py側に `st.cache_data(ttl=3600)` でラップした `cached_get_stock_data` / `cached_get_latest_news` を追加し、呼び出し口だけ差し替え

・効果：DCFスライダー操作時にGemini呼び出しが発生しなくなり、体感速度が大幅改善。PDFの内容が生成のたびに微妙に変わる問題も解消

完了

---

## Sprint11

タブレイアウト化

完了

内容

・PROJECT_RULES.mdをVer4.0として改訂し、「画面順序を変更しない」ルールを「タブの並び順」「タブ内の並び順」の2階層に再定義（表示する情報・機能自体は変更なし）

・タブ構成：`[📊 サマリー] [📈 定量分析] [🧠 定性分析] [📰 ニュース] [📋 仮説・レポート]`

・会社情報（企業名・セクター・国・株価・時価総額）のみタブの外、常に画面上部に固定

・サマリータブは新規のヘルパー関数（`_star_line`, `_moat_rating_label`。app.py内に追加、report.pyは無変更）を使い、MOAT・ブランド・経営者は星評価のみ、Red Teamは結論一行のみを表示。新しいAI呼び出しは追加していない

・DCFはコード上「定量分析タブ」のブロックで計算し、その結果をサマリータブのブロックで再利用（コードの実行順とタブの表示順は独立しているため問題なし）

・その他のタブ（定性分析／ニュース／仮説・レポート）は、Ver3.0時点の表示内容をそのままタブに振り分けただけで、ロジック変更なし

完了

---

## 不具合修正（Sprint10〜11の間に対応）

・JSON読込（`st.file_uploader`）の無限ループ防止：読込成功後に `st.rerun()` していたが、再実行後もアップロード済みファイルが残るため再読込を繰り返す可能性があった。処理済みファイルの `file_id` を `st.session_state.last_loaded_hypothesis_file_id` に記録し、同じファイルは再処理しないよう修正

・フッターのデータソース表記を「データソース: Google RSS」→「データソース: yfinance / Google News RSS」に修正（yfinanceも使用しているため）

修正済

---

# app.py

最新版

Sprint11対応済

現在の構成

会社情報（企業名・セクター・国・株価・時価総額。タブの外、常に上部固定）

↓

タブ切り替え

　📊 サマリー：Buffett Score／DCF理論株価の要約／MOAT・ブランド・経営者の星評価／Red Teamの結論一行

　📈 定量分析：レーダーチャート／採点詳細／DCF分析（スライダー＋フル表示）

　🧠 定性分析：AI定性分析／Checklist／MOAT／ブランド／経営者／Red Team（いずれも詳細表示）

　📰 ニュース：最新ニュース一覧／AIニュース要約／ニュース確認ポイント

　📋 仮説・レポート：投資仮説管理／PDFレポート出力

↓

終了

---

# hypothesis.py

完成済（Ver3.0から変更なし）

クラス

InvestmentHypothesis

HypothesisManager

HypothesisStatus

JSON対応済

generate_default_hypotheses はGemini未設定時／APIエラー時のフォールバックとして ai_analysis.py 経由で使用される（app.pyから直接は呼ばない）

---

# ai_analysis.py

完成済（Ver3.0から変更なし）

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

いずれもGemini APIキー未設定・APIエラー時はルールベース関数へ自動フォールバックする設計で統一されている。

Sprint10により、これらの関数はapp.py内で「分析開始」ボタン押下時に1回だけ呼ばれ、結果は `st.session_state.analysis_bundle` に保存される。

---

# report.py

Ver3.0から関数自体の変更なし。

create_hypothesis_display()

は未使用（削除しなくてよい）

Sprint11でapp.py側に `_star_line` / `_moat_rating_label` という表示ヘルパーを追加したが、これはapp.py内に定義しており、report.pyへは追加していない。

---

# pdf_report.py

Sprint8で新規追加（Ver3.0から変更なし）

PDFBuilderクラスでページ送り・文字折り返しを管理

generate_pdf_report()が唯一の公開関数

---

# dcf_analysis.py

Sprint9で新規追加

PDFBuilderと同様、services/配下・他モジュールと同階層に配置

calculate_dcf()が唯一の公開関数。ルールベース計算のみでAIは不使用。

---

# AI分析

Gemini使用

OpenAIは使用しない

ニュース本文もGeminiへ渡している

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

Gemini確認ポイント生成（Sprint7）

---

# 次Sprint

Sprint12

テーマ

分析モードの選択（クイック／標準／フル）

内容予定

・クイックモード：財務スコアとレーダーのみ（API呼び出しゼロ、即時表示）

・標準モード：クイック＋AI定性分析／Checklist／ニュース要約

・フルモード：現行の全機能

・サイドバーのラジオボタンで切り替え

・各セクションに「🔄 この分析だけ再生成」ボタンを追加する案も検討

---

# 将来実装予定

□ Excel出力

□ Gemini呼び出しの統合（Checklist・MOAT・ブランド・経営者を1プロンプト化してAPI呼び出しを4分の1に削減）

□ app.pyの分割（`ui_sections.py` をservices/配下に追加し、`render_summary_tab()` 等へ切り出し）

□ Owner Earnings

□ Buffett Intrinsic Value（DCF以外の手法）

□ 10年財務推移

□ ROIC

□ Insider Ownership

□ SEC EDGAR

□ 有価証券報告書解析

□ 決算説明資料解析

□ AIチャット

□ Portfolio管理

□ WatchList

□ 比較分析

□ AI投資日誌

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

UIルール（PROJECT_RULES.md Ver4.0）のタブ順・タブ内順を守ること。

---

Git Commit

feat: Sprint7 AI news confirmation points

feat: Sprint8 PDF report output via ReportLab

feat: Sprint9 DCF analysis (intrinsic value)

perf: Sprint10 cache AI analysis results in session_state, add st.cache_data wrappers for stock/news fetch

fix: prevent infinite rerun loop on hypothesis JSON upload

fix: correct footer data source label (yfinance + Google News RSS)

docs: PROJECT_RULES Ver4.0 - redefine UI order rule for tab layout

feat: Sprint11 tab layout (summary/quant/qual/news/hypothesis tabs)

---

現在Version

Ver4.0

Sprint11完了

次回はSprint12（分析モードの選択）から開始する