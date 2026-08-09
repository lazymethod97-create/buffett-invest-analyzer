"""
watchlist_insights.py (Sprint28)
Watchlist Insights（ウォッチリスト横断の集計・ランキング表示）モジュール。

Sprint27のPortfolio Riskと同様、複数銘柄（ウォッチリスト登録銘柄全体）を
評価単位とするため、analysis_bundle.py / overall_eval.py（単一銘柄の
190点満点スコア・BUY/WATCH/PASS判定）には組み込まない、独立した分析として
実装する（設計判断の詳細はdocs/AI_HANDOVER.mdのSprint28セクションを参照）。

Portfolio Riskとの違い：Portfolio Riskは10点満点のスコア・ratingを持つ
「共通形式」（PROJECT_RULES.md Rule 12: id/title/score/max_score/rating/
summary/details/warnings）で結果を返すが、Watchlist Insightsは得点化を
行わない（Sprint28で得点化しないことをきたと確認済み）。そのため本モジュールは
共通形式には従わず、集計・ランキングのための専用の戻り値形式を返す。
scoring_engine.pyのような「エンジン」も持たない（数値計算は単純なソート・
差分%計算のみのため、engines/には切り出さず本モジュール内で完結させる）。
"""

from typing import Dict, Any, List, Optional


def build_watchlist_insights(
    watchlist_rows: List[Dict[str, Any]],
    portfolio_rows: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    ウォッチリスト登録銘柄を横断した集計・ランキングを構築する。

    引数
    ----
    watchlist_rows: app.py「👀 ウォッチリスト」で既に構築済みの一覧。
        [{"item": WatchListItem, "data": dict|None,
          "score_result": dict|None, "error": str|None}, ...]
        既存のcached_get_stock_data / calculate_buffett_scoreの結果を
        そのまま再利用する（新規のデータ取得・スコア計算は行わない。ルール14）。
    portfolio_rows: app.py「💼 Portfolio」タブで既に構築済みの一覧
        （Portfolio Riskと同一形式）。保有銘柄とのセクター重複の参考表示にのみ
        使用する（省略時は重複表示なしで動作する）。

    戻り値
    ----
    success: bool（ウォッチリストが空、または有効データが1件もない場合False寄りだが、
        「空」と「データ取得失敗のみ」は区別する。空の場合のみFalse）
    watchlist_count / valid_count / error_count: 件数
    target_price_ranking: 目標株価を設定した銘柄を、到達までの差分%昇順
        （到達済み＝マイナス値が先頭）でソートしたリスト
    no_target_count: 目標株価が未設定の銘柄数
    score_ranking: Buffett Scoreの高い順にソートしたリスト
    sector_overlap: セクターごとのウォッチリスト件数／Portfolio件数の単純集計
        （Portfolio Riskのような時価評価額加重・HHIは計算しない、件数ベースの
        簡易参考表示にとどめる）
    warnings: 注意事項のリスト
    summary: 一行サマリー文字列
    """
    portfolio_rows = portfolio_rows or []
    warnings: List[str] = []

    watchlist_count = len(watchlist_rows)

    if watchlist_count == 0:
        return {
            "success": False,
            "watchlist_count": 0,
            "valid_count": 0,
            "error_count": 0,
            "target_price_ranking": [],
            "no_target_count": 0,
            "score_ranking": [],
            "sector_overlap": [],
            "warnings": [],
            "summary": "ウォッチリストに銘柄が登録されていないため、集計できません。",
        }

    valid_rows = [r for r in watchlist_rows if r.get("data") and not r.get("error")]
    error_count = watchlist_count - len(valid_rows)
    if error_count > 0:
        warnings.append(f"データを取得できなかった{error_count}銘柄は集計から除外されています。")

    # --- 目標株価接近度ランキング ---
    target_ranking: List[Dict[str, Any]] = []
    no_target_count = 0
    for row in valid_rows:
        item = row["item"]
        data = row["data"]
        target_price = getattr(item, "target_price", None)
        if not target_price or target_price <= 0:
            no_target_count += 1
            continue
        current_price = data.get("current_price", 0) or 0
        diff_pct = (
            (current_price - target_price) / target_price * 100
            if target_price > 0
            else None
        )
        target_ranking.append(
            {
                "ticker": getattr(item, "ticker", ""),
                "company_name": data.get("company_name") or getattr(item, "ticker", ""),
                "current_price": current_price,
                "target_price": target_price,
                "diff_pct": diff_pct,
                "reached": current_price <= target_price,
                "currency": "¥" if data.get("country") == "Japan" else "$",
            }
        )
    target_ranking.sort(
        key=lambda x: (x["diff_pct"] if x["diff_pct"] is not None else float("inf"))
    )

    # --- ウォッチリスト内Buffett Scoreランキング ---
    score_ranking: List[Dict[str, Any]] = []
    for row in valid_rows:
        item = row["item"]
        data = row["data"]
        score_result = row.get("score_result")
        if not score_result:
            continue
        score_ranking.append(
            {
                "ticker": getattr(item, "ticker", ""),
                "company_name": data.get("company_name") or getattr(item, "ticker", ""),
                "score": score_result.get("total_score", 0),
                "max_score": score_result.get("max_score", 0),
                "verdict": score_result.get("verdict", ""),
            }
        )
    score_ranking.sort(key=lambda x: x["score"], reverse=True)

    # --- Portfolioとの重複・セクター構成 参考表示（単純な件数集計） ---
    # Portfolio Riskのような時価評価額加重のHHI計算は行わない。あくまで
    # 「同じセクターの銘柄が両方にどれだけあるか」の簡易な件数集計にとどめる。
    watchlist_sector_counts: Dict[str, int] = {}
    for row in valid_rows:
        sector = row["data"].get("sector") or "不明"
        watchlist_sector_counts[sector] = watchlist_sector_counts.get(sector, 0) + 1

    portfolio_sector_counts: Dict[str, int] = {}
    for row in portfolio_rows:
        data = row.get("data")
        if not data:
            continue
        sector = data.get("sector") or "不明"
        portfolio_sector_counts[sector] = portfolio_sector_counts.get(sector, 0) + 1

    all_sectors = sorted(set(watchlist_sector_counts) | set(portfolio_sector_counts))
    sector_overlap: List[Dict[str, Any]] = []
    for sector in all_sectors:
        w_count = watchlist_sector_counts.get(sector, 0)
        p_count = portfolio_sector_counts.get(sector, 0)
        sector_overlap.append(
            {
                "sector": sector,
                "watchlist_count": w_count,
                "portfolio_count": p_count,
                "overlap": w_count > 0 and p_count > 0,
            }
        )
    sector_overlap.sort(
        key=lambda x: (x["watchlist_count"] + x["portfolio_count"]), reverse=True
    )

    overlapping_sectors = [s["sector"] for s in sector_overlap if s["overlap"]]
    if overlapping_sectors:
        warnings.append(
            "保有銘柄（Portfolio）と同じセクター（"
            + "、".join(overlapping_sectors)
            + "）の銘柄がウォッチリストに含まれています。"
        )

    summary_parts = [f"ウォッチリスト登録銘柄数: {watchlist_count}銘柄"]
    if error_count:
        summary_parts.append(f"データ取得エラー: {error_count}件")
    if target_ranking:
        reached = sum(1 for t in target_ranking if t["reached"])
        summary_parts.append(f"目標株価到達済み: {reached}/{len(target_ranking)}件")

    return {
        "success": True,
        "watchlist_count": watchlist_count,
        "valid_count": len(valid_rows),
        "error_count": error_count,
        "target_price_ranking": target_ranking,
        "no_target_count": no_target_count,
        "score_ranking": score_ranking,
        "sector_overlap": sector_overlap,
        "warnings": warnings,
        "summary": "　/　".join(summary_parts),
    }
