"""
Owner Earnings（オーナーアーニングス）計算エンジン（Sprint20）

バフェットが1986年のBerkshire Hathaway株主への手紙で提唱した「本当の利益」の指標。
会計上の純利益ではなく、株主が実質的に自由に使える現金創出力を測る。

Owner Earnings = 当期純利益 + 減価償却費等（非現金費用） - 設備投資（CapEx）

減価償却費等（D&A）と設備投資（CapEx）は、取得可能なデータから以下のように推定する。
  D&A   ≈ EBITDA - 営業利益（EBIT）
  CapEx ≈ 営業キャッシュフロー - フリーキャッシュフロー

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any


def calculate_owner_earnings(data: Dict[str, Any]) -> Dict[str, Any]:
    """Owner Earnings計算。引数dataはget_stock_data()の戻り値。"""
    net_income = data.get("net_income")
    ebitda = data.get("ebitda")
    operating_income = data.get("operating_income") or data.get("ebit")
    operating_cashflow = data.get("operating_cashflow")
    free_cashflow = data.get("free_cashflow")
    market_cap = data.get("market_cap")
    total_revenue = data.get("total_revenue")

    # --- 減価償却費等（D&A）の推定 ---
    da = None
    if ebitda is not None and operating_income is not None:
        estimated_da = ebitda - operating_income
        if estimated_da >= 0:
            da = estimated_da

    # --- 設備投資（CapEx）の推定 ---
    capex = None
    if operating_cashflow is not None and free_cashflow is not None:
        estimated_capex = operating_cashflow - free_cashflow
        capex = estimated_capex if estimated_capex >= 0 else 0

    # --- Owner Earnings ---
    owner_earnings = None
    if net_income is not None:
        owner_earnings = net_income + (da or 0) - (capex or 0)

    # --- Owner Earnings Yield（時価総額に対する実質利回り）---
    oe_yield = None
    if owner_earnings is not None and market_cap:
        oe_yield = owner_earnings / market_cap

    # --- Owner Earnings Margin（売上高に対する比率）---
    oe_margin = None
    if owner_earnings is not None and total_revenue:
        oe_margin = owner_earnings / total_revenue

    result: Dict[str, Any] = {
        "success": owner_earnings is not None,
        "net_income": net_income,
        "depreciation_amortization": da,
        "capital_expenditures": capex,
        "owner_earnings": owner_earnings,
        "owner_earnings_yield": oe_yield,
        "owner_earnings_margin": oe_margin,
    }

    warnings = []
    if da is None:
        warnings.append("減価償却費等（D&A）のデータが取得できないため、0として計算しています。")
    if capex is None:
        warnings.append("設備投資（CapEx）のデータが取得できないため、0として計算しています。")

    if oe_yield is not None:
        if oe_yield >= 0.08:
            result["rating"] = "excellent"
            result["summary"] = "Owner Earnings利回り8%以上。極めて高い株主価値創出力です。"
            result["verdict"] = "Excellent（優良）"
        elif oe_yield >= 0.05:
            result["rating"] = "good"
            result["summary"] = "Owner Earnings利回り5%以上。良好な現金創出力です。"
            result["verdict"] = "Good（良好）"
        elif oe_yield >= 0.03:
            result["rating"] = "average"
            result["summary"] = "Owner Earnings利回り3%以上。業界平均的な水準です。"
            result["verdict"] = "Average（平均的）"
        elif oe_yield >= 0.0:
            result["rating"] = "below_average"
            result["summary"] = "Owner Earnings利回りが低水準です。"
            result["verdict"] = "Below Average（やや低い）"
        else:
            result["rating"] = "poor"
            result["summary"] = "Owner Earningsがマイナスです。実質的な現金創出ができていません。"
            result["verdict"] = "Poor（低い）"
    else:
        result["rating"] = "unknown"
        if net_income is None:
            result["summary"] = "当期純利益のデータが不足しています。"
        elif not market_cap:
            result["summary"] = "時価総額のデータが不足しています。"
        else:
            result["summary"] = "Owner Earnings計算に必要なデータが不足しています。"
        result["verdict"] = "データ不足"

    result["warnings"] = warnings
    return result

