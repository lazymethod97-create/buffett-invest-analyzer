"""
Share Buyback（自社株買い）計算エンジン（Sprint23）

Capital Allocation（Sprint22）では、自社株買いの「タイミング」を
安全余裕（MOS）との突合で単年評価した。
Share Buybackでは、自社株買いそのものの「質・効果・一貫性」を
複数年の推移データから独立した分析軸として評価する。
Sprint22と評価対象データ・評価軸ともに重複しない（ルール14）。

評価軸（4観点、合計10点）
1. 買い入れの一貫性（Consistency）: 3点
   複数年にわたり継続的に自社株買いを行っているか
2. 発行済株式数の減少効果（Share Reduction）: 3点
   期中平均株式数が実際にどれだけ減少しているか
3. 財務健全性とのバランス（Balance）: 2点
   負債の急増を伴う無理な買い戻しになっていないか
4. 買い入れの効果的なタイミング（Timing）: 2点
   現在のPERが自社の過去5年平均PER（簡易推定）と比べて割高でないか
   ※Sprint22の「タイミング」評価はDCF/Intrinsic Valueの安全余裕（MOS）を
     基準にしたが、Sprint23はPER水準（過去5年平均との比較）を基準にする点で異なる。

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any, List, Optional


def calculate_share_buyback(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    自社株買いそのものの質・効果・一貫性を評価する。

    引数
    ----
    data: get_stock_data() が返す企業データ辞書
          buyback_history, shares_outstanding_history, total_debt_history,
          avg_price_5y, trailing_eps, pe_ratio を使用する。

    戻り値
    ----
    success=True, consistency_score, reduction_score, balance_score,
    timing_score, total_score, rating, summary, verdict
    """
    buyback_history: List[float] = data.get("buyback_history") or []
    shares_history: List[float] = data.get("shares_outstanding_history") or []
    debt_history: List[float] = data.get("total_debt_history") or []
    pe_ratio = data.get("pe_ratio")
    avg_price_5y = data.get("avg_price_5y")
    trailing_eps = data.get("trailing_eps")

    # --- 軸1: 買い入れの一貫性（3点）---
    # Sprint34-3: 複数年データが無い場合は「悪い」（0点）ではなく
    # 中立評価（3点満点中1点）とする。同ファイルのbalance_score/timing_score
    # の欠損時の扱いと足並みを揃える。
    consistency_score = 1
    consistency_detail = ""
    years_with_buyback = 0
    total_years = len(buyback_history)
    if total_years > 0:
        years_with_buyback = sum(1 for v in buyback_history if v and v > 0)
        ratio = years_with_buyback / total_years
        if ratio >= 1.0 and total_years >= 3:
            consistency_score = 3
            consistency_detail = f"直近{total_years}年すべてで自社株買いを実施しており、極めて高い継続性があります。"
        elif ratio >= 0.75:
            consistency_score = 2
            consistency_detail = f"直近{total_years}年中{years_with_buyback}年で自社株買いを実施し、継続性は良好です。"
        elif ratio > 0:
            consistency_score = 1
            consistency_detail = f"直近{total_years}年中{years_with_buyback}年のみ自社株買いを実施しており、継続性に課題があります。"
        else:
            consistency_score = 0
            consistency_detail = f"直近{total_years}年間、自社株買いの実施が確認できません。"
    else:
        consistency_detail = "自社株買いの複数年データが不足しているため、継続性を評価できません（中立評価）。"

    # --- 軸2: 発行済株式数の減少効果（3点）---
    # Sprint34-3: 複数年データが無い／不正な場合は「悪い」（0点）ではなく
    # 中立評価（3点満点中1点）とする。
    reduction_score = 1
    reduction_detail = ""
    reduction_rate = None
    if len(shares_history) >= 2:
        newest = shares_history[0]
        oldest = shares_history[-1]
        if oldest and oldest > 0:
            reduction_rate = (oldest - newest) / oldest
            if reduction_rate >= 0.10:
                reduction_score = 3
                reduction_detail = f"発行済株式数が過去{len(shares_history)}年で{reduction_rate*100:.1f}%減少し、EPS押し上げ効果が大きいです。"
            elif reduction_rate >= 0.05:
                reduction_score = 2
                reduction_detail = f"発行済株式数が過去{len(shares_history)}年で{reduction_rate*100:.1f}%減少し、一定のEPS押し上げ効果があります。"
            elif reduction_rate > 0:
                reduction_score = 1
                reduction_detail = f"発行済株式数は過去{len(shares_history)}年で{reduction_rate*100:.1f}%減少していますが、効果は限定的です。"
            else:
                reduction_score = 0
                reduction_detail = f"発行済株式数はむしろ{abs(reduction_rate)*100:.1f}%増加しており、希薄化が進んでいます。"
        else:
            reduction_detail = "発行済株式数データが不正なため、減少効果を評価できません（中立評価）。"
    else:
        reduction_detail = "発行済株式数の複数年データが不足しているため、減少効果を評価できません（中立評価）。"

    # --- 軸3: 財務健全性とのバランス（2点）---
    balance_score = 1
    balance_detail = ""
    debt_change_rate = None
    has_buyback = years_with_buyback > 0 or (buyback_history and buyback_history[0] and buyback_history[0] > 0)
    if len(debt_history) >= 2:
        newest_debt = debt_history[0]
        oldest_debt = debt_history[-1]
        if oldest_debt and oldest_debt > 0:
            debt_change_rate = (newest_debt - oldest_debt) / oldest_debt
            if debt_change_rate <= 0:
                balance_score = 2
                balance_detail = f"負債は過去{len(debt_history)}年で{debt_change_rate*100:+.1f}%と抑制されており、無理のない買い戻しです。"
            elif debt_change_rate <= 0.20:
                balance_score = 1
                balance_detail = f"負債は過去{len(debt_history)}年で{debt_change_rate*100:+.1f}%増加していますが、許容範囲内です。"
            else:
                balance_score = 0
                balance_detail = f"負債が過去{len(debt_history)}年で{debt_change_rate*100:+.1f}%と急増しており、負債増を伴う無理な買い戻しの懸念があります。"
        else:
            balance_detail = "負債データが不正なため、財務健全性とのバランスを評価できません。"
            balance_score = 1
    else:
        balance_detail = "負債の複数年データが不足しているため、財務健全性とのバランスを評価できません（中立評価）。"
        balance_score = 1

    # --- 軸4: 買い入れの効果的なタイミング（2点）---
    timing_score = 1
    timing_detail = ""
    avg_pe_5y = None
    if pe_ratio is not None and avg_price_5y is not None and trailing_eps:
        try:
            if trailing_eps > 0:
                avg_pe_5y = avg_price_5y / trailing_eps
        except Exception:
            avg_pe_5y = None

    if pe_ratio is not None and avg_pe_5y is not None and avg_pe_5y > 0:
        relative = pe_ratio / avg_pe_5y
        if relative <= 0.9:
            timing_score = 2
            timing_detail = f"現在のPER({pe_ratio:.1f}倍)は過去5年平均PER(概算{avg_pe_5y:.1f}倍)より割安圏にあり、効果的な買い戻しタイミングです。"
        elif relative <= 1.1:
            timing_score = 1
            timing_detail = f"現在のPER({pe_ratio:.1f}倍)は過去5年平均PER(概算{avg_pe_5y:.1f}倍)とほぼ同水準です。"
        else:
            timing_score = 0
            timing_detail = f"現在のPER({pe_ratio:.1f}倍)は過去5年平均PER(概算{avg_pe_5y:.1f}倍)より割高で、高値づかみの懸念があります。"
    else:
        timing_detail = "PERの過去5年平均を推定するデータが不足しているため、タイミングを評価できません（中立評価）。"
        timing_score = 1

    # --- 合計スコア ---
    total_score = consistency_score + reduction_score + balance_score + timing_score

    if total_score >= 8:
        rating = "excellent"
        summary = "自社株買いの質・効果・一貫性は極めて高いです。株主価値向上に強くコミットしています。"
        verdict = "Excellent（優良）"
    elif total_score >= 6:
        rating = "good"
        summary = "自社株買いの質・効果・一貫性は良好です。概ね規律ある実施が行われています。"
        verdict = "Good（良好）"
    elif total_score >= 4:
        rating = "average"
        summary = "自社株買いの質・効果・一貫性は平均的です。改善の余地があります。"
        verdict = "Average（平均的）"
    elif total_score >= 2:
        rating = "below_average"
        summary = "自社株買いの質・効果・一貫性に課題があります。実施状況を注視すべきです。"
        verdict = "Below Average（やや低い）"
    else:
        rating = "poor"
        summary = "自社株買いの質・効果・一貫性は低いです。株主価値向上への貢献が乏しい可能性があります。"
        verdict = "Poor（低い）"

    warnings = []
    if consistency_score == 0 and total_years > 0:
        warnings.append("自社株買いの継続的な実施が確認できません。")
    if reduction_rate is not None and reduction_rate < 0:
        warnings.append("発行済株式数が増加しており、希薄化が進んでいます。")
    if debt_change_rate is not None and debt_change_rate > 0.20 and has_buyback:
        warnings.append("負債が急増する中での自社株買いは財務健全性を損なう可能性があります。")
    if timing_score == 0:
        warnings.append("現在のPERが過去平均より割高であり、買い戻しの効果が薄れている可能性があります。")

    return {
        "success": True,
        "consistency_score": consistency_score,
        "consistency_detail": consistency_detail,
        "reduction_score": reduction_score,
        "reduction_detail": reduction_detail,
        "balance_score": balance_score,
        "balance_detail": balance_detail,
        "timing_score": timing_score,
        "timing_detail": timing_detail,
        "total_score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": summary,
        "verdict": verdict,
        "warnings": warnings,
        "raw": {
            "buyback_history": buyback_history,
            "shares_outstanding_history": shares_history,
            "total_debt_history": debt_history,
            "years_with_buyback": years_with_buyback,
            "total_years": total_years,
            "reduction_rate": reduction_rate,
            "debt_change_rate": debt_change_rate,
            "pe_ratio": pe_ratio,
            "avg_pe_5y": avg_pe_5y,
        },
    }
