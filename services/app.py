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


# 再実行のたびに初期化されないよう、セッション状態に保持する
if "hypothesis_manager" not in st.session_state:
	st.session_state.hypothesis_manager = HypothesisManager()
hypothesis_manager = st.session_state.hypothesis_manager

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

	with st.spinner("🤖 AIが分析中...（初回のみ少し時間がかかります）"):
		news = cached_get_latest_news(data["company_name"])
		analysis = generate_ai_analysis(data, score_result)
		summary = generate_news_summary(news) if news else ""
		confirmation_points = generate_news_confirmation_points(data, news, score_result)
		checklist = generate_buffett_checklist(data, score_result)
		moat = generate_moat_analysis(data, score_result)
		brand = generate_brand_analysis(data, score_result)
		mgmt = generate_management_analysis(data, score_result)
		red_team = generate_red_team_analysis(data, score_result, checklist, moat, brand, mgmt)

	st.session_state.analysis_bundle = {
		"news": news,
		"analysis": analysis,
		"summary": summary,
		"confirmation_points": confirmation_points,
		"checklist": checklist,
		"moat": moat,
		"brand": brand,
		"mgmt": mgmt,
		"red_team": red_team,
	}

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

	news = bundle["news"]
	analysis = bundle["analysis"]
	summary = bundle["summary"]
	confirmation_points = bundle["confirmation_points"]
	checklist = bundle["checklist"]
	moat = bundle["moat"]
	brand = bundle["brand"]
	mgmt = bundle["mgmt"]
	red_team = bundle["red_team"]

	currency = "¥" if data.get("country") == "Japan" else "$"

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

	tab_summary, tab_quant, tab_qual, tab_news, tab_hypo = st.tabs(
		["📊 サマリー", "📈 定量分析", "🧠 定性分析", "📰 ニュース", "📋 仮説・レポート"]
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

		st.divider()
		st.markdown("### 🔴 Red Teamの結論")
		st.warning(red_team.get("conclusion", "結論なし"))

	####################################################
	# 🧠 定性分析タブ
	####################################################
	with tab_qual:
		st.subheader("🤖 AI定性分析")
		st.info(analysis)

		st.divider()
		st.subheader("📋 Buffett Investment Checklist")
		st.markdown(create_checklist_display(checklist))

		st.divider()
		st.subheader("🏰 MOAT評価（経済的堀）")
		st.markdown(create_moat_display(moat))

		st.divider()
		st.subheader("🏷️ ブランド力評価")
		st.markdown(create_brand_display(brand))

		st.divider()
		st.subheader("👔 経営者評価")
		st.markdown(create_management_display(mgmt))

		st.divider()
		st.subheader("🔴 Red Team AI（反対意見）")
		st.markdown(create_red_team_display(red_team))

	####################################################
	# 📰 ニュースタブ
	####################################################
	with tab_news:
		st.subheader("📰 最新ニュース")
		if news:
			for article in news:
				st.markdown(f"**• {article['title']}**")
				if article["publisher"]:
					st.caption(article["publisher"])
		else:
			st.info("ニュースは取得できませんでした。")

		st.divider()
		st.subheader("📝 AIニュース要約")
		if news:
			st.success(summary)
		else:
			st.info("要約するニュースがありません。")

		st.divider()
		st.subheader("🔍 ニュースから確認すべきポイント")
		st.markdown(create_confirmation_points_display(confirmation_points))

	####################################################
	# 📋 仮説・レポートタブ
	####################################################
	with tab_hypo:
		####################################################
		# Sprint6 投資仮説管理
		####################################################
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

elif analyze_button and not ticker_input:	
	st.warning("ティッカーシンボルを入力してください。")

st.divider()
st.caption("⚠️ このアプリは投資の参考情報を提供するものです。実際の投資判断はご自身の責任で行ってください。")
st.caption("データソース: yfinance / Google News RSS")