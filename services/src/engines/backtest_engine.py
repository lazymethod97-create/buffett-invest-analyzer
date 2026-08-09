"""
Backtest（簡易品質スコア × フォワードリターン検証）計算エンジン（Sprint26）

「過去のBuffett Score（総合判定）が高かった時点で買っていたら、実際のリターンは
どうだったか」を検証する機能。

制約と設計方針
---------------------------------
yfinanceで取得できる複数年財務データ（income_stmt/balance_sheet）は通常直近4年分
程度であり、また過去の任意時点でDCF・AI定性MOAT判定・Red Team等まで含めた
フルのBuffett Score（190点満点）を再計算することは、当時の市場前提やGemini判定を
再現できないため事実上不可能である。

そのため本エンジンでは、Sprint23〜25で取得済みの複数年データ（ROE・営業利益率・
総負債・売上高の推移）から、AI判定やDCFを含まない「簡易品質スコア代理指標」を
決算期ごとにルールベースで算出し、その時点の株価から翌決算期（直近年のみ現在
株価）までの実際のフォワードリターンと突き合わせて検証する（重複実装禁止・ルール14。既存の
Buffett Score計算＝scoring_engine.pyは再利用のみで再実装しない）。

評価軸（4観点、合計10点）
フォワードリターンは「決算期から現在までの累積リターン」ではなく、「翌決算期
（直近年のみ現在）までの約1年間のリターン」に統一する。決算期が古いほど保有期間が
長くなり複利で見かけ上リターンが伸びる交絡（期間長の効果）を避けるためである。

1. 高品質年 vs 低品質年のリターン差検証（Persistence of Edge）: 3点
   決算期を簡易品質スコアの中央値で高品質群・低品質群に分け、翌決算期までの
   フォワードリターンの平均差を検証する（質の高さが実際にリターンの優位に
   繋がっていたか）。
2. 最高品質期間の実績リターン（Best Period Return）: 3点
   複数年の中で最も簡易品質スコアが高かった決算期の、翌決算期までのフォワード
   リターンを評価する。
3. 一貫性（順位相関）（Consistency）: 2点
   簡易品質スコアとフォワードリターンの相関係数（Pearson）で、質とリターンの
   関係が一貫していたかを検証する。
4. 現在のBuffett Scoreとの整合性（Current Consistency）: 2点
   score_result（scoring_engine.pyの計算結果、再利用のみ）を引数として受け取り、
   「過去に質の高さがリターンに繋がっていたか」と「現在のBuffett Scoreが高水準か」の
   整合性を検証する（例：過去は質がリターンに繋がっていたが現在のスコアは低水準、
   など乖離がある場合は警告を出す）。

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any, List, Optional


def _roe_tier(v: Optional[float]) -> Optional[int]:
    if v is None:
        return None
    if v >= 0.20:
        return 3
    elif v >= 0.12:
        return 2
    elif v >= 0.05:
        return 1
    return 0


def _margin_tier(v: Optional[float]) -> Optional[int]:
    return _roe_tier(v)


def _growth_tier(v: Optional[float]) -> Optional[int]:
    if v is None:
        return None
    if v >= 0.10:
        return 2
    elif v >= 0.0:
        return 1
    return 0


def _debt_ratio_tier(total_debt: Optional[float], revenue: Optional[float]) -> Optional[int]:
    if total_debt is None or revenue is None or revenue == 0:
        return None
    if total_debt <= 0:
        return 2
    ratio = total_debt / revenue
    if ratio <= 0.3:
        return 2
    elif ratio <= 0.6:
        return 1
    return 0


def _median(values: List[float]) -> Optional[float]:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def _pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    if var_x == 0 or var_y == 0:
        return None
    return cov / ((var_x ** 0.5) * (var_y ** 0.5))


def _build_year_records(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    決算期ごとに「簡易品質スコア代理指標」と「フォワードリターン」を組み立てる。
    データ不足の年は自動的に除外する（絶対に例外を投げない）。

    フォワードリターンの窓は「その決算期から現在までの累積リターン」ではなく、
    「翌決算期（直近年のみ現在）までの約1年間」に統一する。決算期が古いほど
    保有期間が長くなり複利で見かけ上リターンが伸びる交絡（期間長の効果）を
    排除し、「その時点の品質」と「その後1年程度のリターン」の関係を検証する。
    """
    roe_history: List[float] = data.get("roe_history") or []
    op_margin_history: List[float] = data.get("operating_margin_history") or []
    revenue_history: List[float] = data.get("revenue_history") or []
    debt_history: List[float] = data.get("total_debt_history") or []
    dates: List[str] = data.get("fiscal_year_end_dates") or []
    prices: List[Optional[float]] = data.get("historical_prices_at_fiscal_year_end") or []
    current_price = data.get("current_price")

    n = min(len(roe_history), len(op_margin_history), len(revenue_history), len(dates), len(prices))

    records = []
    for i in range(n):
        roe_t = _roe_tier(roe_history[i])
        margin_t = _margin_tier(op_margin_history[i])

        growth_t = None
        if i + 1 < len(revenue_history) and revenue_history[i + 1]:
            try:
                growth = (revenue_history[i] - revenue_history[i + 1]) / revenue_history[i + 1]
                growth_t = _growth_tier(growth)
            except Exception:
                growth_t = None

        debt_t = None
        if i < len(debt_history):
            debt_t = _debt_ratio_tier(debt_history[i], revenue_history[i])

        tiers = [t for t in (roe_t, margin_t, growth_t, debt_t) if t is not None]
        if not tiers:
            continue
        quality_proxy = sum(tiers)

        price_i = prices[i]
        # 翌決算期（i=0のみ現在株価）までの約1年間のフォワードリターンを使う。
        next_price = current_price if i == 0 else (prices[i - 1] if i - 1 >= 0 else None)
        forward_return = None
        if price_i and price_i > 0 and next_price:
            try:
                forward_return = (next_price - price_i) / price_i
            except Exception:
                forward_return = None

        records.append({
            "date": dates[i],
            "quality_proxy": quality_proxy,
            "forward_return": forward_return,
            "price": price_i,
        })
    return records


def calculate_backtest(data: Dict[str, Any], score_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    「過去に質の高さがリターンに繋がっていたか」を簡易品質スコア代理指標と
    フォワードリターンの突合で検証する。

    引数
    ----
    data: get_stock_data() が返す企業データ辞書
          roe_history, operating_margin_history, revenue_history,
          total_debt_history, fiscal_year_end_dates,
          historical_prices_at_fiscal_year_end, current_price を使用する。
    score_result: scoring_engine.calculate_buffett_score() の戻り値（再計算しない）。
                  total_scoreを現在のBuffett Scoreとして整合性チェックに使う。

    戻り値
    ----
    success=True, edge_score, best_period_score, consistency_score,
    current_consistency_score, total_score, rating, summary, verdict
    """
    records = _build_year_records(data)
    valid_years = [r for r in records if r["forward_return"] is not None]

    # --- 軸1: 高品質年 vs 低品質年のリターン差検証（3点）---
    edge_score = 1
    edge_detail = ""
    return_diff = None
    if len(valid_years) >= 3:
        qualities = [y["quality_proxy"] for y in valid_years]
        median_q = _median(qualities)
        high_group = [y for y in valid_years if y["quality_proxy"] >= median_q]
        low_group = [y for y in valid_years if y["quality_proxy"] < median_q]
        if high_group and low_group:
            avg_high = sum(y["forward_return"] for y in high_group) / len(high_group)
            avg_low = sum(y["forward_return"] for y in low_group) / len(low_group)
            return_diff = avg_high - avg_low
            if return_diff >= 0.20:
                edge_score = 3
                edge_detail = f"高品質期間の平均フォワードリターン（{avg_high*100:.1f}%）は低品質期間（{avg_low*100:.1f}%）を大きく上回り、質の高さが明確にリターンの優位に繋がっています。"
            elif return_diff >= 0.05:
                edge_score = 2
                edge_detail = f"高品質期間の平均フォワードリターン（{avg_high*100:.1f}%）は低品質期間（{avg_low*100:.1f}%）を上回っており、質の高さが一定のリターン優位に繋がっています。"
            elif return_diff >= -0.05:
                edge_score = 1
                edge_detail = f"高品質期間（{avg_high*100:.1f}%）と低品質期間（{avg_low*100:.1f}%）のリターン差はほぼ無く、質の高さとリターンの関係は明確ではありません。"
            else:
                edge_score = 0
                edge_detail = f"高品質期間の平均フォワードリターン（{avg_high*100:.1f}%）はむしろ低品質期間（{avg_low*100:.1f}%）を下回っており、この銘柄では質の高さがリターンに繋がっていません。"
        else:
            edge_detail = "高品質群・低品質群のいずれかが空のため、リターン差を検証できません（中立評価）。"
    else:
        edge_detail = "フォワードリターンを算出できる決算期が3期未満のため、高品質年と低品質年のリターン差を検証できません（中立評価）。"

    # --- 軸2: 最高品質期間の実績リターン（3点）---
    best_period_score = 1
    best_period_detail = ""
    if valid_years:
        best = max(valid_years, key=lambda y: y["quality_proxy"])
        best_date = best["date"]
        r = best["forward_return"]
        if r >= 0.50:
            best_period_score = 3
            best_period_detail = f"最も簡易品質スコアが高かった決算期（{best_date}）から翌決算期（直近年のみ現在）までのリターンは{r*100:.1f}%と極めて良好です。"
        elif r >= 0.15:
            best_period_score = 2
            best_period_detail = f"最も簡易品質スコアが高かった決算期（{best_date}）から翌決算期（直近年のみ現在）までのリターンは{r*100:.1f}%と良好です。"
        elif r >= 0.0:
            best_period_score = 1
            best_period_detail = f"最も簡易品質スコアが高かった決算期（{best_date}）から翌決算期（直近年のみ現在）までのリターンは{r*100:.1f}%とプラスですが、伸び悩んでいます。"
        else:
            best_period_score = 0
            best_period_detail = f"最も簡易品質スコアが高かった決算期（{best_date}）から翌決算期（直近年のみ現在）までのリターンでも、{r*100:.1f}%とマイナスです。"
    else:
        best_period_detail = "フォワードリターンを算出できる決算期が無いため、最高品質期間の実績を評価できません（中立評価）。"

    # --- 軸3: 一貫性（順位相関）（2点）---
    consistency_score = 1
    consistency_detail = ""
    corr = None
    if len(valid_years) >= 3:
        qs = [y["quality_proxy"] for y in valid_years]
        rs = [y["forward_return"] for y in valid_years]
        corr = _pearson(qs, rs)
        if corr is not None:
            if corr >= 0.5:
                consistency_score = 2
                consistency_detail = f"簡易品質スコアとフォワードリターンの相関係数は{corr:.2f}と強い正の相関があり、質の高さとリターンの関係は一貫しています。"
            elif corr >= 0.0:
                consistency_score = 1
                consistency_detail = f"簡易品質スコアとフォワードリターンの相関係数は{corr:.2f}と弱い正の相関にとどまり、一貫性はやや限定的です。"
            else:
                consistency_score = 0
                consistency_detail = f"簡易品質スコアとフォワードリターンの相関係数は{corr:.2f}と負の相関であり、質の高さとリターンの関係に一貫性が見られません。"
        else:
            consistency_detail = "分散がゼロのため相関係数を算出できません（中立評価）。"
    else:
        consistency_detail = "フォワードリターンを算出できる決算期が3期未満のため、一貫性（相関）を検証できません（中立評価）。"

    # --- 軸4: 現在のBuffett Scoreとの整合性（2点）---
    current_consistency_score = 1
    current_consistency_detail = ""
    current_buffett_score = None
    consistency_warning = None
    if score_result:
        current_buffett_score = score_result.get("total_score")

    if current_buffett_score is not None and edge_score is not None and len(valid_years) >= 3:
        quality_paid_off = edge_score >= 2
        current_high = current_buffett_score >= 70
        if quality_paid_off and current_high:
            current_consistency_score = 2
            current_consistency_detail = "過去は質の高さが実際のリターン優位に繋がっており、現在のBuffett Scoreも高水準であるため、整合的です。"
        elif quality_paid_off and not current_high:
            current_consistency_score = 1
            current_consistency_detail = f"過去は質の高さがリターン優位に繋がっていましたが、現在のBuffett Score（{current_buffett_score}点）は相対的に低水準であり、投資妙味が低下している可能性があります。"
            consistency_warning = "過去の実績では質の高さがリターンに繋がっていましたが、現在のBuffett Scoreは低下しています。ファンダメンタルズの悪化がないか確認してください。"
        elif not quality_paid_off and current_high:
            current_consistency_score = 1
            current_consistency_detail = f"現在のBuffett Score（{current_buffett_score}点）は高水準ですが、この銘柄の過去の実績では質の高さが必ずしも良いリターンに繋がっていません。"
            consistency_warning = "現在のBuffett Scoreは高水準ですが、過去の実績では質の高さとリターンの関係が弱く、定量スコアへの過信に注意が必要です。"
        else:
            current_consistency_score = 2
            current_consistency_detail = "過去も質の高さが明確なリターン優位に繋がっておらず、現在のBuffett Scoreの水準ともおおむね整合的です。"
    else:
        current_consistency_detail = "Buffett Scoreの情報、またはフォワードリターンを算出できる決算期が不足しているため、整合性を評価できません（中立評価）。"

    total_score = edge_score + best_period_score + consistency_score + current_consistency_score

    if total_score >= 8:
        rating = "excellent"
        summary = "過去の実績データは、質の高さが明確にリターンの優位に繋がっていたことを示しています。"
        verdict = "Excellent（優良）"
    elif total_score >= 6:
        rating = "good"
        summary = "過去の実績データは、質の高さがリターンに一定の優位性をもたらしていたことを示しています。"
        verdict = "Good（良好）"
    elif total_score >= 4:
        rating = "average"
        summary = "過去の実績データからは、質の高さとリターンの関係は平均的です。"
        verdict = "Average（平均的）"
    elif total_score >= 2:
        rating = "below_average"
        summary = "過去の実績データでは、質の高さがリターンに明確には繋がっていません。"
        verdict = "Below Average（やや低い）"
    else:
        rating = "poor"
        summary = "過去の実績データでは、質の高さがリターンに繋がっておらず、この銘柄への定量スコアの当てはめには注意が必要です。"
        verdict = "Poor（低い）"

    warnings = []
    if consistency_warning:
        warnings.append(consistency_warning)
    if edge_score == 0:
        warnings.append("この銘柄では、過去の高品質期間が低品質期間よりもリターンが低く、質とリターンが逆相関している可能性があります。")
    if best_period_score == 0:
        warnings.append("最も品質が高かった決算期から翌決算期（直近年のみ現在）までのリターンでも、マイナスです。")

    return {
        "success": True,
        "edge_score": edge_score,
        "edge_detail": edge_detail,
        "best_period_score": best_period_score,
        "best_period_detail": best_period_detail,
        "consistency_score": consistency_score,
        "consistency_detail": consistency_detail,
        "current_consistency_score": current_consistency_score,
        "current_consistency_detail": current_consistency_detail,
        "total_score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": summary,
        "verdict": verdict,
        "warnings": warnings,
        "raw": {
            "years": records,
            "valid_year_count": len(valid_years),
            "return_diff": return_diff,
            "correlation": corr,
            "current_buffett_score": current_buffett_score,
        },
    }
