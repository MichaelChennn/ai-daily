"""Sites whose article list is a JSON endpoint behind a JS front end (Qwen, ByteDance Seed).

These endpoints are undocumented and may change without notice; a missing list fails the source
loudly, so it shows up in the fetch report.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, get
from daily.models import Candidate
from daily.text import clean_text, clean_title, parse_datetime, truncate
from daily.window import Window

_LINK_FIELD = re.compile(r"\{([^{}]+)\}")
# Above this a timestamp is in milliseconds: as seconds it would be past the year 5000.
_MILLIS_FROM = 100_000_000_000


async def fetch_json_api(client: httpx.AsyncClient, source: SourceConfig, window: Window) -> list[Candidate]:
    """Options, all field paths dotted (`a.b.c`):

    url; items (path to the array); title (path); link (template, `{path}` per field);
    date (path to an ISO / RFC 2822 string or an epoch in seconds or milliseconds);
    date_pattern (optional regex: its first group is the date, when it sits inside a longer field);
    date_timezone (optional: the value is only a date, written as midnight in this zone);
    summary (optional path).
    """
    options = source.options
    entries = _field((await get(client, options["url"])).json(), options["items"])
    if not entries or not isinstance(entries, list):
        raise ValueError(f"no list at {options['items']}; the API may have changed")

    items: list[Candidate] = []
    for entry in entries:
        published = _date(_field(entry, options["date"]), options.get("date_pattern"))
        precision = "second"
        if published is not None and (zone := options.get("date_timezone")):
            day = published.astimezone(ZoneInfo(zone))
            published = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            precision = "day"
        if not window.contains(published, precision):
            continue
        title = clean_title(_field(entry, options["title"]))
        url = _link(options["link"], entry)
        if not title or not url:
            continue
        body = _field(entry, options["summary"]) if options.get("summary") else None
        items.append(
            candidate(
                source,
                title=title,
                url=url,
                summary=truncate(clean_text(body), SUMMARY_MAX_CHARS),
                published_at=published,
                published_precision=precision,
            )
        )
    return items


def _field(value: Any, path: str) -> Any:
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _link(template: str, entry: Any) -> str | None:
    values = {name: _field(entry, name) for name in _LINK_FIELD.findall(template)}
    if not all(values.values()):
        return None
    return _LINK_FIELD.sub(lambda m: quote(str(values[m.group(1)]), safe=""), template)


def _date(value: Any, pattern: str | None) -> datetime | None:
    if pattern:
        match = re.search(pattern, str(value or ""))
        value = match.group(1) if match else None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        seconds = value / 1000 if value >= _MILLIS_FROM else value
        return datetime.fromtimestamp(seconds, timezone.utc)
    return parse_datetime(value) if isinstance(value, str) else None
