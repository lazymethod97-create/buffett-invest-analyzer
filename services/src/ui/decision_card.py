"""decision_card: 判定内訳の描画 (Sprint18)"""
import streamlit as st


def render_decision_card(overall: dict) -> None:
    """BUY/WATCH/PASS の根拠（項目別スコア）を表示する。"""
    detail = overall.get("detail", {})
    labels = [
        ("buffett", "Buffett Score"),
        ("dcf", "DCF（安全余裕）"),
        ("moat", "MOAT"),
        ("brand", "ブランド"),
        ("management", "経営者"),
        ("redteam", "Red Team"),
    ]
    st.markdown("#### 判定内訳")
    for key, label in labels:
        val = detail.get(key, 0)
        st.progress(min(val / 100.0, 1.0), text=f"{label}：{val}点")