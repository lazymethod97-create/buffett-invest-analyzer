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

### Sprint34-1：DCF未計算バグの修正

分析開始時に`dcf_result = globals().get("dcf_result") or {}`となっており、
まだ計算されていないDCF結果（常に空`{}`）が`create_analysis_bundle()`へ
渡っていた問題を修正。`dcf_result = calculate_dcf(data)`を分析開始時に
実行するよう変更。

### Sprint34-2：データ取得不能を減点扱いにしない

Buffett Score（`calculate_buffett_score()`、8項目・100点満点）が、
データを取得できなかった項目を暗黙のうちに減点として扱っていた（分母が
常に固定100点のままだったため）問題を修正。データを取得できた項目の
達成率のみでスコアを正規化し、`data_coverage`（データ取得率）を新たに
返すよう変更。app.py側では「データなし」（❓）と「悪い評価」（❌）を
UI上で区別し、データ取得率のキャプションを追加した。190点満点の構造・
判定基準（S:167等）に変更なし。あわせて`.gitignore`の文字化け
（UTF-16/UTF-8混在）を修正。

### Sprint34-3：他エンジンの同型「データ欠損=暗黙の減点」バグ調査・修正

Sprint34-2完了後、`services/src/engines/`配下の全9エンジンを横断調査。
`capital_allocation_engine.py`（reinvestment_score）と
`share_buyback_engine.py`（consistency_score・reduction_score）に、
Sprint34-2と同型のバグ（データ欠損時に初期値0＝最低評価のまま返される）
を発見し、他エンジン（debt_quality/moat_strength/backtest）と同水準の
中立評価に修正。debt_quality_engine.py・moat_strength_engine.py・
backtest_engine.py・intrinsic_engine.pyは調査の結果、既に正しく
実装されていたため変更なし。190点満点の構造・判定基準に変更なし。


### Sprint34-4：ニュース結果の190点総合判定への安全な統合

既存のニュース取得・Gemini要約を、190点満点の総合判定へ安全に接続。
ニュース自体を新しい採点項目にはせず、190点満点のスコア・配点・Grade閾値は変更しない。

`generate_news_summary_result()`でニュース要約と構造化評価（positive/neutral/negative、
severity、confidence）を1回のGemini呼び出しで取得し、
`overall_eval.py`では「negative + high severity + high confidence」の場合のみ
BUY→WATCH、WATCH→PASSへ一段階引き下げる。ニュース取得不能・AI失敗・信頼度不足では
総合判定を変更しない。

app.pyにはニュース影響の表示を追加し、health_check.pyにスコア不変・重大ニュース時の
Decision降格・ニュース無し時の中立動作を検証する回帰テストを追加した。

### Sprint34-4 追加修正：初回health_checkで発見した2件のテスト/配線問題

Windows実環境のhealth_checkで、ニュース無し時に`bundle["news_impact"]`キーが未生成となる問題と、
重大ネガティブニュースの回帰テスト期待値がBUY→WATCHではなくPASSになっていた問題を修正。
ニュース評価ロジック・190点満点スコア・Grade閾値は変更なし。

### Sprint35：永続化層

単一銘柄評価結果を保存するための独立した永続化層を追加。

- `services/src/storage/`を新設
- `ScoreSnapshot`データモデルを追加
- `JsonScoreStorage`を追加
- 銘柄ごとのJSON履歴保存に対応
- `data/history/`をGit管理対象外へ追加
- Portfolio Risk / Watchlist Insightsを単一銘柄Snapshotへ混在させない設計を維持
- 永続化層をUI・analysis_bundle・overall_evalから独立
- storage専用テスト6件を追加

検証：

- `py_compile`：PASS
- `pytest`：6 passed
- `health_check.py`：`=== HEALTH: ALL OK ===`
- `git diff --check`：PASS

### Sprint36：スコア履歴の自動保存（保存導線のみ）

Sprint35で作った永続化層(storage)を、単一銘柄の分析実行時に自動保存する
導線としてapp.pyへ配線。時系列表示UIは含まない（次Sprint以降の候補）。

- `services/src/storage/snapshot_builder.py`を新設
  - `resolve_snapshot_mode()`：UIの分析モードラベル→storageのmode変換
  - `build_score_snapshot()`：analysis_bundleの`overall`とBuffett Score結果
    からScoreSnapshotを組み立て
- `services/src/storage/__init__.py`：上記2関数をpackage APIとして公開
- `services/app.py`
  - `BASE_DIR`配下の`data/history/`を保存先として`JsonScoreStorage`を初期化
  - 分析実行（analyze_button）のたびに`ScoreSnapshot`を自動保存
  - 保存失敗時は`st.warning`で通知し、分析結果の表示自体は継続（既存機能を壊さない）
- `health_check.py`にSprint36検証項目を追加
  - モードラベル変換の回帰確認
  - `build_score_snapshot`が`ScoreSnapshot`を返すことの確認
- `tests/test_snapshot_builder.py`を新設（6件）

設計上の重要事項：

- 190点満点のスコア構造・overall_evalの判定責務は変更していない
- app.py側にはUIモード変換やScoreSnapshot組み立てロジックを書かず、
  storageパッケージへ切り出した（ルール4：app.pyへ分析ロジックを書かない）
- Portfolio Risk / Watchlist Insightsは引き続きScoreSnapshotへ混在させない

検証：

- `py_compile`：PASS（`services/app.py` / `services/src/storage/*.py` /
  `tests/test_snapshot_builder.py`）
- `pytest`：`tests/test_storage.py` + `tests/test_snapshot_builder.py` →
  12 passed
- `health_check.py`：Sprint36検証項目（`Sprint36 members (score snapshot
  auto-save wiring)`）はPASS。他項目のFAILはAIサンドボックス環境固有の
  差異（Windows固定BASEパス・Gemini APIキー未設定）によるもので、
  Sprint36の変更による回帰ではない（ローカルWindows環境での
  `python health_check.py`実行結果での最終確認を推奨）
- `git diff --check`：PASS

### Sprint37：スコア推移（履歴）の表示UI

Sprint36で自動保存しているScoreSnapshotを、サマリータブ末尾に折れ線
チャートとして表示。保存・読み込みロジックには手を入れず、既存の
`JsonScoreStorage.load_history()`を読み取って表示するだけ。

- `services/src/report/report.py`
  - `create_score_history_chart(history)`を追加
  - ScoreSnapshotのリストから`evaluated_at`/`overall_score`を折れ線に、
    `grade`/`decision`/`mode`をホバーテキストに表示
  - 空リストのときは空のFigureを返す（表示要否の判断はapp.py側）
- `services/app.py`
  - サマリータブ末尾（Red Teamセクションの後）に
    「📈 スコア推移（履歴）」セクションを追加
  - `score_storage.load_history(data["ticker"])`を呼び、
    0件なら「履歴はまだありません」、1件以上ならチャート＋直近の
    記録テキストを表示
  - 読み込み失敗時は`st.warning`で通知し、他の表示は継続
- `health_check.py`にSprint37検証項目を追加
- `tests/test_score_history_chart.py`を新設（4件）

検証：

- `py_compile`：PASS
- `pytest`：`test_storage.py`(6) + `test_snapshot_builder.py`(6) +
  `test_score_history_chart.py`(4) → 16 passed
- `health_check.py`：Sprint37検証項目PASS
- `git diff --check`：PASS
