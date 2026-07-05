
import streamlit as st

# -----------------------------
# Page Settings
# -----------------------------
st.set_page_config(
	page_title="Buffett Investment Analyzer",
	page_icon="📈",
	layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("📈 Buffett Investment Analyzer")

st.markdown(
	"""
	ウォーレン・バフェットの投資哲学をもとに、
	企業を分析するWebアプリです。
	"""
)

st.divider()

# -----------------------------
# Input
# -----------------------------
ticker = st.text_input(
	"銘柄コードまたはティッカーを入力してください",
	placeholder="例：7203 または AAPL"
)

# -----------------------------
# Analyze Button
# -----------------------------
if st.button("分析開始"):

	if ticker == "":
		st.warning("銘柄コードを入力してください。")

	else:
		st.success(f"{ticker} の分析を開始します。")
		st.info("Version 0.3.1では画面のみ実装しています。")

st.divider()

st.caption("Version 0.3.1")
