import yfinance as yf


def _extract_buyback_amount(stock) -> float:
    """
    現金フロー計算書から自社株買い額を取得する（Sprint22）。
    yfinanceのバージョン・企業によってラベル名が揺れるため、複数の候補から探す。
    取得できない場合はNoneを返す（絶対に例外を投げない）。
    """
    try:
        cf = stock.cashflow
        if cf is None or cf.empty:
            return None
        candidates = [
            "Repurchase Of Capital Stock",
            "BuyBack Shares",
            "Common Stock Repurchased",
            "Common Stock Repurchase",
            "Stock Repurchased",
            "Stock Buyback",
        ]
        for label in candidates:
            if label in cf.index:
                vals = cf.loc[label].dropna()
                if len(vals) > 0:
                    return abs(float(vals.iloc[0]))
    except Exception:
        pass
    return None


def _extract_buyback_history(stock) -> list:
    """
    自社株買い額の複数年推移を取得する（Sprint23）。
    _extract_buyback_amount()と同じラベル候補を使い、直近年から古い年の順で
    利用可能な全年度分をリストで返す（最新年が先頭）。
    取得できない場合は空リストを返す（絶対に例外を投げない）。
    """
    try:
        cf = stock.cashflow
        if cf is None or cf.empty:
            return []
        candidates = [
            "Repurchase Of Capital Stock",
            "BuyBack Shares",
            "Common Stock Repurchased",
            "Common Stock Repurchase",
            "Stock Repurchased",
            "Stock Buyback",
        ]
        for label in candidates:
            if label in cf.index:
                vals = cf.loc[label].dropna()
                if len(vals) > 0:
                    return [abs(float(v)) for v in vals.tolist()]
    except Exception:
        pass
    return []


def _extract_shares_history(stock) -> list:
    """
    発行済株式数（期中平均）の複数年推移を取得する（Sprint23）。
    損益計算書（income_stmt）の基準株式数行から、直近年から古い年の順で返す。
    取得できない場合は空リストを返す（絶対に例外を投げない）。
    """
    try:
        stmt = stock.income_stmt
        if stmt is None or stmt.empty:
            return []
        candidates = [
            "Basic Average Shares",
            "Diluted Average Shares",
        ]
        for label in candidates:
            if label in stmt.index:
                vals = stmt.loc[label].dropna()
                if len(vals) > 0:
                    return [float(v) for v in vals.tolist()]
    except Exception:
        pass
    return []


def _extract_debt_history(stock) -> list:
    """
    総負債の複数年推移を取得する（Sprint23）。
    貸借対照表（balance_sheet）から、直近年から古い年の順で返す。
    取得できない場合は空リストを返す（絶対に例外を投げない）。
    """
    try:
        bs = stock.balance_sheet
        if bs is None or bs.empty:
            return []
        if "Total Debt" in bs.index:
            vals = bs.loc["Total Debt"].dropna()
            if len(vals) > 0:
                return [float(v) for v in vals.tolist()]
        # フォールバック: 長期負債＋短期負債の合算
        lt = bs.loc["Long Term Debt"] if "Long Term Debt" in bs.index else None
        st = bs.loc["Current Debt"] if "Current Debt" in bs.index else None
        if lt is not None:
            combined = []
            for i in range(len(lt)):
                lt_v = lt.iloc[i] if i < len(lt) else 0
                st_v = st.iloc[i] if st is not None and i < len(st) else 0
                lt_v = 0 if lt_v is None or (hasattr(lt_v, "__float__") is False) else lt_v
                st_v = 0 if st_v is None else st_v
                try:
                    combined.append(float(lt_v) + float(st_v))
                except Exception:
                    continue
            if combined:
                return combined
    except Exception:
        pass
    return []


def _extract_interest_expense(stock) -> float:
    """
    支払利息（Interest Expense）を取得する（Sprint24、インタレスト・カバレッジ・レシオ用）。
    損益計算書（income_stmt）から直近年度分を取得する。
    yfinanceのバージョン・企業によってラベル名が揺れるため、複数の候補から探す。
    取得できない場合はNoneを返す（絶対に例外を投げない）。
    """
    try:
        stmt = stock.income_stmt
        if stmt is None or stmt.empty:
            return None
        candidates = [
            "Interest Expense",
            "Interest Expense Non Operating",
            "Net Interest Income",
        ]
        for label in candidates:
            if label in stmt.index:
                vals = stmt.loc[label].dropna()
                if len(vals) > 0:
                    return abs(float(vals.iloc[0]))
    except Exception:
        pass
    return None


def _extract_avg_price_5y(stock) -> float:
    """
    過去5年間の終値平均を取得する（Sprint23、PER水準比較用の簡易推定に使用）。
    取得できない場合はNoneを返す（絶対に例外を投げない）。
    """
    try:
        hist = stock.history(period="5y")
        if hist is None or hist.empty or "Close" not in hist.columns:
            return None
        closes = hist["Close"].dropna()
        if len(closes) == 0:
            return None
        return float(closes.mean())
    except Exception:
        return None


def _extract_revenue_history(stock) -> list:
    """
    売上高の複数年推移を取得する（Sprint25、市場地位の安定性・利益率計算用）。
    損益計算書（income_stmt）から、直近年から古い年の順で返す。
    取得できない場合は空リストを返す（絶対に例外を投げない）。
    """
    try:
        stmt = stock.income_stmt
        if stmt is None or stmt.empty:
            return []
        if "Total Revenue" in stmt.index:
            vals = stmt.loc["Total Revenue"].dropna()
            if len(vals) > 0:
                return [float(v) for v in vals.tolist()]
    except Exception:
        pass
    return []


def _extract_operating_margin_history(stock) -> list:
    """
    営業利益率の複数年推移を取得する（Sprint25、収益性の持続性・安定性の検証用）。
    損益計算書（income_stmt）の営業利益 ÷ 売上高を、各年ごとに算出する。
    yfinanceのバージョン・企業によってラベル名が揺れるため、複数の候補から探す。
    取得できない場合は空リストを返す（絶対に例外を投げない）。
    """
    try:
        stmt = stock.income_stmt
        if stmt is None or stmt.empty or "Total Revenue" not in stmt.index:
            return []
        op_candidates = ["Operating Income", "Total Operating Income As Reported", "EBIT"]
        op_row = None
        for label in op_candidates:
            if label in stmt.index:
                op_row = stmt.loc[label]
                break
        if op_row is None:
            return []
        rev_row = stmt.loc["Total Revenue"]
        margins = []
        for col in stmt.columns:
            op_v = op_row.get(col)
            rev_v = rev_row.get(col)
            if op_v is None or rev_v is None:
                continue
            try:
                rev_f = float(rev_v)
                if rev_f != 0:
                    margins.append(float(op_v) / rev_f)
            except Exception:
                continue
        return margins
    except Exception:
        return []


def _extract_gross_margin_history(stock) -> list:
    """
    粗利率（売上総利益率）の複数年推移を取得する（Sprint25、価格決定力の定量的検証用）。
    損益計算書（income_stmt）の売上総利益 ÷ 売上高を、各年ごとに算出する。
    売上総利益が取得できない場合はEBITDAマージンにフォールバックする。
    取得できない場合は空リストを返す（絶対に例外を投げない）。
    """
    try:
        stmt = stock.income_stmt
        if stmt is None or stmt.empty or "Total Revenue" not in stmt.index:
            return []
        rev_row = stmt.loc["Total Revenue"]
        margin_row = None
        if "Gross Profit" in stmt.index:
            margin_row = stmt.loc["Gross Profit"]
        elif "EBITDA" in stmt.index:
            margin_row = stmt.loc["EBITDA"]
        if margin_row is None:
            return []
        margins = []
        for col in stmt.columns:
            m_v = margin_row.get(col)
            rev_v = rev_row.get(col)
            if m_v is None or rev_v is None:
                continue
            try:
                rev_f = float(rev_v)
                if rev_f != 0:
                    margins.append(float(m_v) / rev_f)
            except Exception:
                continue
        return margins
    except Exception:
        return []


def _extract_roe_history(stock) -> list:
    """
    ROE（自己資本利益率）の複数年推移を取得する（Sprint25、収益性の持続性・安定性の検証用）。
    損益計算書（income_stmt）の当期純利益 ÷ 貸借対照表（balance_sheet）の自己資本を、
    各年ごとに算出する（年度末時点の自己資本を使用する簡易計算）。
    取得できない場合は空リストを返す（絶対に例外を投げない）。
    """
    try:
        stmt = stock.income_stmt
        bs = stock.balance_sheet
        if stmt is None or stmt.empty or bs is None or bs.empty:
            return []
        ni_candidates = ["Net Income", "Net Income Common Stockholders"]
        ni_row = None
        for label in ni_candidates:
            if label in stmt.index:
                ni_row = stmt.loc[label]
                break
        eq_candidates = ["Stockholders Equity", "Total Stockholder Equity", "Common Stock Equity"]
        eq_row = None
        for label in eq_candidates:
            if label in bs.index:
                eq_row = bs.loc[label]
                break
        if ni_row is None or eq_row is None:
            return []
        roe_list = []
        for col in stmt.columns:
            ni_v = ni_row.get(col)
            eq_v = eq_row.get(col)
            if ni_v is None or eq_v is None:
                continue
            try:
                eq_f = float(eq_v)
                if eq_f != 0:
                    roe_list.append(float(ni_v) / eq_f)
            except Exception:
                continue
        return roe_list
    except Exception:
        return []


def get_stock_data(ticker: str) -> dict:
    """
    ティッカーシンボルから財務データを取得する。
    日本株の場合は4桁の数字を入れるだけで自動的に .T を付ける（例: 7203 → 7203.T）
    米国株はそのまま入力する（例: AAPL）
    """

    ticker = ticker.strip().upper()

    # 日本株の処理（数字4桁なら .T を付ける）
    if ticker.isdigit() and len(ticker) == 4:
        ticker = ticker + ".T"

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        data = {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "不明"),
            "industry": info.get("industry", "不明"),
            "country": info.get("country", "不明"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "market_cap": info.get("marketCap", 0),

            # バフェット判定に使う指標
            "roe": info.get("returnOnEquity"),
            "roa": info.get("returnOnAssets"),
            "operating_margin": info.get("operatingMargins"),
            "profit_margin": info.get("profitMargins"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "free_cashflow": info.get("freeCashflow"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "dividend_yield": info.get("dividendYield"),
            "operating_income": info.get("operatingIncome"),
            "income_tax_expense": info.get("incomeTaxExpense"),
            "income_before_tax": info.get("incomeBeforeTax"),
            "long_term_debt": info.get("longTermDebt"),
            "short_term_debt": info.get("shortLongTermDebt"),
            "total_equity": info.get("totalStockholderEquity"),
            "cash": info.get("cash"),
            "short_term_investments": info.get("shortTermInvestments"),
            "total_assets": info.get("totalAssets"),
            "total_current_assets": info.get("totalCurrentAssets"),
            "total_current_liabilities": info.get("totalCurrentLiabilities"),


            # Sprint19: ROIC分析用データ
            "operating_income": info.get("operatingIncome") or info.get("ebit"),
            "ebit": info.get("operatingIncome") or info.get("ebit"),
            "pretax_income": info.get("pretaxIncome"),
            "income_tax_expense": info.get("incomeTaxExpense"),
            "tax_rate": info.get("taxRate"),
            "total_assets": info.get("totalAssets"),
            "total_debt": info.get("totalDebt"),
            "total_cash": info.get("totalCash"),
            "stockholder_equity": info.get("totalStockholderEquity"),

            # Sprint20: Owner Earnings分析用データ
            "net_income": info.get("netIncomeToCommon"),
            "ebitda": info.get("ebitda"),
            "operating_cashflow": info.get("operatingCashflow"),
            "total_revenue": info.get("totalRevenue"),
            "shares_outstanding": info.get("sharesOutstanding"),

            # Sprint22: Capital Allocation分析用データ
            "payout_ratio": info.get("payoutRatio"),
            "buyback_amount": _extract_buyback_amount(stock),

            # Sprint23: Share Buyback分析用データ
            "buyback_history": _extract_buyback_history(stock),
            "shares_outstanding_history": _extract_shares_history(stock),
            "total_debt_history": _extract_debt_history(stock),
            "avg_price_5y": _extract_avg_price_5y(stock),
            "trailing_eps": info.get("trailingEps"),

            # Sprint24: Debt Quality分析用データ
            "interest_expense": _extract_interest_expense(stock),

            # Sprint25: Economic Moat強化分析用データ
            "revenue_history": _extract_revenue_history(stock),
            "operating_margin_history": _extract_operating_margin_history(stock),
            "gross_margin_history": _extract_gross_margin_history(stock),
            "roe_history": _extract_roe_history(stock),
        }

        return {"success": True, "error": None, "data": data}

    except Exception as e:
        return {"success": False, "error": str(e), "data": None}


def format_value(value, format_type: str = "percent") -> str:
    """数値を表示用にフォーマットする"""
    if value is None:
        return "データなし"

    if format_type == "percent":
        return f"{value * 100:.1f}%"
    elif format_type == "ratio":
        return f"{value:.2f}"
    elif format_type == "currency_b":
        return f"{value / 1_000_000_000:.1f}B"
    else:
        return str(value)

