import plotly.graph_objects as go
from typing import Dict, Any, List


def create_radar_chart(details: List[Dict[str, Any]]) -> go.Figure:
    """
    details: [{"item": str, "value": ..., "score": float, "max_score": float, ...}, ...]
    各項目のスコアを max_score に対する割合に正規化し、0〜10のレンジで表示する。
    """
    categories = [d["item"] for d in details]
    values = [
        (d["score"] / d["max_score"]) * 10 if d.get("max_score") else 0
        for d in details
    ]

    values += values[:1]
    categories += categories[:1]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Score'
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10])
        ),
        showlegend=False,
        title="Buffett Score Radar"
    )
    return fig


def create_score_bar(score: float, max_score: float = 100) -> go.Figure:
    """スコアをゲージ（インジケーター）チャートとして表示する"""
    if score >= 75:
        bar_color = "#2ca02c"
    elif score >= 55:
        bar_color = "#ff7f0e"
    else:
        bar_color = "#d62728"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Buffett Score"},
        gauge={
            'axis': {'range': [0, max_score]},
            'bar': {'color': bar_color},
            'steps': [
                {'range': [0, 55], 'color': "#ffe0e0"},
                {'range': [55, 75], 'color': "#fff3cd"},
                {'range': [75, max_score], 'color': "#d4edda"},
            ],
            'threshold': {
                'line': {'color': "black", 'width': 3},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def create_checklist_display(checklist: List[Dict[str, Any]]) -> str:
	"""
	checklist: [{"item": str, "status": "pass"/"warning"/"fail", "reason": str}, ...]
	"""
	if not checklist:
		return "*チェックリスト項目がありません。*\n"

	status_map = {
		"pass": "✅ 合格",
		"warning": "⚠️ 要注意",
		"fail": "❌ 不適合",
	}

	md = "| 項目 | 判定 | 理由 |\n|:---|:---|:---|\n"
	for entry in checklist:
		status = status_map.get(entry.get("status", ""), entry.get("status", ""))
		md += f"| {entry.get('item', '')} | {status} | {entry.get('reason', '')} |\n"
	return md


def create_moat_display(moat: Dict[str, Any]) -> str:
	"""
	moat: {"rating": "wide"/"narrow"/"none", "stars": int,
	       "quantitative": {"roe_evidence":..., "margin_evidence":..., "fcf_evidence":..., "growth_evidence":..., "score":...},
	       "qualitative": [{"type":..., "strength": "strong"/"moderate"/"weak", "reason":...}, ...],
	       "summary": str}
	"""
	rating = moat.get("rating", "none")
	stars = moat.get("stars", 0) or 0
	rating_label = {
		"wide": "🟢 Wide MOAT（広い堀）",
		"narrow": "🟡 Narrow MOAT（狭い堀）",
		"none": "🔴 No MOAT（堀なし）",
	}.get(rating, rating)

	md = f"**総合評価:** {rating_label}　{'★' * stars}{'☆' * (5 - stars)}\n\n"

	quant = moat.get("quantitative", {})
	if quant:
		md += "#### 定量根拠\n"
		for key in ["roe_evidence", "margin_evidence", "fcf_evidence", "growth_evidence"]:
			val = quant.get(key)
			if val:
				md += f"- {val}\n"
		md += "\n"

	qual = moat.get("qualitative", [])
	if qual:
		icon_map = {"strong": "✅", "moderate": "⚠️", "weak": "❌"}
		md += "#### 定性評価\n"
		for q in qual:
			icon = icon_map.get(q.get("strength", ""), "❔")
			md += f"- {icon} **{q.get('type', '')}**: {q.get('reason', '')}\n"
		md += "\n"

	summary = moat.get("summary", "")
	if summary:
		md += f"> {summary}\n"
	return md


def create_brand_display(brand: Dict[str, Any]) -> str:
	"""
	brand: {"stars": int, "brand_type": str, "pricing_power": str, "loyalty": str,
	        "recognition": str, "maintenance_cost": str, "sustainability": str,
	        "buffet_view": str, "quantitative": {"margin_evidence":..., "growth_evidence":..., "score":...}}
	"""
	stars = brand.get("stars", 0) or 0
	md = f"**総合評価:** {'★' * stars}{'☆' * (5 - stars)}　（{brand.get('brand_type', '不明')}）\n\n"

	quant = brand.get("quantitative", {})
	if quant:
		md += "#### 定量根拠\n"
		for key in ["margin_evidence", "growth_evidence"]:
			val = quant.get(key)
			if val:
				md += f"- {val}\n"
		md += "\n"

	icon_map = {"strong": "✅", "moderate": "⚠️", "weak": "❌", "low": "✅", "high": "❌"}
	qual_fields = [
		("pricing_power", "価格決定力"),
		("loyalty", "顧客ロイヤルティ"),
		("recognition", "世界的認知度"),
		("maintenance_cost", "維持コスト"),
	]
	md += "#### 定性評価\n"
	for key, label in qual_fields:
		val = brand.get(key)
		if val:
			icon = icon_map.get(val, "❔")
			md += f"- {icon} **{label}**: {val}\n"
	md += "\n"

	sustainability = brand.get("sustainability", "")
	if sustainability:
		md += f"**持続性判断:** {sustainability}\n\n"

	buffet_view = brand.get("buffet_view", "")
	if buffet_view:
		md += f"> {buffet_view}\n"
	return md


def create_management_display(mgmt: Dict[str, Any]) -> str:
	"""
	mgmt: {"stars": int, "capital_allocation": str, "transparency": str, "long_term": str,
	       "self_interest": str, "founder_led": str, "debt_management": str,
	       "buffet_view": str, "conclusion": str,
	       "quantitative": {"roe_evidence":..., "fcf_evidence":..., "dividend_evidence":..., "score":...}}
	"""
	stars = mgmt.get("stars", 0) or 0
	md = f"**総合評価:** {'★' * stars}{'☆' * (5 - stars)}\n\n"

	quant = mgmt.get("quantitative", {})
	if quant:
		md += "#### 定量根拠\n"
		for key in ["roe_evidence", "fcf_evidence", "dividend_evidence"]:
			val = quant.get(key)
			if val:
				md += f"- {val}\n"
		md += "\n"

	field_map = [
		("capital_allocation", "資本配分能力"),
		("transparency", "情報開示の透明性"),
		("long_term", "長期視点"),
		("self_interest", "自己利益度"),
		("founder_led", "創業者経営"),
		("debt_management", "負債管理"),
	]
	md += "#### 定性評価\n"
	for key, label in field_map:
		val = mgmt.get(key)
		if val:
			md += f"- **{label}**: {val}\n"
	md += "\n"

	buffet_view = mgmt.get("buffet_view", "")
	if buffet_view:
		md += f"**バフェット視点:** {buffet_view}\n\n"

	conclusion = mgmt.get("conclusion", "")
	if conclusion:
		md += f"**結論:** {conclusion}\n"
	return md


def create_red_team_display(red_team: Dict[str, Any]) -> str:
	"""
	red_team: {"financial_skepticism": str, "moat_vulnerability": str,
	           "brand_demand_risk": str, "management_blindspot": str,
	           "valuation_concern": str, "conclusion": str}
	"""
	md = ""
	sections = [
		("financial_skepticism", "財務への疑問"),
		("moat_vulnerability", "MOATの脆弱性"),
		("brand_demand_risk", "ブランド・需要リスク"),
		("management_blindspot", "経営・組織リスク"),
		("valuation_concern", "バリュエーション懸念"),
	]

	for key, title in sections:
		val = red_team.get(key, "")
		if val:
			md += f"#### {title}\n- ⚠️ {val}\n\n"

	conclusion = red_team.get("conclusion", "")
	if conclusion:
		md += f"> **結論:** {conclusion}\n"
	return md


def create_hypothesis_display(hypotheses: List[Dict[str, Any]]) -> str:
    if not hypotheses:
        return "📋 投資仮説がまだ登録されていません。"

    md = "### 📋 投資仮説管理\n\n"

    status_map = {
        "未検証": "⏳",
        "検証中": "🔍",
        "成立": "✅",
        "却下": "❌",
        "保留": "⏸️"
    }

    for h in hypotheses:
        status = h.get("status", "未検証")
        icon = status_map.get(status, "⏳")
        h_id = h.get("id", "?")
        title = h.get("title", "無題")
        source = h.get("source", "manual")

        md += f"---\n\n#### {icon} #{h_id} {title}\n"
        md += f"**ステータス:** `{status}` | **来源:** {source}\n\n"

        rationale = h.get("rationale", "")
        if rationale:
            md += f"**根拠:**\n{rationale}\n\n"

        evidence = h.get("evidence", [])
        if evidence:
            md += "**証拠:**\n"
            for ev in evidence:
                md += f"- {ev}\n"
            md += "\n"

        verification = h.get("verification_items", [])
        if verification:
            md += "**検証項目:**\n"
            for v in verification:
                md += f"- [ ] {v}\n"
            md += "\n"

    return md
