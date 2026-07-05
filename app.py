import streamlit as st

from services.market_data import get_company_name

st.set_page_config(
    page_title="Buffett Investment Analyzer",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Buffett Investment Analyzer")

ticker = st.text_input(
    "銘柄コードまたはティッカー",
    placeholder="7203 または AAPL",
)

if st.button("分析開始"):

    if ticker.strip() == "":
        st.warning("銘柄コードを入力してください。")

    else:

        company = get_company_name(ticker)

        st.success("企業情報を取得しました")

        st.write("### 企業名")

        st.write(company)

st.caption("Version 0.3.3")
