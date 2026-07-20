# Buffett Investment Analyzer 引継ぎ書（Sprint2完了）

## GitHub

https://github.com/lazymethod97-create/buffett-invest-analyzer

---

# プロジェクト概要

## 目的

「ウォーレン・バフェットならこの会社へ投資するか？」

をAIと財務分析で可視化するWebアプリ。

対象市場

* 日本株
* 米国株

フレームワーク

* Streamlit

AI

* Gemini API（google-genai）
* OpenAI APIは使用しない

---

# 開発ルール

このプロジェクトでは以下を厳守する。

* 初心者向けに説明する
* 一度に1機能だけ開発する
* 必ず完成イメージを最初に示す
* VSCodeでクリックする場所まで説明する
* GitHubへコミットするタイミングを指示する
* AIリレー開発を前提とする
* 既存コードを壊さない
* リファクタリングは理由を説明してから行う
* コードは必ずファイル全体をコピペできる完成版で提示する

---

# 現在の完成状況

## Sprint1

### 財務分析

* yfinanceで企業情報取得
* Buffett Score算出
* ROE
* ROA
* 営業利益率
* D/E
* PER
* PBR
* FCF
* 売上成長率

100点満点評価

---

### グラフ

* Plotlyレーダーチャート
* スコアバー

---

### AI企業分析

Gemini APIを利用。

APIキー未設定時は

generate_rule_analysis()

へ自動フォールバック。

---

### ニュース取得

yfinance.newsは廃止済み。

現在は

Google News RSS

↓

feedparser

↓

newspaper4k

↓

記事本文取得

まで実装済み。

会社名検索でニュースを取得する。

---

### AIニュース分析

generate_news_summary()

でGeminiへ

* タイトル
* 記事本文

を渡して分析する。

Sprint2でプロンプトを改善し、以下の観点で分析するようになった。

* ニュース要約
* 重要ニュース
* ポジティブ要因
* ネガティブ要因
* MOATへの影響
* ブランド力への影響
* 価格決定力への影響
* 経営陣への印象
* 短期株価への影響
* 長期投資への影響
* Buffettならどう考えるか
* 買い／様子見／見送り

---

# 現在の構成

```text
buffett-invest-analyzer

├── .env
├── .gitignore
├── requirements.txt

├── services
│   ├── app.py
│   └── src
│       ├── ai_analysis.py
│       ├── news_fetcher.py
│       ├── data_fetcher.py
│       ├── scoring_engine.py
│       ├── report.py
│       └── ...

└── docs
```

---

# requirements.txt

使用ライブラリ

* streamlit
* yfinance
* pandas
* plotly
* google-genai
* python-dotenv
* feedparser
* newspaper4k
* lxml_html_clean

---

# .env

プロジェクトルートのみ。

```text
GEMINI_API_KEY=xxxxxxxxxxxxxxxx
```

GitHubへアップロードしない。

---

# 次回のSprint

## Sprint3

目的

ニュース分析を文章だけではなく数値化する。

実装予定

* MOATスコア（0〜100）
* ブランド力評価（A〜E）
* 価格決定力評価（A〜E）
* 経営者評価（A〜E）
* Buffettなら買う確率（%）
* AI評価カードの表示

既存コードを壊さずに追加実装する。

---

# Version1.0 完成予定

* Buffett Score
* AI企業分析
* Google News RSS
* newspaper4k本文取得
* AIニュース分析
* レーダーチャート
* スコアバー
* PDF出力

---

# Version1.1

* MOAT評価
* ブランド力
* 価格決定力
* 経営者評価
* Buffettなら買うか
* AI評価カード

---

# Version2.0

* 決算短信読込
* 有価証券報告書読込
* DCF評価
* ROIC
* 適正株価
* 業界比較
* ランキング
* ウォッチリスト
* お気に入り銘柄
