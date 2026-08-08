"""moat_strength.py (Sprint25) Economic Moat強化（経済的堀の定量的検証）分析モジュール。共通形式で返す。"""

from typing import Dict, Any, Optional
from engines.moat_strength_engine import calculate_moat_strength


def analyze_moat_strength(data: Dict[str, Any], moat_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Economic Moat強化分析を実行し、共通形式で返す。

    既存のMOAT定性判定（Sprint18、generate_moat_analysis）は単年の断面データに
    基づくAI判定のみで、複数年のルールベース検証が存在しない。本分析は、
    ROE・営業利益率・粗利率・売上高の複数年推移から、moatの定量的な裏付けを
    独立して検証する（重複実装禁止・ルール14）。既存MOAT判定（moat_result）は
    整合性チェックの引数として受け取るのみで、再計算はしない。
    """
    engine_result = calculate_moat_strength(data, moat_result=moat_result)

    total_score = engine_result.get("total_score", 0)
    rating = engine_result.get("rating", "unknown")

    details = []
    details.append({
        "item": "収益性の持続性・安定性（ROE・営業利益率）",
        "value": f"{engine_result.get('persistence_score', 0)} / 3点",
        "score": engine_result.get("persistence_score", 0),
        "max_score": 3,
        "passed": engine_result.get("persistence_score", 0) >= 2,
        "comment": engine_result.get("persistence_detail", ""),
    })
    details.append({
        "item": "価格決定力の定量的検証（粗利率の防衛力）",
        "value": f"{engine_result.get('pricing_power_score', 0)} / 3点",
        "score": engine_result.get("pricing_power_score", 0),
        "max_score": 3,
        "passed": engine_result.get("pricing_power_score", 0) >= 2,
        "comment": engine_result.get("pricing_power_detail", ""),
    })
    details.append({
        "item": "市場地位の安定性（売上高成長率のブレ幅）",
        "value": f"{engine_result.get('market_position_score', 0)} / 2点",
        "score": engine_result.get("market_position_score", 0),
        "max_score": 2,
        "passed": engine_result.get("market_position_score", 0) >= 1,
        "comment": engine_result.get("market_position_detail", ""),
    })
    details.append({
        "item": "既存MOAT判定との整合性",
        "value": f"{engine_result.get('consistency_score', 0)} / 2点",
        "score": engine_result.get("consistency_score", 0),
        "max_score": 2,
        "passed": engine_result.get("consistency_score", 0) >= 1,
        "comment": engine_result.get("consistency_detail", ""),
    })

    warnings = list(engine_result.get("warnings", []))

    return {
        "id": "moat_strength",
        "title": "Economic Moat強化（経済的堀の定量的検証）分析",
        "score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }
