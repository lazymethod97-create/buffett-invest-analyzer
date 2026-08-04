"""intrinsic_value.py (Sprint21) Intrinsic Value分析モジュール。共通形式で返す。"""

from typing import Dict, Any
from engines.intrinsic_engine import calculate_intrinsic_value


def analyze_intrinsic_value(data: Dict[str, Any], dcf_result: Dict[str, Any] = None) -> Dict[str, Any]:
    """Intrinsic Value分析を実行し、共通形式で返す。"""
    engine_result = calculate_intrinsic_value(data, dcf_result=dcf_result or {})

    mosp = engine_result.get("margin_of_safety_pct")
    rating = engine_result.get("rating", "unknown")

    if mosp is not None:
        if mosp >= 30:
            score = 15
        elif mosp >= 15:
            score = 12
        elif mosp >= 0:
            score = 8
        elif mosp >= -20:
            score = 4
        else:
            score = 0
    else:
        score = 0

    details = []
    consensus = engine_result.get("consensus_intrinsic_value_per_share")
    current_price = engine_result.get("current_price")

    if consensus is not None:
        details.append({
            "item": "コンセンサス内在価値（1株）",
            "value": f"{consensus:,.2f}",
            "score": score,
            "max_score": 15,
            "passed": mosp is not None and mosp >= 0,
            "comment": engine_result.get("summary", ""),
        })
    else:
        details.append({
            "item": "コンセンサス内在価値（1株）",
            "value": "データ不足",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "comment": engine_result.get("error", "データ不足"),
        })

    if current_price is not None:
        details.append({
            "item": "現在株価",
            "value": f"{current_price:,.2f}",
            "score": 0, "max_score": 0,
            "passed": True,
            "comment": "比較対象",
        })

    if mosp is not None:
        details.append({
            "item": "安全余裕（Margin of Safety）",
            "value": f"{mosp:+.1f}%",
            "score": 0, "max_score": 0,
            "passed": mosp >= 0,
            "comment": engine_result.get("verdict", ""),
        })

    for est in engine_result.get("estimates", []):
        est_value = est.get("value", 0)
        details.append({
            "item": est.get("label", est.get("method", "")),
            "value": f"{est_value:,.2f}",
            "score": 0, "max_score": 0,
            "passed": current_price is not None and est_value > current_price,
            "comment": est.get("detail", ""),
        })

    warnings = list(engine_result.get("warnings", []))
    if mosp is not None and mosp < 0:
        warnings.append("安全余裕がありません。価格が内在価値を上回っています。")

    return {
        "id": "intrinsic_value",
        "title": "Intrinsic Value（内在価値）分析",
        "score": score,
        "max_score": 15,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }
