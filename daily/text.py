"""Text and date helpers. Cleaning rules adapted from Verita's external_sources / output_sanitizer."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

SMART_PUNCTUATION = str.maketrans(
    {
        "…": "...",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        " ": " ",
    }
)

_TAG = re.compile(r"<[^>]+>")
_BLOCK_TAG = re.compile(r"<(script|style|svg)\b.*?</\1>", re.S | re.I)
_MARKDOWN = re.compile(r"[`*_>#]+")


def clean_text(value: str | None) -> str:
    """Strip HTML/markdown noise and collapse whitespace; keeps URLs out of prose."""
    if not value:
        return ""
    text = _BLOCK_TAG.sub(" ", value)
    text = unescape(_TAG.sub(" ", text))
    text = re.sub(r"https?://\S+", " ", text)
    text = _MARKDOWN.sub(" ", text)
    text = re.sub(r"\s[-*]\s", " ", text)
    text = text.translate(SMART_PUNCTUATION)
    return " ".join(_strip_controls(text).split())


def clean_title(value: str | None) -> str:
    """Titles keep markdown-ish characters (e.g. `C#`, `v1.2_rc`) but lose HTML and controls."""
    if not value:
        return ""
    text = unescape(_TAG.sub(" ", value)).translate(SMART_PUNCTUATION)
    return " ".join(_strip_controls(text).split())


def truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    cut = value[:limit].rsplit(" ", 1)[0]
    return (cut or value[:limit]) + "..."


def _strip_controls(text: str) -> str:
    return "".join(
        " " if unicodedata.category(ch) == "Cc" else "" if unicodedata.category(ch) == "Cf" else ch
        for ch in text
    )


def parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO 8601 or RFC 2822 timestamps; naive values are assumed UTC."""
    if not value:
        return None
    value = value.strip()
    parsed: datetime | None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
    return as_utc(parsed)


_MONTHS = {
    m: i
    for i, names in enumerate(
        [
            ("jan", "january"),
            ("feb", "february"),
            ("mar", "march"),
            ("apr", "april"),
            ("may",),
            ("jun", "june"),
            ("jul", "july"),
            ("aug", "august"),
            ("sep", "sept", "september"),
            ("oct", "october"),
            ("nov", "november"),
            ("dec", "december"),
        ],
        start=1,
    )
    for m in names
}
_TEXT_DATE = re.compile(r"\b([A-Z][a-z]{2,8})\.?\s+(\d{1,2}),\s+(\d{4})\b")
_ISO_DATE = re.compile(r"\b(\d{4})[-/](\d{2})[-/](\d{2})\b")


def find_date(text: str) -> datetime | None:
    """Find the first human-written date like 'Oct 6, 2026', '2026-10-06' or '2026/10/06' (day, UTC)."""
    for match in _TEXT_DATE.finditer(text):
        month = _MONTHS.get(match.group(1).lower())
        if month:
            try:
                return datetime(int(match.group(3)), month, int(match.group(2)), tzinfo=timezone.utc)
            except ValueError:
                continue
    match = _ISO_DATE.search(text)
    if match:
        try:
            return datetime(*map(int, match.groups()), tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
