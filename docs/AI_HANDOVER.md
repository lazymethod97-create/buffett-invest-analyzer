# Buffett Investment Analyzer
# AI 引継ぎ書（Sprint8完了時点）
Version: 3.0
Date: 2026-07-25

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

---

# 完了済みSprint

## Sprint1

Buffett Score

・財務データ取得

・100点評価

・判定コメント

完了

---

## Sprint2

AI定性分析

Gemini

完了

---

## Sprint3

Google News RSS

記事本文取得

ニュース要約

完了

---

## Sprint4

Buffett Checklist

AIチェックリスト

完了

---

## Sprint5

MOAT分析

ブランド分析

経営者分析

Red Team AI

完了

---

## Sprint6

投資仮説管理

実装済

内容

・HypothesisManager

・InvestmentHypothesis

・HypothesisStatus

・AIによる仮説生成（generate_investment_hypothesis／Gemini連携、未設定時はルールベースへ自動フォールバック）

・手動追加

・状態変更

・削除

・JSON保存

・JSON読込

・企業変更時に仮説リセット

完了

※初版ではAI仮説生成関数がapp.pyから未接続だったが、修正済み。現在はGemini APIキー設定時、Geminiが企業データ・MOAT・ブランド・経営者・Red Team評価を踏まえて動的に仮説を生成する。

---

## Sprint7

ニュース確認ポイント自動生成

実装済

内容

・generate_news_confirmation_points（ai_analysis.py）

・ニュース本文を踏まえ「決算確認項目」「リスクイベント」「競合動向」「設備投資」「規制」「為替」等のカテゴリ別に確認事項を生成

・優先度（high/medium/low）付き

・Gemini未設定時はルールベース（_generate_rule_confirmation_points）へ自動フォールバック

・create_confirmation_points_display（report.py）でカテゴリ別・優先度アイコン付き表示

・UI配置：「📝 AIニュース要約」の直後、「📋 Buffett Investment Checklist」の直前

完了

---

## Sprint8

PDFレポート出力

実装済

内容

・pdf_report.py 新規作成（services/配下、他モジュールと同階層）

・ReportLab使用、日本語はCIDフォント（HeiseiKakuGo-W5／HeiseiMin-W3）使用のためフォントファイル不要

・generate_pdf_report()で以下を1つのPDFに集約

　会社情報／Buffett Score／採点詳細／AI定性分析／ニュース要約／

　ニュース確認ポイント（Sprint7）／Checklist／MOAT／ブランド／

　経営者／Red Team／投資仮説一覧

・app.py側：「📄 PDFレポートを生成」ボタン→生成後「⬇️ PDFをダウンロード」ボタン表示

・依存追加：reportlab（requirements.txtへの追記が必要）

完了

※注意：pdf_report.pyは他のモジュール（report.py, ai_analysis.py等）と必ず同じフォルダに置くこと。別フォルダに置くとModuleNotFoundErrorになる（実際に発生し、配置修正で解決済み）。

---

# app.py

最新版

Sprint8対応済

現在の構成

会社情報

↓

Buffett Score

↓

レーダーチャート

↓

AI分析

↓

ニュース

↓

ニュース要約

↓

ニュース確認ポイント（Sprint7）

↓

Checklist

↓

MOAT

↓

ブランド

↓

経営者

↓

Red Team

↓

採点詳細

↓

投資仮説管理

↓

PDFレポート（Sprint8）

↓

終了

---

# hypothesis.py

完成済

クラス

InvestmentHypothesis

HypothesisManager

HypothesisStatus

JSON対応済

generate_default_hypotheses はGemini未設定時／APIエラー時のフォールバックとして ai_analysis.py 経由で使用される（app.pyから直接は呼ばない）

---

# ai_analysis.py

完成済

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

---

# report.py

現在は

create_hypothesis_display()

は未使用

表示はapp.pyで行っている

削除しなくてよい

Sprint7でcreate_confirmation_points_displayを追加済み

---

# pdf_report.py

Sprint8で新規追加

PDFBuilderクラスでページ送り・文字折り返しを管理

generate_pdf_report()が唯一の公開関数

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

Sprint9

テーマ

DCF分析（Discounted Cash Flow）

内容予定

・将来FCF予測

・割引率（WACC）設定

・現在価値算出

・理論株価との比較表示

---

# 将来実装予定

□ Excel出力

□ DCF分析（Sprint9予定）

□ Owner Earnings

□ Buffett Intrinsic Value

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

---

Git Commit

feat: Sprint7 AI news confirmation points

feat: Sprint8 PDF report output via ReportLab

---

現在Version

Ver3.0

Sprint8完了

次回はSprint9（DCF分析）から開始する