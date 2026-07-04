import streamlit as st

from src.data_fetcher import StockDataFetcher
from src.financial_analyzer import FinancialAnalyzer
from src.buffett_score import BuffettScore

st.set_page_config(
    page_title="Buffett Investment Analyzer",
    page_icon="📈",
)

st.title("📈 Buffett Investment Analyzer")

ticker = st.text_input(
    "銘柄コード",
    placeholder="例：AAPL または 7203.T"
)

if st.button("分析開始"):

    if ticker == "":
        st.warning("銘柄コードを入力してください。")

    else:
        fetcher = StockDataFetcher(ticker)
        data = fetcher.fetch()

        analyzer = FinancialAnalyzer()
        score_engine = BuffettScore()

        scores = []

        st.subheader(data["company_name"])

        for metric in ["ROE", "PER", "PBR"]:
            value = data[metric.lower()]

            rating, score = analyzer.evaluate(metric, value)

            scores.append(score)

            st.write(f"### {metric}")
            st.write(f"値 : {value}")
            st.write(f"評価 : {rating}")
            st.write(f"点数 : {score}")

        result = score_engine.calculate(scores)

        st.divider()

        st.subheader("Buffett Score")

        st.metric(
            label="総合点",
            value=f"{result['total']} 点"
        )

        st.write(result["rating"])
        st.success(result["message"])
