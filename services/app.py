import os
import sys

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, ".env"))

import streamlit as st

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
)
from news_fetcher import get_latest_news
from pdf_report import generate_pdf_report
from dcf_analysis import calculate_dcf

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

	**75点以上 → 投資推奨**
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
	# Sprint12: 選択された分析モードに応じてAI呼び出しを行う
	# クイックモードはここを一切通らないため、Gemini呼び出しはゼロ。
	####################################################
	bundle = {
		"mode": analysis_mode,
		"news": None,
		"analysis": None,
		"summary": None,
		"confirmation_points": None,
		"checklist": None,
		"moat": None,
		"brand": None,
		"mgmt": None,
		"red_team": None,
	}

	if not analysis_mode.startswith("⚡"):
		with st.spinner("🤖 AIが分析中...（初回のみ少し時間がかかります）"):
			news = cached_get_latest_news(data["company_name"])
			bundle["news"] = news
			bundle["analysis"] = generate_ai_analysis(data, score_result)
			bundle["summary"] = generate_news_summary(news) if news else ""
			bundle["checklist"] = generate_buffett_checklist(data, score_result)

			if analysis_mode.startswith("🔎"):
				bundle["confirmation_points"] = generate_news_confirmation_points(
					data, news, score_result
				)
				bundle["moat"] = generate_moat_analysis(data, score_result)
				bundle["brand"] = generate_brand_analysis(data, score_result)
				bundle["mgmt"] = generate_management_analysis(data, score_result)
				bundle["red_team"] = generate_red_team_analysis(
					data,
					score_result,
					bundle["checklist"],
					bundle["moat"],
					bundle["brand"],
					bundle["mgmt"],
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
	checklist = bundle.get("checklist")
	moat = bundle.get("moat")
	brand = bundle.get("brand")
	mgmt = bundle.get("mgmt")
	red_team = bundle.get("red_team")

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

	tab_summary, tab_quant, tab_qual, tab_news, tab_hypo, tab_portfolio = st.tabs(
		["📊 サマリー", "📈 定量分析", "🧠 定性分析", "📰 ニュース", "📋 仮説・レポート", "💼 Portfolio"]
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
		for d in score_result["details"]:
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
					)
				st.download_button(
					"⬇️ PDFをダウンロード",
					data=pdf_bytes,
					file_name=f"{data.get('company_name', 'report')}_buffett_report.pdf",
					mime="application/pdf",
					key="button_download_pdf",
				)

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
			#########################################
			portfolio_rows = []
			with st.spinner("保有銘柄のデータを取得中..."):
				for h in portfolio_holdings:
					p_result = cached_get_stock_data(h.ticker)
					if not p_result["success"]:
						portfolio_rows.append(
							{"holding": h, "data": None, "score_result": None, "error": p_result["error"]}
						)
						continue
					p_data = p_result["data"]
					p_score = calculate_buffett_score(p_data)
					portfolio_rows.append(
						{"holding": h, "data": p_data, "score_result": p_score, "error": None}
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

			with st.spinner("ウォッチリストのデータを取得中..."):
				watchlist_rows = []
				for w in watchlist_items:
					w_result = cached_get_stock_data(w.ticker)
					if not w_result["success"]:
						watchlist_rows.append(
							{"item": w, "data": None, "score_result": None, "error": w_result["error"]}
						)
						continue
					w_data = w_result["data"]
					w_score = calculate_buffett_score(w_data)
					watchlist_rows.append(
						{"item": w, "data": w_data, "score_result": w_score, "error": None}
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

elif analyze_button and not ticker_input:	
	st.warning("ティッカーシンボルを入力してください。")

st.divider()
st.caption("⚠️ このアプリは投資の参考情報を提供するものです。実際の投資判断はご自身の責任で行ってください。")
st.caption("データソース: yfinance / Google News RSS")