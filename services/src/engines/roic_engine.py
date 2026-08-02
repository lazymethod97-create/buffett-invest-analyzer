"""
ROIC（投下資本利益率）計算エンジン（Sprint19）

ROIC = NOPAT / Invested Capital

NOPAT = Operating Income * (1 - Effective Tax Rate)
Invested Capital = Total Equity + Total Debt - Cash & Short-term Investments

すべてルールベース。AIは使用しない。
"""

from typing import Dict, Any


def calculate_roic(data: Dict[str, Any]) -> Dict[str, Any]:
    """ROIC計算。引数dataはget_stock_data()の戻り値。"""
    op_income = data.get("operating_income")
    income_tax = data.get("income_tax_expense")
    income_before_tax = data.get("income_before_tax")
    lt_debt = data.get("long_term_debt")
    st_debt = data.get("short_term_debt")
    equity = data.get("total_equity")
    cash = data.get("cash")
    st_inv = data.get("short_term_investments")

    # --- NOPAT ---
    nopat = None
    tax_rate = 0.25
    if op_income is not None:
        if income_before_tax and income_before_tax > 0 and income_tax is not None:
            raw_tax = income_tax / income_before_tax
            tax_rate = max(0.0, min(raw_tax, 0.50))
        nopat = op_income * (1 - tax_rate)

    # --- 投下資本 ---
    total_debt = None
    cash_and_equiv = None
    invested_capital = None
    if lt_debt is not None or st_debt is not None:
        total_debt = (lt_debt or 0) + (st_debt or 0)
    if cash is not None or st_inv is not None:
        cash_and_equiv = (cash or 0) + (st_inv or 0)
    if equity is not None:
        invested_capital = equity + (total_debt or 0) - (cash_and_equiv or 0)

    # --- ROIC ---
    roic = None
    if nopat is not None and invested_capital is not None and invested_capital > 0:
        roic = nopat / invested_capital

    result = {
        "success": nopat is not None and invested_capital is not None,
        "nopat": nopat,
        "invested_capital": invested_capital,
        "roic": roic,
        "tax_rate": tax_rate,
        "total_debt": total_debt,
        "cash_and_equivalents": cash_and_equiv,
        "operating_income": op_income,
    }

    if roic is not None:
        if roic >= 0.20:
            result["rating"] = "excellent"
            result["summary"] = "ROIC 20%以上。強力な競争優位性を証明しています。"
            result["verdict"] = "Excellent（優良）"
        elif roic >= 0.15:
            result["rating"] = "good"
            result["summary"] = "ROIC 15%以上。良好な資本効率。"
            result["verdict"] = "Good（良好）"
        elif roic >= 0.10:
            result["rating"] = "average"
            result["summary"] = "ROIC 10%以上。業界平均的水準。"
            result["verdict"] = "Average（平均的）"
        elif roic >= 0.05:
            result["rating"] = "below_average"
            result["summary"] = "ROIC 5%以上。資本コストをやや上回る。"
            result["verdict"] = "Below Average（やや低い）"
        else:
            result["rating"] = "poor"
            result["summary"] = "ROIC 5%未満。価値創造ができていません。"
            result["verdict"] = "Poor（低い）"
    else:
        result["rating"] = "unknown"
        if nopat is None:
            result["summary"] = "営業利益のデータが不足しています。"
        elif invested_capital is None:
            result["summary"] = "純資産のデータが不足しています。"
        elif invested_capital <= 0:
            result["summary"] = "投下資本がゼロまたはマイナスです。"
        else:
            result["summary"] = "ROIC計算に必要なデータが不足しています。"
        result["verdict"] = "データ不足"

    return result
