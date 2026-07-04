import streamlit as st

st.set_page_config(
    page_title="Buffett Investment Analyzer",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Buffett Investment Analyzer")

st.write("ウォーレン・バフェットの投資基準で企業を分析します。")

ticker = st.text_input(
    "銘柄コードを入力してください",
    placeholder="例：AAPL または 7203.T"
)

if st.button("分析開始"):
    if ticker:
        st.success(f"{ticker} を分析します。（次回実装）")
    else:
        st.warning("銘柄コードを入力してください。")
