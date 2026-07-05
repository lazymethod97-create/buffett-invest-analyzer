# Buffett Investment Analyzer

## プロジェクト概要

ウォーレン・バフェットの投資哲学をもとに、
企業の財務指標・定性情報・AI分析を組み合わせて
「バフェットなら投資するか」を判定するWebアプリを開発する。

---

## Version 1.0 の目標

- Streamlit によるWebアプリ
- Buffett Score
- 日本株対応
- 米国株対応
- AI定性分析
- 判定理由の表示
- PDFレポート出力

---

## 開発ルール

- GitHubを唯一の正本とする
- 1 Sprint = 1機能
- 変更ファイルは最大2つ
- 毎回動作確認後にGitHubへPush
- 完成コードをファイル単位で管理する
- Claude・Gemini・ChatGPT間で引き継げる設計を維持する

---

## ディレクトリ構成（予定）

```
app.py
config/
core/
data/
reports/
docs/
tests/
assets/
```

---

## 開発方針

まずはシンプルな構成を維持し、
Version1.0完成後に機能追加しやすい設計とする。
