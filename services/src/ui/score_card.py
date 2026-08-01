"""score_card: Buffett Score 詳細の描画 (Sprint18)"""
import streamlit as st
from report import create_score_bar


def render_score_card(score_result: dict) -> None:
    """Buffett Score ゲージと項目別スコアを表示する。"""
    total = score_result.get("total_score", 0)
    max_score = score_result.get("max_score", 100)
    st.plotly_chart(create_score_bar(total, max_score), use_container_width=True)
    st.markdown(f"**判定：{score_result.get('verdict', '-')}**")
    for d in score_result.get("details", []):
        icon = "✅" if d.get("passed") else "❌"
        st.markdown(
            f"{icon} **{d.get('item', '')}**：{d.get('value', '')} "
            f"（{d.get('score', 0)}/{d.get('max_score', 0)}点）\n\n"
            f"{d.get('comment', '')}"
        )