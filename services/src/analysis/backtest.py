"""backtest.py (Sprint26) Backtest（簡易品質スコア × フォワードリターン検証）分析モジュール。共通形式で返す。"""

from typing import Dict, Any, Optional
from engines.backtest_engine import calculate_backtest


def analyze_backtest(data: Dict[str, Any], score_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Backtest分析を実行し、共通形式で返す。

    「過去のBuffett Score（総合判定）が高かった時点で買っていたら、実際のリターンは
    どうだったか」を検証する。フルのBuffett Score（DCF・AI定性MOAT判定・Red Team等を
    含む190点満点）を過去の任意時点で再計算することは事実上不可能なため、Sprint23〜25で
    取得済みの複数年データから算出する簡易品質スコア代理指標を用いる（重複実装禁止・
    ルール14。既存のscoring_engine.pyは再利用のみ）。
    """
    engine_result = calculate_backtest(data, score_result=score_result)

    total_score = engine_result.get("total_score", 0)
    rating = engine_result.get("rating", "unknown")

    details = []
    details.append({
        "item": "高品質年 vs 低品質年のリターン差検証",
        "value": f"{engine_result.get('edge_score', 0)} / 3点",
        "score": engine_result.get("edge_score", 0),
        "max_score": 3,
        "passed": engine_result.get("edge_score", 0) >= 2,
        "comment": engine_result.get("edge_detail", ""),
    })
    details.append({
        "item": "最高品質期間の実績リターン",
        "value": f"{engine_result.get('best_period_score', 0)} / 3点",
        "score": engine_result.get("best_period_score", 0),
        "max_score": 3,
        "passed": engine_result.get("best_period_score", 0) >= 2,
        "comment": engine_result.get("best_period_detail", ""),
    })
    details.append({
        "item": "一貫性（品質スコアとリターンの相関）",
        "value": f"{engine_result.get('consistency_score', 0)} / 2点",
        "score": engine_result.get("consistency_score", 0),
        "max_score": 2,
        "passed": engine_result.get("consistency_score", 0) >= 1,
        "comment": engine_result.get("consistency_detail", ""),
    })
    details.append({
        "item": "現在のBuffett Scoreとの整合性",
        "value": f"{engine_result.get('current_consistency_score', 0)} / 2点",
        "score": engine_result.get("current_consistency_score", 0),
        "max_score": 2,
        "passed": engine_result.get("current_consistency_score", 0) >= 1,
        "comment": engine_result.get("current_consistency_detail", ""),
    })

    warnings = list(engine_result.get("warnings", []))

    return {
        "id": "backtest",
        "title": "Backtest（簡易品質スコア × フォワードリターン検証）分析",
        "score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": engine_result,
    }
