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

現在Sprint18完了。

次回はSprint19（ROIC分析）から開始。

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

---

### engines

数値計算のみ。

対象

scoring_engine

dcf_engine

checklist_engine

Sprint19以降

roic_engine

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

---

# overall_eval

総合判定はここだけ。

BUY

WATCH

PASS

などをここで決定する。

他モジュールでは判定しない。

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

# Sprint19

ROIC分析

実装予定

・ROIC計算

・NOPAT計算

・投下資本計算

・Buffett基準評価

・Buffett Score反映

・PDF表示

・AI評価反映

・UI追加

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