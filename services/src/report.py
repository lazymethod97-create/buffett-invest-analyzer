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
