import streamlit as st
# 正しいパスから関数をインポート
from services.market_data import get_financial_data

st.title("Buffett Invest Analyzer 🚀")

ticker = st.text_input("ティッカーシンボルを入力してください (例: AAPL):", "AAPL")

if st.button("データ取得"):
    try:
        # 関数の呼び出しテスト
        data = get_financial_data(ticker)
        st.success("データのインポートと取得に成功しました！")
        st.write(data)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
