"""
Portfolio Risk（保有ポートフォリオのリスク分散評価）計算エンジン（Sprint27）

「保有銘柄全体として、リスクがどれだけ分散されているか」を検証する機能。

制約と設計方針
---------------------------------
既存のBuffett Score（scoring_engine.py、190点満点）をはじめとする全エンジンは
「単一銘柄」を評価単位とするが、本エンジンは「複数銘柄からなるポートフォリオ全体」を
評価単位とする点で根本的に異なる。そのため、overall_eval.pyの総合判定
（BUY/WATCH/PASS、単一銘柄向け）には組み込まず、独立したポートフォリオレベルの
分析軸として実装する（重複実装禁止・ルール14。既存のPortfolioManager／
data_fetcher.get_stock_dataは再利用のみで再実装しない。設計判断の詳細は
docs/AI_HANDOVER.mdのSprint27セクションを参照）。

評価軸（4観点、合計10点）
1. セクター分散度（3点）: 時価評価額ベースのセクター別構成比から
   HHI（ハーフィンダール・ハーシュマン指数、構成比の二乗和）を算出して評価する。
   HHIが低いほど特定セクターへの依存が小さく、分散されている。
2. 銘柄集中度（3点）: 時価評価額ベースで最大の構成比を持つ1銘柄の比率を評価する。
   セクター分散度（軸1）とは異なり、同一セクター内であっても特定の1社に
   偏っていないかを個別銘柄単位で検証する。
3. 地域分散度（2点）: 国内（日本）／海外の構成比の内訳を評価する。
   一方に極端に偏っている場合、為替・地域固有リスクへの耐性が低いと判断する。
4. 保有銘柄数の充足度（2点）: 分散効果を得るために必要な最低限の銘柄数が
   確保されているかを評価する（銘柄数が極端に少ないと、他の軸のスコアが
   高くても実際の分散効果は乏しい）。

いずれの軸も、時価評価額を算出できる銘柄が1件も無い場合は分析不能として扱い、
絶対に例外を投げない。

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any, List


def _market_value(holding: Dict[str, Any]) -> float:
    shares = holding.get("shares") or 0
    price = holding.get("current_price") or 0
    try:
        return float(shares) * float(price)
    except (TypeError, ValueError):
        return 0.0


def _hhi(weights: List[float]) -> float:
    return sum(w * w for w in weights)


def calculate_portfolio_risk(holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    保有銘柄のリスク分散度を評価する。

    引数
    ----
    holdings: 各銘柄の辞書のリスト。以下のキーを使用する。
        ticker (str), company_name (str), shares (float),
        current_price (float), sector (str), country (str)
        （いずれもdata_fetcher.get_stock_data()が返す既存フィールドを再利用。
        新規のデータ取得は行わない。ルール14）

    戻り値
    ----
    success, sector_score, concentration_score, region_score, count_score,
    total_score, max_score, rating, summary, verdict, warnings, raw
    """
    valid = [h for h in holdings if _market_value(h) > 0]
    excluded_count = len(holdings) - len(valid)
    n = len(valid)

    if n == 0:
        return {
            "success": False,
            "error": "時価評価額を算出できる保有銘柄がありません。",
            "sector_score": 0,
            "concentration_score": 0,
            "region_score": 0,
            "count_score": 0,
            "total_score": 0,
            "max_score": 10,
            "rating": "no_data",
            "summary": "分析可能な保有銘柄がないため、リスク分散評価を実施できません。",
            "verdict": "データなし",
            "warnings": [],
            "raw": {
                "holding_count": 0,
                "excluded_count": excluded_count,
                "sector_weights": {},
                "country_weights": {},
                "holding_weights": [],
                "hhi_sector": None,
                "max_holding_weight": None,
                "max_holding_ticker": None,
                "total_market_value": 0.0,
            },
        }

    total_value = sum(_market_value(h) for h in valid)

    holding_weights = []
    for h in valid:
        mv = _market_value(h)
        holding_weights.append({
            "ticker": h.get("ticker", ""),
            "company_name": h.get("company_name") or h.get("ticker", ""),
            "market_value": mv,
            "weight": (mv / total_value) if total_value > 0 else 0.0,
            "sector": h.get("sector") or "不明",
            "country": h.get("country") or "不明",
        })

    sector_weights: Dict[str, float] = {}
    for w in holding_weights:
        sector_weights[w["sector"]] = sector_weights.get(w["sector"], 0.0) + w["weight"]

    country_weights: Dict[str, float] = {}
    for w in holding_weights:
        country_weights[w["country"]] = country_weights.get(w["country"], 0.0) + w["weight"]

    hhi_sector = _hhi(list(sector_weights.values()))
    max_holding = max(holding_weights, key=lambda w: w["weight"])
    max_holding_weight = max_holding["weight"]
    max_ticker = max_holding["ticker"]

    # --- 軸1: セクター分散度（3点）---
    if hhi_sector <= 0.20:
        sector_score = 3
        sector_detail = f"セクター別構成比のHHI（{hhi_sector:.2f}）は低く、特定セクターへの依存が小さい良好な分散状態です。"
    elif hhi_sector <= 0.35:
        sector_score = 2
        sector_detail = f"セクター別構成比のHHI（{hhi_sector:.2f}）はやや低く、一定のセクター分散ができています。"
    elif hhi_sector <= 0.50:
        sector_score = 1
        sector_detail = f"セクター別構成比のHHI（{hhi_sector:.2f}）はやや高く、特定セクターへの依存が見られます。"
    else:
        sector_score = 0
        sector_detail = f"セクター別構成比のHHI（{hhi_sector:.2f}）は高く、特定セクターに大きく偏っています。"

    # --- 軸2: 銘柄集中度（3点）---
    if max_holding_weight <= 0.15:
        concentration_score = 3
        concentration_detail = f"最大保有銘柄（{max_ticker}）の構成比は{max_holding_weight*100:.1f}%と低く、個別銘柄リスクは抑えられています。"
    elif max_holding_weight <= 0.25:
        concentration_score = 2
        concentration_detail = f"最大保有銘柄（{max_ticker}）の構成比は{max_holding_weight*100:.1f}%であり、概ね妥当な水準です。"
    elif max_holding_weight <= 0.40:
        concentration_score = 1
        concentration_detail = f"最大保有銘柄（{max_ticker}）の構成比は{max_holding_weight*100:.1f}%とやや高く、個別銘柄リスクに注意が必要です。"
    else:
        concentration_score = 0
        concentration_detail = f"最大保有銘柄（{max_ticker}）の構成比は{max_holding_weight*100:.1f}%と非常に高く、その銘柄固有のリスクにポートフォリオ全体が大きく左右される状態です。"

    # --- 軸3: 地域分散度（2点）---
    domestic_weight = country_weights.get("Japan", 0.0)
    overseas_weight = max(0.0, 1.0 - domestic_weight)
    minor_side_weight = min(domestic_weight, overseas_weight)
    if minor_side_weight >= 0.30:
        region_score = 2
        region_detail = f"国内（{domestic_weight*100:.1f}%）・海外（{overseas_weight*100:.1f}%）ともに一定の比率があり、地域分散ができています。"
    elif minor_side_weight >= 0.10:
        region_score = 1
        region_detail = f"国内（{domestic_weight*100:.1f}%）・海外（{overseas_weight*100:.1f}%）のいずれかに偏りがあり、地域分散はやや限定的です。"
    else:
        region_score = 0
        region_detail = f"国内（{domestic_weight*100:.1f}%）・海外（{overseas_weight*100:.1f}%）の一方にほぼ集中しており、地域分散ができていません。"

    # --- 軸4: 保有銘柄数の充足度（2点）---
    if n >= 8:
        count_score = 2
        count_detail = f"保有銘柄数は{n}銘柄であり、分散効果を得るために十分な数が確保されています。"
    elif n >= 4:
        count_score = 1
        count_detail = f"保有銘柄数は{n}銘柄であり、最低限の分散はできていますが、さらに銘柄を増やすことで分散効果を高められます。"
    else:
        count_score = 0
        count_detail = f"保有銘柄数は{n}銘柄と少なく、他の軸のスコアが高くても実際の分散効果は限定的です。"

    total_score = sector_score + concentration_score + region_score + count_score

    if total_score >= 8:
        rating = "excellent"
        summary = "セクター・銘柄・地域のいずれの観点からも、リスクが良好に分散されたポートフォリオです。"
        verdict = "Excellent（優良）"
    elif total_score >= 6:
        rating = "good"
        summary = "全体としてリスク分散はできていますが、一部の軸に改善の余地があります。"
        verdict = "Good（良好）"
    elif total_score >= 4:
        rating = "average"
        summary = "リスク分散は平均的な水準です。集中している軸を中心に見直しの余地があります。"
        verdict = "Average（平均的）"
    elif total_score >= 2:
        rating = "below_average"
        summary = "特定のセクター・銘柄・地域への偏りが見られ、リスク分散はやや不十分です。"
        verdict = "Below Average（やや低い）"
    else:
        rating = "poor"
        summary = "リスクがほとんど分散されておらず、特定の要因による下落の影響を大きく受けやすい状態です。"
        verdict = "Poor（低い）"

    warnings = []
    if concentration_score == 0:
        warnings.append(f"最大保有銘柄（{max_ticker}）への集中度が非常に高く、個別銘柄リスクが大きい状態です。")
    if sector_score == 0:
        top_sector = max(sector_weights.items(), key=lambda kv: kv[1])
        warnings.append(f"特定セクター（{top_sector[0]}、構成比{top_sector[1]*100:.1f}%）への依存度が高く、セクターごとの逆風に弱い可能性があります。")
    if count_score == 0:
        warnings.append("保有銘柄数が少なく、十分な分散効果を得られていない可能性があります。")
    if region_score == 0:
        warnings.append("国内・海外のいずれか一方に偏っており、地域固有リスク（為替・規制等）への耐性が低い可能性があります。")
    if excluded_count > 0:
        warnings.append(f"データを取得できなかった{excluded_count}銘柄は集計から除外されています（参考値としてご覧ください）。")

    return {
        "success": True,
        "sector_score": sector_score,
        "sector_detail": sector_detail,
        "concentration_score": concentration_score,
        "concentration_detail": concentration_detail,
        "region_score": region_score,
        "region_detail": region_detail,
        "count_score": count_score,
        "count_detail": count_detail,
        "total_score": total_score,
        "max_score": 10,
        "rating": rating,
        "summary": summary,
        "verdict": verdict,
        "warnings": warnings,
        "raw": {
            "holding_count": n,
            "excluded_count": excluded_count,
            "sector_weights": sector_weights,
            "country_weights": country_weights,
            "holding_weights": holding_weights,
            "hhi_sector": hhi_sector,
            "max_holding_weight": max_holding_weight,
            "max_holding_ticker": max_ticker,
            "total_market_value": total_value,
        },
    }
