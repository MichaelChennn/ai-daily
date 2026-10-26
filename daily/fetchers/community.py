"""Tier-2 community signals: Hacker News (Algolia API) and Reddit (public RSS).

These are heat signals, not facts: when they link to a first-hand page, dedup merges them into
that page's candidate and the score travels along as a signal.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import feedparser
import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, get, is_ai_related
from daily.fetchers.feeds import entry_datetime
from daily.models import Candidate
from daily.text import clean_text, clean_title, truncate
from daily.window import Window

HN_ITEM_URL = "https://news.ycombinator.com/item?id={}"


async def fetch_hackernews(
    client: httpx.AsyncClient, source: SourceConfig, window: Window
) -> list[Candidate]:
    """Options: min_points (default 50), extra_keywords."""
    min_points = int(source.options.get("min_points", 50))
    extra = source.options.get("extra_keywords", [])
    filters = (
        f"created_at_i>={int(window.start.timestamp())},"
        f"created_at_i<{int(window.end.timestamp())},points>={min_points}"
    )
    response = await get(
        client,
        "https://hn.algolia.com/api/v1/search_by_date",
        params={"tags": "story", "numericFilters": filters, "hitsPerPage": 1000},
    )

    items: list[Candidate] = []
    for hit in response.json().get("hits", []):
        title = clean_title(hit.get("title"))
        if not title or not is_ai_related(title, extra_keywords=extra):
            continue
        discussion = HN_ITEM_URL.format(hit["objectID"])
        items.append(
            candidate(
                source,
                title=title,
                url=hit.get("url") or discussion,
                summary=truncate(clean_text(hit.get("story_text")), SUMMARY_MAX_CHARS),
                published_at=datetime.fromtimestamp(hit["created_at_i"], timezone.utc),
                discussion_url=discussion,
                signals={"hn_points": hit.get("points") or 0, "hn_comments": hit.get("num_comments") or 0},
            )
        )
    return items


_LINK = re.compile(r"<a href=\"([^\"]+)\">\s*\[link\]\s*</a>")
_SUBMITTED_BY = re.compile(r"submitted by .*", re.S)


async def fetch_reddit(client: httpx.AsyncClient, source: SourceConfig, window: Window) -> list[Candidate]:
    """Options: subreddit (several joined with '+'); limit (default 25). Uses the 'top of the day' RSS feed.

    The JSON API rejects anonymous cloud clients; RSS works but carries no score, so the rank in
    today's top list is the signal.
    """
    subreddit = source.options["subreddit"]
    response = await get(
        client,
        f"https://www.reddit.com/r/{subreddit}/top/.rss",
        params={"t": "day", "limit": int(source.options.get("limit", 25))},
    )
    feed = feedparser.parse(response.content)
    if feed.bozo and not feed.entries:
        raise ValueError(f"unparseable feed: {feed.bozo_exception}")

    items: list[Candidate] = []
    for rank, entry in enumerate(feed.entries, start=1):
        published = entry_datetime(entry)
        if not window.contains(published):
            continue
        comments = entry.get("link")
        title = clean_title(entry.get("title"))
        if not comments or not title:
            continue
        content = entry.get("content") or []
        html = content[0].get("value", "") if content else entry.get("summary", "")
        link = _LINK.search(html)
        url = urljoin(comments, link.group(1)) if link else comments
        body = _SUBMITTED_BY.sub("", clean_text(html)).strip()
        tags = entry.get("tags") or []  # a multi-subreddit feed tags each entry with its own
        items.append(
            candidate(
                source,
                title=title,
                url=url,
                summary=truncate(body, SUMMARY_MAX_CHARS),
                published_at=published,
                discussion_url=comments,
                signals={"reddit_rank": rank, "subreddit": tags[0].get("term") if tags else subreddit},
            )
        )
    return items
