"""
Capital Allocation（資本配分）計算エンジン（Sprint22）

バフェットが最も重視する経営者の能力の一つ「資本配分」を評価する。
既存の ROIC / Owner Earnings / Intrinsic Value の計算結果を再利用する。

評価軸（3観点、合計10点）
1. 再投資効率（Reinvestment Efficiency）: 4点
   ROICの水準から、内部留保を効率的に再投資できているかを評価
2. 株主還元の規律（Dividend/Payout Discipline）: 3点
   配当性向が適切か（高すぎず低すぎず、バフェット基準）
3. 自社株買いのタイミング（Buyback Timing）: 3点
   安全余裕（MOS）がある時に自社株買いを行っているか

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any, Optional


def calculate_capital_allocation(
    data: Dict[str, Any],
    roic_result: Optional[Dict[str, Any]] = None,
    owner_earnings_result: Optional[Dict[str, Any]] = None,
    intrinsic_value_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    資本配分の質を評価する。

    引数
    ----
    data: get_stock_data() が返す企業データ辞書
    roic_result: calculate_roic() の戻り値（省略時はNone）
    owner_earnings_result: calculate_owner_earnings() の戻り値（省略時はNone）
    intrinsic_value_result: calculate_intrinsic_value() の戻り値（省略時はNone）

    戻り値
    ----
    成功時: success=True, reinvestment_score, payout_score, buyback_score,
            total_score, rating, summary, verdict
    失敗時: success=False, error（データ不足の理由）
    """
    # --- 軸1: 再投資効率（4点）---
    reinvestment_score = 0
    reinvestment_detail = ""
    if roic_result:
        roic = roic_result.get("roic")
        if roic is not None:
            if roic >= 0.25:
                reinvestment_score = 4
                reinvestment_detail = f"ROIC {roic*100:.1f}%は極めて高く、内部留保を非常に効率的に再投資できています。"
            elif roic >= 0.20:
                reinvestment_score = 3
                reinvestment_detail = f"ROIC {roic*100:.1f}%は優秀で、再投資効率は良好です。"
            elif roic >= 0.15:
                reinvestment_score = 2
                reinvestment_detail = f"ROIC {roic*100:.1f}%は一定の水準。再投資リターンはまずまずです。"
            elif roic >= 0.10:
                reinvestment_score = 1
                reinvestment_detail = f"ROIC {roic*100:.1f}%は平均的。再投資効率に改善余地があります。"
            else:
                reinvestment_score = 0
                reinvestment_detail = f"ROIC {roic*100:.1f}%は低く、再投資による価値創造ができていません。"
        else:
            reinvestment_detail = "ROICデータが不足しているため、再投資効率を評価できません。"
    else:
        reinvestment_detail = "ROICデータが不足しているため、再投資効率を評価できません。"

    # --- 軸2: 株主還元の規律（3点）---
    payout_score = 0
    payout_detail = ""
    payout_ratio = data.get("payout_ratio")
    dividend_yield = data.get("dividend_yield")

    if payout_ratio is not None:
        if payout_ratio <= 0:
            # 無配当: 成長重視（バフェットもBerkshireは無配）
            payout_score = 2
            payout_detail = "無配当ですが、成長への再投資を優先していると評価できます。"
        elif payout_ratio <= 0.30:
            payout_score = 3
            payout_detail = f"配当性向{payout_ratio*100:.0f}%は適切。成長投資と株主還元のバランスが良好です。"
        elif payout_ratio <= 0.50:
            payout_score = 2
            payout_detail = f"配当性向{payout_ratio*100:.0f}%は許容範囲。持続可能な水準です。"
        elif payout_ratio <= 0.75:
            payout_score = 1
            payout_detail = f"配当性向{payout_ratio*100:.0f}%はやや高い。景気後退時の減配リスクに注意。"
        else:
            payout_score = 0
            payout_detail = f"配当性向{payout_ratio*100:.0f}%は極めて高い。持続可能性に懸念があります。"
    elif dividend_yield is not None and dividend_yield > 0:
        # 配当利回りしかない場合、簡易判定
        if dividend_yield < 0.01:
            payout_score = 2
            payout_detail = "配当利回りが低く、成長重視の姿勢と見られます。"
        elif dividend_yield < 0.03:
            payout_score = 2
            payout_detail = f"配当利回り{dividend_yield*100:.1f}%は適度。バランスの取れた株主還元です。"
        elif dividend_yield < 0.05:
            payout_score = 1
            payout_detail = f"配当利回り{dividend_yield*100:.1f}%はやや高い。持続可能性を確認すべきです。"
        else:
            payout_score = 0
            payout_detail = f"配当利回り{dividend_yield*100:.1f}%は極めて高い。減配リスクに注意。"
    else:
        # 配当データなし
        payout_score = 1
        payout_detail = "配当データが不足しています。現時点では中立評価。"
        payout_ratio = None

    # --- 軸3: 自社株買いのタイミング（3点）---
    buyback_score = 0
    buyback_detail = ""
    buyback_amount = data.get("buyback_amount")
    need_cash = data.get("free_cashflow")

    if intrinsic_value_result and intrinsic_value_result.get("success"):
        mosp = intrinsic_value_result.get("margin_of_safety_pct")
        if mosp is not None:
            if mosp >= 15:
                # MOSが十分にある → 買いやすい環境だが、自社株買いデータがなければ想定で評価
                if buyback_amount is not None and buyback_amount > 0 and need_cash is not None and need_cash > 0:
                    if buyback_amount < need_cash * 0.5:
                        buyback_score = 3
                        buyback_detail = f"安全余裕{mosp:+.0f}%の局面で、FCFの範囲内で適切な自社株買いを実施しています。"
                    else:
                        buyback_score = 2
                        buyback_detail = f"安全余裕{mosp:+.0f}%の局面ですが、自社株買い規模がやや大きいです。"
                else:
                    # 自社株買いデータなし・またはMOS十分だがデータなし
                    buyback_score = 2
                    buyback_detail = f"安全余裕{mosp:+.0f}%と割安感があります。自社株買いの実施有無を確認してください。"
            elif mosp >= 0:
                buyback_score = 1
                buyback_detail = f"安全余裕{mosp:+.0f}%と価格は適正水準。自社株買いの効果は限定的です。"
            else:
                buyback_score = 0
                buyback_detail = f"安全余裕{mosp:+.0f}%と割高局面。現在の自社株買いは資本効率を悪化させる可能性があります。"
        else:
            buyback_detail = "安全余裕が不明なため、自社株買いのタイミングを評価できません。"
            buyback_score = 1
    else:
        # Intrinsic Valueデータなし
        if buyback_amount is not None and buyback_amount > 0:
            buyback_score = 1
            buyback_detail = "自社株買いを実施していますが、バリュエーションとの関係で評価できません。"
        else:
            buyback_score = 1
            buyback_detail = "Intrinsic Valueのデータが不足しているため、自社株買いのタイミングを評価できません。"

    # --- 合計スコア ---
    total_score = reinvestment_score + payout_score + buyback_score

    if total_score >= 8:
        rating = "excellent"
        summary = "資本配分の質は極めて高いです。バフェットが最も重視する経営能力を備えています。"
        verdict = "Excellent（優良）"
    elif total_score >= 6:
        rating = "good"
        summary = "資本配分の質は良好です。経営者は概ね合理的な資本配分を行っています。"
        verdict = "Good（良好）"
    elif total_score >= 4:
        rating = "average"
        summary = "資本配分の質は平均的です。改善の余地があります。"
        verdict = "Average（平均的）"
    elif total_score >= 2:
        rating = "below_average"
        summary = "資本配分の質に課題があります。経営者の資本配分判断を注視すべきです。"
        verdict = "Below Average（やや低い）"
    else:
        rating = "poor"
        summary = "資本配分の質は低いです。経営者の資本配分能力に重大な懸念があります。"
        verdict = "Poor（低い）"

    warnings = []
    if reinvestment_score < 2:
        warnings.append("再投資効率が低く、内部留保の活用に課題があります。")
    if payout_score < 2 and payout_ratio is not None and payout_ratio > 0.75:
        warnings.append("配当性向が高すぎます。持続可能性を確認してください。")
    if buyback_score < 2 and intrinsic_value_result and intrinsic_value_result.get("margin_of_safety_pct", 0) >= 15:
        warnings.append("安全余裕があるにもかかわらず、自社株買いが適切に行われていない可能性があります。")

    return {
        "success": True,
        "reinvestment_score": reinvestment_score,
        "reinvestment_detail": reinvestment_detail,
        "payout_score": payout_score,
        "payout_detail": payout_detail,
        "buyback_score": buyback_score,
        "buyback_detail": buyback_detail,
        "total_score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": summary,
        "verdict": verdict,
        "warnings": warnings,
        "raw": {
            "roic_result_used": roic_result is not None,
            "intrinsic_value_result_used": intrinsic_value_result is not None,
            "payout_ratio": payout_ratio,
            "dividend_yield": dividend_yield,
            "buyback_amount": buyback_amount,
            "free_cashflow": need_cash,
        },
    }
