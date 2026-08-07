"""analysis_bundle (Sprint18 Phase4 / Sprint20)

Run all analyses at once.
app.py calls only create_analysis_bundle().

Returns a bundle dict (keys compatible with the legacy app.py bundle):
  mode, news, analysis, summary, confirmation_points, checklist,
  moat, brand, mgmt (alias: management), red_team, roic, owner_earnings, overall
"""

from typing import Any, Dict, Optional

from .overall_eval import calculate_overall_grade
from .roic import analyze_roic
from .owner_earnings import analyze_owner_earnings
from .intrinsic_value import analyze_intrinsic_value
from .capital_allocation import analyze_capital_allocation
from ai.ai_analysis import (
    generate_ai_analysis,
    generate_news_summary,
    generate_buffett_checklist,
    generate_moat_analysis,
    generate_brand_analysis,
    generate_management_analysis,
    generate_red_team_analysis,
    generate_news_confirmation_points,
    generate_roic_analysis,
    generate_owner_earnings_analysis,
    generate_intrinsic_value_analysis,
    generate_capital_allocation_analysis,
)


def _safe_ai(fn, *args):
    """Call an AI analysis function safely. Never raises."""
    try:
        return fn(*args)
    except Exception:
        return None


def _merge_ai_narrative(base: Dict[str, Any], ai_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    ルールベース結果(base)に、Gemini評価(ai_result)の考察部分だけを上書き追加する。
    base側の score / max_score / details / raw（数値の根拠）は絶対に上書きしない
    （Sprint19で発生した「AI結果でrawが失われ、報告書の数値が消える」不具合の再発防止）。
    """
    if not ai_result:
        return base
    for key in ("buffet_view", "competitive_advantage", "capital_efficiency", "improvement_area"):
        if ai_result.get(key):
            base[key] = ai_result[key]
    if ai_result.get("conclusion"):
        base["ai_conclusion"] = ai_result["conclusion"]
    return base


def create_analysis_bundle(
    data: Dict[str, Any],
    score_result: Optional[Dict[str, Any]] = None,
    dcf_result: Optional[Dict[str, Any]] = None,
    mode: str = "standard",
    news: Optional[list] = None,
    is_quick: Optional[bool] = None,
    is_full: Optional[bool] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Run every analysis at once (Sprint18 / Sprint20).

    - is_quick / is_full: explicit flags from the controller (app.py).
      If not given, they are inferred from the mode string.
    - Data fetching (news etc.) is done by app.py (controller), not here.
    """
    score_result = score_result or {}
    dcf_result = dcf_result or {}
    news = news or []

    if is_quick is None:
        is_quick = mode.startswith("quick")
    if is_full is None:
        is_full = mode.startswith("full")

    bundle: Dict[str, Any] = {
        "mode": mode,
        "news": news,
        "analysis": None,
        "summary": None,
        "confirmation_points": None,
        "checklist": None,
        "moat": None,
        "brand": None,
        "mgmt": None,
        "management": None,
        "red_team": None,
        "roic": None,
        "owner_earnings": None,
        "intrinsic_value": None,
        "capital_allocation": None,
        "overall": None,
    }

    if not is_quick:
        # news summary
        if news:
            bundle["summary"] = _safe_ai(generate_news_summary, news) or ""

        # main AI analysis
        bundle["analysis"] = _safe_ai(generate_ai_analysis, data, score_result)

        # checklist (rule-based)
        bundle["checklist"] = _safe_ai(generate_buffett_checklist, data, score_result) or []

        if is_full:
            bundle["confirmation_points"] = _safe_ai(
                generate_news_confirmation_points, data, news, score_result
            )

            moat = _safe_ai(generate_moat_analysis, data, score_result) or {}
            brand = _safe_ai(generate_brand_analysis, data, score_result) or {}
            mgmt = _safe_ai(generate_management_analysis, data, score_result) or {}
            red_team = _safe_ai(
                generate_red_team_analysis,
                data,
                score_result,
                bundle["checklist"],
                moat,
                brand,
                mgmt,
            ) or {}

            bundle["moat"] = moat
            bundle["brand"] = brand
            bundle["mgmt"] = mgmt
            bundle["management"] = mgmt
            bundle["red_team"] = red_team

            ####################################################
            # Sprint19: ROIC分析
            # ルールベース計算（analyze_roic）を必ず実行し、
            # Geminiが使える場合のみAIの考察（buffet_view等）を追加する。
            # ※Sprint19では analyze_roic() が一度も呼ばれておらず、
            #   bundle["roic"] が常にNoneになる不具合があったため、Sprint20で修正。
            ####################################################
            roic = analyze_roic(data)
            ai_roic = _safe_ai(generate_roic_analysis, data, roic.get("raw", {}))
            bundle["roic"] = _merge_ai_narrative(roic, ai_roic)

            ####################################################
            # Sprint20: Owner Earnings分析
            # ROICと同じ形式（ルールベース基礎 + AI考察の上乗せ）で実装する。
            ####################################################
            owner_earnings = analyze_owner_earnings(data)
            ai_oe = _safe_ai(generate_owner_earnings_analysis, data, owner_earnings.get("raw", {}))
            bundle["owner_earnings"] = _merge_ai_narrative(owner_earnings, ai_oe)

            ####################################################
            # Sprint21: Intrinsic Value分析
            # ROIC / Owner Earningsと同じ形式（ルールベース基礎 + AI考察の上乗せ）。
            ####################################################
            intrinsic_value = analyze_intrinsic_value(data, dcf_result or {})
            ai_iv = _safe_ai(generate_intrinsic_value_analysis, data, intrinsic_value.get("raw", {}))
            bundle["intrinsic_value"] = _merge_ai_narrative(intrinsic_value, ai_iv)

            ####################################################
            # Sprint22: Capital Allocation分析
            # ROIC / Owner Earnings / Intrinsic Value の計算結果を再利用し、
            # 同じ形式（ルールベース基礎 + AI考察の上乗せ）で実装する。
            ####################################################
            capital_allocation = analyze_capital_allocation(
                data,
                roic_result=bundle["roic"].get("raw", {}) if bundle.get("roic") else None,
                owner_earnings_result=(
                    bundle["owner_earnings"].get("raw", {}) if bundle.get("owner_earnings") else None
                ),
                intrinsic_value_result=(
                    bundle["intrinsic_value"].get("raw", {}) if bundle.get("intrinsic_value") else None
                ),
            )
            ai_ca = _safe_ai(
                generate_capital_allocation_analysis,
                data,
                capital_allocation.get("raw", {}),
            )
            bundle["capital_allocation"] = _merge_ai_narrative(capital_allocation, ai_ca)

        # Normalize bundle values (Sprint18)
    bundle["checklist"] = bundle["checklist"] or []
    bundle["news"] = bundle["news"] or []

    # Overall verdict - ONLY overall_eval decides BUY / WATCH / PASS
    bundle["overall"] = calculate_overall_grade(
        score_result=score_result,
        dcf_result=dcf_result,
        moat=bundle["moat"] or {},
        brand=bundle["brand"] or {},
        mgmt=bundle["mgmt"] or {},
        red_team=bundle["red_team"] or {},
        roic=bundle["roic"] or {},
        owner_earnings=bundle["owner_earnings"] or {},
        intrinsic_value=bundle["intrinsic_value"] or {},
        capital_allocation=bundle["capital_allocation"] or {},
    )

    return bundle

