"""
Debt Quality（負債の質）計算エンジン（Sprint24）

既存のROIC分析（投下資本に総負債を使用）、Capital Allocation分析（財務健全性の
一部評価）、Share Buyback分析（total_debt_historyで負債推移を取得済み）とは
異なる切り口で、負債の返済能力・構成・リスクを独立して深掘りする。
負債の「量」（Share Buybackで評価済み）ではなく「質」を評価する。

評価軸（4観点、合計10点）
1. 負債水準の適正さ（Level）: 3点
   Debt/Equity比率、Debt/EBITDA倍率が過大でないか（厳しい方の水準を採用）
2. 金利負担能力（Coverage）: 3点
   インタレスト・カバレッジ・レシオ（営業利益 ÷ 支払利息）が十分な余裕を持っているか
3. 負債の質・構成（Composition）: 2点
   短期負債への依存度（借り換えリスク）
4. 負債推移のトレンド（Trend）: 2点
   直近数年の負債の年平均増減率（Sprint23で取得済みのtotal_debt_historyを再利用）
   ※Share Buyback（Sprint23）の財務健全性バランス軸は「自社株買いと負債増の
     同時発生」を見る単純な始点・終点比較だが、本軸は自社株買いと無関係に
     負債推移そのものの年平均変化率を独立して評価する点で異なる（重複実装禁止・ルール14）。

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any, List, Optional


def calculate_debt_quality(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    負債の返済能力・構成・リスクを評価する。

    引数
    ----
    data: get_stock_data() が返す企業データ辞書
          debt_to_equity, total_debt, ebitda, operating_income（またはebit）,
          interest_expense, long_term_debt, short_term_debt,
          total_debt_history（Sprint23で追加済み）を使用する。

    戻り値
    ----
    success=True, level_score, coverage_score, composition_score, trend_score,
    total_score, rating, summary, verdict
    """
    debt_to_equity = data.get("debt_to_equity")
    total_debt = data.get("total_debt")
    ebitda = data.get("ebitda")
    operating_income = data.get("operating_income") or data.get("ebit")
    interest_expense = data.get("interest_expense")
    long_term_debt = data.get("long_term_debt")
    short_term_debt = data.get("short_term_debt")
    debt_history: List[float] = data.get("total_debt_history") or []

    # yfinanceが%表記（150.0など）で返す場合があるため補正（scoring_engineと同じ規則）
    de = debt_to_equity
    if de is not None and de > 100:
        de = de / 100

    debt_free = total_debt is not None and total_debt <= 0

    # --- 軸1: 負債水準の適正さ（3点）---
    def _de_tier(v: Optional[float]) -> Optional[int]:
        if v is None:
            return None
        if v <= 0.5:
            return 3
        elif v <= 1.0:
            return 2
        elif v <= 2.0:
            return 1
        return 0

    def _debt_ebitda_tier(v: Optional[float]) -> Optional[int]:
        if v is None:
            return None
        if v <= 1.5:
            return 3
        elif v <= 3.0:
            return 2
        elif v <= 5.0:
            return 1
        return 0

    debt_ebitda = None
    if total_debt is not None and ebitda and ebitda > 0:
        debt_ebitda = total_debt / ebitda

    level_score = 1
    level_detail = ""
    if debt_free:
        level_score = 3
        level_detail = "実質無借金経営であり、負債水準は極めて健全です。"
    else:
        de_tier = _de_tier(de)
        eb_tier = _debt_ebitda_tier(debt_ebitda)
        tiers = [t for t in (de_tier, eb_tier) if t is not None]
        if tiers:
            # 厳しい方（より低い評価）を採用し、保守的に評価する
            level_score = min(tiers)
            parts = []
            if de is not None:
                parts.append(f"D/E比率 {de:.2f}倍")
            if debt_ebitda is not None:
                parts.append(f"Debt/EBITDA {debt_ebitda:.2f}倍")
            level_detail = "、".join(parts) + f"。負債水準は{'健全' if level_score >= 2 else 'やや過大' if level_score == 1 else '過大'}な水準です。"
        else:
            level_detail = "D/E比率・Debt/EBITDA倍率のいずれも算出できるデータが不足しているため、負債水準を評価できません（中立評価）。"

    # --- 軸2: 金利負担能力（3点）---
    coverage_score = 1
    coverage_detail = ""
    interest_coverage_ratio = None
    if debt_free:
        coverage_score = 3
        coverage_detail = "実質無借金経営であり、金利負担リスクはありません。"
    elif operating_income is not None and interest_expense is not None and interest_expense > 0:
        interest_coverage_ratio = operating_income / interest_expense
        if interest_coverage_ratio >= 10:
            coverage_score = 3
            coverage_detail = f"インタレスト・カバレッジ・レシオは{interest_coverage_ratio:.1f}倍と極めて高く、金利負担に十分な余裕があります。"
        elif interest_coverage_ratio >= 5:
            coverage_score = 2
            coverage_detail = f"インタレスト・カバレッジ・レシオは{interest_coverage_ratio:.1f}倍と良好で、金利負担能力は十分です。"
        elif interest_coverage_ratio >= 2:
            coverage_score = 1
            coverage_detail = f"インタレスト・カバレッジ・レシオは{interest_coverage_ratio:.1f}倍とやや低く、金利負担余力に注意が必要です。"
        else:
            coverage_score = 0
            coverage_detail = f"インタレスト・カバレッジ・レシオは{interest_coverage_ratio:.1f}倍と低く、金利負担能力に懸念があります。"
    else:
        coverage_detail = "支払利息または営業利益のデータが不足しているため、金利負担能力を評価できません（中立評価）。"

    # --- 軸3: 負債の質・構成（2点）---
    composition_score = 1
    composition_detail = ""
    short_term_ratio = None
    if debt_free:
        composition_score = 2
        composition_detail = "実質無借金経営であり、借り換えリスクはありません。"
    elif short_term_debt is not None and total_debt and total_debt > 0:
        short_term_ratio = short_term_debt / total_debt
        if short_term_ratio <= 0.20:
            composition_score = 2
            composition_detail = f"短期負債比率は{short_term_ratio*100:.1f}%と低く、借り換えリスクは限定的です。"
        elif short_term_ratio <= 0.40:
            composition_score = 1
            composition_detail = f"短期負債比率は{short_term_ratio*100:.1f}%であり、一定の借り換えリスクがあります。"
        else:
            composition_score = 0
            composition_detail = f"短期負債比率は{short_term_ratio*100:.1f}%と高く、借り換えリスクが大きいです。"
    else:
        composition_detail = "短期負債・総負債のデータが不足しているため、負債構成を評価できません（中立評価）。"

    # --- 軸4: 負債推移のトレンド（2点）---
    trend_score = 1
    trend_detail = ""
    avg_debt_change_rate = None
    if len(debt_history) >= 2:
        changes = []
        for i in range(len(debt_history) - 1):
            newer = debt_history[i]
            older = debt_history[i + 1]
            if older and older > 0:
                changes.append((newer - older) / older)
        if changes:
            avg_debt_change_rate = sum(changes) / len(changes)
            years = len(debt_history)
            if avg_debt_change_rate <= 0:
                trend_score = 2
                trend_detail = f"直近{years}年間、負債は年平均{avg_debt_change_rate*100:+.1f}%で推移し、健全に抑制されています。"
            elif avg_debt_change_rate <= 0.10:
                trend_score = 1
                trend_detail = f"直近{years}年間、負債は年平均{avg_debt_change_rate*100:+.1f}%で緩やかに増加していますが、許容範囲内です。"
            else:
                trend_score = 0
                trend_detail = f"直近{years}年間、負債は年平均{avg_debt_change_rate*100:+.1f}%で増加しており、負債膨張のリスクがあります。"
        else:
            trend_detail = "負債推移データが不正なため、トレンドを評価できません（中立評価）。"
    else:
        trend_detail = "負債の複数年データが不足しているため、トレンドを評価できません（中立評価）。"

    # --- 合計スコア ---
    total_score = level_score + coverage_score + composition_score + trend_score

    if total_score >= 8:
        rating = "excellent"
        summary = "負債の質（返済能力・構成・リスク）は極めて健全です。財務規律の高い経営が行われています。"
        verdict = "Excellent（優良）"
    elif total_score >= 6:
        rating = "good"
        summary = "負債の質は良好です。返済能力・構成ともに大きな問題はありません。"
        verdict = "Good（良好）"
    elif total_score >= 4:
        rating = "average"
        summary = "負債の質は平均的です。一部の指標に注意が必要です。"
        verdict = "Average（平均的）"
    elif total_score >= 2:
        rating = "below_average"
        summary = "負債の質に課題があります。返済能力または構成のリスクを注視すべきです。"
        verdict = "Below Average（やや低い）"
    else:
        rating = "poor"
        summary = "負債の質は低いです。返済能力・構成の両面でリスクが高い可能性があります。"
        verdict = "Poor（低い）"

    warnings = []
    if not debt_free and coverage_score == 0:
        warnings.append("金利負担能力が低く、支払利息の負担が重い可能性があります。")
    if not debt_free and composition_score == 0:
        warnings.append("短期負債への依存度が高く、借り換えリスクが大きい可能性があります。")
    if not debt_free and level_score == 0:
        warnings.append("D/E比率またはDebt/EBITDA倍率が過大であり、負債水準に懸念があります。")
    if avg_debt_change_rate is not None and avg_debt_change_rate > 0.10:
        warnings.append("負債が年平均10%を超えて増加しており、財務健全性の悪化に注意が必要です。")

    return {
        "success": True,
        "level_score": level_score,
        "level_detail": level_detail,
        "coverage_score": coverage_score,
        "coverage_detail": coverage_detail,
        "composition_score": composition_score,
        "composition_detail": composition_detail,
        "trend_score": trend_score,
        "trend_detail": trend_detail,
        "total_score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": summary,
        "verdict": verdict,
        "warnings": warnings,
        "raw": {
            "debt_to_equity": de,
            "debt_ebitda": debt_ebitda,
            "interest_coverage_ratio": interest_coverage_ratio,
            "short_term_ratio": short_term_ratio,
            "avg_debt_change_rate": avg_debt_change_rate,
            "total_debt": total_debt,
            "long_term_debt": long_term_debt,
            "short_term_debt": short_term_debt,
            "interest_expense": interest_expense,
            "ebitda": ebitda,
            "operating_income": operating_income,
            "total_debt_history": debt_history,
            "debt_free": debt_free,
        },
    }
