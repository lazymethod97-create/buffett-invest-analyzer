# AI引継ぎ文書 / AI Handover Document

## プロジェクト概要
ウォーレン・バフェットの投資基準に基づいて株式を評価するWebアプリ。

## GitHub
https://github.com/lazymethod97-create/buffett-invest-analyzer

## 技術スタック
- Python 3.11+ / Streamlit / yfinance / Plotly

## ファイル構成
buffett-invest-analyzer/
├── app.py
├── requirements.txt
├── src/ (__init__.py, data_fetcher.py, scoring_engine.py, report.py)
└── docs/AI_HANDOVER.md

## 起動方法
python -m venv venv
venv\Scripts\activate （Macは source venv/bin/activate）
pip install -r requirements.txt
streamlit run app.py

## AI開発の厳守ルール（これまでの反省から）
1. 推測でコードを書かない。既存のファイル構成と変数名を必ず確認する。
2. 1 Sprint = 1機能。一度に複数の機能を詰め込まない。
3. 変更するファイルは最大2つまで。
4. 省略記号（...）を使わず、必ずファイル全体の完成版コードを提示する。
5. UI（app.py）とロジック（src/以下）は分離を維持する。
6. 動作確認が取れたコードのみ提示し、確認後にGitHubへコミットする。

## 既知の制限事項（次のSprintで改善予定）
- 時価総額の表示単位は現状「B（十億）」固定。日本株は本来「兆円」表示が自然。
- debtToEquityの値はyfinance側で単位が揺れる（100の倍率で返る場合とそうでない場合がある）ため、100超の場合のみ100で割る簡易補正をしている。
- ROICと自社株買いの実施有無は無料APIでは取得しづらいため、代わりにROAとPBRで代替している。

## 次にやること（Next Tasks / Version 0.4以降）
- [×] AI定性分析の追加
- [ ] ニュース取得・要約
- [ ] PDFレポート出力
- [ ] 分析履歴の保存（SQLite）
- [ ] お気に入り銘柄リスト

## 現在のバージョン
v0.3.0（MVP完成版）
