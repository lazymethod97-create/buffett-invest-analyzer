"""decision_card: 判定内訳の描画 (Sprint18, Sprint32で14項目に更新)"""
import streamlit as st


def render_decision_card(overall: dict) -> None:
    """BUY/WATCH/PASS の根拠（190点満点・14項目の内訳）を表示する。

    Sprint32: Sprint18時点では6項目・/100正規化のままだったが、
    overall_eval.calculate_overall_grade()のdetailは既にSprint19〜26の
    8項目（roic〜backtest）を含む14項目になっていたため、表示側を
    実際の項目・満点に合わせて更新した（計算ロジック自体は変更なし）。
    """
    detail = overall.get("detail", {})
    # (キー, ラベル, 満点) - overall_eval.calculate_overall_grade()の
    # 内訳（s1〜s14）と満点構成に対応させている。
    labels = [
        ("buffett", "Buffett Score", 40),
        ("dcf", "DCF（安全余裕）", 20),
        ("moat", "MOAT", 15),
        ("brand", "ブランド", 10),
        ("management", "経営者", 10),
        ("redteam", "Red Team", 5),
        ("roic", "ROIC", 15),
        ("owner_earnings", "Owner Earnings", 10),
        ("intrinsic_value", "Intrinsic Value", 15),
        ("capital_allocation", "Capital Allocation", 10),
        ("share_buyback", "Share Buyback", 10),
        ("debt_quality", "Debt Quality", 10),
        ("moat_strength", "Economic Moat強化", 10),
        ("backtest", "Backtest", 10),
    ]
    st.markdown("#### 判定内訳（190点満点）")
    for key, label, max_score in labels:
        val = detail.get(key, 0)
        ratio = (val / max_score) if max_score else 0
        st.progress(min(max(ratio, 0.0), 1.0), text=f"{label}：{val}/{max_score}点")