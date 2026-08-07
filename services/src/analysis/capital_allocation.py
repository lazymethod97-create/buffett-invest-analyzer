"""capital_allocation.py (Sprint22) Capital Allocation分析モジュール。共通形式で返す。"""

from typing import Dict, Any, Optional
from engines.capital_allocation_engine import calculate_capital_allocation


def analyze_capital_allocation(
    data: Dict[str, Any],
    roic_result: Optional[Dict[str, Any]] = None,
    owner_earnings_result: Optional[Dict[str, Any]] = None,
    intrinsic_value_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Capital Allocation分析を実行し、共通形式で返す。

    ROIC / Owner Earnings / Intrinsic Value のエンジン結果を再利用する
    （重複実装禁止・ルール14）。
    """
    engine_result = calculate_capital_allocation(
        data,
        roic_result=roic_result,
        owner_earnings_result=owner_earnings_result,
        intrinsic_value_result=intrinsic_value_result,
    )

    total_score = engine_result.get("total_score", 0)
    rating = engine_result.get("rating", "unknown")

    details = []
    details.append({
        "item": "再投資効率（ROIC基準）",
        "value": f"{engine_result.get('reinvestment_score', 0)} / 4点",
        "score": engine_result.get("reinvestment_score", 0),
        "max_score": 4,
        "passed": engine_result.get("reinvestment_score", 0) >= 2,
        "comment": engine_result.get("reinvestment_detail", ""),
    })
    details.append({
        "item": "株主還元の規律（配当性向）",
        "value": f"{engine_result.get('payout_score', 0)} / 3点",
        "score": engine_result.get("payout_score", 0),
        "max_score": 3,
        "passed": engine_result.get("payout_score", 0) >= 2,
        "comment": engine_result.get("payout_detail", ""),
    })
    details.append({
        "item": "自社株買いのタイミング（MOSとの突合）",
        "value": f"{engine_result.get('buyback_score', 0)} / 3点",
        "score": engine_result.get("buyback_score", 0),
        "max_score": 3,
        "passed": engine_result.get("buyback_score", 0) >= 2,
        "comment": engine_result.get("buyback_detail", ""),
    })

    warnings = list(engine_result.get("warnings", []))

    return {
        "id": "capital_allocation",
        "title": "Capital Allocation（資本配分）分析",
        "score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }
