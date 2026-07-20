import feedparser
from urllib.parse import quote
from newspaper import Article


def get_latest_news(company_name):
    query = quote(company_name)

    url = (
        f"https://news.google.com/rss/search?"
        f"q={query}&hl=ja&gl=JP&ceid=JP:ja"
    )

    feed = feedparser.parse(url)

    news = []

    for entry in feed.entries[:5]:

        article_text = ""

        try:
            article = Article(entry.link, language="ja")
            article.download()
            article.parse()
            article_text = article.text[:4000]
        except Exception:
            article_text = ""

        news.append(
            {
                "title": entry.title,
                "publisher": getattr(entry, "source", {}).get("title", ""),
                "link": entry.link,
                "content": article_text,
            }
        )

    return news