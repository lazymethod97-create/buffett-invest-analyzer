import plotly.graph_objects as go
from typing import Dict, Any, List


def create_radar_chart(score_dict: Dict[str, float]) -> go.Figure:
	categories = list(score_dict.keys())
	values = list(score_dict.values())

	# レーダーチャートを閉じる
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


def create_score_bar(score: float, rating: str) -> str:
	filled = min(10, max(0, int(score // 10)))
	bar = "█" * filled + "░" * (10 - filled)
	return f"**Score:** {score}/100 `{bar}` | **Rating:** {rating}"


def create_checklist_display(checklist_result: Dict[str, Any]) -> str:
	md = "### 📋 バフェット投資チェックリスト\n\n"
	md += f"**総合判定:** {checklist_result.get('overall', 'N/A')}\n\n"

	items = checklist_result.get("items", {})
	if items:
		md += "| 項目 | 判定 | 詳細 |\n|:---|:---|:---|\n"
		status_map = {
			"pass": "✅ 合格",
			"attention": "⚠️ 要注意",
			"fail": "❌ 不適合"
		}
		for key, val in items.items():
			status = status_map.get(val, val)
			detail = checklist_result.get("details", {}).get(key, "")
			md += f"| {key} | {status} | {detail} |\n"
	else:
		md += "*チェックリスト項目がありません。*\n"

	analysis = checklist_result.get("analysis", "")
	if analysis:
		md += f"\n**AI分析:**\n{analysis}\n"
	return md


def create_moat_display(moat_result: Dict[str, Any]) -> str:
	md = "### 🏰 MOAT評価\n\n"
	rating = moat_result.get("rating", "")
	md += f"**総合評価:** {rating} {moat_result.get('moat_type', '')}\n\n"

	qe = moat_result.get("quantitative_evidence", [])
	if qe:
		md += "#### 定量根拠\n"
		for item in qe:
			md += f"- {item}\n"
		md += "\n"

	qf = moat_result.get("qualitative_factors", {})
	if qf:
		md += "#### 定性評価\n"
		for factor, val in qf.items():
			icon = "✅" if val in ("strong", "優秀") else "⚠️" if val in ("moderate", "普通") else "❌"
			md += f"- {icon} **{factor}**: {val}\n"
		md += "\n"

	conclusion = moat_result.get("conclusion", "")
	if conclusion:
		md += f"> {conclusion}\n"
	return md


def create_brand_display(brand_result: Dict[str, Any]) -> str:
	md = "### 🏷️ ブランド力評価\n\n"
	rating = brand_result.get("rating", 0)
	if isinstance(rating, (int, float)):
		stars = "★" * int(rating) + "☆" * (5 - int(rating))
	else:
		stars = str(rating)
	md += f"**総合評価:** {stars}\n\n"

	qm = brand_result.get("quantitative_metrics", [])
	if qm:
		md += "#### 定量指標\n"
		for item in qm:
			md += f"- {item}\n"
		md += "\n"

	qa = brand_result.get("qualitative_assessment", {})
	if qa:
		md += "#### AI定性評価\n"
		for factor, val in qa.items():
			icon = "✅" if val in ("strong", "優秀") else "⚠️" if val in ("moderate", "普通") else "❌"
			md += f"- {icon} **{factor}**: {val}\n"
		md += "\n"

	md += f"**持続性判断:** {brand_result.get('sustainability', 'N/A')}\n"

	conclusion = brand_result.get("conclusion", "")
	if conclusion:
		md += f"\n> {conclusion}\n"
	return md


def create_management_display(mgmt_result: Dict[str, Any]) -> str:
	md = "### 👔 経営者評価\n\n"
	rating = mgmt_result.get("rating", 0)
	if isinstance(rating, (int, float)):
		stars = "★" * int(rating) + "☆" * (5 - int(rating))
	else:
		stars = str(rating)
	md += f"**総合評価:** {stars}\n\n"

	qs = mgmt_result.get("quantitative_scores", [])
	if qs:
		md += "#### 定量スコア・証拠\n"
		for item in qs:
			md += f"- {item}\n"
		md += "\n"

	qa = mgmt_result.get("qualitative_assessment", {})
	if qa:
		md += "#### 定性評価\n"
		for factor, val in qa.items():
			icon = "✅" if val in ("excellent", "優秀") else "⚠️" if val in ("good", "良好") else "❌"
			md += f"- {icon} **{factor}**: {val}\n"
		md += "\n"

	md += f"**バフェット視点:** {mgmt_result.get('buffett_view', 'N/A')}\n"
	md += f"\n**結論:** {mgmt_result.get('conclusion', 'N/A')}\n"
	return md


def create_red_team_display(red_team_result: Dict[str, Any]) -> str:
	md = "### 🔴 Red Team AI（楽観バイアス対抗分析）\n\n"

	sections = [
		("financial_doubts", "財務への疑問"),
		("moat_vulnerabilities", "MOATの脆弱性"),
		("brand_risks", "ブランド・需要リスク"),
		("management_risks", "経営・組織リスク"),
		("valuation_concerns", "バリュエーション懸念"),
	]

	for key, title in sections:
		items = red_team_result.get(key, [])
		if items:
			md += f"#### {title}\n"
			for item in items:
				md += f"- ⚠️ {item}\n"
			md += "\n"

	conclusion = red_team_result.get("conclusion", "")
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

