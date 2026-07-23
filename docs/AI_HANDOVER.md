# AI_HANDOVER.md

# Buffett Investment Analyzer 引継ぎ書

## 現在のバージョン

Version 2 Sprint1 完了

Version1 基本機能は完成。
Version2 Sprint1「Buffett Investment Checklist」は実装済み。

---

# Version1 完成済み

## 財務分析

* Buffett Score
* ROE
* ROA
* PER
* PBR
* D/E
* 営業利益率
* フリーキャッシュフロー
* 売上成長率

---

## 可視化

* レーダーチャート

* スコアバー

---

## AI分析

Gemini API

企業分析

ニュース分析

---

## ニュース

Google News RSS

↓

feedparser

↓

newspaper4k

↓

記事本文取得

↓

Gemini分析

---

## AIニュース分析

分析内容

* ニュース要約
* ポジティブ要因
* ネガティブ要因
* MOATへの影響
* ブランド力への影響
* 価格決定力への影響
* 経営者評価
* 短期影響
* 長期影響
* Buffettならどう考えるか

---

# Version2 Sprint1 完了

## Buffett Investment Checklist

実装済み。

以下の6項目を画面に表示する。

1. 経営圏（Understandable Business）
2. 競争優位性（MOAT）
3. 財務健全性（Conservative Debt）
4. 収益性（High Margin）
5. 経営者（Management Quality）
6. 安全余裕（Margin of Safety）

各項目は pass / warning / fail で判定。
Gemini API あり → AI判定
Gemini API なし → ルールベース判定

表示場所：AIニュース要約と採点詳細の間。

---

# Version2 残Sprint

現在開発中

---

## Sprint2

MOAT評価

未実装

最優先で開発する。

---

## Sprint3

ブランド力評価

未実装

---

## Sprint4

経営者評価

未実装

---

## Sprint5

Red Team AI

未実装

---

## Sprint6

投資仮説管理

未実装

---

## Sprint7

ニュース→確認項目

未実装

---

## Sprint8

判断賞味期限

未実装

---

## Sprint9

投資メモ

未実装

---

## Sprint10

ウォッチリスト

未実装

---

# 次回最初に行うこと

Sprint2

MOAT評価

を実装する。

変更予定ファイル

* ai_analysis.py
* app.py
* report.py（必要なら）

既存コードは壊さない。

まずMOAT評価を画面へ表示する。

---

# Git

Sprintごとにコミットする。

例

feat: add Buffett Investment Checklist

次は

feat: add MOAT evaluation

---

# AIへの指示

このファイルを読んだら

最初に

1. 現在の完成状況

2. 次Sprint

3. 変更するファイル

4. 完成イメージ

5. 既存コードへ影響しない理由

を説明すること。

ユーザーが

**「進めて」**

と言うまでコードを書いてはいけない。

承認を得てから実装すること。
