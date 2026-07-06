import yfinance as yf


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
        }

        return {"success": True, "data": data}

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
