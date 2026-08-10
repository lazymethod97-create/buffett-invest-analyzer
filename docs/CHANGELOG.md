# CHANGELOG.md

# Buffett Investment Analyzer

Sprint単位（1 Sprint = 1機能、docs/PROJECT_RULES.md参照）の開発履歴を、
リリース単位でまとめたもの。詳細な設計判断・不具合修正の経緯は
docs/AI_HANDOVER.md（Sprint18以降は各Sprintごとに詳細記録）を参照。

---

## [2.0.0] - Version 2.0 Release（Sprint31）

Sprint1〜30までに実装した全機能を集約したメジャーリリース。
新規機能追加ではなく、README.md・CHANGELOG.mdの整備とリポジトリ内の
旧配布物（fix.patch / fix_app.py / fix_bundle.py / sprint25.bundle /
sprint26.bundle）の削除を行った。

### スコアリング（Buffett Score、190点満点）

Sprint26時点で確定。判定基準：S:167 / A:138 / B:115 / C:92 / D:92点未満。

- Buffett Score: 40点
- DCF: 20点
- MOAT（経済的堀・定性）: 15点
- ブランド力: 10点
- 経営者評価: 10点
- Red Team（反証的レビュー）: 5点
- ROIC（投下資本利益率）: 15点
- Owner Earnings: 10点
- Intrinsic Value（内在価値・DCF併用）: 15点
- Capital Allocation（資本配分）: 10点
- Share Buyback（自社株買い）: 10点
- Debt Quality（負債の質）: 10点
- Economic Moat強化（MOATの定量的トレンド検証）: 10点
- Backtest（簡易品質スコア×フォワードリターン検証）: 10点

### 独立分析（190点満点スコアには含まれない）

- Portfolio Risk（保有ポートフォリオのリスク分散評価、10点満点の独立スコア）
- Watchlist Insights（ウォッチリスト横断の集計・ランキング表示、非スコア型）

### 分析モード

- ⚡ クイック（財務スコアのみ、Gemini呼び出し0回）
- 📊 標準（+AI定性分析・ニュース要約、Gemini呼び出し2回）
- 🔎 フル（すべて、Gemini呼び出し7回）

### 画面構成（タブ）

サマリー / 定量分析 / 定性分析 / ニュース / 仮説・レポート / Portfolio /
比較分析 / 決算資料解析

### その他の機能

- 投資仮説管理（JSON保存・読込）
- AI投資日誌（手入力、AI呼び出しなし）
- 決算資料（PDF）解析、有価証券報告書（経営方針・事業等のリスク）解析
- PDFレポート出力（単一銘柄／Portfolio Risk）
- 日本株・米国株の両方に対応

---

## Sprint別履歴

### Sprint1〜9（初期開発）

アプリの基盤を構築。Buffett Score計算エンジン、日本株・米国株のデータ取得
（yfinance）、AI定性分析（MOAT・ブランド・経営者・Red Team）、投資仮説管理
（Sprint6）、ニュースからの確認ポイント自動生成（Sprint7）、PDFレポート
出力（Sprint8）、DCF（ディスカウント・キャッシュフロー）分析（Sprint9）を
実装。

### Sprint10：AI分析結果のキャッシュ化

同一ティッカーへの重複したAI呼び出しを避けるためのキャッシュ導入。

### Sprint11：五タブ構成への再編

サマリー／定量分析／定性分析／ニュース／仮説・レポートのタブ構成を確立。

### Sprint12：分析モード選択

⚡クイック／📊標準／🔎フルの3モードを導入し、Gemini呼び出し回数
（0/2/7回）をユーザーが選択できるようにした。

### Sprint13：Portfolio（保有銘柄管理）

保有銘柄の登録・損益管理・Buffett Scoreの一覧表示。

### Sprint14：ウォッチリスト

目標株価到達判定付きのウォッチリスト機能。

### Sprint15：比較分析

複数銘柄を重ね合わせたレーダーチャートによる比較表示。

### Sprint16：AI投資日誌

売買判断の手入力記録機能（AIコメントなし）。

### Sprint17：決算資料解析

決算資料（PDF）をpdfplumberで解析するタブを追加。

### Sprint18：責務分離リファクタリング

Version2のディレクトリ構成（analysis / engines / data / ai / ui / report）
を確定。app.pyをController専用とし、create_analysis_bundle()による
分析の一元化を実施。有価証券報告書の経営方針・事業等のリスクセクション
解析も追加。

### Sprint19：ROIC分析

投下資本利益率の分析軸を追加（170点満点化の前段）。

### Sprint20：Owner Earnings分析 + Sprint19不具合修正

Owner Earningsパイプラインを追加。Sprint19で発生していた
「analyze_roic()が一度も呼ばれない」不具合を含む5件の配線不具合を修正。
health_check.pyにimportレベルの検証を追加（ルール20）。

### Sprint21：Intrinsic Value分析

内在価値分析（DCF結果と連携）を追加。

### Sprint22：Capital Allocation分析

ROIC / Owner Earnings / Intrinsic Valueの計算結果を再利用した資本配分評価。

### Sprint23：Share Buyback分析（160点満点）

自社株買いの一貫性・株式数減少効果・財務健全性バランス・PERタイミングを
評価。以降、Gitコード配布はbundle方式に統一。

### Sprint24：Debt Quality分析（170点満点）

D/E比率・インタレスト・カバレッジ・レシオ・短期負債構成・負債推移トレンド
を評価。

### Sprint25：Economic Moat強化（180点満点）

Sprint18の定性的MOAT判定を、複数年の定量トレンドで裏付け検証する独立軸。

### Sprint26：Backtest（190点満点）

過去の簡易品質スコア代理指標と実際のフォワードリターンを突き合わせる検証。
フォワードリターンの期間を「翌決算期までの約1年間」に統一し、期間長による
交絡を排除。

### Sprint27：Portfolio Risk

保有ポートフォリオ全体のリスク分散評価（セクター集中度・銘柄集中度・
地域分散・保有銘柄数）。単一銘柄の190点満点スコアとは評価単位が異なるため、
独立した10点満点の分析として実装（analysis_bundle / overall_evalには
組み込まない）。

### Sprint28：Watchlist Insights

ウォッチリスト登録銘柄全体の集計・ランキング表示。Portfolio Riskと異なり
得点化を行わない（点数化する明確な評価基準が無い機能まで無理にスコアへ
圧縮しないという判断）。

### Sprint29：Performance改善

Watchlist Insightsのループ内配置による重複実行バグを修正。Portfolio /
Watchlistタブの行構築（データ取得・スコア計算）を、無関係な操作による
Streamlitの全体再実行のたびに毎回やり直していた問題を、
signature + TTLベースのsession_stateキャッシュ（`_build_rows_cached()`）
で解消。

### Sprint30：Performance改善（続き）

候補2（フルモード一括計算の無駄）を調査した結果、対応不要と判断。
候補3（PDF生成）では、Portfolio Risk PDFが`st.download_button`の
data引数として無条件に毎回再生成されていた問題を発見し、
`_build_rows_cached()`のキャッシュ機構を汎用ヘルパー
`_cache_by_signature()`として一般化したうえで解消。

### Sprint31：Version 2.0 Release

README.md・CHANGELOG.mdの整備、リポジトリ内の旧配布物
（fix.patch / fix_app.py / fix_bundle.py / sprint25.bundle /
sprint26.bundle）の削除。新規機能追加なし。

### Sprint32：総合判定(overall)をサマリータブ・PDFレポートに表示

`bundle["overall"]`（190点満点・S〜Dグレード・BUY/WATCH/PASS判定）は
Sprint18から毎回計算されていたが、画面にもPDFにも一度も表示されていな
かった問題を発見・修正。Sprint18製で未使用だった`render_summary_card`・
`render_decision_card`（後者は14項目対応に更新）を再利用してサマリー
タブに表示し、PDFレポートにも総合判定セクションを追加した。計算ロジック
（`calculate_overall_grade()`）自体の変更なし。
