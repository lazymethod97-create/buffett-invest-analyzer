import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_fetcher import get_stock_data, format_value
from scoring_engine import calculate_buffett_score
from report import create_radar_chart, create_score_bar

st.set_page_config(page_title="Buffett Investment Analyzer", page_icon="📈", layout="wide")

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
    st.write(""); st.write("")
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
        st.plotly_chart(create_score_bar(score_result["total_score"], score_result["max_score"]),
                         use_container_width=True)
    with verdict_col:
        st.write(""); st.write(""); st.write("")
        st.markdown(f"## {score_result['verdict']}")
        st.markdown(f"**スコア: {score_result['total_score']} / 100点**")
        st.info(score_result["verdict_comment"])

    st.divider()
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

elif analyze_button and not ticker_input:
    st.warning("ティッカーシンボルを入力してください。")

st.divider()
st.caption("⚠️ このアプリは投資の参考情報を提供するものです。実際の投資判断はご自身の責任で行ってください。")
st.caption("データソース: Yahoo Finance (yfinance)")
