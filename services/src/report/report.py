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


def create_score_history_chart(history: List[Any]) -> go.Figure:
    """
    Sprint37: 単一銘柄のスコア推移（履歴）を折れ線チャートとして表示する。

    history: storage.JsonScoreStorage.load_history()等が返す、保存順に
    並んだスナップショットのリスト。各要素は evaluated_at / overall_score /
    grade / decision / mode 属性を持つオブジェクトであればよい
    （report層はstorageパッケージを直接importせず、値の受け渡しのみで
    独立性を保つ。Sprint35/36の「永続化層はUI/analysis_bundle/overall_eval
    から独立」という設計方針の延長）。

    空リストの場合、空のFigureを返す（呼び出し側で件数を見て
    「履歴がありません」等のメッセージ表示を制御する）。
    """
    if not history:
        return go.Figure()

    x_values = [snapshot.evaluated_at for snapshot in history]
    y_values = [snapshot.overall_score for snapshot in history]
    hover_text = [
        f"Grade {snapshot.grade} / {snapshot.decision} / {snapshot.mode}"
        for snapshot in history
    ]

    fig = go.Figure(
        data=go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines+markers",
            name="総合スコア",
            text=hover_text,
            hovertemplate="%{x}<br>スコア: %{y}/190点<br>%{text}<extra></extra>",
        )
    )
    fig.update_layout(
        yaxis=dict(title="総合スコア（190点満点）", range=[0, 190]),
        xaxis=dict(title="評価日時"),
        height=320,
        margin=dict(l=10, r=10, t=30, b=10),
        title="スコア推移",
    )
    return fig


def create_score_comparison_display(history: List[Any]) -> str:
    """
    Sprint38: 直近の評価と1つ前の評価の差分をMarkdown形式で表示する。

    history: storage.JsonScoreStorage.load_history()等が返す、保存順に
    並んだスナップショットのリスト（Sprint37のcreate_score_history_chartと
    同じ入力形式）。report層はSprint37同様storageパッケージを直接importせず、
    evaluated_at / overall_score / grade / decision / mode / buffett_score
    属性を持つオブジェクトであれば動作する（ダックタイピングによる独立性維持）。

    比較対象が2件未満の場合は比較不能である旨のメッセージを返す
    （表示可否の分岐はapp.py側ではなくここで完結させ、app.py側は
    st.markdown()で結果をそのまま表示するだけにする）。
    """
    if len(history) < 2:
        return "*比較対象となる過去の記録がありません（2回目以降の分析から表示されます）。*\n"

    previous = history[-2]
    current = history[-1]

    score_diff = current.overall_score - previous.overall_score
    if score_diff > 0:
        score_diff_text = f"+{score_diff}点 ⬆️"
    elif score_diff < 0:
        score_diff_text = f"{score_diff}点 ⬇️"
    else:
        score_diff_text = "±0点 ➡️"

    md = "#### 📊 前回評価との比較\n\n"
    md += f"- **前回:** {previous.evaluated_at}（{previous.overall_score}点 / Grade {previous.grade} / {previous.decision} / モード: {previous.mode}）\n"
    md += f"- **今回:** {current.evaluated_at}（{current.overall_score}点 / Grade {current.grade} / {current.decision} / モード: {current.mode}）\n\n"
    md += f"**スコア差分:** {score_diff_text}\n\n"

    if current.grade != previous.grade:
        md += f"**グレード変化:** {previous.grade} → {current.grade}\n\n"
    else:
        md += f"**グレード変化:** 変化なし（{current.grade}）\n\n"

    if current.decision != previous.decision:
        md += f"**判定変化:** {previous.decision} → {current.decision}\n\n"
    else:
        md += f"**判定変化:** 変化なし（{current.decision}）\n\n"

    if current.buffett_score is not None and previous.buffett_score is not None:
        buffett_diff = current.buffett_score - previous.buffett_score
        if buffett_diff != 0:
            sign = "+" if buffett_diff > 0 else ""
            md += f"**Buffett Score差分:** {sign}{buffett_diff}点（前回 {previous.buffett_score} → 今回 {current.buffett_score}）\n\n"

    if current.mode != previous.mode:
        md += (
            "⚠️ **注意:** 前回と今回で分析モードが異なります"
            f"（{previous.mode} → {current.mode}）。項目網羅度が異なるため、"
            "スコア差分は単純比較ではなく参考値としてご覧ください。\n"
        )

    return md


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

def create_confirmation_points_display(points: List[Dict[str, Any]]) -> str:
    """
    points: [{"category": str, "point": str, "priority": "high"/"medium"/"low"}, ...]
    """
    if not points:
        return "*確認すべきポイントはありません（ニュースが取得できなかった可能性があります）。*\n"

    priority_icon = {
        "high": "🔴 高",
        "medium": "🟡 中",
        "low": "🟢 低",
    }

    grouped = {}
    for p in points:
        cat = p.get("category", "その他")
        grouped.setdefault(cat, []).append(p)

    md = ""
    for cat, items in grouped.items():
        md += f"#### 📌 {cat}\n"
        for item in items:
            icon = priority_icon.get(item.get("priority", ""), "⚪ -")
            md += f"- **[{icon}]** {item.get('point', '')}\n"
        md += "\n"

    return md

def create_dcf_display(dcf: Dict[str, Any]) -> str:
    """
    dcf: calculate_dcf() の戻り値
    """
    if not dcf.get("success"):
        return f"*{dcf.get('error', 'DCF評価を計算できませんでした。')}*\n"

    a = dcf["assumptions"]
    md = "#### 前提条件\n"
    md += f"- FCF成長率: {a['growth_rate']*100:.1f}%（{a['projection_years']}年間）\n"
    md += f"- 割引率（WACC簡易値）: {a['discount_rate']*100:.1f}%\n"
    md += f"- 永久成長率: {a['terminal_growth']*100:.1f}%\n\n"

    md += "#### 将来FCF予測（1株あたり）\n"
    md += "| 年 | 予測FCF | 現在価値 |\n|:---:|---:|---:|\n"
    for p in dcf["projections"]:
        md += f"| {p['year']}年後 | {p['fcf_per_share']:.2f} | {p['present_value']:.2f} |\n"
    md += "\n"

    md += f"**ターミナルバリュー（現在価値）:** {dcf['terminal_value_pv']:.2f}\n\n"
    md += f"### 💰 理論株価（Intrinsic Value）: {dcf['intrinsic_value_per_share']:.2f}\n"
    md += f"**現在株価:** {dcf['current_price']:.2f}\n\n"
    md += f"**安全余裕（Margin of Safety）:** {dcf['margin_of_safety_pct']:+.1f}%\n\n"
    md += f"**判定:** {dcf['verdict']}\n"
    return md


def create_roic_display(roic: Dict[str, Any]) -> str:
    """ROIC分析結果をMarkdown形式で表示する。"""
    if not roic:
        return "*ROIC分析結果がありません。*\n"

    raw = roic.get("raw", {})
    roic_val = raw.get("roic")
    nopat = raw.get("nopat")
    ic = raw.get("invested_capital")
    tax_rate = raw.get("tax_rate", 0.25)

    md = "#### ROIC（投下資本利益率）分析\n\n"
    if roic_val is not None:
        md += f"**ROIC:** {roic_val*100:.1f}%\n\n"
    else:
        md += "**ROIC:** データ不足\n\n"

    md += f"**評価:** {roic.get('summary', '')}\n\n"
    md += f"**スコア:** {roic.get('score', 0)} / {roic.get('max_score', 15)}点\n\n"

    md += "#### 内訳\n"
    if nopat is not None:
        md += f"- **NOPAT（税引後営業利益）:** {nopat:,.0f}\n"
    else:
        md += "- **NOPAT（税引後営業利益）:** データ不足\n"
    if ic is not None:
        md += f"- **投下資本:** {ic:,.0f}\n"
    else:
        md += "- **投下資本:** データ不足\n"
    md += f"- **実効税率:** {tax_rate*100:.1f}%\n"

    md += "\n#### 計算式\n"
    md += "```\n"
    md += "NOPAT = 営業利益 * (1 - 実効税率)\n"
    md += "投下資本 = 純資産 + 総負債 - 現金同等物\n"
    md += "ROIC = NOPAT / 投下資本\n"
    md += "```\n"

    warnings = roic.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md
def create_intrinsic_value_display(intrinsic_value: Dict[str, Any]) -> str:
    """Intrinsic Value（内在価値）分析結果をMarkdown形式で表示する（Sprint21）。"""
    if not intrinsic_value:
        return "*Intrinsic Value分析結果がありません。*\n"

    raw = intrinsic_value.get("raw", {})
    consensus = raw.get("consensus_intrinsic_value_per_share")
    current_price = raw.get("current_price")
    mosp = raw.get("margin_of_safety_pct")

    md = "#### Intrinsic Value（内在価値）分析\n\n"
    if consensus is not None:
        md += f"**コンセンサス内在価値（1株）:** {consensus:,.2f}\n\n"
    else:
        md += "**コンセンサス内在価値（1株）:** データ不足\n\n"

    if current_price is not None:
        md += f"**現在株価:** {current_price:,.2f}\n\n"

    if mosp is not None:
        md += f"**安全余裕（Margin of Safety）:** {mosp:+.1f}%\n\n"

    md += f"**評価:** {intrinsic_value.get('summary', '')}\n\n"
    md += f"**スコア:** {intrinsic_value.get('score', 0)} / {intrinsic_value.get('max_score', 15)}点\n\n"

    estimates = raw.get("estimates", [])
    if estimates:
        md += "#### 各方式の推定値\n"
        for est in estimates:
            label = est.get("label", est.get("method", ""))
            value = est.get("value", 0)
            detail = est.get("detail", "")
            md += f"- **{label}:** {value:,.2f}（{detail}）\n"
        md += "\n"

    md += "#### 計算方式\n```\n"
    md += "コンセンサス = Σ(方式の推定値 × 重み) / Σ(重み)\n"
    md += "・DCF（FCF割引）: 重み40%\n"
    md += "・Owner Earnings方式: 重み30%\n"
    md += "・Earnings Power方式（純利益×適正PER）: 重み30%\n"
    md += "安全余裕 = (内在価値 − 現在株価) ÷ 現在株価\n"
    md += "```\n"

    warnings = intrinsic_value.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md


def create_owner_earnings_display(owner_earnings: Dict[str, Any]) -> str:
    """
    Owner Earnings（オーナーアーニングス）分析結果をMarkdown形式で表示する（Sprint20）。
    ※Sprint20でapp.pyから参照されていたにもかかわらず実装漏れだった関数をSprint22で追加（バグ修正）。
    """
    if not owner_earnings:
        return "*Owner Earnings分析結果がありません。*\n"

    raw = owner_earnings.get("raw", {})
    oe = raw.get("owner_earnings")
    oe_yield = raw.get("owner_earnings_yield")
    net_income = raw.get("net_income")
    da = raw.get("depreciation_amortization")
    capex = raw.get("capital_expenditures")

    md = "#### Owner Earnings（オーナーアーニングス）分析\n\n"
    if oe is not None:
        md += f"**Owner Earnings:** {oe:,.0f}\n\n"
    else:
        md += "**Owner Earnings:** データ不足\n\n"

    if oe_yield is not None:
        md += f"**Owner Earnings利回り:** {oe_yield*100:.1f}%\n\n"

    md += f"**評価:** {owner_earnings.get('summary', '')}\n\n"
    md += f"**スコア:** {owner_earnings.get('score', 0)} / {owner_earnings.get('max_score', 10)}点\n\n"

    md += "#### 内訳\n"
    if net_income is not None:
        md += f"- **当期純利益:** {net_income:,.0f}\n"
    else:
        md += "- **当期純利益:** データ不足\n"
    if da is not None:
        md += f"- **減価償却費等（推定）:** {da:,.0f}\n"
    else:
        md += "- **減価償却費等（推定）:** データ不足（0として計算）\n"
    if capex is not None:
        md += f"- **設備投資CapEx（推定）:** {capex:,.0f}\n"
    else:
        md += "- **設備投資CapEx（推定）:** データ不足（0として計算）\n"

    md += "\n#### 計算式\n```\n"
    md += "Owner Earnings = 当期純利益 + 減価償却費等（D&A） - 設備投資（CapEx）\n"
    md += "D&A（推定） = EBITDA - 営業利益\n"
    md += "CapEx（推定） = 営業キャッシュフロー - フリーキャッシュフロー\n"
    md += "```\n"

    warnings = owner_earnings.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md


def create_capital_allocation_display(capital_allocation: Dict[str, Any]) -> str:
    """Capital Allocation（資本配分）分析結果をMarkdown形式で表示する（Sprint22）。"""
    if not capital_allocation:
        return "*Capital Allocation分析結果がありません。*\n"

    raw = capital_allocation.get("raw", {})
    reinvestment_score = raw.get("reinvestment_score", 0)
    reinvestment_detail = raw.get("reinvestment_detail", "")
    payout_score = raw.get("payout_score", 0)
    payout_detail = raw.get("payout_detail", "")
    buyback_score = raw.get("buyback_score", 0)
    buyback_detail = raw.get("buyback_detail", "")

    md = "#### Capital Allocation（資本配分）分析\n\n"
    md += f"**スコア:** {capital_allocation.get('score', 0)} / {capital_allocation.get('max_score', 10)}点\n\n"
    md += f"**評価:** {capital_allocation.get('summary', '')}\n\n"

    md += "#### 3つの評価軸\n"
    md += f"- **再投資効率（ROIC基準）:** {reinvestment_score} / 4点\n  - {reinvestment_detail}\n"
    md += f"- **株主還元の規律（配当性向）:** {payout_score} / 3点\n  - {payout_detail}\n"
    md += f"- **自社株買いのタイミング（MOSとの突合）:** {buyback_score} / 3点\n  - {buyback_detail}\n"

    md += "\n#### 計算方式\n```\n"
    md += "資本配分 = 再投資効率(4) + 株主還元の規律(3) + 自社株買いのタイミング(3)\n"
    md += "・再投資効率: ROICの水準から評価（既存 roic_engine 再利用）\n"
    md += "・株主還元の規律: 配当性向の適切性で評価\n"
    md += "・自社株買い: 安全余裕(MOS)との突合で評価（既存 intrinsic_engine 再利用）\n"
    md += "```\n"

    warnings = capital_allocation.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md


def create_share_buyback_display(share_buyback: Dict[str, Any]) -> str:
    """Share Buyback（自社株買い）分析結果をMarkdown形式で表示する（Sprint23）。"""
    if not share_buyback:
        return "*Share Buyback分析結果がありません。*\n"

    raw = share_buyback.get("raw", {})
    consistency_score = raw.get("consistency_score", 0)
    consistency_detail = raw.get("consistency_detail", "")
    reduction_score = raw.get("reduction_score", 0)
    reduction_detail = raw.get("reduction_detail", "")
    balance_score = raw.get("balance_score", 0)
    balance_detail = raw.get("balance_detail", "")
    timing_score = raw.get("timing_score", 0)
    timing_detail = raw.get("timing_detail", "")

    md = "#### Share Buyback（自社株買い）分析\n\n"
    md += f"**スコア:** {share_buyback.get('score', 0)} / {share_buyback.get('max_score', 10)}点\n\n"
    md += f"**評価:** {share_buyback.get('summary', '')}\n\n"

    md += "#### 4つの評価軸\n"
    md += f"- **買い入れの一貫性:** {consistency_score} / 3点\n  - {consistency_detail}\n"
    md += f"- **発行済株式数の減少効果:** {reduction_score} / 3点\n  - {reduction_detail}\n"
    md += f"- **財務健全性とのバランス:** {balance_score} / 2点\n  - {balance_detail}\n"
    md += f"- **買い入れの効果的なタイミング（PER水準）:** {timing_score} / 2点\n  - {timing_detail}\n"

    md += "\n#### 計算方式\n```\n"
    md += "自社株買い = 一貫性(3) + 株式数減少効果(3) + 財務健全性バランス(2) + タイミング(2)\n"
    md += "・一貫性: 複数年の自社株買い実施率で評価\n"
    md += "・株式数減少効果: 期中平均株式数の減少率で評価\n"
    md += "・財務健全性バランス: 負債推移とのバランスで評価\n"
    md += "・タイミング: 現在PERと過去5年平均PER（簡易推定）の比較で評価\n"
    md += "```\n"

    warnings = share_buyback.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md


def create_debt_quality_display(debt_quality: Dict[str, Any]) -> str:
    """Debt Quality（負債の質）分析結果をMarkdown形式で表示する（Sprint24）。"""
    if not debt_quality:
        return "*Debt Quality分析結果がありません。*\n"

    raw = debt_quality.get("raw", {})
    level_score = raw.get("level_score", 0)
    level_detail = raw.get("level_detail", "")
    coverage_score = raw.get("coverage_score", 0)
    coverage_detail = raw.get("coverage_detail", "")
    composition_score = raw.get("composition_score", 0)
    composition_detail = raw.get("composition_detail", "")
    trend_score = raw.get("trend_score", 0)
    trend_detail = raw.get("trend_detail", "")

    md = "#### Debt Quality（負債の質）分析\n\n"
    md += f"**スコア:** {debt_quality.get('score', 0)} / {debt_quality.get('max_score', 10)}点\n\n"
    md += f"**評価:** {debt_quality.get('summary', '')}\n\n"

    md += "#### 4つの評価軸\n"
    md += f"- **負債水準の適正さ（D/E・Debt/EBITDA）:** {level_score} / 3点\n  - {level_detail}\n"
    md += f"- **金利負担能力（インタレスト・カバレッジ・レシオ）:** {coverage_score} / 3点\n  - {coverage_detail}\n"
    md += f"- **負債の質・構成（短期負債比率）:** {composition_score} / 2点\n  - {composition_detail}\n"
    md += f"- **負債推移のトレンド:** {trend_score} / 2点\n  - {trend_detail}\n"

    md += "\n#### 計算方式\n```\n"
    md += "負債の質 = 水準適正さ(3) + 金利負担能力(3) + 質・構成(2) + トレンド(2)\n"
    md += "・水準適正さ: D/E比率とDebt/EBITDA倍率のうち厳しい方の水準で評価\n"
    md += "・金利負担能力: インタレスト・カバレッジ・レシオ(営業利益÷支払利息)で評価\n"
    md += "・質・構成: 短期負債 ÷ 総負債の比率（借り換えリスク）で評価\n"
    md += "・トレンド: 直近数年の総負債の年平均変化率で評価（Sprint23のtotal_debt_historyを再利用）\n"
    md += "```\n"

    warnings = debt_quality.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md


def create_moat_strength_display(moat_strength: Dict[str, Any]) -> str:
    """Economic Moat強化（経済的堀の定量的検証）分析結果をMarkdown形式で表示する（Sprint25）。"""
    if not moat_strength:
        return "*Economic Moat強化分析結果がありません。*\n"

    raw = moat_strength.get("raw", {})
    persistence_score = raw.get("persistence_score", 0)
    persistence_detail = raw.get("persistence_detail", "")
    pricing_power_score = raw.get("pricing_power_score", 0)
    pricing_power_detail = raw.get("pricing_power_detail", "")
    market_position_score = raw.get("market_position_score", 0)
    market_position_detail = raw.get("market_position_detail", "")
    consistency_score = raw.get("consistency_score", 0)
    consistency_detail = raw.get("consistency_detail", "")

    md = "#### Economic Moat強化（経済的堀の定量的検証）分析\n\n"
    md += f"**スコア:** {moat_strength.get('score', 0)} / {moat_strength.get('max_score', 10)}点\n\n"
    md += f"**評価:** {moat_strength.get('summary', '')}\n\n"

    md += "#### 4つの評価軸\n"
    md += f"- **収益性の持続性・安定性（ROE・営業利益率）:** {persistence_score} / 3点\n  - {persistence_detail}\n"
    md += f"- **価格決定力の定量的検証（粗利率の防衛力）:** {pricing_power_score} / 3点\n  - {pricing_power_detail}\n"
    md += f"- **市場地位の安定性（売上高成長率のブレ幅）:** {market_position_score} / 2点\n  - {market_position_detail}\n"
    md += f"- **既存MOAT判定との整合性:** {consistency_score} / 2点\n  - {consistency_detail}\n"

    md += "\n#### 計算方式\n```\n"
    md += "Economic Moat強化 = 収益性の持続性(3) + 価格決定力(3) + 市場地位の安定性(2) + 既存MOAT判定との整合性(2)\n"
    md += "・収益性の持続性: ROE（優先）または営業利益率の複数年推移の水準と変動係数で評価\n"
    md += "・価格決定力: 粗利率（またはEBITDAマージン）の直近年 vs 過去平均の防衛度合いで評価\n"
    md += "・市場地位の安定性: 売上高成長率の複数年推移のブレ幅（標準偏差・最小値）で評価\n"
    md += "・既存MOAT判定との整合性: Sprint18のwide/narrow/none判定と本エンジンの定量トレンド評価を突合\n"
    md += "```\n"

    warnings = moat_strength.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md


def create_backtest_display(backtest: Dict[str, Any]) -> str:
    """Backtest（簡易品質スコア × フォワードリターン検証）分析結果をMarkdown形式で表示する（Sprint26）。"""
    if not backtest:
        return "*Backtest分析結果がありません。*\n"

    raw = backtest.get("raw", {})
    edge_score = raw.get("edge_score", 0)
    edge_detail = raw.get("edge_detail", "")
    best_period_score = raw.get("best_period_score", 0)
    best_period_detail = raw.get("best_period_detail", "")
    consistency_score = raw.get("consistency_score", 0)
    consistency_detail = raw.get("consistency_detail", "")
    current_consistency_score = raw.get("current_consistency_score", 0)
    current_consistency_detail = raw.get("current_consistency_detail", "")
    years = raw.get("raw", {}).get("years", [])

    md = "#### Backtest（簡易品質スコア × フォワードリターン検証）分析\n\n"
    md += f"**スコア:** {backtest.get('score', 0)} / {backtest.get('max_score', 10)}点\n\n"
    md += f"**評価:** {backtest.get('summary', '')}\n\n"

    md += "#### 4つの評価軸\n"
    md += f"- **高品質年 vs 低品質年のリターン差検証:** {edge_score} / 3点\n  - {edge_detail}\n"
    md += f"- **最高品質期間の実績リターン:** {best_period_score} / 3点\n  - {best_period_detail}\n"
    md += f"- **一貫性（品質スコアとリターンの相関）:** {consistency_score} / 2点\n  - {consistency_detail}\n"
    md += f"- **現在のBuffett Scoreとの整合性:** {current_consistency_score} / 2点\n  - {current_consistency_detail}\n"

    if years:
        md += "\n#### 決算期別の簡易品質スコア・フォワードリターン（翌決算期まで、直近年のみ現在）\n"
        md += "| 決算期末 | 簡易品質スコア | フォワードリターン |\n"
        md += "|---|---|---|\n"
        for y in years:
            r = y.get("forward_return")
            r_text = f"{r*100:.1f}%" if r is not None else "算出不可"
            md += f"| {y.get('date', '')} | {y.get('quality_proxy', 0)} | {r_text} |\n"

    md += "\n#### 計算方式\n```\n"
    md += "Backtest = リターン差検証(3) + 最高品質期間実績(3) + 一貫性(2) + 現在スコアとの整合性(2)\n"
    md += "・簡易品質スコア代理指標: ROE・営業利益率・売上成長率・負債水準（対売上高）の\n"
    md += "  複数年データ（Sprint23〜25で取得済み）からルールベースで算出（AI判定・DCFは含まない）\n"
    md += "・フォワードリターン: 各決算期から翌決算期（直近年のみ現在）までの約1年間のリターン。\n"
    md += "  現在までの累積リターンにすると決算期が古いほど保有期間が長くなり複利で\n"
    md += "  見かけ上リターンが伸びる交絡が生じるため、期間を統一している\n"
    md += "・リターン差検証: 決算期を品質スコアの中央値で高品質群・低品質群に分け、\n"
    md += "  フォワードリターンの平均差で評価\n"
    md += "・最高品質期間実績: 最も品質スコアが高かった決算期の実際のフォワードリターンで評価\n"
    md += "・一貫性: 品質スコアとフォワードリターンの相関係数（Pearson）で評価\n"
    md += "・現在スコアとの整合性: 過去の質とリターンの関係と、現在のBuffett Scoreの水準を突合\n"
    md += "```\n"

    warnings = backtest.get("warnings", [])
    if warnings:
        md += "#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"
    return md


def create_portfolio_risk_display(portfolio_risk: Dict[str, Any]) -> str:
    """
    Portfolio Risk（保有ポートフォリオのリスク分散評価）分析結果をMarkdown形式で
    表示する（Sprint27）。単一銘柄向けの各create_X_displayとは異なり、複数銘柄
    からなるポートフォリオ全体を対象とする。
    """
    if not portfolio_risk:
        return "*Portfolio Risk分析結果がありません。*\n"

    raw = portfolio_risk.get("raw", {})
    # raw はengines.portfolio_risk_engine.calculate_portfolio_risk()の戻り値
    # （engine_result）をそのまま保持しており、engine_result自身の詳細データ
    # （銘柄別構成比等）はさらにその内側の raw["raw"] にネストされている
    # （Sprint26 create_backtest_displayと同じ構造）。
    engine_raw = raw.get("raw", {})
    if not engine_raw.get("holding_count"):
        return f"*{portfolio_risk.get('summary', 'Portfolio Risk分析結果がありません。')}*\n"

    sector_score = raw.get("sector_score", 0)
    sector_detail = raw.get("sector_detail", "")
    concentration_score = raw.get("concentration_score", 0)
    concentration_detail = raw.get("concentration_detail", "")
    region_score = raw.get("region_score", 0)
    region_detail = raw.get("region_detail", "")
    count_score = raw.get("count_score", 0)
    count_detail = raw.get("count_detail", "")

    md = "#### Portfolio Risk（保有ポートフォリオのリスク分散評価）分析\n\n"
    md += f"**スコア:** {portfolio_risk.get('score', 0)} / {portfolio_risk.get('max_score', 10)}点\n\n"
    md += f"**評価:** {portfolio_risk.get('summary', '')}\n\n"

    weighted_avg = raw.get("weighted_avg_buffett_score")
    weighted_max = raw.get("weighted_avg_buffett_max_score")
    if weighted_avg is not None and weighted_max:
        md += (
            f"**（参考）保有銘柄の加重平均Buffett Score:** {weighted_avg:.1f} / {weighted_max}点"
            "　※時価評価額で加重。Portfolio Riskスコアそのものには含まれません。\n\n"
        )

    md += "#### 4つの評価軸\n"
    md += f"- **セクター分散度:** {sector_score} / 3点\n  - {sector_detail}\n"
    md += f"- **銘柄集中度:** {concentration_score} / 3点\n  - {concentration_detail}\n"
    md += f"- **地域分散度:** {region_score} / 2点\n  - {region_detail}\n"
    md += f"- **保有銘柄数の充足度:** {count_score} / 2点\n  - {count_detail}\n"

    sector_weights = engine_raw.get("sector_weights", {})
    if sector_weights:
        md += "\n#### セクター別構成比（時価評価額ベース）\n"
        md += "| セクター | 構成比 |\n|---|---|\n"
        for sector, w in sorted(sector_weights.items(), key=lambda kv: kv[1], reverse=True):
            md += f"| {sector} | {w*100:.1f}% |\n"

    country_weights = engine_raw.get("country_weights", {})
    if country_weights:
        md += "\n#### 国・地域別構成比（時価評価額ベース）\n"
        md += "| 国・地域 | 構成比 |\n|---|---|\n"
        for country, w in sorted(country_weights.items(), key=lambda kv: kv[1], reverse=True):
            md += f"| {country} | {w*100:.1f}% |\n"

    holding_weights = engine_raw.get("holding_weights", [])
    if holding_weights:
        md += "\n#### 保有銘柄別構成比（時価評価額ベース）\n"
        md += "| 銘柄 | セクター | 国・地域 | 構成比 |\n|---|---|---|---|\n"
        for w in sorted(holding_weights, key=lambda x: x["weight"], reverse=True):
            md += f"| {w.get('company_name', w.get('ticker',''))}（{w.get('ticker','')}） | {w.get('sector','')} | {w.get('country','')} | {w.get('weight',0)*100:.1f}% |\n"

    md += "\n#### 計算方式\n```\n"
    md += "Portfolio Risk = セクター分散度(3) + 銘柄集中度(3) + 地域分散度(2) + 保有銘柄数の充足度(2)\n"
    md += "・セクター分散度: セクター別構成比のHHI（ハーフィンダール・ハーシュマン指数）で評価\n"
    md += "・銘柄集中度: 時価評価額ベースで最大の構成比を持つ1銘柄の比率で評価\n"
    md += "・地域分散度: 国内（日本）／海外の構成比の内訳で評価\n"
    md += "・保有銘柄数の充足度: 分散効果を得るために必要な最低限の銘柄数が確保されているかで評価\n"
    md += "・単一銘柄向けのBuffett Score（190点満点）とは評価単位が異なるため、\n"
    md += "  総合判定（BUY/WATCH/PASS）には含まれない、独立したポートフォリオ分析です\n"
    md += "```\n"

    warnings = portfolio_risk.get("warnings", [])
    if warnings:
        md += "\n#### 警告\n"
        for w in warnings:
            md += f"- {w}\n"

    buffet_view = portfolio_risk.get("buffet_view")
    if buffet_view:
        md += "\n#### 🤖 AI考察（バフェット視点）\n"
        md += f"{buffet_view}\n"
        if portfolio_risk.get("improvement_area"):
            md += f"\n**改善点:** {portfolio_risk.get('improvement_area')}\n"
        if portfolio_risk.get("ai_conclusion"):
            md += f"\n**総合結論:** {portfolio_risk.get('ai_conclusion')}\n"

    return md


def create_watchlist_insights_display(insights: Dict[str, Any]) -> str:
    """
    Watchlist Insights（ウォッチリスト横断の集計・ランキング表示）結果を
    Markdown形式で表示する（Sprint28）。Portfolio Riskと異なり得点化は
    行わないため、スコア・rating・警告条件による色分け等は扱わず、
    ランキング表・集計表のみを表示する。
    """
    if not insights or not insights.get("success"):
        summary = (insights or {}).get(
            "summary", "Watchlist Insightsを表示するためのデータがありません。"
        )
        return f"*{summary}*\n"

    md = "#### 📊 Watchlist Insights（ウォッチリスト横断分析）\n\n"
    md += f"**{insights.get('summary', '')}**\n\n"

    target_ranking = insights.get("target_price_ranking", [])
    if target_ranking:
        md += "#### 🎯 目標株価接近度ランキング（到達済み・近い順）\n"
        md += "| 銘柄 | 現在値 | 目標株価 | 差分 | 状態 |\n|---|---|---|---|---|\n"
        for t in target_ranking:
            currency = t.get("currency", "")
            diff_pct = t.get("diff_pct")
            diff_text = f"{diff_pct:+.1f}%" if diff_pct is not None else "-"
            status = "🎯 到達済み" if t.get("reached") else "未到達"
            md += (
                f"| {t.get('company_name', '')}（{t.get('ticker', '')}） | "
                f"{currency}{t.get('current_price', 0):,.2f} | "
                f"{currency}{t.get('target_price', 0):,.2f} | {diff_text} | {status} |\n"
            )
        no_target = insights.get("no_target_count", 0)
        if no_target:
            md += f"\n※目標株価が未設定の銘柄（{no_target}件）はランキング対象外です。\n"
    else:
        md += "#### 🎯 目標株価接近度ランキング\n"
        md += "*目標株価を設定した銘柄がないため、ランキングを表示できません。*\n"

    score_ranking = insights.get("score_ranking", [])
    if score_ranking:
        md += "\n#### 🏆 ウォッチリスト内 Buffett Score ランキング\n"
        md += "| 銘柄 | Buffett Score | 判定 |\n|---|---|---|\n"
        for s in score_ranking:
            md += (
                f"| {s.get('company_name', '')}（{s.get('ticker', '')}） | "
                f"{s.get('score', 0)} / {s.get('max_score', 0)}点 | {s.get('verdict', '')} |\n"
            )

    sector_overlap = insights.get("sector_overlap", [])
    if sector_overlap:
        md += "\n#### 🗂 セクター別 件数（ウォッチリスト vs Portfolio、参考）\n"
        md += "| セクター | ウォッチリスト件数 | Portfolio件数 | 重複 |\n|---|---|---|---|\n"
        for s in sector_overlap:
            overlap_mark = "⚠️ あり" if s.get("overlap") else "-"
            md += (
                f"| {s.get('sector', '')} | {s.get('watchlist_count', 0)} | "
                f"{s.get('portfolio_count', 0)} | {overlap_mark} |\n"
            )
        md += (
            "\n※時価評価額加重のHHI計算（Portfolio Riskで使用）ではなく、"
            "単純な銘柄数の集計による参考情報です。\n"
        )

    md += "\n#### 計算方式\n```\n"
    md += "Watchlist Insightsは得点化を行わない集計・ランキング表示のみの機能です。\n"
    md += "・目標株価接近度: (現在値 - 目標株価) / 目標株価 × 100（マイナスまたは0は到達済み）\n"
    md += "・Buffett Scoreランキング: 既存calculate_buffett_scoreの結果を降順ソート（再計算なし）\n"
    md += "・セクター件数: ウォッチリスト・Portfolioそれぞれのsector値を単純カウント\n"
    md += "・単一銘柄向けのBuffett Score（190点満点）や総合判定（BUY/WATCH/PASS）には\n"
    md += "  含まれない、独立したウォッチリスト横断の参考情報です\n"
    md += "```\n"

    warnings = insights.get("warnings", [])
    if warnings:
        md += "\n#### 注意事項\n"
        for w in warnings:
            md += f"- {w}\n"

    return md
