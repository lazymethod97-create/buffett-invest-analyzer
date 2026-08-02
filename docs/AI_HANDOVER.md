@'
# AI_HANDOVER.md

# Buffett Investment Analyzer Ver2
## AI引き継ぎ書

---

# GitHub

GitHubを唯一の正とする。

ローカルよりGitHub最新版を優先。

新しいSprintを開始する前に必ず最新コードを確認すること。

---

# Version

Buffett Investment Analyzer Ver2

現在Sprint19完了。

次回はSprint20（Owner Earnings）から開始。

---

# Sprint18 完了内容

## リファクタリング（責務分離）

Version2の責務分離方針を確定・実装完了。

### app.py

app.pyはController専用とする。

以下のみ担当する。

・入力受付

・データ取得（cached_get_latest_news等）

・分析呼び出し（create_analysis_bundle() のみ）

・UI表示

分析ロジックは禁止。

---

### analysis

分析処理を集約するディレクトリ。

対象

overall_eval

moat

brand

management

red_team

analysis_bundle

roic

---

### engines

数値計算のみ。

対象

scoring_engine

dcf_engine

checklist_engine

roic_engine

Sprint20以降

intrinsic_engine

owner_earnings_engine

追加予定。

---

### data

データ取得のみ。

data_fetcher

news_fetcher

---

### ai

Geminiとの通信のみ。

gemini.py

ai_analysis.py

---

### ui

Streamlit描画専用。

summary_card

decision_card

financial_table

score_card

chart_panel

---

### report

PDF関連

report.py

pdf_report.py

---

# analysis_bundle

Version2から導入。

全分析を一括実行する。

create_analysis_bundle()

のみをapp.pyから呼び出す。

戻り値

overall

brand

moat

management（mgmt）

red_team

checklist

news

roic

---

# overall_eval

総合判定はここだけ。

BUY

WATCH

PASS

などをここで決定する。

他モジュールでは判定しない。

---

# Sprint19 完了内容

## ROIC分析

### 新規作成

engines/roic_engine.py

ROIC計算エンジン（ルールベース）

NOPAT = 営業利益 × (1 - 実効税率)

投下資本 = 純資産 + 総負債 - 現金同等物

ROIC = NOPAT ÷ 投下資本

analysis/roic.py

ROIC分析モジュール（共通形式）

### 修正

data/data_fetcher.py

ROIC関連フィールド追加

operating_income

income_tax_expense

income_before_tax

long_term_debt

short_term_debt

total_equity

cash

short_term_investments

analysis/analysis_bundle.py

create_analysis_bundle() に roic を追加

analysis/overall_eval.py

_score_roic() 追加（15点満点）

report/report.py

create_roic_display() 追加

report/pdf_report.py

PDFにROICセクション追加

ai/ai_analysis.py

generate_roic_analysis() 追加（Gemini評価）

app.py

定性分析タブ + PDFダウンロードにROIC表示追加

### スコア配分（115点満点）

Buffett Score: 40点

DCF: 20点

MOAT: 15点

ブランド: 10点

経営者: 10点

Red Team: 5点

ROIC: 15点（新規）

### 判定基準（調整後）

S: 100点以上

A: 85点以上

B: 70点以上

C: 55点以上

D: 55点未満

---

# 互換ラッパーについて

services/src直下には、旧import互換のためのラッパーが残っている。

例）

data_fetcher.py → data/data_fetcher.py

scoring_engine.py → engines/scoring_engine.py

ai_analysis.py → ai/ai_analysis.py

など。

削除する場合は、app.py等のimport先を新パッケージに変更してから行うこと。

---

# 今後のSprint

Sprint20

Owner Earnings

Sprint21

Intrinsic Value

Sprint22

Capital Allocation

Sprint23

Share Buyback

Sprint24

Debt Quality

Sprint25

Economic Moat強化

Sprint26

Backtest

Sprint27

Portfolio Analyzer

Sprint28

Watchlist

Sprint29

Performance改善

Sprint30

Version2.0 Release

---

# 注意事項

GitHub最新版を必ず確認。

重複実装禁止。

既存機能を壊さない。

分析ロジックはanalysisへ。

計算ロジックはenginesへ。

画面はuiへ。
'@ | Set-Content -Path "docs\AI_HANDOVER.md" -Encoding UTF8
Write-Host "✅ AI_HANDOVER.md updated for Sprint19"
