"""data: data fetching only (Sprint18)"""
from .data_fetcher import get_stock_data, format_value
from .news_fetcher import get_latest_news

__all__ = ["get_stock_data", "format_value", "get_latest_news"]