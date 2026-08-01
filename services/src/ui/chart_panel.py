"""chart_panel: レーダーチャート等の描画 (Sprint18)"""
import streamlit as st
from report import create_radar_chart


def render_chart_panel(score_result: dict) -> None:
    """Buffett Score レーダーチャートを表示する。"""
    details = score_result.get("details", [])
    if details:
        st.plotly_chart(create_radar_chart(details), use_container_width=True)
    else:
        st.info("スコア詳細がありません。")