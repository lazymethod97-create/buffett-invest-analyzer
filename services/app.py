
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
)
from news_fetcher import get_latest_news

st.set_page_config(page_title="Buffett Investment Analyzer", page_icon="📈", layout="wide")

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
# 分析実行（結果はセッション状態に保存し、以降の再実行でも表示を維持する）
# ------------------------------------------------------------
if analyze_button and ticker_input:
	with st.spinner(f"「{ticker_input}」のデータを取得中..."):
		result = get_stock_data(ticker_input)

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

# ------------------------------------------------------------
# 結果表示（データが保存されている限り表示する）
# ------------------------------------------------------------
if "current_data" in st.session_state and "current_score_result" in st.session_state:
	data = st.session_state.current_data
	score_result = st.session_state.current_score_result

	news = get_latest_news(data["company_name"])
	currency = "¥" if data.get("country") == "Japan" else "$"

	st.subheader(f"🏢 {data['company_name']}")
	c1, c2, c3, c4 = st.columns(4)
	c1.metric("セクター", data.get("sector", "不明"))
	c2.metric("国", data.get("country", "不明"))
	price = data.get("current_price", 0)
	c3.metric("現在株価", f"{currency}{price:,.2f}" if price else "不明")
	cap = data.get("market_cap", 0)
	c4.metric("時価総額", f"{currency}{cap/1_000_000_000:.1f}B" if cap else "不明")

	st.divider()

	score_col, verdict_col = st.columns([1, 1])
	with score_col:
		st.plotly_chart(
			create_score_bar(score_result["total_score"], score_result["max_score"]),
			use_container_width=True,
		)
	with verdict_col:
		st.write("")
		st.write("")
		st.write("")
		st.markdown(f"## {score_result['verdict']}")
		st.markdown(f"**スコア: {score_result['total_score']} / 100点**")
		st.info(score_result["verdict_comment"])

	st.divider()
	st.subheader("📊 指標レーダーチャート")
	st.plotly_chart(create_radar_chart(score_result["details"]), use_container_width=True)

	st.divider()

	st.subheader("🤖 AI定性分析")
	analysis = generate_ai_analysis(data, score_result)
	st.info(analysis)

	st.divider()

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
		summary = generate_news_summary(news)
		st.success(summary)
	else:
		st.info("要約するニュースがありません。")

	st.divider()

	st.subheader("📋 Buffett Investment Checklist")
	checklist = generate_buffett_checklist(data, score_result)
	st.markdown(create_checklist_display(checklist))

	st.divider()

	st.subheader("🏰 MOAT評価（経済的堀）")
	moat = generate_moat_analysis(data, score_result)
	st.markdown(create_moat_display(moat))

	st.divider()

	st.subheader("🏷️ ブランド力評価")
	brand = generate_brand_analysis(data, score_result)
	st.markdown(create_brand_display(brand))

	st.divider()

	st.subheader("👔 経営者評価")
	mgmt = generate_management_analysis(data, score_result)
	st.markdown(create_management_display(mgmt))

	st.divider()

	st.subheader("🔴 Red Team AI（反対意見）")
	red_team = generate_red_team_analysis(data, score_result, checklist, moat, brand, mgmt)
	st.markdown(create_red_team_display(red_team))

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

	####################################################
	# Sprint6 投資仮説管理
	####################################################
	st.subheader("📋 投資仮説管理")

	if len(hypothesis_manager.get_all()) == 0:
		defaults = generate_default_hypotheses(
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
		try:
			hypothesis_manager.load_from_json(uploaded.read().decode("utf-8"))
			st.success("読み込みました。")
			st.rerun()
		except Exception as e:
			st.error(f"JSONの読み込みに失敗しました。\n{e}")

elif analyze_button and not ticker_input:
	st.warning("ティッカーシンボルを入力してください。")

st.divider()
st.caption("⚠️ このアプリは投資の参考情報を提供するものです。実際の投資判断はご自身の責任で行ってください。")
st.caption("データソース: Google RSS")
