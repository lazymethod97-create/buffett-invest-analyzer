"""roic.py (Sprint19) ROIC分析モジュール。共通形式で返す。"""

from typing import Dict, Any
from engines.roic_engine import calculate_roic


def analyze_roic(data: Dict[str, Any]) -> Dict[str, Any]:
    """ROIC分析を実行し、共通形式で返す。"""
    engine_result = calculate_roic(data)
    roic = engine_result.get("roic")

    if roic is not None:
        if roic >= 0.20:
            score = 15
            rating = "excellent"
        elif roic >= 0.15:
            score = 12
            rating = "good"
        elif roic >= 0.10:
            score = 8
            rating = "average"
        elif roic >= 0.05:
            score = 4
            rating = "below_average"
        else:
            score = 0
            rating = "poor"
    else:
        score = 0
        rating = "unknown"

    details = []
    if roic is not None:
        details.append({
            "item": "ROIC（投下資本利益率）",
            "value": f"{roic*100:.1f}%",
            "score": score,
            "max_score": 15,
            "passed": roic >= 0.10,
            "comment": engine_result.get("summary", ""),
        })
    else:
        details.append({
            "item": "ROIC（投下資本利益率）",
            "value": "データ不足",
            "score": 0,
            "max_score": 15,
            "passed": False,
            "comment": engine_result.get("summary", "データ不足"),
        })

    nopat = engine_result.get("nopat")
    if nopat is not None:
        details.append({
            "item": "NOPAT（税引後営業利益）",
            "value": f"{nopat:,.0f}",
            "score": 0, "max_score": 0,
            "passed": nopat > 0,
            "comment": "本業の税引後利益",
        })
    else:
        details.append({
            "item": "NOPAT（税引後営業利益）",
            "value": "データ不足",
            "score": 0, "max_score": 0,
            "passed": False, "comment": "データ不足",
        })

    ic = engine_result.get("invested_capital")
    if ic is not None:
        details.append({
            "item": "投下資本",
            "value": f"{ic:,.0f}",
            "score": 0, "max_score": 0,
            "passed": ic > 0,
            "comment": "純資産+総負債-現金同等物",
        })
    else:
        details.append({
            "item": "投下資本",
            "value": "データ不足",
            "score": 0, "max_score": 0,
            "passed": False, "comment": "データ不足",
        })

    tax_rate = engine_result.get("tax_rate", 0.25)
    details.append({
        "item": "実効税率",
        "value": f"{tax_rate*100:.1f}%",
        "score": 0, "max_score": 0,
        "passed": True,
        "comment": "NOPAT計算に使用",
    })

    warnings = []
    if roic is not None:
        if roic < 0.10:
            warnings.append("ROICが10%未満。資本効率に改善の余地があります。")
        elif 0.10 <= roic < 0.15:
            warnings.append("ROICは10%以上ですが、バフェット基準(15%以上)には届いていません。")

    return {
        "id": "roic",
        "title": "ROIC（投下資本利益率）分析",
        "score": score,
        "max_score": 15,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }
