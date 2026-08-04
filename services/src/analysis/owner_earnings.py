"""owner_earnings.py (Sprint20) Owner Earnings分析モジュール。共通形式で返す。"""

from typing import Dict, Any
from engines.owner_earnings_engine import calculate_owner_earnings


def analyze_owner_earnings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Owner Earnings分析を実行し、共通形式で返す。"""
    engine_result = calculate_owner_earnings(data)
    oe = engine_result.get("owner_earnings")
    oe_yield = engine_result.get("owner_earnings_yield")
    rating = engine_result.get("rating", "unknown")

    if oe_yield is not None:
        if oe_yield >= 0.08:
            score = 10
        elif oe_yield >= 0.05:
            score = 8
        elif oe_yield >= 0.03:
            score = 5
        elif oe_yield >= 0.0:
            score = 2
        else:
            score = 0
    else:
        score = 0

    details = []
    if oe is not None:
        details.append({
            "item": "Owner Earnings（オーナーアーニングス）",
            "value": f"{oe:,.0f}",
            "score": score,
            "max_score": 10,
            "passed": oe > 0,
            "comment": engine_result.get("summary", ""),
        })
    else:
        details.append({
            "item": "Owner Earnings（オーナーアーニングス）",
            "value": "データ不足",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "comment": engine_result.get("summary", "データ不足"),
        })

    if oe_yield is not None:
        details.append({
            "item": "Owner Earnings利回り",
            "value": f"{oe_yield*100:.1f}%",
            "score": 0, "max_score": 0,
            "passed": oe_yield >= 0.05,
            "comment": "時価総額に対するOwner Earningsの割合",
        })
    else:
        details.append({
            "item": "Owner Earnings利回り",
            "value": "データ不足",
            "score": 0, "max_score": 0,
            "passed": False, "comment": "データ不足",
        })

    da = engine_result.get("depreciation_amortization")
    details.append({
        "item": "減価償却費等（D&A、推定）",
        "value": f"{da:,.0f}" if da is not None else "データ不足（0として計算）",
        "score": 0, "max_score": 0,
        "passed": da is not None,
        "comment": "EBITDA − 営業利益から推定",
    })

    capex = engine_result.get("capital_expenditures")
    details.append({
        "item": "設備投資（CapEx、推定）",
        "value": f"{capex:,.0f}" if capex is not None else "データ不足（0として計算）",
        "score": 0, "max_score": 0,
        "passed": capex is not None,
        "comment": "営業キャッシュフロー − フリーキャッシュフローから推定",
    })

    warnings = list(engine_result.get("warnings", []))
    if oe_yield is not None and 0 <= oe_yield < 0.03:
        warnings.append("Owner Earnings利回りが3%未満。実質的な現金創出力が弱い可能性があります。")
    elif oe is not None and oe < 0:
        warnings.append("Owner Earningsがマイナスです。会計上の利益と実際のキャッシュ創出力が乖離している可能性があります。")

    return {
        "id": "owner_earnings",
        "title": "Owner Earnings（オーナーアーニングス）分析",
        "score": score,
        "max_score": 10,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }

