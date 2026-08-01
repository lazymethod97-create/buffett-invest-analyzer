"""summary_card: 総合判定カードの描画 (Sprint18)"""
import streamlit as st


def render_summary_card(overall: dict, score_result: dict) -> None:
    """総合判定（BUY/WATCH/PASS）をカード表示する。"""
    decision = overall.get("decision", "PASS")
    icon = {"BUY": "🟢", "WATCH": "🟡", "PASS": "🔴"}.get(decision, "⚪")
    grade = overall.get("grade", "-")
    score = overall.get("overall_score", 0)
    risk = overall.get("risk", "-")
    confidence = overall.get("confidence", "-")
    action = overall.get("action", "")

    st.markdown(
        f"### {icon} 総合判定：**{decision}**（Grade {grade} / {score}点）\n"
        f"- リスク：{risk}　|　確信度：{confidence}\n"
        f"- {action}"
    )