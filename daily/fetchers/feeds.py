"""Generic RSS/Atom feeds."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from time import struct_time

import feedparser
import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, filtered, get
from daily.models import Candidate
from daily.text import clean_text, clean_title, parse_datetime, parse_written_datetime, truncate
from daily.window import Window

logger = logging.getLogger(__name__)


async def fetch_rss(client: httpx.AsyncClient, source: SourceConfig, window: Window) -> list[Candidate]:
    """Options: url; exclude_title_pattern (optional regex: matching entries are filtered out)."""
    exclude = source.options.get("exclude_title_pattern")
    response = await get(client, source.options["url"])
    feed = feedparser.parse(response.content)
    if feed.bozo and not feed.entries:
        raise ValueError(f"unparseable feed: {feed.bozo_exception}")
    # A post that never shows up despite its date: this tells whether the feed we got was stale.
    logger.info(
        "source %s: feed lastBuildDate=%s, %d entries", source.id, feed.feed.get("updated"), len(feed.entries)
    )

    items: list[Candidate] = []
    for entry in feed.entries:
        published, precision = entry_published(entry)
        if not window.contains(published, precision):
            continue
        link = entry.get("link")
        title = clean_title(entry.get("title"))
        if not link or not title:
            continue
        if exclude and re.search(exclude, title):
            filtered(source, "exclude_title", title, link, f"title matches {exclude}")
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
                published_precision=precision,
                tags=tags[:8],
            )
        )
    return items


def entry_published(entry: feedparser.FeedParserDict) -> tuple[datetime | None, str]:
    """The entry's time and precision. Exactly midnight on the feed's own clock means it only knows
    the date (OpenAI, Hugging Face, Ai2: often the post goes up hours later), and the date is the
    one written there, not the UTC one. A post really published at midnight just shows up once more.
    """
    published = entry_datetime(entry)
    written = parse_written_datetime(entry.get("published") or entry.get("updated")) or published
    if written is None or (written.hour, written.minute, written.second) != (0, 0, 0):
        return published, "second"
    return datetime(written.year, written.month, written.day, tzinfo=timezone.utc), "day"


def entry_datetime(entry: feedparser.FeedParserDict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value: struct_time | None = entry.get(key)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return parse_datetime(entry.get("published") or entry.get("updated"))
