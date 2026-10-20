"""Generic RSS/Atom feeds."""

from __future__ import annotations

from datetime import datetime, timezone
from time import struct_time

import feedparser
import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, get
from daily.models import Candidate
from daily.text import clean_text, clean_title, parse_datetime, truncate
from daily.window import Window


async def fetch_rss(client: httpx.AsyncClient, source: SourceConfig, window: Window) -> list[Candidate]:
    """Options: url; arxiv_announce_types (arXiv feeds only, e.g. [new])."""
    response = await get(client, source.options["url"])
    feed = feedparser.parse(response.content)
    if feed.bozo and not feed.entries:
        raise ValueError(f"unparseable feed: {feed.bozo_exception}")

    announce_types = source.options.get("arxiv_announce_types")
    items: list[Candidate] = []
    for entry in feed.entries:
        if announce_types and entry.get("arxiv_announce_type") not in announce_types:
            continue
        published = entry_datetime(entry)
        if not window.contains(published):
            continue
        link = entry.get("link")
        title = clean_title(entry.get("title"))
        if not link or not title:
            continue
        content = entry.get("content") or []
        body = content[0].get("value") if content else entry.get("summary")
        tags = [t.get("term") for t in entry.get("tags", []) if t.get("term")]
        items.append(
            candidate(
                source,
                title=title,
                url=link,
                summary=truncate(clean_text(body), SUMMARY_MAX_CHARS),
                published_at=published,
                tags=tags[:8],
            )
        )
    return items


def entry_datetime(entry: feedparser.FeedParserDict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value: struct_time | None = entry.get(key)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return parse_datetime(entry.get("published") or entry.get("updated"))
