from typing import List

import feedparser
from bs4 import BeautifulSoup
from dateutil import parser

from airembr.model.gui.rss import RssItem
from airembr.sdk.service.remote.http.http_client import HttpClient

RSS_FEEDS = ['https://blog.tracardi.com/rss/', 'https://www.tracardi.com/index.php/feed']
RSS_LIMIT = 15


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from a string."""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=' ', strip=True)


async def fetch_and_parse(url: str) -> List[RssItem]:
    async with HttpClient(2, [200], headers={"Content-Type": "application/rss+xml; charset=UTF-8"}) as client:
        async with client.get(url) as response:
            text = await response.read()
            feed = feedparser.parse(text)
            return [
                RssItem(
                    title=entry.title,
                    description=strip_html_tags(entry.description),
                    link=entry.link,
                    publish_date=parser.parse(entry.published)
                )
                for entry in feed.entries
            ]


async def get_rss() -> List[RssItem]:
    all_entries = []
    for url in RSS_FEEDS:
        all_entries.extend(await fetch_and_parse(url))

    return sorted(all_entries, key=lambda x: x.publish_date, reverse=True)[:RSS_LIMIT]
