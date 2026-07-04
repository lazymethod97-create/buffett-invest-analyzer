import yfinance as yf
from src.utils import normalize_ticker

class StockDataFetcher:
    def __init__(self, symbol):
        self.symbol = normalize_ticker(symbol)
        self.stock = yf.Ticker(self.symbol)

    def fetch(self):
        info = self.stock.info

        return {
            "ticker": self.symbol,
            "company_name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "roe": info.get("returnOnEquity"),
            "per": info.get("trailingPE"),
            "pbr": info.get("priceToBook"),
            "market_cap": info.get("marketCap"),
        }
