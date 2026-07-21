# PROJECT_RULES.md

# Buffett Investment Analyzer 開発ルール

## プロジェクト概要

Buffett Investment Analyzer は、

**「ウォーレン・バフェットなら、この会社へ投資するか？」**

を分析する投資判断支援Webアプリである。

目的は売買シグナルを出すことではなく、

**投資判断を支援すること**である。

最終判断は必ずユーザーが行う。

---

# AIの役割

AIは

* 企業分析
* ニュース要約
* MOAT分析
* ブランド分析
* 経営者分析
* 投資仮説整理

のみを担当する。

数値計算はAIへ任せない。

---

# プログラムの役割

プログラムが担当するもの

* Buffett Score
* 財務計算
* グラフ
* スコアリング
* データ取得
* 数値比較
* 判定ロジック

AIへ計算を任せない。

---

# 使用技術

## Framework

Streamlit

## AI

Gemini API

google-genai

OpenAI APIは使用しない。

---

# ニュース取得

使用するもの

Google News RSS

feedparser

newspaper4k

使用しないもの

yfinance.news

---

# APIキー

.env

のみ使用する。

GitHubへアップロードしない。

.gitignoreへ追加済みであること。

---

# コーディングルール

コードは必ず

**ファイル全体を書き換えられる完成版**

で提示する。

部分コードは禁止。

---

# 開発ルール

必ず守ること

* 初心者向けに説明する
* 一度に1機能だけ実装する
* 完成イメージを最初に示す
* VSCodeでクリックする場所まで説明する
* GitHubへコミットするタイミングを指示する
* AIリレー開発を前提とする
* 既存コードを壊さない
* リファクタリングは理由を説明してから行う

---

# Gitルール

Sprint終了後のみコミットする。

コミットメッセージ例

feat:

fix:

refactor:

docs:

---

# ディレクトリ構成

buffett-invest-analyzer/

├── services/

│   ├── app.py

│   └── src/

│       ├── ai_analysis.py

│       ├── news_fetcher.py

│       ├── data_fetcher.py

│       ├── scoring_engine.py

│       ├── report.py

│       └── ...

├── docs/

│   ├── PROJECT_RULES.md

│   └── AI_HANDOVER.md

├── .env

├── requirements.txt

└── README.md

---

# Version2 開発方針

Version2では

AIが投資判断を代行するのではなく、

投資家が納得して判断できる情報を提供する。

追加予定機能

* Buffett Investment Checklist
* MOAT評価
* ブランド力評価
* 経営者評価
* Red Team AI
* 投資仮説管理
* ニュース→確認項目
* 判断賞味期限
* 投資メモ
* ウォッチリスト

---

# Version3

将来的に

* DCF
* ROIC
* 適正株価
* 決算短信
* 有価証券報告書
* 業界比較
* ポートフォリオ分析

などを追加予定。

---

# このアプリの思想

Buffett Investment Analyzer は

**「上がる株を当てるアプリ」**

ではない。

**「間違いに早く気づくための投資判断支援アプリ」**

である。
