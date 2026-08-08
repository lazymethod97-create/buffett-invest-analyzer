"""debt_quality.py (Sprint24) Debt Quality（負債の質）分析モジュール。共通形式で返す。"""

from typing import Dict, Any
from engines.debt_quality_engine import calculate_debt_quality


def analyze_debt_quality(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Debt Quality分析を実行し、共通形式で返す。

    ROIC（投下資本に総負債を使用）、Capital Allocation（財務健全性の一部評価）、
    Share Buyback（total_debt_historyで負債推移を評価済み）とは異なる評価軸
    （D/E・Debt/EBITDA水準、インタレスト・カバレッジ・レシオ、短期負債依存度、
    負債推移の年平均変化率）で、負債の返済能力・構成・リスクを評価する
    （重複実装禁止・ルール14）。
    """
    engine_result = calculate_debt_quality(data)

    total_score = engine_result.get("total_score", 0)
    rating = engine_result.get("rating", "unknown")

    details = []
    details.append({
        "item": "負債水準の適正さ（D/E・Debt/EBITDA）",
        "value": f"{engine_result.get('level_score', 0)} / 3点",
        "score": engine_result.get("level_score", 0),
        "max_score": 3,
        "passed": engine_result.get("level_score", 0) >= 2,
        "comment": engine_result.get("level_detail", ""),
    })
    details.append({
        "item": "金利負担能力（インタレスト・カバレッジ・レシオ）",
        "value": f"{engine_result.get('coverage_score', 0)} / 3点",
        "score": engine_result.get("coverage_score", 0),
        "max_score": 3,
        "passed": engine_result.get("coverage_score", 0) >= 2,
        "comment": engine_result.get("coverage_detail", ""),
    })
    details.append({
        "item": "負債の質・構成（短期負債比率）",
        "value": f"{engine_result.get('composition_score', 0)} / 2点",
        "score": engine_result.get("composition_score", 0),
        "max_score": 2,
        "passed": engine_result.get("composition_score", 0) >= 1,
        "comment": engine_result.get("composition_detail", ""),
    })
    details.append({
        "item": "負債推移のトレンド",
        "value": f"{engine_result.get('trend_score', 0)} / 2点",
        "score": engine_result.get("trend_score", 0),
        "max_score": 2,
        "passed": engine_result.get("trend_score", 0) >= 1,
        "comment": engine_result.get("trend_detail", ""),
    })

    warnings = list(engine_result.get("warnings", []))

    return {
        "id": "debt_quality",
        "title": "Debt Quality（負債の質）分析",
        "score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }
