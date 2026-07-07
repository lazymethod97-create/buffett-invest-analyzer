import yfinance as yf


def get_latest_news(ticker):

    if ticker.isdigit() and len(ticker) == 4:
        ticker += ".T"

    try:

        stock = yf.Ticker(ticker)

        news = stock.news

        if not news:
            return []

        result = []

        for article in news[:5]:

            result.append({
                "title": article.get("title", ""),
                "publisher": article.get("publisher", ""),
                "link": article.get("link", "")
            })

        return result

    except Exception:

        return []
