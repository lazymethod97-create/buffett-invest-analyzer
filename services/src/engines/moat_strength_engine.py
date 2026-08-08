"""
Economic Moat強化（経済的堀の定量的検証）計算エンジン（Sprint25）

既存のMOAT評価（Sprint18、ai/ai_analysis.py の generate_moat_analysis）は、
単年のROE・営業利益率等の断面データをもとにGeminiが定性的に6観点
（ブランド力／規模の経済／価格決定力／ネットワーク効果／スイッチングコスト／規制障壁）
を判定し、wide/narrow/noneを決めるAI判定のみであり、複数年のルールベース検証が
存在しない。

Sprint25では、この定性判定を「複数年の定量トレンド」で裏付ける独立した
ルールベース分析軸を新設する。既存のMOAT判定（qualitative）とは評価データ・
評価軸ともに重複しない（重複実装禁止・ルール14）。

評価軸（4観点、合計10点）
1. 収益性の持続性・安定性（Persistence）: 3点
   ROE・営業利益率の複数年推移が高水準かつ低ボラティリティで維持されているか
   （moatが「本物」であることの定量的裏付け）
2. 価格決定力の定量的検証（Pricing Power）: 3点
   粗利率（またはEBITDAマージン）の複数年推移から、コスト上昇局面でも
   利益率を防衛できているか（値上げ耐性の実証）
3. 市場地位の安定性（Market Position）: 2点
   売上高成長率の複数年推移のブレ幅（急激な浮沈がなく、安定的にシェアを
   維持・拡大しているか）
4. 既存MOAT判定との整合性（Consistency）: 2点
   Sprint18の generate_moat_analysis による wide/narrow/none 判定と、
   本エンジンの定量トレンド評価（軸1〜3の合計）が整合しているかを検証する。
   乖離がある場合は「AI判定が楽観的すぎる可能性」等の警告を出す。
   ※既存MOAT判定は引数として受け取るのみで、再計算しない（重複実装禁止・ルール14）。

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any, List, Optional


def _avg_std_cv(values: List[float]):
    """平均・標準偏差・変動係数(CV=std/|avg|)を返す。データ不足時は(None, None, None)。"""
    if not values or len(values) < 2:
        return None, None, None
    avg = sum(values) / len(values)
    var = sum((v - avg) ** 2 for v in values) / len(values)
    std = var ** 0.5
    cv = (std / abs(avg)) if avg != 0 else None
    return avg, std, cv


def _level_tier(avg: Optional[float]) -> Optional[int]:
    if avg is None:
        return None
    if avg >= 0.20:
        return 3
    elif avg >= 0.12:
        return 2
    elif avg >= 0.05:
        return 1
    return 0


def _stability_tier(cv: Optional[float]) -> Optional[int]:
    if cv is None:
        return None
    if cv <= 0.15:
        return 3
    elif cv <= 0.30:
        return 2
    elif cv <= 0.50:
        return 1
    return 0


def calculate_moat_strength(data: Dict[str, Any], moat_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    複数年の定量トレンドから経済的堀（MOAT）の強さを検証する。

    引数
    ----
    data: get_stock_data() が返す企業データ辞書
          roe_history, operating_margin_history, gross_margin_history,
          revenue_history（すべてSprint25で追加済み、直近年が先頭）を使用する。
    moat_result: Sprint18の generate_moat_analysis() の戻り値（qualitative判定）。
                 rating（wide/narrow/none）を整合性チェックに使う。再計算しない。

    戻り値
    ----
    success=True, persistence_score, pricing_power_score, market_position_score,
    consistency_score, total_score, rating, summary, verdict
    """
    roe_history: List[float] = data.get("roe_history") or []
    op_margin_history: List[float] = data.get("operating_margin_history") or []
    gross_margin_history: List[float] = data.get("gross_margin_history") or []
    revenue_history: List[float] = data.get("revenue_history") or []

    # --- 軸1: 収益性の持続性・安定性（3点）---
    # ROE推移を優先し、取得できない場合は営業利益率推移で代替する。
    persistence_score = 1
    persistence_detail = ""
    roe_avg, roe_std, roe_cv = _avg_std_cv(roe_history)
    op_avg, op_std, op_cv = _avg_std_cv(op_margin_history)

    primary_avg, primary_cv, primary_label = (roe_avg, roe_cv, "ROE") if roe_avg is not None else (op_avg, op_cv, "営業利益率")

    if primary_avg is not None:
        level_t = _level_tier(primary_avg)
        stab_t = _stability_tier(primary_cv)
        tiers = [t for t in (level_t, stab_t) if t is not None]
        if tiers:
            persistence_score = min(tiers)
            years = len(roe_history) if roe_avg is not None else len(op_margin_history)
            cv_text = f"変動係数{primary_cv*100:.1f}%" if primary_cv is not None else "変動係数は算出不可"
            persistence_detail = (
                f"直近{years}年間の{primary_label}平均は{primary_avg*100:.1f}%、{cv_text}。"
                f"収益性は{'高水準かつ安定的' if persistence_score >= 2 else 'やや不安定または低水準'}に推移しています。"
            )
        else:
            persistence_detail = f"{primary_label}のデータはありますが、変動係数を算出できないため中立評価とします。"
    else:
        persistence_detail = "ROE・営業利益率いずれも複数年データが不足しているため、収益性の持続性を評価できません（中立評価）。"

    # --- 軸2: 価格決定力の定量的検証（3点）---
    # 粗利率（またはEBITDAマージン）の直近年 vs 過去平均の防衛度合いで評価する。
    pricing_power_score = 1
    pricing_power_detail = ""
    margin_diff = None
    if len(gross_margin_history) >= 2:
        recent = gross_margin_history[0]
        older = gross_margin_history[1:]
        older_avg = sum(older) / len(older)
        margin_diff = recent - older_avg
        years = len(gross_margin_history)
        if margin_diff >= -0.01:
            pricing_power_score = 3
            pricing_power_detail = (
                f"直近の粗利率（{recent*100:.1f}%）は過去{years-1}年平均（{older_avg*100:.1f}%）を"
                f"維持・上回っており、コスト上昇局面でも価格決定力を発揮できています。"
            )
        elif margin_diff >= -0.03:
            pricing_power_score = 2
            pricing_power_detail = (
                f"直近の粗利率（{recent*100:.1f}%）は過去{years-1}年平均（{older_avg*100:.1f}%）から"
                f"小幅な低下にとどまっており、一定の値上げ耐性があります。"
            )
        elif margin_diff >= -0.05:
            pricing_power_score = 1
            pricing_power_detail = (
                f"直近の粗利率（{recent*100:.1f}%）は過去{years-1}年平均（{older_avg*100:.1f}%）から"
                f"低下しており、価格決定力にやや陰りが見られます。"
            )
        else:
            pricing_power_score = 0
            pricing_power_detail = (
                f"直近の粗利率（{recent*100:.1f}%）は過去{years-1}年平均（{older_avg*100:.1f}%）から"
                f"大きく低下しており、コスト上昇を価格転嫁できていない可能性があります。"
            )
    else:
        pricing_power_detail = "粗利率（またはEBITDAマージン）の複数年データが不足しているため、価格決定力を評価できません（中立評価）。"

    # --- 軸3: 市場地位の安定性（2点）---
    # 売上高成長率の複数年推移のブレ幅（標準偏差）と急激な落ち込みの有無で評価する。
    market_position_score = 1
    market_position_detail = ""
    growth_std = None
    growth_min = None
    if len(revenue_history) >= 3:
        growth_rates = []
        for i in range(len(revenue_history) - 1):
            newer = revenue_history[i]
            older = revenue_history[i + 1]
            if older and older != 0:
                growth_rates.append((newer - older) / older)
        if len(growth_rates) >= 2:
            g_avg = sum(growth_rates) / len(growth_rates)
            growth_std = (sum((g - g_avg) ** 2 for g in growth_rates) / len(growth_rates)) ** 0.5
            growth_min = min(growth_rates)
            if growth_std <= 0.10 and growth_min > -0.10:
                market_position_score = 2
                market_position_detail = (
                    f"売上高成長率のブレ幅（標準偏差{growth_std*100:.1f}%）は小さく、"
                    f"急激な浮沈もなく市場地位は安定的に推移しています。"
                )
            elif growth_std <= 0.20 and growth_min > -0.20:
                market_position_score = 1
                market_position_detail = (
                    f"売上高成長率のブレ幅（標準偏差{growth_std*100:.1f}%）はやや大きく、"
                    f"市場地位の安定性には一定の注意が必要です。"
                )
            else:
                market_position_score = 0
                market_position_detail = (
                    f"売上高成長率のブレ幅（標準偏差{growth_std*100:.1f}%、最小{growth_min*100:.1f}%）が大きく、"
                    f"急激な浮沈が見られるため、市場地位が不安定な可能性があります。"
                )
        else:
            market_position_detail = "売上高成長率を算出するためのデータが不足しているため、市場地位の安定性を評価できません（中立評価）。"
    else:
        market_position_detail = "売上高の複数年データが不足しているため、市場地位の安定性を評価できません（中立評価）。"

    # --- 軸4: 既存MOAT判定（Sprint18）との整合性（2点）---
    consistency_score = 1
    consistency_detail = ""
    ai_rating = None
    quantitative_subtotal = persistence_score + pricing_power_score + market_position_score  # 最大8点

    if moat_result:
        ai_rating = (moat_result.get("rating") or "").lower()

    if quantitative_subtotal >= 6:
        quant_tier = "strong"
    elif quantitative_subtotal >= 3:
        quant_tier = "moderate"
    else:
        quant_tier = "weak"

    consistency_warning = None
    if ai_rating in ("wide", "narrow", "none"):
        if ai_rating == "wide":
            if quant_tier == "strong":
                consistency_score = 2
                consistency_detail = (
                    f"既存MOAT判定（wide）は、定量トレンド評価（{quantitative_subtotal}/8点、strong）と整合しています。"
                )
            elif quant_tier == "moderate":
                consistency_score = 1
                consistency_detail = (
                    f"既存MOAT判定（wide）に対し、定量トレンド評価は{quantitative_subtotal}/8点（moderate）にとどまり、"
                    f"やや裏付けが弱い可能性があります。"
                )
            else:
                consistency_score = 0
                consistency_detail = (
                    f"既存MOAT判定（wide）に対し、定量トレンド評価は{quantitative_subtotal}/8点（weak）と低く、乖離があります。"
                )
                consistency_warning = "既存のMOAT判定（wide）は、複数年の定量トレンドによる裏付けが弱く、AI判定が楽観的すぎる可能性があります。"
        elif ai_rating == "narrow":
            if quant_tier in ("strong", "moderate"):
                consistency_score = 2
                consistency_detail = (
                    f"既存MOAT判定（narrow）は、定量トレンド評価（{quantitative_subtotal}/8点、{quant_tier}）と整合しています。"
                )
            else:
                consistency_score = 1
                consistency_detail = (
                    f"既存MOAT判定（narrow）に対し、定量トレンド評価は{quantitative_subtotal}/8点（weak）にとどまり、"
                    f"narrow判定すら楽観的な可能性があります。"
                )
                consistency_warning = "既存のMOAT判定（narrow）に対し、定量トレンドは裏付けに乏しく、AI判定がやや楽観的な可能性があります。"
        else:  # none
            if quant_tier == "weak":
                consistency_score = 2
                consistency_detail = (
                    f"既存MOAT判定（none）は、定量トレンド評価（{quantitative_subtotal}/8点、weak）と整合しています。"
                )
            else:
                consistency_score = 1
                consistency_detail = (
                    f"既存MOAT判定（none）に対し、定量トレンド評価は{quantitative_subtotal}/8点（{quant_tier}）であり、"
                    f"実際にはより強いMOATが存在する可能性があります（AI判定が過度に保守的な可能性）。"
                )
    else:
        consistency_detail = "既存MOAT判定（Sprint18）の結果が取得できないため、整合性を評価できません（中立評価）。"

    total_score = persistence_score + pricing_power_score + market_position_score + consistency_score

    if total_score >= 8:
        rating = "excellent"
        summary = "複数年の定量トレンドが経済的堀の強さを明確に裏付けており、moatは極めて頑健です。"
        verdict = "Excellent（優良）"
    elif total_score >= 6:
        rating = "good"
        summary = "複数年の定量トレンドは経済的堀の存在を概ね裏付けています。"
        verdict = "Good（良好）"
    elif total_score >= 4:
        rating = "average"
        summary = "定量トレンドによるmoatの裏付けは平均的です。一部指標に注意が必要です。"
        verdict = "Average（平均的）"
    elif total_score >= 2:
        rating = "below_average"
        summary = "定量トレンドによるmoatの裏付けは弱く、既存の定性判定との乖離に注意が必要です。"
        verdict = "Below Average（やや低い）"
    else:
        rating = "poor"
        summary = "複数年の定量トレンドはmoatの存在を裏付けておらず、既存の定性判定を再検証すべきです。"
        verdict = "Poor（低い）"

    warnings = []
    if consistency_warning:
        warnings.append(consistency_warning)
    if persistence_score == 0:
        warnings.append("収益性（ROEまたは営業利益率）の水準・安定性が低く、moatが「本物」であるか疑問が残ります。")
    if pricing_power_score == 0:
        warnings.append("粗利率が過去平均から大きく低下しており、価格決定力（値上げ耐性）に懸念があります。")
    if market_position_score == 0:
        warnings.append("売上高成長率のブレ幅が大きく、市場地位が不安定な可能性があります。")

    return {
        "success": True,
        "persistence_score": persistence_score,
        "persistence_detail": persistence_detail,
        "pricing_power_score": pricing_power_score,
        "pricing_power_detail": pricing_power_detail,
        "market_position_score": market_position_score,
        "market_position_detail": market_position_detail,
        "consistency_score": consistency_score,
        "consistency_detail": consistency_detail,
        "total_score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": summary,
        "verdict": verdict,
        "warnings": warnings,
        "raw": {
            "roe_avg": roe_avg,
            "roe_cv": roe_cv,
            "operating_margin_avg": op_avg,
            "operating_margin_cv": op_cv,
            "gross_margin_diff": margin_diff,
            "revenue_growth_std": growth_std,
            "revenue_growth_min": growth_min,
            "ai_moat_rating": ai_rating,
            "quantitative_subtotal": quantitative_subtotal,
            "quantitative_tier": quant_tier,
            "roe_history": roe_history,
            "operating_margin_history": op_margin_history,
            "gross_margin_history": gross_margin_history,
            "revenue_history": revenue_history,
        },
    }
