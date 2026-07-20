import feedparser
from urllib.parse import quote


def get_latest_news(company_name):
	"""
	Google News RSSから企業名でニュースを取得
	"""

	query = quote(company_name)

	url = (
		f"https://news.google.com/rss/search?"
		f"q={query}&hl=ja&gl=JP&ceid=JP:ja"
	)

	feed = feedparser.parse(url)

	news = []

	for entry in feed.entries[:5]:
		news.append(
			{
				"title": entry.title,
				"publisher": getattr(entry, "source", {}).get("title", ""),
				"link": entry.link,
			}
		)

	return news


