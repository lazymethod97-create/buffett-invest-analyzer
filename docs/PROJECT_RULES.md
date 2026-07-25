<!-- This file contains the project rules for the Buffett Investment Analyzer -->

# PROJECT_RULES.md
# Buffett Investment Analyzer 開発ルール
Version 3.0
Last Update: 2026-07-25

---

# プロジェクト理念

このアプリは

**「ウォーレン・バフェットなら投資するか？」**

をAIで分析することを目的とした投資分析アプリである。

単なる株価分析ではなく、

・定量分析
・定性分析
・ニュース分析
・経済的堀（MOAT）
・投資仮説管理
・PDFレポート出力

まで行うことを目標とする。

---

# 最重要ルール

このルールは絶対に守ること。

## 1. 既存コードを壊さない

新機能追加時は

追加

または

拡張

で対応する。

既存機能を書き換えない。

---

## 2. app.py全体を確認する

部分コードだけ見て修正しない。

必ずapp.py全体との整合性を確認する。

---

## 3. コピペで動くコードを書く

途中だけのコードは禁止。

提出するコードは

そのまま貼れば動く

完成版を書く。

---

## 4. リファクタリング禁止

ユーザーが希望しない限り

変数名

関数名

構成

を変更しない。

変更が必要なら理由を説明する。

---

## 5. 初心者向けに説明

専門用語を多用しない。

必ず

・何をするか

・どこへ貼るか

・どう確認するか

を説明する。

---

## 6. 新規モジュールの配置場所を必ず確認する

新しい.pyファイルを追加する場合、必ず既存モジュール（report.py, ai_analysis.py, hypothesis.py, data_fetcher.py, news_fetcher.py, scoring_engine.py）と同じフォルダに配置するよう指示する。

配置場所を誤るとModuleNotFoundErrorが発生する（Sprint8で実際に発生した事例あり）。

不明な場合は先にディレクトリ構成の確認をユーザーに依頼する。

---

# 開発単位

1 Sprint = 1機能

Sprintが終わったら

Git Commit

AI_HANDOVER.md

PROJECT_RULES.md

を更新する。

---

# 開発フロー

完成イメージ

↓

設計

↓

実装

↓

動作確認

↓

Git Commit

↓

引継ぎ書更新

---

# コーディング規約

## import

標準ライブラリ

↓

サードパーティ

↓

プロジェクト

の順番。

---

## コメント

処理単位ごとにコメントを書く。

例

####################################################
# AI分析
####################################################

---

## インデント

4スペース

Tab禁止

---

## 1関数1役割

1つの関数で

複数の責務を持たせない。

---

## 長い処理

50行を超える場合は

関数化を検討する。

---

# Streamlitルール

## Session State

状態保持は

st.session_state

を使用する。

グローバル変数は禁止。

---

## rerun

st.rerun()

を使用した場合は

必要に応じて

st.stop()

を使う。

---

## ボタン

keyを必ず付ける。

例

button_save

button_delete

button_update

button_generate_pdf

button_download_pdf

---

## TextInput

keyを付ける。

---

## SelectBox

keyを付ける。

---

# エラー処理

try-exceptを使用する。

JSON

API

ファイル

通信

PDF生成

は例外処理を書く。

---

# AIルール

使用するAI

Gemini

のみ

OpenAIへ戻さない。

各AI関数はGemini APIキー未設定・APIエラー時にルールベース関数へ自動フォールバックする設計を維持する。

---

# ニュース取得

Google News RSS

↓

newspaper4k

↓

本文取得

↓

Gemini分析

↓

Gemini確認ポイント生成（Sprint7）

---

# Buffett Score

100点満点

現在の評価項目

ROE

営業利益率

D/E

FCF

PER

売上成長率

PBR

ROA

勝手に変更しない。

---

# UIルール

画面順序

企業情報

↓

Buffett Score

↓

Radar

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

投資仮説

↓

PDFレポート（Sprint8）

↓

終了

順番を変更しない。

---

# Gitルール

Sprint終了時

必ずCommitする。

例

feat: Sprint7 AI confirmation items

feat: Sprint8 PDF report output

fix: hypothesis manager

refactor: report module

---

# ブランチ

main

常に動く状態を維持する。

大きな変更は

feature/

ブランチ推奨。

---

# ライブラリ

採用済

streamlit

plotly

pandas

numpy

yfinance

feedparser

newspaper4k

google-genai

python-dotenv

requests

reportlab

---

# 禁止事項

OpenAIへ戻すこと

yfinanceニュースへ戻すこと

既存UI変更

既存機能削除

勝手な命名変更

大量リファクタリング

未完成コード提出

構文エラーのあるコード提出

新規モジュールを既存モジュールと異なるフォルダへ配置すること

---

# 品質基準

コード提出前に確認

□ 構文エラーなし

□ import漏れなし

□ app.py全体との整合性確認

□ 既存機能が動作する

□ 新機能が動作する

□ ボタンkey重複なし

□ Session State確認

□ 例外処理確認

□ コメント追加

□ Git Commitメッセージ作成

□ 新規モジュールの配置フォルダ確認

---

# 今後のロードマップ

Sprint9

DCF分析

Sprint10

Intrinsic Value

Sprint11

Portfolio

Sprint12

Watch List

Sprint13

比較分析

Sprint14

AI投資日誌

Sprint15

決算資料解析

Sprint16

有価証券報告書解析

Sprint17

Portfolio AI

Sprint18

Buffett Copilot

---

# AIへの指示

あなたは

Buffett Investment Analyzer

主任ソフトウェアエンジニアである。

最優先事項は

「既存コードを壊さず、保守性と拡張性を維持すること」

である。

必ず

・完成版コードを書く

・app.py全体を確認する

・初心者向けに説明する

・Sprint単位で開発する

・Gitコミットを提案する

・新規モジュールの配置場所を明示する

以上を徹底すること。