"""
Market data service.

Version: 0.3.3
"""

import yfinance as yf


def get_company_name(ticker: str) -> str:
    """
    銘柄コードから企業名を取得する。
    """

    ticker = ticker.strip().upper()

    # 日本株なら .T を付与
    if ticker.isdigit():
        ticker = f"{ticker}.T"

    stock = yf.Ticker(ticker)

    try:
        info = stock.info

        return info.get("longName") or info.get("shortName") or "企業名が取得できませんでした"

    except Exception:
        return "企業情報を取得できませんでした"
