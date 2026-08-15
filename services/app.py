import os
import sys
import datetime
import time

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, ".env"))

import streamlit as st

####################################################
# Sprint15: 比較分析タブの重ね合わせレーダーチャートのために追加。
# report.py側は変更せず、比較専用の描画はapp.py側で行う。
####################################################
import plotly.graph_objects as go

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_fetcher import get_stock_data, format_value
from scoring_engine import calculate_buffett_score
from report import (
	create_radar_chart,
	create_score_bar,
	create_checklist_display,
	create_moat_display,
	create_brand_display,
	create_management_display,
	create_red_team_display,
	create_confirmation_points_display,
	create_dcf_display,
	create_roic_display,
	create_owner_earnings_display,
	create_intrinsic_value_display,
	create_capital_allocation_display,
	create_share_buyback_display,
	create_debt_quality_display,
	create_moat_strength_display,
	create_backtest_display,
	create_portfolio_risk_display,
	create_watchlist_insights_display,
)
from hypothesis import (
	HypothesisManager,
	HypothesisStatus,
	InvestmentHypothesis,
	generate_default_hypotheses,
)
from portfolio import (
	PortfolioHolding,
	PortfolioManager,
)
from watchlist import (
	WatchListItem,
	WatchListManager,
)
from journal import (
	JournalEntry,
	JournalManager,
)
from ai_analysis import (
	generate_ai_analysis,
	generate_news_summary,
	generate_buffett_checklist,
	generate_moat_analysis,
	generate_brand_analysis,
	generate_management_analysis,
	generate_red_team_analysis,
	generate_investment_hypothesis,
	generate_news_confirmation_points,
	generate_earnings_material_analysis,
)
from analysis import create_analysis_bundle
from news_fetcher import get_latest_news
from pdf_report import generate_pdf_report
from dcf_analysis import calculate_dcf
from earnings_material import extract_text_from_pdf

####################################################
# Sprint27: Portfolio Risk（保有ポートフォリオのリスク分散評価）
# 単一銘柄向けの分析（analysis_bundle経由）とは評価単位が異なる独立機能のため、
# 旧配置ラッパー（data_fetcher.py等）は触らず、新パッケージ（analysis / report）
# から直接importする。generate_portfolio_pdf_reportはreportパッケージが
# 再エクスポート済み（services/src/report/__init__.py）。
####################################################
from analysis.portfolio_risk import analyze_portfolio_risk
from report import generate_portfolio_pdf_report

####################################################
# Sprint32: 総合判定(overall)をサマリータブに表示する。
# create_analysis_bundle()はSprint18から毎回overall_eval.calculate_overall_grade()
# を実行し bundle["overall"] に格納していたが、これまでapp.py側で一度も
# 取り出して表示していなかった（計算はされるが画面に出ない状態）。
# 表示部品はSprint18時点で用意されていたservices/src/ui/を再利用する
# （重複実装禁止・ルール14）。render_decision_card()のみ、Sprint19〜26で
# 追加された8項目に対応していなかったため中身を更新した。
####################################################
from ui import render_summary_card, render_decision_card

####################################################
# Sprint28: Watchlist Insights（ウォッチリスト横断の集計・ランキング表示）
# Portfolio Risk（Sprint27）と同じく複数銘柄が評価単位のため独立機能とし、
# 新パッケージ（analysis / report）から直接importする。得点化は行わない
# （PROJECT_RULES.md / docs/AI_HANDOVER.md Sprint28セクション参照）。
####################################################
from analysis.watchlist_insights import build_watchlist_insights

st.set_page_config(page_title="Buffett Investment Analyzer", page_icon="📈", layout="wide")

####################################################
# Sprint10: キャッシュ化
# 既存モジュール(data_fetcher.py / news_fetcher.py)は変更せず、
# app.py側でst.cache_dataのラッパーを作って呼び出し口だけ差し替える。
# 同じティッカーなら1時間はAPIを再取得しない。
####################################################
@st.cache_data(ttl=3600)
def cached_get_stock_data(ticker):
	return get_stock_data(ticker)


@st.cache_data(ttl=3600)
def cached_get_latest_news(company_name):
	return get_latest_news(company_name)


####################################################
# Sprint29: Performance改善
# Portfolio / Watchlistタブは、アプリ内のどこか（他タブ含む）で
# ボタン/入力が操作されるたびにStreamlitがスクリプト全体を再実行するため、
# 「登録銘柄ぶんループしてcached_get_stock_data + calculate_buffett_scoreを
# 実行する」処理も、無関係な操作のたびに毎回再実行されていた。
# cached_get_stock_data自体はst.cache_data(ttl=3600)でキャッシュ済みのため
# キャッシュヒット時は軽いが、キャッシュミス時（1時間経過後等）は登録銘柄数ぶんの
# yfinance呼び出しが直列に発生し、アプリ全体の応答が重くなる（Portfolio/Watchlist
# タブを見ていない操作のときも含めて）。
#
# 対策：構築済みのrows自体を「銘柄構成（signature）」と紐付けてsession_stateに
# 保持し、銘柄構成が変わっておらず、かつcached_get_stock_dataと同じTTL（3600秒）
# 以内であれば再構築をスキップする。データ取得・スコア計算のロジック自体（build_row_fn）
# は変更しないため、出力される値は変更前と完全に同一（重複実装禁止・ルール14により
# Portfolio/Watchlistで共通のヘルパーとして1箇所にまとめる）。
####################################################
####################################################
# Sprint30: Performance改善（続き）
# Sprint29の_build_rows_cached()が使っていた「signature + TTLでsession_state
# キャッシュし、両方一致すれば再計算をスキップする」という仕組みは、
# rows（Portfolio/Watchlistの銘柄一覧）以外の重い処理（例：PDFバイト列生成）
# にも共通して使える汎用パターンである。重複実装禁止（ルール14）のため、
# 汎用ヘルパー_cache_by_signature()を新設し、_build_rows_cached()自体も
# これを呼び出す薄いラッパーに書き換える（signature計算・TTL判定・戻り値は
# 完全に同一のため、Portfolio/Watchlist側の挙動・出力は一切変わらない）。
####################################################
def _cache_by_signature(session_key, signature, build_fn, ttl_seconds=3600):
	cached = st.session_state.get(session_key)
	now = time.time()
	if (
		cached is not None
		and cached.get("signature") == signature
		and (now - cached.get("built_at", 0)) < ttl_seconds
	):
		return cached["value"]

	value = build_fn()
	st.session_state[session_key] = {
		"signature": signature,
		"built_at": now,
		"value": value,
	}
	return value


def _build_rows_cached(session_key, items, ticker_of, build_row_fn, ttl_seconds=3600):
	signature = tuple(sorted(ticker_of(item) for item in items))
	return _cache_by_signature(
		session_key,
		signature,
		lambda: [build_row_fn(item) for item in items],
		ttl_seconds=ttl_seconds,
	)


####################################################
# Sprint11: サマリータブ用の小さな表示ヘルパー
# report.py の create_moat_display 等（詳細表示）はそのまま「定性分析」タブで使う。
# ここではサマリータブ専用に、既存の辞書データから
# 星評価・結論だけを抜き出して表示する。新しいAI呼び出しは追加しない。
####################################################
def _star_line(stars):
	stars = stars or 0
	return "★" * stars + "☆" * (5 - stars)


def _moat_rating_label(rating):
	return {
		"wide": "🟢 Wide MOAT",
		"narrow": "🟡 Narrow MOAT",
		"none": "🔴 No MOAT",
	}.get(rating, rating or "不明")


def _mode_locked_message(required_mode_label):
	"""Sprint12: 現在の分析モードでは実行していない項目に表示する案内"""
	st.info(
		f"🔒 この項目は「{required_mode_label}」モードで表示されます。"
		f"サイドバーでモードを切り替えて、もう一度「🔍 分析開始」を押してください。"
	)


####################################################
# Sprint12: 分析モード選択
# クイック: 財務スコア・レーダー・DCFのみ（すべてルールベース計算、Gemini呼び出し0回）
# 標準　 : クイック + AI定性分析 + Checklist + ニュース要約（Gemini 2回）
# フル　 : 標準 + MOAT/ブランド/経営者/RedTeam + ニュース確認ポイント + 投資仮説 + PDF（Gemini 7回、従来通り）
####################################################
st.sidebar.subheader("🔍 分析モード")
analysis_mode = st.sidebar.radio(
	"どこまで分析しますか？",
	["⚡ クイック（財務スコアのみ）", "📊 標準（+AI定性分析・要約）", "🔎 フル（すべて）"],
	index=2,
	key="analysis_mode_radio",
)
st.sidebar.caption(
	"フルモードはGeminiを7回呼び出します。まず複数銘柄をクイックで比較し、"
	"気になった銘柄だけフルで分析するのがおすすめです。"
)

# 再実行のたびに初期化されないよう、セッション状態に保持する
if "hypothesis_manager" not in st.session_state:
	st.session_state.hypothesis_manager = HypothesisManager()
hypothesis_manager = st.session_state.hypothesis_manager

####################################################
# Sprint13: Portfolio（保有銘柄管理）
# session_stateにPortfolioManagerを保持する。
# 今回はセッション中のみ保持し、JSON保存/読込は行わない
# （保存機能はSprint14以降で検討）。
####################################################
if "portfolio_manager" not in st.session_state:
	st.session_state.portfolio_manager = PortfolioManager()
portfolio_manager = st.session_state.portfolio_manager

####################################################
# Sprint14: ウォッチリスト
# Portfolioと同じパターンでsession_stateに保持する。
# セッション中のみ保持し、JSON保存/読込は行わない（保有銘柄と同様の方針）。
####################################################
if "watchlist_manager" not in st.session_state:
	st.session_state.watchlist_manager = WatchListManager()
watchlist_manager = st.session_state.watchlist_manager

####################################################
# Sprint15: 比較分析
# 「比較する」ボタンを押した時だけ計算し、結果をsession_stateに保持する。
# こうしないと、他のウィジェット操作のたびに毎回全銘柄を再取得してしまうため
# （Sprint10のキャッシュ化と同じ考え方）。
####################################################
if "compare_bundle" not in st.session_state:
	st.session_state.compare_bundle = None

####################################################
# Sprint16: AI投資日誌（手入力のみ、AI呼び出しなし）
# 投資仮説管理と同様、JSON保存/読込に対応する。
# last_loaded_journal_file_idは、hypothesis.pyのJSON読込で発生した
# 無限ループ不具合と同じ問題を防ぐためのもの（Sprint10〜11の間の修正と同じ考え方）。
####################################################
if "journal_manager" not in st.session_state:
	st.session_state.journal_manager = JournalManager()
journal_manager = st.session_state.journal_manager

if "last_loaded_journal_file_id" not in st.session_state:
	st.session_state.last_loaded_journal_file_id = None

####################################################
# Sprint17: 決算資料解析
# 「📑 資料を解析する」ボタンを押した時だけPDF抽出・Gemini呼び出しを行い、
# 結果をsession_stateに保持する（Sprint15の比較分析と同じ考え方）。
####################################################
if "earnings_material_result" not in st.session_state:
	st.session_state.earnings_material_result = None

st.title("📈 Buffett Investment Analyzer")
st.caption("ウォーレン・バフェットならこの株を買うか？を分析します")
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
	ticker_input = st.text_input(
		"ティッカーシンボルを入力してください",
		placeholder="例：AAPL（米国株）または 7203（日本株）",
	)
with col2:
	st.write("")
	st.write("")
	analyze_button = st.button("🔍 分析開始", type="primary", use_container_width=True)

with st.expander("📖 使い方 / 判定基準"):
	st.markdown("""
	**例**：`AAPL`（Apple）、`7203`（トヨタ自動車）、`9984`（ソフトバンクグループ）

	### 総合判定（190点満点）

	Buffett Score・DCF・MOAT・ブランド・経営者・Red Team・ROIC・
	Owner Earnings・Intrinsic Value・Capital Allocation・Share Buyback・
	Debt Quality・Economic Moat強化・Backtestの14項目を統合した判定です
	（🔎フルモードで全項目が揃います）。

	| Grade | 点数 | Action |
	|-------|------|--------|
	| S | 167点以上 | 積極的に投資候補 |
	| A | 138点以上 | 買い候補 |
	| B | 115点以上 | 監視継続 |
	| C | 92点以上 | 慎重に様子見 |
	| D | 92点未満 | 見送り |

	総合判定（BUY🟢/WATCH🟡/PASS🔴）：S・Aかつリスク高でない→BUY、
	Bかつリスク高でない→WATCH、それ以外→PASS

	### Buffett Score（上記の1項目、100点満点）

	| 項目 | 満点 | 合格ライン |
	|------|------|-----------|
	| ROE | 20点 | 15%以上 |
	| 営業利益率 | 15点 | 15%以上 |
	| 負債比率(D/E) | 15点 | 1.0以下 |
	| FCF | 15点 | プラス |
	| PER | 10点 | 25倍以下 |
	| 売上成長率 | 10点 | 5%以上 |
	| PBR | 10点 | 3.0倍以下 |
	| ROA | 5点 | 5%以上 |

	**75点以上 → 投資推奨**（Buffett Score単体の判定。総合判定とは別）
	""")

# ------------------------------------------------------------
# 分析実行
# Sprint10: ここでAI分析を1回だけ実行し、結果をまとめて
# st.session_state.analysis_bundle に保存する。
# 以降、DCFスライダーなどを動かして再実行されても、
# このブロックはボタンを押さない限り通らないため、
# Gemini呼び出しは走らない。
# ------------------------------------------------------------
if analyze_button and ticker_input:
	with st.spinner(f"「{ticker_input}」のデータを取得中..."):
		result = cached_get_stock_data(ticker_input)

	if not result["success"]:
		st.error(
			f"データを取得できませんでした。ティッカーシンボルを確認してください。\n\n"
			f"エラー: {result['error']}"
		)
		st.stop()

	data = result["data"]
	score_result = calculate_buffett_score(data)

	if (
		"last_company" not in st.session_state
		or st.session_state.last_company != data["company_name"]
	):
		hypothesis_manager.clear()
		st.session_state.last_company = data["company_name"]

	st.session_state.current_data = data
	st.session_state.current_score_result = score_result
	####################################################
	# Sprint18 Phase4: 分析はanalysis_bundleに一元化
	# app.pyはControllerとしてcreate_analysis_bundle()を呼ぶだけ。
	# データ取得(news)のみapp.pyが担当する。
	####################################################
	if analysis_mode.startswith("⚡"):
		news = None
	else:
		news = cached_get_latest_news(data["company_name"])

	# Sprint34-1: calculate the default DCF before building the analysis bundle.
	dcf_result = calculate_dcf(data)
	with st.spinner("🤖 AIが分析中...（初回のみ少し時間がかかります）"):
		bundle = create_analysis_bundle(
			data=data,
			score_result=score_result,
			dcf_result=dcf_result,
			mode=analysis_mode,
			news=news,
			is_quick=analysis_mode.startswith("⚡"),
			is_full=analysis_mode.startswith("🔎"),
		)

	st.session_state.analysis_bundle = bundle

# ------------------------------------------------------------
# 結果表示
# Sprint11: PROJECT_RULES.md Ver4.0のタブ構成に合わせて表示する。
# タブの並び: [サマリー][定量分析][定性分析][ニュース][仮説・レポート]
# 会社情報のみタブの外（常に上部固定）。
# ------------------------------------------------------------
if (
	"current_data" in st.session_state
	and "current_score_result" in st.session_state
	and "analysis_bundle" in st.session_state
):
	data = st.session_state.current_data
	score_result = st.session_state.current_score_result
	bundle = st.session_state.analysis_bundle

	# Sprint12: この分析がどのモードで実行されたかを見て、表示できる項目を判定する
	current_mode = bundle.get("mode", "🔎 フル（すべて）")
	is_standard_plus = not current_mode.startswith("⚡")
	is_full = current_mode.startswith("🔎")

	news = bundle.get("news")
	analysis = bundle.get("analysis")
	summary = bundle.get("summary")
	confirmation_points = bundle.get("confirmation_points")
	news_impact = bundle.get("news_impact")
	checklist = bundle.get("checklist")
	moat = bundle.get("moat")
	brand = bundle.get("brand")
	mgmt = bundle.get("mgmt")
	red_team = bundle.get("red_team")
	roic = bundle.get("roic")
	owner_earnings = bundle.get("owner_earnings")
	intrinsic_value = bundle.get("intrinsic_value")
	capital_allocation = bundle.get("capital_allocation")
	share_buyback = bundle.get("share_buyback")
	debt_quality = bundle.get("debt_quality")
	moat_strength = bundle.get("moat_strength")
	backtest = bundle.get("backtest")
	overall = bundle.get("overall")

	currency = "¥" if data.get("country") == "Japan" else "$"
	st.caption(f"現在の分析モード: **{current_mode}**")

	####################################################
	# 会社情報（タブの外、常に上部固定）
	####################################################
	st.subheader(f"🏢 {data['company_name']}")
	c1, c2, c3, c4 = st.columns(4)
	c1.metric("セクター", data.get("sector", "不明"))
	c2.metric("国", data.get("country", "不明"))
	price = data.get("current_price", 0)
	c3.metric("現在株価", f"{currency}{price:,.2f}" if price else "不明")
	cap = data.get("market_cap", 0)
	c4.metric("時価総額", f"{currency}{cap/1_000_000_000:.1f}B" if cap else "不明")

	st.divider()

	tab_summary, tab_quant, tab_qual, tab_news, tab_hypo, tab_portfolio, tab_compare, tab_earnings = st.tabs(
		["📊 サマリー", "📈 定量分析", "🧠 定性分析", "📰 ニュース", "📋 仮説・レポート", "💼 Portfolio", "⚖️ 比較分析", "📑 決算資料解析"]
	)

	####################################################
	# 📈 定量分析タブ
	# 先にここでDCFを計算しておく（サマリータブで結果を再利用するため）。
	# スライダーはこのタブ内に表示されるが、コードの実行順自体は
	# タブの表示順と無関係なので、サマリータブより先に計算しても問題ない。
	####################################################
	with tab_quant:
		st.subheader("📊 指標レーダーチャート")
		st.plotly_chart(create_radar_chart(score_result["details"]), use_container_width=True)

		st.divider()
		st.subheader("📋 採点詳細")
		coverage = score_result.get("data_coverage")
		if coverage:
			st.caption(
				f"データ取得率: {coverage['available_items']}/{coverage['total_items']}項目"
				f"（{coverage['coverage_pct']}%） ※データ未取得の項目は減点せず、"
				f"取得できた項目のみで採点しています。"
			)
		for d in score_result["details"]:
			# Sprint34-2: 「データなし」は減点対象外のため、悪い評価（❌）と
			# 区別して未評価（❓）として表示する。
			if not d.get("data_available", True):
				icon = "❓"
			else:
				icon = "✅" if d["passed"] else "❌"
			col_a, col_b, col_c, col_d = st.columns([3, 2, 1, 4])
			col_a.write(f"{icon} **{d['item']}**")
			col_b.write(f"📊 {d['value']}")
			col_c.write(f"**{d['score']}/{d['max_score']}点**")
			col_d.caption(d["comment"])

		st.divider()
		st.subheader("💰 DCF分析（理論株価）")
		st.caption("フリーキャッシュフローを将来に投影し、現在価値に割り引いて理論株価を算出します。")

		dcf_col1, dcf_col2, dcf_col3 = st.columns(3)
		with dcf_col1:
			dcf_growth_rate = st.slider(
				"FCF成長率（年率）", 0.0, 0.20, 0.05, step=0.005,
				format="%.1f%%", key="slider_dcf_growth",
			)
		with dcf_col2:
			dcf_discount_rate = st.slider(
				"割引率（WACC簡易値）", 0.05, 0.20, 0.10, step=0.005,
				format="%.1f%%", key="slider_dcf_discount",
			)
		with dcf_col3:
			dcf_terminal_growth = st.slider(
				"永久成長率", 0.0, 0.05, 0.025, step=0.005,
				format="%.1f%%", key="slider_dcf_terminal",
			)

		dcf_result = calculate_dcf(
			data,
			growth_rate=dcf_growth_rate,
			discount_rate=dcf_discount_rate,
			terminal_growth=dcf_terminal_growth,
		)
		st.markdown(create_dcf_display(dcf_result))

	####################################################
	# 📊 サマリータブ
	# 既存の詳細表示関数は使わず、辞書から星評価・結論だけを抜き出して表示する。
	# 新しいAI呼び出しは追加していない。
	####################################################
	with tab_summary:
		####################################################
		# Sprint32: 総合判定(overall)をサマリータブ最上部に表示する。
		# bundle["overall"]はSprint18から毎回計算されていたが、これまで
		# app.py側で一度も表示していなかった（詳細はdocs/AI_HANDOVER.md
		# Sprint32セクション参照）。
		# クイック/標準モードではMOAT・ROIC等の一部項目が未評価
		# （calculate_overall_grade側で0点扱い）になるため、フルモードで
		# ない場合はその旨を注記する。
		####################################################
		render_summary_card(overall, score_result)
		if not is_full:
			st.caption(
				"⚠️ 現在の分析モードでは一部の項目（MOAT・ROIC等）が未評価のため、"
				"総合判定は暫定値です。🔎フルモードで再分析すると全14項目で判定されます。"
			)
		render_decision_card(overall)

		# Sprint34-4: ニュースは190点満点の加点/減点ではなく、重大リスクが
		# ある場合のみ最終Decisionの安全装置として表示する。
		if news_impact and news_impact.get("available"):
			impact_label = {"positive": "ポジティブ", "neutral": "中立", "negative": "ネガティブ"}.get(
				news_impact.get("impact"), "不明"
			)
			severity_label = {"low": "低", "medium": "中", "high": "高"}.get(
				news_impact.get("severity"), "不明"
			)
			confidence_label = {"low": "低", "medium": "中", "high": "高"}.get(
				news_impact.get("confidence"), "不明"
			)
			st.info(
				f"📰 ニュース評価：{impact_label} / 重大度：{severity_label} / 信頼度：{confidence_label}\n\n"
				f"{news_impact.get('reason', '')}"
			)
		elif is_standard_plus and news:
			st.caption("📰 ニュース評価は利用できないため、総合判定には影響していません。")

		st.divider()
		st.plotly_chart(
			create_score_bar(score_result["total_score"], score_result["max_score"]),
			use_container_width=True,
		)
		st.markdown(f"## {score_result['verdict']}")
		st.markdown(f"**スコア: {score_result['total_score']} / 100点**")
		st.info(score_result["verdict_comment"])

		st.divider()
		st.markdown("### 💰 DCF理論株価")
		if dcf_result.get("success"):
			st.markdown(
				f"**理論株価:** {currency}{dcf_result['intrinsic_value_per_share']:.2f}　"
				f"**現在株価:** {currency}{dcf_result['current_price']:.2f}\n\n"
				f"**安全余裕:** {dcf_result['margin_of_safety_pct']:+.1f}%\n\n"
				f"**判定:** {dcf_result['verdict']}"
			)
		else:
			st.info(dcf_result.get("error", "DCF評価を計算できませんでした。"))

		st.divider()
		st.markdown("### 🏰🏷️👔 MOAT・ブランド・経営者（総合評価）")
		if is_full:
			m1, m2, m3 = st.columns(3)
			with m1:
				st.markdown(
					f"**MOAT**\n\n{_moat_rating_label(moat.get('rating'))}\n\n"
					f"{_star_line(moat.get('stars'))}"
				)
			with m2:
				st.markdown(
					f"**ブランド**\n\n（{brand.get('brand_type', '不明')}）\n\n"
					f"{_star_line(brand.get('stars'))}"
				)
			with m3:
				st.markdown(
					f"**経営者**\n\n{_star_line(mgmt.get('stars'))}"
				)
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.markdown("### 🔴 Red Teamの結論")
		if is_full:
			st.warning(red_team.get("conclusion", "結論なし"))
		else:
			_mode_locked_message("🔎 フル（すべて）")

	####################################################
	# 🧠 定性分析タブ
	####################################################
	with tab_qual:
		st.subheader("🤖 AI定性分析")
		if is_standard_plus:
			st.info(analysis)
		else:
			_mode_locked_message("📊 標準（+AI定性分析・要約）")

		st.divider()
		st.subheader("📋 Buffett Investment Checklist")
		if is_standard_plus:
			st.markdown(create_checklist_display(checklist))
		else:
			_mode_locked_message("📊 標準（+AI定性分析・要約）")

		st.divider()
		st.subheader("🏰 MOAT評価（経済的堀）")
		if is_full:
			st.markdown(create_moat_display(moat))
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("💰 ROIC（投下資本利益率）分析")
		if is_full:
			if roic:
				st.markdown(create_roic_display(roic))
			else:
				st.info("ROIC分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("💵 Owner Earnings（オーナーアーニングス）分析")
		if is_full:
			if owner_earnings:
				st.markdown(create_owner_earnings_display(owner_earnings))
			else:
				st.info("Owner Earnings分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("🎯 Intrinsic Value（内在価値）分析")
		if is_full:
			if intrinsic_value:
				st.markdown(create_intrinsic_value_display(intrinsic_value))
			else:
				st.info("Intrinsic Value分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("🔄 Capital Allocation（資本配分）分析")
		if is_full:
			if capital_allocation:
				st.markdown(create_capital_allocation_display(capital_allocation))
			else:
				st.info("Capital Allocation分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("🔁 Share Buyback（自社株買い）分析")
		if is_full:
			if share_buyback:
				st.markdown(create_share_buyback_display(share_buyback))
			else:
				st.info("Share Buyback分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("🏦 Debt Quality（負債の質）分析")
		if is_full:
			if debt_quality:
				st.markdown(create_debt_quality_display(debt_quality))
			else:
				st.info("Debt Quality分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("🏰 Economic Moat強化（経済的堀の定量的検証）分析")
		if is_full:
			if moat_strength:
				st.markdown(create_moat_strength_display(moat_strength))
			else:
				st.info("Economic Moat強化分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("📈 Backtest（簡易品質スコア × フォワードリターン検証）分析")
		if is_full:
			if backtest:
				st.markdown(create_backtest_display(backtest))
			else:
				st.info("Backtest分析結果がありません。")
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("🏷️ ブランド力評価")
		if is_full:
			st.markdown(create_brand_display(brand))
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("👔 経営者評価")
		if is_full:
			st.markdown(create_management_display(mgmt))
		else:
			_mode_locked_message("🔎 フル（すべて）")

		st.divider()
		st.subheader("🔴 Red Team AI（反対意見）")
		if is_full:
			st.markdown(create_red_team_display(red_team))
		else:
			_mode_locked_message("🔎 フル（すべて）")

	####################################################
	# 📰 ニュースタブ
	####################################################
	with tab_news:
		st.subheader("📰 最新ニュース")
		if not is_standard_plus:
			_mode_locked_message("📊 標準（+AI定性分析・要約）")
		elif news:
			for article in news:
				st.markdown(f"**• {article['title']}**")
				if article["publisher"]:
					st.caption(article["publisher"])
		else:
			st.info("ニュースは取得できませんでした。")

		st.divider()
		st.subheader("📝 AIニュース要約")
		if not is_standard_plus:
			_mode_locked_message("📊 標準（+AI定性分析・要約）")
		elif news:
			st.success(summary)
		else:
			st.info("要約するニュースがありません。")

		st.divider()
		st.subheader("⚖️ 総合判定へのニュース影響")
		if not is_standard_plus:
			_mode_locked_message("📊 標準（+AI定性分析・要約）")
		elif news_impact and news_impact.get("available"):
			if overall.get("news_adjusted"):
				st.warning("⚠️ 重大かつ信頼度の高いネガティブニュースを考慮し、最終判定を一段階引き下げています。190点満点のスコア自体は変更していません。")
			else:
				st.success("✅ ニュースによる最終判定の引き下げはありません。190点満点のスコア自体は変更していません。")
		elif news:
			st.info("ニュース評価を実行できなかったため、総合判定には影響していません。")
		else:
			st.info("ニュースが取得できないため、総合判定には影響していません。")

		st.divider()
		st.subheader("🔍 ニュースから確認すべきポイント")
		if is_full:
			st.markdown(create_confirmation_points_display(confirmation_points))
		else:
			_mode_locked_message("🔎 フル（すべて）")

	####################################################
	# 📋 仮説・レポートタブ
	####################################################
	with tab_hypo:
		####################################################
		# Sprint6 投資仮説管理 / Sprint8 PDFレポート
		# Sprint12: 投資仮説・PDFレポートはMOAT/ブランド/経営者/RedTeamの
		# 結果を使うため、フルモードでのみ実行する。
		# st.stop()は画面全体（フッターまで）を止めてしまうため使わず、
		# if/elseでこのタブの中だけを出し分ける。
		####################################################
		if not is_full:
			st.subheader("📋 投資仮説管理")
			_mode_locked_message("🔎 フル（すべて）")
			st.divider()
			st.subheader("📄 PDFレポート")
			_mode_locked_message("🔎 フル（すべて）")
		else:
			st.subheader("📋 投資仮説管理")

			if len(hypothesis_manager.get_all()) == 0:
				with st.spinner("🤖 AIが投資仮説を生成中..."):
					defaults = generate_investment_hypothesis(
						data,
						score_result,
						checklist,
						moat,
						brand,
						mgmt,
						red_team,
					)
				for h in defaults:
					hypothesis_manager.add(h)

			#########################################
			# 手動追加
			#########################################
			with st.expander("➕ 新しい投資仮説を追加"):
				title = st.text_input("仮説タイトル", key="new_hypothesis_title")
				rationale = st.text_area("根拠", key="new_hypothesis_rationale")

				if st.button("追加", key="add_hypothesis"):
					if not title.strip():
						st.warning("タイトルを入力してください。")
					else:
						hypothesis_manager.add(
							InvestmentHypothesis(
								id=0,
								title=title,
								rationale=rationale,
								evidence=[],
								verification_items=[],
								source="user",
							)
						)
						st.success("追加しました。")
						st.rerun()

			#########################################
			# 一覧
			#########################################
			status_options = [
				HypothesisStatus.UNVERIFIED,
				HypothesisStatus.IN_PROGRESS,
				HypothesisStatus.VALIDATED,
				HypothesisStatus.REJECTED,
				HypothesisStatus.PENDING,
			]

			for h in hypothesis_manager.get_all():
				with st.container(border=True):
					st.markdown(f"### {h.title}")
					st.write(h.rationale)

					status = st.selectbox(
						"状態",
						status_options,
						index=status_options.index(h.status),
						key=f"status_{h.id}",
					)

					if status != h.status:
						hypothesis_manager.update_status(h.id, status)

					if st.button("🗑 削除", key=f"delete_{h.id}"):
						hypothesis_manager.delete(h.id)
						st.rerun()

			st.divider()

			st.subheader("💾 仮説データ")
			json_data = hypothesis_manager.to_json()
			st.download_button(
				"JSON保存",
				json_data,
				file_name="investment_hypotheses.json",
				mime="application/json",
			)

			uploaded = st.file_uploader("JSON読込", type="json")
			if uploaded:
				# 不具合修正：同じファイルを読み込み→rerun→読み込み…と繰り返さないよう、
				# 処理済みファイルのIDをsession_stateに記録しておき、
				# 同じファイルなら再度読み込まない。
				if st.session_state.get("last_loaded_hypothesis_file_id") != uploaded.file_id:
					try:
						hypothesis_manager.load_from_json(uploaded.read().decode("utf-8"))
						st.session_state.last_loaded_hypothesis_file_id = uploaded.file_id
						st.success("読み込みました。")
						st.rerun()
					except Exception as e:
						st.error(f"JSONの読み込みに失敗しました。\n{e}")

			st.divider()

			####################################################
			# Sprint8 PDFレポート出力
			####################################################
			st.subheader("📄 PDFレポート")
			if st.button("📄 PDFレポートを生成", key="button_generate_pdf"):
				with st.spinner("PDFを生成中..."):
					pdf_bytes = generate_pdf_report(
						data,
						score_result,
						analysis,
						summary,
						checklist,
						moat,
						brand,
						mgmt,
						red_team,
						confirmation_points,
						hypothesis_manager.get_all(),
					roic,
					owner_earnings,
					intrinsic_value,
					capital_allocation,
					share_buyback,
					debt_quality,
					moat_strength,
					backtest,
					overall,
				)
				st.download_button(
					"⬇️ PDFをダウンロード",
					data=pdf_bytes,
					file_name=f"{data.get('company_name', 'report')}_buffett_report.pdf",
					mime="application/pdf",
					key="button_download_pdf",
				)

		####################################################
		# 📓 AI投資日誌（Sprint16）
		# 実体は「投資日誌」。手入力のみで、AI（Gemini）は一切使用しない。
		# 保有銘柄（Portfolio）とは無関係に、自由に記録できる。
		# 投資仮説と同様、長期保存のニーズを想定しJSON保存/読込に対応する。
		####################################################
		st.divider()
		st.subheader("📓 AI投資日誌")
		st.caption("売買の判断とその理由を記録します（AIによる自動コメントは行いません）。")

		with st.form("journal_add_form"):
			j_date = st.date_input("日付", value=datetime.date.today(), key="journal_date_input")
			j_col1, j_col2 = st.columns(2)
			with j_col1:
				j_ticker = st.text_input(
					"ティッカーシンボル（任意）",
					placeholder="例：AAPL、7203",
					key="journal_ticker_input",
				)
			with j_col2:
				j_decision = st.selectbox(
					"売買の判断",
					["買い", "売り", "様子見", "保有継続"],
					key="journal_decision_input",
				)
			j_reason = st.text_area(
				"理由・メモ", placeholder="なぜその判断をしたか記録しておきましょう", key="journal_reason_input"
			)
			j_submitted = st.form_submit_button("📓 日誌に記録する", type="primary")

			if j_submitted:
				if not j_reason.strip():
					st.warning("理由・メモを入力してください。")
				else:
					journal_manager.add(
						JournalEntry(
							id=0,
							date=j_date.isoformat(),
							ticker=j_ticker.strip().upper(),
							decision=j_decision,
							reason=j_reason.strip(),
						)
					)
					st.success("日誌に記録しました。")
					st.rerun()

		st.divider()

		#########################################
		# 保存・読込（JSON）
		# 投資仮説管理と同様、無限ループ防止のため
		# last_loaded_journal_file_id で読込済みファイルを記録する
		#########################################
		j_save_col, j_load_col = st.columns(2)
		with j_save_col:
			st.download_button(
				"💾 日誌をJSON保存",
				data=journal_manager.to_json(),
				file_name="investment_journal.json",
				mime="application/json",
				key="button_download_journal",
			)
		with j_load_col:
			journal_uploaded_file = st.file_uploader(
				"📂 日誌をJSON読込", type=["json"], key="journal_json_uploader"
			)
			if journal_uploaded_file is not None:
				if st.session_state.last_loaded_journal_file_id != journal_uploaded_file.file_id:
					try:
						journal_manager.load_from_json(
							journal_uploaded_file.read().decode("utf-8")
						)
						st.session_state.last_loaded_journal_file_id = journal_uploaded_file.file_id
						st.success("日誌を読み込みました。")
						st.rerun()
					except Exception as e:
						st.error(f"読込に失敗しました：{e}")

		st.divider()

		#########################################
		# 日誌一覧（日付が新しい順）
		#########################################
		journal_entries = journal_manager.get_all()

		if not journal_entries:
			st.info("まだ日誌が記録されていません。上のフォームから記録してください。")
		else:
			st.subheader("📖 日誌一覧")
			for entry in journal_entries:
				with st.container(border=True):
					j_col_a, j_col_b, j_col_c = st.columns([1, 1, 2])
					j_col_a.write(f"📅 {entry.date}")
					j_col_b.write(f"{entry.ticker}" if entry.ticker else "（銘柄未指定）")
					j_col_c.write(f"**{entry.decision}**")
					st.write(entry.reason)
					if st.button("🗑 削除", key=f"journal_delete_{entry.id}"):
						journal_manager.delete(entry.id)
						st.rerun()

	####################################################
	# 💼 Portfolioタブ（Sprint13）
	# 現在分析中の銘柄とは独立に、保有銘柄を複数登録・管理する。
	# 各銘柄の現在株価・Buffett Scoreは、Sprint10のキャッシュ関数
	# cached_get_stock_data と、既存のscoring_engine.calculate_buffett_score を
	# そのまま再利用して計算する（新しいGemini呼び出しは追加していない）。
	# データはセッション中のみ保持し、JSON保存/読込は行わない（Sprint14以降で検討）。
	####################################################
	with tab_portfolio:
		st.subheader("➕ 保有銘柄を追加")
		with st.form("portfolio_add_form"):
			p_ticker = st.text_input(
				"ティッカーシンボル",
				placeholder="例：AAPL、7203",
				key="portfolio_ticker_input",
			)
			p_col1, p_col2 = st.columns(2)
			with p_col1:
				p_shares = st.number_input(
					"保有株数", min_value=0.0, step=1.0, key="portfolio_shares_input"
				)
			with p_col2:
				p_cost = st.number_input(
					"取得単価（1株あたり）", min_value=0.0, step=0.01, key="portfolio_cost_input"
				)
			p_submitted = st.form_submit_button("追加", type="primary")

			if p_submitted:
				if not p_ticker.strip():
					st.warning("ティッカーシンボルを入力してください。")
				elif p_shares <= 0:
					st.warning("保有株数は1以上を入力してください。")
				else:
					portfolio_manager.add(
						PortfolioHolding(
							id=0,
							ticker=p_ticker.strip().upper(),
							shares=p_shares,
							cost_basis=p_cost,
						)
					)
					st.success(f"{p_ticker.strip().upper()} を追加しました。")
					st.rerun()

		st.divider()

		portfolio_holdings = portfolio_manager.get_all()

		if not portfolio_holdings:
			st.info("まだ保有銘柄が登録されていません。上のフォームから追加してください。")
		else:
			#########################################
			# 各銘柄の現在データ取得・スコア計算
			# （ルールベースのみ、Gemini呼び出しなし。
			# 　cached_get_stock_dataによりSprint10のキャッシュがそのまま効く）
			#
			# Sprint29: rows自体を_build_rows_cached()でsession_stateにキャッシュし、
			# 保有銘柄構成が変わっていない・TTL内であれば、無関係な操作による
			# 再実行のたびにこのループが走らないようにする（データ・スコア計算
			# ロジック自体は変更なし＝出力値は変更前と同一）。
			#########################################
			def _build_portfolio_row(h):
				p_result = cached_get_stock_data(h.ticker)
				if not p_result["success"]:
					return {"holding": h, "data": None, "score_result": None, "error": p_result["error"]}
				p_data = p_result["data"]
				p_score = calculate_buffett_score(p_data)
				return {"holding": h, "data": p_data, "score_result": p_score, "error": None}

			with st.spinner("保有銘柄のデータを取得中..."):
				portfolio_rows = _build_rows_cached(
					"portfolio_rows_cache",
					portfolio_holdings,
					lambda h: h.ticker,
					_build_portfolio_row,
				)

			#########################################
			# ポートフォリオ合計
			#########################################
			st.subheader("💼 ポートフォリオ合計")
			total_cost = sum(
				r["holding"].shares * r["holding"].cost_basis for r in portfolio_rows
			)
			total_value = sum(
				r["holding"].shares * r["data"]["current_price"]
				for r in portfolio_rows
				if r["data"]
			)
			total_pl = total_value - total_cost
			total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0

			s1, s2, s3 = st.columns(3)
			s1.metric("取得金額合計", f"{total_cost:,.0f}")
			s2.metric("評価額合計", f"{total_value:,.0f}")
			s3.metric("評価損益", f"{total_pl:+,.0f}", f"{total_pl_pct:+.1f}%")
			st.caption(
				"※ 通貨は銘柄ごとに異なる場合があります（日本株＝円、米国株＝ドル等）。"
				"複数通貨が混在する場合、合計は簡易計算のため参考値としてご覧ください。"
			)

			st.divider()

			#########################################
			# 保有銘柄一覧
			#########################################
			st.subheader("📋 保有銘柄一覧")
			for row in portfolio_rows:
				h = row["holding"]
				with st.container(border=True):
					if row["error"]:
						st.error(f"**{h.ticker}**：データを取得できませんでした（{row['error']}）")
						if st.button("🗑 削除", key=f"portfolio_delete_{h.id}"):
							portfolio_manager.delete(h.id)
							st.rerun()
						continue

					p_data = row["data"]
					p_score = row["score_result"]
					currency_p = "¥" if p_data.get("country") == "Japan" else "$"
					current_price = p_data.get("current_price", 0)
					current_value = h.shares * current_price
					cost_value = h.shares * h.cost_basis
					pl = current_value - cost_value
					pl_pct = (pl / cost_value * 100) if cost_value > 0 else 0

					col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
					col_a.markdown(f"**{p_data['company_name']}**（{h.ticker}）")
					col_b.write(f"保有: {h.shares:,.0f}株")
					col_c.write(f"取得単価: {currency_p}{h.cost_basis:,.2f}")
					col_d.write(f"現在値: {currency_p}{current_price:,.2f}")

					col_e, col_f, col_g = st.columns([2, 2, 1])
					pl_icon = "🟢" if pl >= 0 else "🔴"
					col_e.write(f"{pl_icon} 評価損益: {currency_p}{pl:+,.0f}（{pl_pct:+.1f}%）")
					col_f.write(
						f"Buffett Score: **{p_score['total_score']}/{p_score['max_score']}点**"
						f"（{p_score['verdict']}）"
					)
					if col_g.button("🗑 削除", key=f"portfolio_delete_{h.id}"):
						portfolio_manager.delete(h.id)
						st.rerun()

			st.divider()

			####################################################
			# 🎯 Portfolio Risk（保有ポートフォリオのリスク分散評価）分析（Sprint27）
			# 上で計算済みのportfolio_rows（cached_get_stock_data /
			# calculate_buffett_scoreの結果）をそのまま再利用する。新たな
			# データ取得・スコア再計算は行わない（ルール14）。
			# 単一銘柄向けの総合判定（190点満点、overall_eval）とは評価単位が異なる
			# （複数銘柄からなるポートフォリオ全体が対象）ため、既存の
			# analysis_bundle / overall_eval（BUY/WATCH/PASS判定）には
			# 組み込まない、独立した分析として表示する。
			# Gemini呼び出しはボタン押下時のみに限定し、タブの再描画のたびに
			# 自動実行しない（既存のフルモード等と同様、コストを抑えるため）。
			####################################################
			st.subheader("🎯 Portfolio Risk（保有ポートフォリオのリスク分散評価）")
			st.caption(
				"保有銘柄全体として、セクター・銘柄・地域のリスクがどれだけ分散されているかを評価します。"
				"単一銘柄のBuffett Scoreとは別軸の評価であり、総合判定（BUY/WATCH/PASS）には含まれません。"
			)

			# 保有銘柄の構成（ティッカー集合）が変わったら、古いAI考察は破棄する
			# （銘柄追加・削除後に、以前の構成に基づく考察が誤って表示されるのを防ぐ）
			portfolio_signature = tuple(sorted(h.ticker for h in portfolio_holdings))
			if st.session_state.get("portfolio_risk_signature") != portfolio_signature:
				st.session_state.portfolio_risk_ai = None
				st.session_state.portfolio_risk_signature = portfolio_signature
			if "portfolio_risk_ai" not in st.session_state:
				st.session_state.portfolio_risk_ai = None

			portfolio_risk_result = analyze_portfolio_risk(portfolio_rows, generate_ai_narrative=False)

			if st.session_state.portfolio_risk_ai:
				portfolio_risk_result.update(st.session_state.portfolio_risk_ai)

			pr_engine_raw = portfolio_risk_result.get("raw", {}).get("raw", {})
			if not pr_engine_raw.get("holding_count"):
				st.info(portfolio_risk_result.get("summary", "分析可能な保有銘柄がありません。"))
			else:
				pr_col1, pr_col2, pr_col3 = st.columns(3)
				pr_col1.metric(
					"Portfolio Riskスコア",
					f"{portfolio_risk_result['score']} / {portfolio_risk_result['max_score']}点",
				)
				pr_weighted_avg = portfolio_risk_result.get("raw", {}).get("weighted_avg_buffett_score")
				pr_weighted_max = portfolio_risk_result.get("raw", {}).get("weighted_avg_buffett_max_score")
				if pr_weighted_avg is not None and pr_weighted_max:
					pr_col2.metric(
						"（参考）加重平均Buffett Score",
						f"{pr_weighted_avg:.1f} / {pr_weighted_max}点",
					)
				pr_col3.metric("保有銘柄数（分析対象）", f"{pr_engine_raw.get('holding_count', 0)}銘柄")

				st.write(portfolio_risk_result.get("summary", ""))

				for w in portfolio_risk_result.get("warnings", []):
					st.warning(w)

				with st.expander("📋 詳細を見る（セクター・地域・銘柄別構成比）", expanded=False):
					st.markdown(create_portfolio_risk_display(portfolio_risk_result))

				pr_ai_col1, pr_ai_col2 = st.columns(2)
				with pr_ai_col1:
					if st.button("🤖 AIによる考察を追加する", key="portfolio_risk_ai_button"):
						with st.spinner("Geminiが考察を生成中..."):
							ai_added_result = analyze_portfolio_risk(
								portfolio_rows, generate_ai_narrative=True
							)
						st.session_state.portfolio_risk_ai = {
							k: ai_added_result.get(k)
							for k in ("buffet_view", "competitive_advantage", "capital_efficiency",
									  "improvement_area", "ai_conclusion")
							if ai_added_result.get(k)
						}
						st.rerun()

				if portfolio_risk_result.get("buffet_view"):
					st.markdown("#### 🤖 AI考察（バフェット視点）")
					st.write(portfolio_risk_result["buffet_view"])
					if portfolio_risk_result.get("improvement_area"):
						st.caption(f"改善点：{portfolio_risk_result['improvement_area']}")

				with pr_ai_col2:
					####################################################
					# Sprint30: Performance改善（続き）
					# st.download_buttonはdata=を毎回の再実行時に同期的に
					# 用意する必要があるため、単一銘柄向けPDF（st.buttonで
					# 生成タイミングを制御できる）と異なり、これまでは
					# generate_portfolio_pdf_report()がアプリ内のどこかで
					# 操作されるたびに（Portfolio Riskタブを見ていないときも
					# 含めて）毎回ゼロから再生成されていた（PDF自体は画像を
					# 含まないため1回あたりは軽いが、無駄な再計算ではある）。
					# portfolio_risk_resultの内容は「保有銘柄構成
					# （portfolio_signature）」と「AI考察の有無・内容
					# （portfolio_risk_ai）」が変わらない限り変化しないため、
					# 両方をsignatureとして_cache_by_signature()でPDFバイト列
					# 自体をキャッシュし、変化が無ければ再生成をスキップする。
					####################################################
					_ai_state = st.session_state.get("portfolio_risk_ai")
					_pdf_signature = (
						portfolio_signature,
						tuple(sorted(_ai_state.items())) if _ai_state else None,
					)
					pr_pdf_bytes = _cache_by_signature(
						"portfolio_risk_pdf_cache",
						_pdf_signature,
						lambda: generate_portfolio_pdf_report(portfolio_risk_result),
					)
					st.download_button(
						label="📄 Portfolio Risk PDFをダウンロード",
						data=pr_pdf_bytes,
						file_name="portfolio_risk_report.pdf",
						mime="application/pdf",
						key="portfolio_risk_pdf_download",
					)

		####################################################
		# 👀 ウォッチリスト（Sprint14）
		# 保有銘柄（portfolio_holdings）とは別の一覧として管理する。
		# 「気になっているが、まだ保有していない銘柄」を登録し、
		# 目標株価（この値段まで下がったら買いたい、等）に到達したかを表示する。
		# Buffett Scoreは保有銘柄一覧と同じく、既存のcached_get_stock_data /
		# calculate_buffett_scoreを再利用して計算する（Gemini呼び出しは追加していない）。
		####################################################
		st.divider()
		st.subheader("👀 ウォッチリストに追加")
		with st.form("watchlist_add_form"):
			w_ticker = st.text_input(
				"ティッカーシンボル",
				placeholder="例：AAPL、7203",
				key="watchlist_ticker_input",
			)
			w_col1, w_col2 = st.columns(2)
			with w_col1:
				w_target_price = st.number_input(
					"目標株価（任意。0のままなら未設定）",
					min_value=0.0,
					step=0.01,
					key="watchlist_target_price_input",
				)
			with w_col2:
				w_memo = st.text_input(
					"メモ（任意）", key="watchlist_memo_input"
				)
			w_submitted = st.form_submit_button("追加", type="primary")

			if w_submitted:
				if not w_ticker.strip():
					st.warning("ティッカーシンボルを入力してください。")
				else:
					watchlist_manager.add(
						WatchListItem(
							id=0,
							ticker=w_ticker.strip().upper(),
							target_price=w_target_price if w_target_price > 0 else None,
							memo=w_memo,
						)
					)
					st.success(f"{w_ticker.strip().upper()} をウォッチリストに追加しました。")
					st.rerun()

		st.divider()

		watchlist_items = watchlist_manager.get_all()

		if not watchlist_items:
			st.info("まだウォッチリストに銘柄が登録されていません。上のフォームから追加してください。")
		else:
			st.subheader("👀 ウォッチリスト一覧")

			####################################################
			# Sprint29: rows自体を_build_rows_cached()でsession_stateにキャッシュし、
			# ウォッチリスト構成が変わっていない・TTL内であれば、無関係な操作による
			# 再実行のたびにこのループが走らないようにする（データ・スコア計算
			# ロジック自体は変更なし＝出力値は変更前と同一。Portfolio側と同じ
			# ヘルパーを再利用＝重複実装禁止・ルール14）。
			####################################################
			def _build_watchlist_row(w):
				w_result = cached_get_stock_data(w.ticker)
				if not w_result["success"]:
					return {"item": w, "data": None, "score_result": None, "error": w_result["error"]}
				w_data = w_result["data"]
				w_score = calculate_buffett_score(w_data)
				return {"item": w, "data": w_data, "score_result": w_score, "error": None}

			with st.spinner("ウォッチリストのデータを取得中..."):
				watchlist_rows = _build_rows_cached(
					"watchlist_rows_cache",
					watchlist_items,
					lambda w: w.ticker,
					_build_watchlist_row,
				)

			for row in watchlist_rows:
				w = row["item"]
				with st.container(border=True):
					if row["error"]:
						st.error(f"**{w.ticker}**：データを取得できませんでした（{row['error']}）")
						if st.button("🗑 削除", key=f"watchlist_delete_{w.id}"):
							watchlist_manager.delete(w.id)
							st.rerun()
						continue

					w_data = row["data"]
					w_score = row["score_result"]
					currency_w = "¥" if w_data.get("country") == "Japan" else "$"
					current_price_w = w_data.get("current_price", 0)

					col_a, col_b, col_c = st.columns([2, 1, 1])
					col_a.markdown(f"**{w_data['company_name']}**（{w.ticker}）")
					col_b.write(f"現在値: {currency_w}{current_price_w:,.2f}")
					col_c.write(
						f"Buffett Score: **{w_score['total_score']}/{w_score['max_score']}点**"
						f"（{w_score['verdict']}）"
					)

					if w.memo:
						st.caption(f"📝 {w.memo}")

					col_d, col_e = st.columns([3, 1])
					if w.target_price:
						diff_pct = (
							(current_price_w - w.target_price) / w.target_price * 100
							if w.target_price > 0
							else 0
						)
						if current_price_w <= w.target_price:
							col_d.success(
								f"🎯 目標株価 {currency_w}{w.target_price:,.2f} に到達しました！"
								f"（現在値との差: {diff_pct:+.1f}%）"
							)
						else:
							col_d.info(
								f"目標株価 {currency_w}{w.target_price:,.2f} まで、"
								f"あと {diff_pct:+.1f}%"
							)
					else:
						col_d.caption("目標株価は未設定です。")

					if col_e.button("🗑 削除", key=f"watchlist_delete_{w.id}"):
						watchlist_manager.delete(w.id)
						st.rerun()

			####################################################
			# 📊 Watchlist Insights（ウォッチリスト横断の集計・ランキング表示）（Sprint28）
			# 上で計算済みのwatchlist_rows（cached_get_stock_data /
			# calculate_buffett_scoreの結果）をそのまま再利用する。新たな
			# データ取得・スコア再計算は行わない（ルール14）。
			# Portfolio Risk（Sprint27）と同じく複数銘柄が評価単位のため
			# analysis_bundle / overall_eval（BUY/WATCH/PASS判定）には
			# 組み込まない独立表示だが、Portfolio Riskとは異なり得点化は
			# 行わない（集計・ランキング表示のみ。設計判断はきたと確認済み。
			# 詳細はdocs/AI_HANDOVER.mdのSprint28セクションを参照）。
			# AI考察（Gemini）も追加しない（数値が既に自己説明的であり、
			# 得点化しない集計機能にまでAI呼び出しを増やす必要性が低いため）。
			####################################################
			st.divider()
			st.subheader("📊 Watchlist Insights（ウォッチリスト横断分析）")
			st.caption(
				"ウォッチリスト登録銘柄全体を、目標株価接近度・Buffett Scoreの高さで"
				"ランキング表示します。得点化は行わず、総合判定（BUY/WATCH/PASS）にも含まれません。"
			)

			# 保有銘柄（Portfolio）が未登録の場合、portfolio_rowsは定義されない
			# （portfolio_holdings truthyのときのみ定義される）ため、その場合は
			# 空リストとして扱う（セクター重複の参考表示なしで動作する）。
			portfolio_rows_for_insights = portfolio_rows if portfolio_holdings else []

			watchlist_insights_result = build_watchlist_insights(
				watchlist_rows, portfolio_rows_for_insights
			)

			if not watchlist_insights_result.get("success"):
				st.info(watchlist_insights_result.get("summary", "集計できるデータがありません。"))
			else:
				wi_col1, wi_col2, wi_col3 = st.columns(3)
				wi_col1.metric(
					"ウォッチリスト銘柄数",
					f"{watchlist_insights_result['watchlist_count']}銘柄",
				)
				wi_target_ranking = watchlist_insights_result.get("target_price_ranking", [])
				wi_reached = sum(1 for t in wi_target_ranking if t.get("reached"))
				wi_col2.metric(
					"目標株価 到達済み",
					f"{wi_reached} / {len(wi_target_ranking)}件"
					if wi_target_ranking
					else "未設定",
				)
				wi_score_ranking = watchlist_insights_result.get("score_ranking", [])
				wi_col3.metric(
					"Buffett Score 集計対象",
					f"{len(wi_score_ranking)}銘柄",
				)

				for w_warn in watchlist_insights_result.get("warnings", []):
					st.warning(w_warn)

				with st.expander("📋 詳細を見る（ランキング・セクター件数）", expanded=False):
					st.markdown(create_watchlist_insights_display(watchlist_insights_result))

	####################################################
	# ⚖️ 比較分析タブ（Sprint15）
	# 複数銘柄のBuffett Scoreを並べて比較する。
	# 現在分析中の1銘柄の状態（current_data等）とは独立している。
	# 比較対象は「登録済み銘柄（Portfolio／ウォッチリスト）から選ぶ」
	# ＋「自由入力」の両方に対応する。
	# 比較する指標はBuffett Scoreのみ（ルールベース、Gemini呼び出しは追加していない）。
	####################################################
	with tab_compare:
		st.subheader("⚖️ 比較する銘柄を選択")

		registered_tickers = sorted(set(
			[h.ticker for h in portfolio_manager.get_all()]
			+ [w.ticker for w in watchlist_manager.get_all()]
		))

		compare_col1, compare_col2 = st.columns(2)
		with compare_col1:
			selected_from_list = st.multiselect(
				"登録済み銘柄（Portfolio／ウォッチリスト）から選ぶ",
				options=registered_tickers,
				key="compare_multiselect",
			)
		with compare_col2:
			free_input = st.text_input(
				"自由入力（カンマ区切り。例：AAPL, MSFT, 7203）",
				key="compare_free_input",
			)

		compare_button = st.button("⚖️ 比較する", type="primary", key="button_compare")

		if compare_button:
			free_tickers = [t.strip().upper() for t in free_input.split(",") if t.strip()]
			all_tickers = []
			for t in selected_from_list + free_tickers:
				if t not in all_tickers:
					all_tickers.append(t)

			if len(all_tickers) < 2:
				st.warning("比較には2銘柄以上を選択・入力してください。")
				st.session_state.compare_bundle = None
			else:
				compare_results = []
				with st.spinner("比較データを取得中..."):
					for t in all_tickers:
						c_result = cached_get_stock_data(t)
						if not c_result["success"]:
							compare_results.append(
								{"ticker": t, "data": None, "score_result": None, "error": c_result["error"]}
							)
							continue
						c_data = c_result["data"]
						c_score = calculate_buffett_score(c_data)
						compare_results.append(
							{"ticker": t, "data": c_data, "score_result": c_score, "error": None}
						)
				st.session_state.compare_bundle = compare_results

		st.divider()

		compare_bundle = st.session_state.compare_bundle

		if not compare_bundle:
			st.info("比較したい銘柄を選択・入力し、「⚖️ 比較する」を押してください。")
		else:
			failed = [r for r in compare_bundle if r["error"]]
			ok_results = [r for r in compare_bundle if not r["error"]]

			if failed:
				failed_tickers = "、".join(r["ticker"] for r in failed)
				st.warning(f"以下の銘柄はデータを取得できませんでした：{failed_tickers}")

			if len(ok_results) < 2:
				st.info("比較できる銘柄が2件未満です。ティッカーシンボルを確認してください。")
			else:
				#########################################
				# スコア比較サマリー
				#########################################
				st.subheader("📋 スコア比較サマリー")
				for r in ok_results:
					c_data = r["data"]
					c_score = r["score_result"]
					col_a, col_b, col_c = st.columns([2, 1, 2])
					col_a.markdown(f"**{c_data['company_name']}**（{r['ticker']}）")
					col_b.write(f"{c_score['total_score']} / {c_score['max_score']}点")
					col_c.write(c_score["verdict"])

				st.divider()

				#########################################
				# 総合スコア比較（棒グラフ）
				#########################################
				st.subheader("📊 総合スコア比較")
				bar_fig = go.Figure()
				bar_fig.add_trace(go.Bar(
					x=[r["data"]["company_name"] for r in ok_results],
					y=[r["score_result"]["total_score"] for r in ok_results],
					text=[r["score_result"]["total_score"] for r in ok_results],
					textposition="auto",
				))
				bar_fig.update_layout(yaxis_range=[0, ok_results[0]["score_result"]["max_score"]])
				st.plotly_chart(bar_fig, use_container_width=True)

				#########################################
				# 指標別スコア比較（レーダーチャート、複数銘柄を重ねて表示）
				# 項目ごとに配点(max_score)が異なるため、達成率(%)に正規化してから
				# 比較する（例：ROEは20点満点、ROAは5点満点、そのままでは比較できない）。
				#########################################
				st.subheader("🕸️ 指標別スコア比較（レーダーチャート）")
				radar_fig = go.Figure()
				for r in ok_results:
					details = r["score_result"]["details"]
					categories = [d["item"] for d in details]
					values = [
						(d["score"] / d["max_score"] * 100) if d["max_score"] else 0
						for d in details
					]
					radar_fig.add_trace(go.Scatterpolar(
						r=values + [values[0]],
						theta=categories + [categories[0]],
						fill="toself",
						name=f"{r['data']['company_name']}（{r['ticker']}）",
					))
				radar_fig.update_layout(
					polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
					showlegend=True,
				)
				st.plotly_chart(radar_fig, use_container_width=True)
				st.caption(
					"※ 各項目は満点に対する達成率(%)で正規化して表示しています"
					"（項目ごとに配点が異なるため）。"
				)

	####################################################
	# 📑 決算資料解析タブ（Sprint17）
	# 決算説明資料などのPDFをアップロードすると、
	# ①pdfplumberでテキストを抽出（ルールベース） →
	# ②Geminiで要約・ポイント抽出（ai_analysis.py の
	#   generate_earnings_material_analysisを利用）
	# を行う。既存の分析モード（クイック／標準／フル）とは独立した、
	# このタブ専用のボタンでのみGemini呼び出しを行う。
	####################################################
	with tab_earnings:
		st.subheader("📑 決算資料を解析する")
		st.caption(
			"決算説明資料などのPDFをアップロードすると、Geminiが要約・ポイント抽出を行います。"
			"（このタブのボタンを押した時だけ解析します）"
		)

		earnings_pdf = st.file_uploader(
			"PDFファイルをアップロード", type=["pdf"], key="earnings_pdf_uploader"
		)

		earnings_analyze_button = st.button(
			"📑 資料を解析する", type="primary", key="button_earnings_analyze"
		)

		if earnings_analyze_button:
			if earnings_pdf is None:
				st.warning("PDFファイルをアップロードしてください。")
			else:
				pdf_text = ""
				with st.spinner("PDFからテキストを抽出しています..."):
					try:
						pdf_text = extract_text_from_pdf(earnings_pdf.read())
					except Exception as e:
						st.error(f"PDFの読み込みに失敗しました：{e}")

				if not pdf_text.strip():
					st.warning(
						"PDFからテキストを抽出できませんでした"
						"（画像だけのPDFの可能性があります）。"
					)
				else:
					with st.spinner("Geminiで分析しています..."):
						analysis_text = generate_earnings_material_analysis(
							pdf_text, company_name=data.get("company_name")
						)
					st.session_state.earnings_material_result = {
						"file_name": earnings_pdf.name,
						"pdf_text": pdf_text,
						"analysis": analysis_text,
					}
					st.rerun()

		st.divider()

		earnings_result = st.session_state.earnings_material_result

		if not earnings_result:
			st.info("PDFをアップロードして「📑 資料を解析する」を押してください。")
		else:
			st.subheader(f"📄 解析結果：{earnings_result['file_name']}")
			st.markdown(earnings_result["analysis"])

			with st.expander("抽出したテキストを確認する（元データ）"):
				preview_text = earnings_result["pdf_text"]
				st.text(preview_text[:5000])
				if len(preview_text) > 5000:
					st.caption("※ 長いため、冒頭5000文字のみ表示しています。")

elif analyze_button and not ticker_input:	
	st.warning("ティッカーシンボルを入力してください。")

st.divider()
st.caption("⚠️ このアプリは投資の参考情報を提供するものです。実際の投資判断はご自身の責任で行ってください。")
st.caption("データソース: yfinance / Google News RSS")
