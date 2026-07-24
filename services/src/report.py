import plotly.graph_objects as go


def create_radar_chart(details: list) -> go.Figure:
    categories = [d["item"].split("（")[0] for d in details]
    scores = [d["score"] for d in details]
    max_scores = [d["max_score"] for d in details]
    normalized = [s / m * 100 if m > 0 else 0 for s, m in zip(scores, max_scores)]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=normalized, theta=categories, fill="toself", name="この銘柄",
        line_color="rgba(0, 120, 200, 0.8)", fillcolor="rgba(0, 120, 200, 0.2)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[100] * len(categories), theta=categories, fill="toself", name="バフェット理想",
        line_color="rgba(200, 50, 50, 0.5)", fillcolor="rgba(200, 50, 50, 0.05)",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True, title="バフェット指標レーダーチャート", height=450,
    )
    return fig


def create_score_bar(total_score: int, max_score: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=total_score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Buffett Score", "font": {"size": 24}},
        gauge={
            "axis": {"range": [0, max_score]},
            "bar": {"color": "royalblue"},
            "steps": [
                {"range": [0, 35], "color": "#ffcccc"},
                {"range": [35, 55], "color": "#ffe0b2"},
                {"range": [55, 75], "color": "#fff9c4"},
                {"range": [75, 100], "color": "#c8e6c9"},
            ],
            "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 75},
        },
    ))
    fig.update_layout(height=300)
    return fig


def create_checklist_display(checklist: list) -> str:
    """
    チェックリストをMarkdown形式で整形する。
    """
    if not checklist:
        return "チェックリストを取得できませんでした。"

    lines = []
    status_map = {
        "pass": "✅",
        "warning": "⚠️",
        "fail": "❌"
    }

    for item in checklist:
        status = item.get("status", "warning")
        icon = status_map.get(status, "⚠️")
        title = item.get("item", "")
        reason = item.get("reason", "")

        lines.append(f"{icon} **{title}**  \n　　→ {reason}")

    return "\n\n".join(lines)


def create_moat_display(moat_result: dict) -> str:
    """
    MOAT評価結果をMarkdown形式で整形する。
    """
    if not moat_result:
        return "MOAT評価を取得できませんでした。"

    rating = moat_result.get("rating", "none")
    stars = moat_result.get("stars", 0)
    summary = moat_result.get("summary", "")
    quantitative = moat_result.get("quantitative", {})
    qualitative = moat_result.get("qualitative", [])

    # ラベル・絵文字変換
    rating_map = {
        "wide": ("🏰 広いMOAT（Wide Moat）", "🟢"),
        "narrow": ("🏯 狭いMOAT（Narrow Moat）", "🟡"),
        "none": ("🏚 MOATなし（No Moat）", "🔴")
    }
    rating_label, rating_icon = rating_map.get(rating, ("不明", "⚪"))
    star_str = "★" * stars + "☆" * (5 - stars)

    lines = []
    lines.append(f"### {rating_icon} {rating_label}")
    lines.append(f"**総合レーティング：{star_str}**\n")

    # 定量証拠
    lines.append("**📊 定量証拠（財務指標から）**")
    q_score = quantitative.get("score", 0)
    lines.append(f"MOAT定量スコア：{q_score}/100点\n")

    for key in ["roe_evidence", "margin_evidence", "fcf_evidence", "growth_evidence"]:
        val = quantitative.get(key, "")
        if val:
            lines.append(f"• {val}")

    lines.append("\n---\n")
    lines.append("**🔍 定性評価（AI分析）**\n")

    # 定性評価テーブル風
    strength_map = {
        "strong": "✅ 強い",
        "moderate": "⚠️ 中程度",
        "weak": "❌ 弱い"
    }

    for item in qualitative:
        stype = item.get("type", "")
        strength = item.get("strength", "weak")
        reason = item.get("reason", "")
        slabel = strength_map.get(strength, "⚪ 不明")
        lines.append(f"**{slabel}**　{stype}")
        lines.append(f"　　→ {reason}\n")

    lines.append("---\n")
    lines.append(f"**💡 総合所見**\n{summary}")

    return "\n".join(lines)


def create_brand_display(brand_result: dict) -> str:
    """
    ブランド力評価結果をMarkdown形式で整形する。
    """
    if not brand_result:
        return "ブランド力評価を取得できませんでした。"

    stars = brand_result.get("stars", 0)
    brand_type = brand_result.get("brand_type", "不明")
    pricing_power = brand_result.get("pricing_power", "weak")
    loyalty = brand_result.get("loyalty", "weak")
    recognition = brand_result.get("recognition", "weak")
    maintenance_cost = brand_result.get("maintenance_cost", "high")
    sustainability = brand_result.get("sustainability", "")
    buffet_view = brand_result.get("buffet_view", "")
    quantitative = brand_result.get("quantitative", {})

    star_str = "★" * stars + "☆" * (5 - stars)

    strength_map = {
        "strong": "✅ 強い",
        "moderate": "⚠️ 中程度",
        "weak": "❌ 弱い"
    }
    cost_map = {
        "low": "✅ 低い",
        "moderate": "⚠️ 中程度",
        "high": "❌ 高い"
    }

    lines = []
    lines.append(f"### 🏷️ ブランド力総合スコア：{star_str}（{stars}/5）")
    lines.append(f"**ブランドタイプ：{brand_type}**\n")

    # 定量証拠
    q_score = quantitative.get("score", 0)
    lines.append("**📊 定量指標（ブランド力の証拠）**")
    lines.append(f"ブランド定量スコア：{q_score}/100点\n")

    margin_evidence = quantitative.get("margin_evidence", "")
    growth_evidence = quantitative.get("growth_evidence", "")
    if margin_evidence:
        lines.append(f"• {margin_evidence}")
    if growth_evidence:
        lines.append(f"• {growth_evidence}")
    if not margin_evidence and not growth_evidence:
        lines.append("• 定量的なブランド力の証拠は取得できませんでした。")

    lines.append("\n---\n")
    lines.append("**🔍 定性評価（AI分析）**\n")

    lines.append(f"**{strength_map.get(pricing_power, '⚪ 不明')}**　価格決定力（Pricing Power）")
    lines.append(f"**{strength_map.get(loyalty, '⚪ 不明')}**　顧客ロイヤルティ（Loyalty）")
    lines.append(f"**{strength_map.get(recognition, '⚪ 不明')}**　認知度・世界的影響力（Recognition）")
    lines.append(f"**{cost_map.get(maintenance_cost, '⚪ 不明')}**　ブランド維持コスト（Maintenance Cost）")

    lines.append("\n---\n")
    lines.append(f"**🕰️ 持続性判定**\n{sustainability}")
    lines.append(f"\n**🧠 バフェット的視点**\n{buffet_view}")

    return "\n".join(lines)
