"""analysis_bundle (Sprint18 Phase4)

Run all analyses at once.
app.py calls only create_analysis_bundle().

Returns a bundle dict (keys compatible with the legacy app.py bundle):
  mode, news, analysis, summary, confirmation_points, checklist,
  moat, brand, mgmt (alias: management), red_team, overall
"""

from typing import Any, Dict, Optional

from .overall_eval import calculate_overall_grade
from ai.ai_analysis import (
    generate_ai_analysis,
    generate_news_summary,
    generate_buffett_checklist,
    generate_moat_analysis,
    generate_brand_analysis,
    generate_management_analysis,
    generate_red_team_analysis,
    generate_news_confirmation_points,
)


def _safe_ai(fn, *args):
    """Call an AI analysis function safely. Never raises."""
    try:
        return fn(*args)
    except Exception:
        return None


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
    Run every analysis at once (Sprint18).

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

    # Overall verdict - ONLY overall_eval decides BUY / WATCH / PASS
    bundle["overall"] = calculate_overall_grade(
        score_result=score_result,
        dcf_result=dcf_result,
        moat=bundle["moat"] or {},
        brand=bundle["brand"] or {},
        mgmt=bundle["mgmt"] or {},
        red_team=bundle["red_team"] or {},
    )

    return bundle