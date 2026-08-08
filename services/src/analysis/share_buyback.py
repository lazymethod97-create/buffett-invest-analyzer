"""share_buyback.py (Sprint23) Share Buyback（自社株買い）分析モジュール。共通形式で返す。"""

from typing import Dict, Any
from engines.share_buyback_engine import calculate_share_buyback


def analyze_share_buyback(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Share Buyback分析を実行し、共通形式で返す。

    Capital Allocation（Sprint22）とは異なる評価軸（複数年の一貫性・
    株式数減少効果・財務健全性とのバランス・PER水準比較）で、
    自社株買いそのものの質・効果を評価する（重複実装禁止・ルール14）。
    """
    engine_result = calculate_share_buyback(data)

    total_score = engine_result.get("total_score", 0)
    rating = engine_result.get("rating", "unknown")

    details = []
    details.append({
        "item": "買い入れの一貫性",
        "value": f"{engine_result.get('consistency_score', 0)} / 3点",
        "score": engine_result.get("consistency_score", 0),
        "max_score": 3,
        "passed": engine_result.get("consistency_score", 0) >= 2,
        "comment": engine_result.get("consistency_detail", ""),
    })
    details.append({
        "item": "発行済株式数の減少効果",
        "value": f"{engine_result.get('reduction_score', 0)} / 3点",
        "score": engine_result.get("reduction_score", 0),
        "max_score": 3,
        "passed": engine_result.get("reduction_score", 0) >= 2,
        "comment": engine_result.get("reduction_detail", ""),
    })
    details.append({
        "item": "財務健全性とのバランス",
        "value": f"{engine_result.get('balance_score', 0)} / 2点",
        "score": engine_result.get("balance_score", 0),
        "max_score": 2,
        "passed": engine_result.get("balance_score", 0) >= 1,
        "comment": engine_result.get("balance_detail", ""),
    })
    details.append({
        "item": "買い入れの効果的なタイミング（PER水準）",
        "value": f"{engine_result.get('timing_score', 0)} / 2点",
        "score": engine_result.get("timing_score", 0),
        "max_score": 2,
        "passed": engine_result.get("timing_score", 0) >= 1,
        "comment": engine_result.get("timing_detail", ""),
    })

    warnings = list(engine_result.get("warnings", []))

    return {
        "id": "share_buyback",
        "title": "Share Buyback（自社株買い）分析",
        "score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }
