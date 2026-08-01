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

# ===== Sprint18 Phase3: ルールベースチェックリスト計算エンジン =====
def generate_buffett_checklist_rule(data: dict, score_result: dict) -> list:
    """
    Buffett Investment Checklist のルールベース生成。
    数値計算のみ。AIは使用しない。
    戻り値: [{"item": str, "status": "pass"|"warning"|"fail", "reason": str}, ...]
    """
    checklist = []
    roe = data.get("roe") or 0
    op = data.get("operating_margin") or 0
    de = data.get("debt_to_equity")
    pe = data.get("pe_ratio")
    pb = data.get("pb_ratio")
    fcf = data.get("free_cashflow")
    sector = data.get("sector", "")

    # 1. 経営圏
    understandable = [
        "Consumer Defensive", "Consumer Cyclical", "Utilities",
        "Financial Services", "Industrials", "Real Estate",
    ]
    if sector in understandable:
        checklist.append({"item": "経営圏（Understandable Business）", "status": "pass",
                          "reason": "シンプルで理解しやすい業種です。"})
    else:
        checklist.append({"item": "経営圏（Understandable Business）", "status": "warning",
                          "reason": "専門的な業種のため、深い理解が必要です。"})

    # 2. 競争優位性
    if roe >= 0.15 and op >= 0.15:
        checklist.append({"item": "競争優位性（MOAT）", "status": "pass",
                          "reason": "高いROEと利益率から、強い競争優位性が考えられます。"})
    elif roe >= 0.10 or op >= 0.10:
        checklist.append({"item": "競争優位性（MOAT）", "status": "warning",
                          "reason": "一定の優位性はありますが、強いMOATは確認できません。"})
    else:
        checklist.append({"item": "競争優位性（MOAT）", "status": "fail",
                          "reason": "利益率が低く、競争優位性が弱い可能性があります。"})

    # 3. 財務健全性
    if de is not None:
        if de > 100:
            de = de / 100
        if de <= 0.5:
            checklist.append({"item": "財務健全性（Conservative Debt）", "status": "pass",
                              "reason": "負債が少なく、保守的な財務体質です。"})
        elif de <= 1.0:
            checklist.append({"item": "財務健全性（Conservative Debt）", "status": "warning",
                              "reason": "負債は許容範囲内ですが、注意が必要です。"})
        else:
            checklist.append({"item": "財務健全性（Conservative Debt）", "status": "fail",
                              "reason": "負債が多く、財務リスクがあります。"})
    else:
        checklist.append({"item": "財務健全性（Conservative Debt）", "status": "warning",
                          "reason": "負債データを取得できませんでした。"})

    # 4. 収益性
    if op >= 0.20:
        checklist.append({"item": "収益性（High Margin）", "status": "pass",
                          "reason": "高い利益率を維持しています。"})
    elif op >= 0.10:
        checklist.append({"item": "収益性（High Margin）", "status": "warning",
                          "reason": "利益率は普通の水準です。"})
    else:
        checklist.append({"item": "収益性（High Margin）", "status": "fail",
                          "reason": "利益率が低く、価格決定力が弱い可能性があります。"})

    # 5. 経営者
    if roe >= 0.15 and fcf and fcf > 0:
        checklist.append({"item": "経営者（Management Quality）", "status": "pass",
                          "reason": "資本効率と現金創出力に優れ、経営者を信頼できます。"})
    elif roe >= 0.15 or (fcf and fcf > 0):
        checklist.append({"item": "経営者（Management Quality）", "status": "warning",
                          "reason": "経営者の質に一部懸念があります。"})
    else:
        checklist.append({"item": "経営者（Management Quality）", "status": "fail",
                          "reason": "資本効率・現金創出力が弱く、経営者評価は慎重です。"})

    # 6. 安全余裕
    if pe and 0 < pe <= 15:
        checklist.append({"item": "安全余裕（Margin of Safety）", "status": "pass",
                          "reason": "株価は割安水準にあります。"})
    elif (pe and pe <= 25) or (pb and pb <= 3.0):
        checklist.append({"item": "安全余裕（Margin of Safety）", "status": "warning",
                          "reason": "株価は適正水準です。"})
    else:
        checklist.append({"item": "安全余裕（Margin of Safety）", "status": "fail",
                          "reason": "株価は割高で、安全余裕がありません。"})

    return checklist