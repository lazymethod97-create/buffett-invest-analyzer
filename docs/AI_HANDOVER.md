# Buffett Investment Analyzer 引継ぎ書

## プロジェクト概要

GitHub
https://github.com/lazymethod97-create/buffett-invest-analyzer

目的

「ウォーレン・バフェットならこの会社へ投資するか？」

をAIで分析するWebアプリ。

対象

・日本株
・米国株

フレームワーク

Streamlit

AI

Gemini API (google-genai)

OpenAIは使用しない。
あなたはBuffett Investment Analyzerの主任ソフトウェアエンジニアです。

このプロジェクトでは以下を厳守してください。

・初心者向けに説明する
・一度に1機能だけ作る
・必ず完成イメージを最初に示す
・クリックする場所まで説明する
・GitHubへコミットするタイミングも指示する
・AIリレー開発を前提とする
・既存コードを壊さない
・リファクタリングは理由を説明してから行う

---

# 現在の完成状況

## 完成済み

✅ Streamlit画面

✅ yfinanceで財務取得

✅ Buffett Score算出

・ROE
・営業利益率
・D/E
・PER
・PBR
・ROA
・FCF
・売上成長率

100点満点評価

---

✅ レーダーチャート

Plotly

---

✅ スコアバー

---

✅ Gemini API連携

google-genai使用

.envから

GEMINI_API_KEY

を取得。

---

✅ AI企業分析

generate_ai_analysis()

Geminiへ

・会社概要
・財務指標
・Buffett Score

を渡して日本語分析を返す。

APIキーが無い場合は

generate_rule_analysis()

へフォールバック。

---

✅ AIニュース要約

generate_news_summary()

Geminiで要約。

---

# 現在の問題

ニュース取得

現在

news_fetcher.py

では

yfinance

stock.news

を利用していたが、

2025以降かなり不安定。

日本株はほぼ取得できない。

そのため

news

が空になる。

Geminiは正常動作している。

つまり

APIキー

Gemini

には問題無し。

---

# 次に実装する内容

yfinanceニュース取得を廃止。

Google News RSSへ変更。

---

news_fetcher.py

Google News RSS

↓

企業名検索

↓

タイトル取得

↓

記事URL取得

↓

記事本文取得(newspaper4k)

↓

Geminiへ本文も渡す

---

希望する流れ

Google News RSS

↓

newspaper4k

↓

記事本文抽出

↓

Gemini

↓

ニュース要約

↓

Buffettコメント

---

# プロジェクト構成

buffett-invest-analyzer

├── .env

├── .gitignore

├── services

│   ├── app.py

│   └── src

│        ├── ai_analysis.py

│        ├── news_fetcher.py

│        ├── data_fetcher.py

│        ├── scoring_engine.py

│        ├── report.py

│        └── ...

└── docs

---

# .env

プロジェクトルート

/.env

のみ使用。

内容

GEMINI_API_KEY=xxxxxxxxxxxxxxxx

---

# .gitignore

.env

を除外。

GitHubへAPIキーはアップロードしない。

---

# requirements.txt

必要

streamlit

yfinance

pandas

plotly

google-genai

python-dotenv

feedparser

newspaper4k

lxml_html_clean

---

# app.py

ニュース取得は

news = get_latest_news(data["company_name"])

を使用。

ティッカーではなく会社名検索。

---

# 今後のロードマップ

Version1.0

・Google News RSS
・Geminiニュース要約
・AI企業分析
・Buffett Score
・レーダーチャート
・PDF出力

Version1.1

・記事本文取得

・MOAT評価

・ブランド力

・価格決定力

・経営者評価

・Buffettなら買うか

Version2.0

・決算短信読込

・有価証券報告書読込

・適正株価

・DCF

・ROIC

・業界比較

・ランキング

・ウォッチリスト

・お気に入り銘柄

---

# 開発方針

コードは必ず

「コピペでそのまま動く完成コード」

を提示すること。

部分修正ではなく

ファイル全体を書き換えられる形で提示する。

初心者でも作業できるよう

変更箇所と理由を説明する。

OpenAI APIは使用しない。

Gemini APIのみ使用する。
