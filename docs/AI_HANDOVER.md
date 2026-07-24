```markdown
# Buffett Investment Analyzer
# AI 引継ぎ書（Sprint6完了時点）
Version: 2.0
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

・AIによる仮説生成

・手動追加

・状態変更

・削除

・JSON保存

・JSON読込

・企業変更時に仮説リセット

完了

---

# app.py

最新版

Sprint6対応済

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

投資仮説管理

↓

採点詳細

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

---

# report.py

現在は

create_hypothesis_display()

は未使用

表示はapp.pyで行っている

削除しなくてよい

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

---

# 次Sprint

Sprint7

テーマ

ニュースから

AIが

「確認すべきポイント」

を自動生成する

例

決算確認項目

リスクイベント

競合動向

設備投資

規制

為替

など

Checklistへ統合予定

---

# 将来実装予定

□ PDFレポート

□ Excel出力

□ DCF分析

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

---

Git Commit

feat: complete Sprint6 Investment Hypothesis Manager

---

現在Version

Ver2.0

Sprint6完了

次回はSprint7から開始する

```
