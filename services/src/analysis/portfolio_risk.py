"""
portfolio_risk.py (Sprint27)
Portfolio Risk（保有ポートフォリオのリスク分散評価）分析モジュール。共通形式で返す。

既存の単一銘柄向け分析（analysis_bundle.py経由でcreate_analysis_bundle()から
呼ばれるもの）とは異なり、複数銘柄からなるポートフォリオ全体を評価単位とするため、
analysis_bundle.py / overall_eval.py（単一銘柄のBUY/WATCH/PASS判定）には
組み込まない、独立したエントリポイントとする（設計判断の詳細はdocs/AI_HANDOVER.md
のSprint27セクションを参照）。
"""

from typing import Dict, Any, List, Optional

from engines.portfolio_risk_engine import calculate_portfolio_risk
from .analysis_bundle import _safe_ai, _merge_ai_narrative


def analyze_portfolio_risk(
    portfolio_rows: List[Dict[str, Any]],
    generate_ai_narrative: bool = False,
) -> Dict[str, Any]:
    """
    Portfolio Risk分析を実行し、共通形式で返す。

    引数
    ----
    portfolio_rows: app.py「💼 Portfolio」タブで既に構築済みの一覧。
        [{"holding": PortfolioHolding, "data": dict|None,
          "score_result": dict|None, "error": str|None}, ...]
        data / score_resultは既存のcached_get_stock_data /
        scoring_engine.calculate_buffett_scoreの戻り値をそのまま再利用する
        （新規のデータ取得・スコア再計算は行わない。ルール14）。
    generate_ai_narrative: TrueのときのみGeminiを呼び出し、AI考察を追加する
        （Portfolioタブは頻繁に再描画されるため、既存のフルモード等と同様に
        Gemini呼び出しは明示的なトリガー時のみに限定する）。
    """
    holdings_for_engine = []
    for row in portfolio_rows:
        h = row.get("holding")
        data = row.get("data")
        if not h or not data:
            continue
        holdings_for_engine.append({
            "ticker": getattr(h, "ticker", ""),
            "company_name": data.get("company_name") or getattr(h, "ticker", ""),
            "shares": getattr(h, "shares", 0),
            "current_price": data.get("current_price", 0),
            "sector": data.get("sector"),
            "country": data.get("country"),
        })

    engine_result = calculate_portfolio_risk(holdings_for_engine)

    total_score = engine_result.get("total_score", 0)
    rating = engine_result.get("rating", "no_data")

    details = []
    if engine_result.get("success"):
        details.append({
            "item": "セクター分散度",
            "value": f"{engine_result.get('sector_score', 0)} / 3点",
            "score": engine_result.get("sector_score", 0),
            "max_score": 3,
            "passed": engine_result.get("sector_score", 0) >= 2,
            "comment": engine_result.get("sector_detail", ""),
        })
        details.append({
            "item": "銘柄集中度",
            "value": f"{engine_result.get('concentration_score', 0)} / 3点",
            "score": engine_result.get("concentration_score", 0),
            "max_score": 3,
            "passed": engine_result.get("concentration_score", 0) >= 2,
            "comment": engine_result.get("concentration_detail", ""),
        })
        details.append({
            "item": "地域分散度",
            "value": f"{engine_result.get('region_score', 0)} / 2点",
            "score": engine_result.get("region_score", 0),
            "max_score": 2,
            "passed": engine_result.get("region_score", 0) >= 1,
            "comment": engine_result.get("region_detail", ""),
        })
        details.append({
            "item": "保有銘柄数の充足度",
            "value": f"{engine_result.get('count_score', 0)} / 2点",
            "score": engine_result.get("count_score", 0),
            "max_score": 2,
            "passed": engine_result.get("count_score", 0) >= 1,
            "comment": engine_result.get("count_detail", ""),
        })

    warnings = list(engine_result.get("warnings", []))
    raw: Dict[str, Any] = dict(engine_result)

    ####################################################
    # 参考情報: 保有銘柄の加重平均Buffett Score
    # Portfolio Riskスコア（10点満点のリスク分散評価）そのものには含めない、
    # あくまで参考値として画面・PDFに表示する。既存のscore_result
    # （scoring_engine.calculate_buffett_score、app.py側で計算済み）を
    # 再利用するのみで、新たなスコア計算は行わない（ルール14）。
    ####################################################
    weighted_numer = 0.0
    weighted_denom = 0.0
    buffett_max_score = None
    for row in portfolio_rows:
        h = row.get("holding")
        data = row.get("data")
        score_result = row.get("score_result")
        if not h or not data or not score_result:
            continue
        mv = (getattr(h, "shares", 0) or 0) * (data.get("current_price", 0) or 0)
        if mv <= 0:
            continue
        weighted_numer += mv * score_result.get("total_score", 0)
        weighted_denom += mv
        if buffett_max_score is None:
            buffett_max_score = score_result.get("max_score")

    raw["weighted_avg_buffett_score"] = (
        (weighted_numer / weighted_denom) if weighted_denom > 0 else None
    )
    raw["weighted_avg_buffett_max_score"] = buffett_max_score

    result: Dict[str, Any] = {
        "id": "portfolio_risk",
        "title": "Portfolio Risk（保有ポートフォリオのリスク分散評価）分析",
        "score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": engine_result.get("summary", "データ不足"),
        "details": details,
        "warnings": warnings,
        "raw": raw,
    }

    if generate_ai_narrative and engine_result.get("success"):
        from ai.ai_analysis import generate_portfolio_risk_analysis
        ai_result = _safe_ai(generate_portfolio_risk_analysis, engine_result)
        result = _merge_ai_narrative(result, ai_result)

    return result
