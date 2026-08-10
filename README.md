# Buffett Investment Analyzer

## 概要

ウォーレン・バフェットの投資哲学をAIで再現し、
企業情報を分析して投資判断をサポートするWebアプリです。

---

## Version

Version 2.0.0

Sprint1〜30で実装した機能一式を集約したリリース。
詳細な変更履歴は docs/CHANGELOG.md を参照。

---

## 実装済み機能

### Buffett Score（190点満点）

Buffett Score / DCF / MOAT / ブランド力 / 経営者評価 / Red Team /
ROIC / Owner Earnings / Intrinsic Value / Capital Allocation /
Share Buyback / Debt Quality / Economic Moat強化 / Backtest

判定：S / A / B / C / D（詳細はdocs/CHANGELOG.md・docs/AI_HANDOVER.md参照）

### 独立分析（190点満点スコアには含まれない）

- Portfolio Risk（保有ポートフォリオのリスク分散評価）
- Watchlist Insights（ウォッチリスト横断の集計・ランキング表示）

### その他

- 日本株・米国株分析
- AI定性分析（⚡クイック／📊標準／🔎フルの3モード）
- Portfolio（保有銘柄管理）・ウォッチリスト・比較分析
- 投資仮説管理・AI投資日誌
- 決算資料（PDF）解析・有価証券報告書解析
- PDFレポート出力（単一銘柄／Portfolio Risk）

---

## 使用技術

- Python
- Streamlit
- yfinance
- GenAI API（Gemini）
- pandas
- Plotly（チャート表示）
- ReportLab（PDFレポート生成）
- pdfplumber（決算資料解析）

---

## 起動方法

```bash
pip install -r requirements.txt

streamlit run services/app.py
```

---

## 開発ルール

Sprint単位（1 Sprint = 1機能）で開発し、GitHubを唯一の正とする。

詳細なルールは docs/PROJECT_RULES.md を参照。

---

## ドキュメント

```
docs/
```

- PROJECT_RULES.md（開発ルール）
- AI_HANDOVER.md（AI引き継ぎ書・Sprint別の詳細な実装記録）
- CHANGELOG.md（Sprint別の変更履歴サマリー）
