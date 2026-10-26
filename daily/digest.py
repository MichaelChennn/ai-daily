"""digest.json, the issue the editor writes, and `daily validate`, the program gate it must pass.

The editor (Claude, .claude/skills/daily-editor) only writes; this module decides what may be
published. Item-level failures drop the item and are never "fixed" (charter, principle 5):

- every source is a candidate from candidates.json, or a page the editor recorded as opened;
- every item has at least one first-hand source, not just a HN / Reddit thread;
- numbers and model names / versions in the Chinese text appear in the cited material
  (candidate title and summary, or a verbatim evidence quote);
- with --check-links: links are not 404, and evidence quotes really are on the cited page.
"""

from __future__ import annotations

import asyncio
import html
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import httpx

from daily.dedup import url_key

SCHEMA_VERSION = 1
SECTIONS = {
    "headline": "🔥 头条",
    "model": "🧠 模型",
    "paper": "📄 论文",
    "tool": "🛠 开源与工具",
    "brief": "⚡ 快讯",
}
MODES = ("full", "fallback")
ITEMS_TARGET = (8, 12)
MIN_ITEMS = 3  # fewer surviving items in a full digest means the edit failed: publish the fallback
SECTION_TARGETS = {"headline": (3, 5), "paper": (2, 3)}
HIGHLIGHTS_MAX = 3
TITLE_MAX = {"full": 60, "fallback": 200}  # fallback keeps the original English titles
SUMMARY_MAX = {"brief": 120}
SUMMARY_MAX_DEFAULT = 400
QUOTE_MAX = 300  # evidence, not reprints
TAGS_MAX = 5
# Daily budget for the editor (charter open item 2); exceeding it is a warning, not a failure.
BUDGET = {"webfetch": 20, "websearch": 5}
DISCUSSION_HOSTS = ("news.ycombinator.com", "reddit.com")

_URL_IN_TEXT = re.compile(r"https?://|www\.", re.I)
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
# Tokens mixing letters and digits: model names and versions (GPT-6, Qwen3.5, v2.1.305, 128K, H100).
_MIXED = re.compile(
    r"(?<![A-Za-z0-9])(?=[A-Za-z0-9._-]*[A-Za-z])(?=[A-Za-z0-9._-]*\d)[A-Za-z0-9][A-Za-z0-9._-]*"
)
_NUMBER_WORDS = (
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen "
    "sixteen seventeen eighteen nineteen twenty"
).split()
_SCRIPT = re.compile(r"<(script|style|noscript)\b.*?</\1>|<!--.*?-->", re.S | re.I)
# A quoted attribute may hold a ">" (Hugging Face puts the model's config, chat template and all, in one).
_TAG = re.compile(r"""<[a-zA-Z/!][^>"']*(?:(?:"[^"]*"|'[^']*')[^>"']*)*>""")
_BODY = re.compile(r"<(article|main)\b.*?</\1>", re.S | re.I)


@dataclass
class Page:
    status: int | None
    text: str | None = None  # page text, when it is HTML / plain text
    error: str | None = None
    body: str | None = None  # its longest <article> or <main>: the page without the navigation


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)  # the digest as a whole is unusable
    item_errors: dict[int, list[str]] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and not self.item_errors


def published_urls(digest: dict[str, Any]) -> list[str]:
    return [
        s["url"]
        for item in digest.get("items") or []
        if isinstance(item, dict)
        for s in item.get("sources") or []
        if isinstance(s, dict) and isinstance(s.get("url"), str)
    ]


# --- validation ------------------------------------------------------------------------------


def validate(digest: Any, candidates: dict[str, Any], pages: dict[str, Page] | None = None) -> Report:
    """pages: url -> fetched page, from check_links(); None skips the online checks."""
    report = Report()
    if not isinstance(digest, dict):
        report.errors.append("digest is not a JSON object")
        return report
    if digest.get("schema_version") != SCHEMA_VERSION:
        report.errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if digest.get("date") != candidates.get("date"):
        report.errors.append(
            f"date {digest.get('date')!r} does not match candidates {candidates.get('date')!r}"
        )
    mode = digest.get("mode")
    if mode not in MODES:
        report.errors.append(f"mode must be one of {MODES}")
    _check_highlights(digest.get("highlights"), mode, report)
    items = digest.get("items")
    if not isinstance(items, list) or not items:
        report.errors.append("items must be a non-empty list")
        return report

    context = _Context(candidates, digest.get("research"), report)
    cited: dict[str, int] = {}
    for index, item in enumerate(items):
        errors = _check_item(item, mode, context, pages, report)
        for cid in _cited_ids(item, context) if not errors else []:
            if cid in cited:
                errors.append(f"candidate {cid} is already used by item {cited[cid] + 1}")
            cited.setdefault(cid, index)
        if errors:
            report.item_errors[index] = errors

    surviving = [item for i, item in enumerate(items) if i not in report.item_errors]
    if mode == "full" and len(surviving) < MIN_ITEMS:
        report.errors.append(f"only {len(surviving)} valid items (minimum {MIN_ITEMS})")
    if mode == "full":
        _check_counts(surviving, report)
    # Highlights summarize the published items: their facts must come from those items.
    published_text = [f"{item['title']}\n{item['summary']}" for item in surviving]
    for highlight in digest.get("highlights") if isinstance(digest.get("highlights"), list) else []:
        for error in _check_facts(str(highlight), published_text):
            report.errors.append(f"highlight: {error.replace('cited material', 'published items')}")
    return report


class _Context:
    def __init__(self, candidates: dict[str, Any], research: Any, report: Report) -> None:
        self.by_id = {c["id"]: c for c in candidates.get("candidates", [])}
        self.by_key: dict[str, str] = {}
        for c in self.by_id.values():
            for url in candidate_urls(c):
                self.by_key.setdefault(url_key(url), c["id"])
        self.opened: set[str] = set()
        if research is None:
            research = []
        if not isinstance(research, list):
            report.errors.append("research must be a list")
            research = []
        used = {"webfetch": 0, "websearch": 0}
        for entry in research:
            if not isinstance(entry, dict) or entry.get("via") not in used:
                report.errors.append(f"research entry must have via webfetch|websearch: {entry!r}"[:200])
                continue
            used[entry["via"]] += 1
            if entry["via"] == "webfetch" and isinstance(entry.get("url"), str):
                self.opened.add(url_key(entry["url"]))
        for via, limit in BUDGET.items():
            if used[via] > limit:
                report.warnings.append(f"{via} used {used[via]} times (budget {limit})")


def candidate_urls(c: dict[str, Any]) -> list[str]:
    urls = [c["url"], c.get("discussion_url")]
    for other in c.get("also_from") or []:
        urls += [other.get("url"), other.get("discussion_url")]
    return [u for u in urls if u]


def _check_highlights(highlights: Any, mode: Any, report: Report) -> None:
    if highlights is None and mode == "fallback":
        return
    if not isinstance(highlights, list) or not all(isinstance(h, str) and h.strip() for h in highlights):
        report.errors.append("highlights must be a list of non-empty strings")
        return
    if mode == "full" and not 1 <= len(highlights) <= HIGHLIGHTS_MAX:
        report.errors.append(f"highlights must have 1-{HIGHLIGHTS_MAX} sentences")
    if any(_URL_IN_TEXT.search(h) for h in highlights):
        report.errors.append("highlights must not contain URLs")


def _check_counts(items: list[dict[str, Any]], report: Report) -> None:
    low, high = ITEMS_TARGET
    if not low <= len(items) <= high:
        report.warnings.append(f"{len(items)} items (target {low}-{high})")
    for section, (low, high) in SECTION_TARGETS.items():
        count = sum(1 for item in items if item["section"] == section)
        if not low <= count <= high:
            report.warnings.append(f"{count} {section} items (target {low}-{high})")


def _cited_ids(item: dict[str, Any], context: _Context) -> list[str]:
    ids = []
    for s in item["sources"]:
        cid = s.get("candidate_id") or context.by_key.get(url_key(s["url"]))
        if cid and cid not in ids:
            ids.append(cid)
    return ids


def _check_item(
    item: Any, mode: Any, context: _Context, pages: dict[str, Page] | None, report: Report
) -> list[str]:
    if not isinstance(item, dict):
        return ["item is not an object"]
    errors: list[str] = []
    section = item.get("section")
    if section not in SECTIONS:
        errors.append(f"section must be one of {list(SECTIONS)}")
    title, summary = item.get("title"), item.get("summary")
    if not isinstance(title, str) or not title.strip():
        errors.append("title is empty")
    elif len(title) > TITLE_MAX.get(mode, TITLE_MAX["full"]):
        errors.append(f"title longer than {TITLE_MAX.get(mode, TITLE_MAX['full'])} characters")
    if not isinstance(summary, str) or (mode == "full" and not summary.strip()):
        errors.append("summary is empty")
    elif len(summary) > SUMMARY_MAX.get(section, SUMMARY_MAX_DEFAULT):
        errors.append(f"summary longer than {SUMMARY_MAX.get(section, SUMMARY_MAX_DEFAULT)} characters")
    if any(isinstance(t, str) and _URL_IN_TEXT.search(t) for t in (title, summary)):
        errors.append("title / summary must not contain URLs (links go in sources)")
    tags = item.get("tags", [])
    if not isinstance(tags, list) or len(tags) > TAGS_MAX or not all(isinstance(t, str) for t in tags):
        errors.append(f"tags must be a list of at most {TAGS_MAX} strings")
    if errors:
        return errors

    sources = item.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["sources must be a non-empty list"]
    cited: list[dict[str, Any]] = []  # candidates this item cites
    urls: list[str] = []
    first_hand = False
    for s in sources:
        if not isinstance(s, dict):
            errors.append("source is not an object")
            continue
        cid, url = s.get("candidate_id"), s.get("url")
        if url is not None and not isinstance(url, str):
            errors.append("source url must be a string")
            continue
        if cid is not None:
            c = context.by_id.get(cid)
            if c is None:
                errors.append(f"unknown candidate_id {cid}")
                continue
            if url is None:
                url = s["url"] = c["url"]  # filled in so the stored digest always carries links
            elif url_key(url) not in {url_key(u) for u in candidate_urls(c)}:
                errors.append(f"{url} is not a link of candidate {cid}")
                continue
        elif url is None:
            errors.append("source needs a candidate_id or a url")
            continue
        else:
            key = url_key(url)
            c = context.by_id.get(context.by_key.get(key, ""))
            if c is None and key not in context.opened:
                errors.append(f"{url} is neither a candidate nor a page recorded as opened in research")
                continue
        if c is not None and c not in cited:
            cited.append(c)
        urls.append(url)
        if not is_discussion(url, c):
            first_hand = True
    if errors:
        return errors
    if not first_hand:
        errors.append("needs a first-hand source, not only a discussion thread")

    material = [part for c in cited for part in _candidate_text(c)]
    quotes, source_keys = [], {url_key(u) for u in urls}
    for e in item.get("evidence") or []:
        if (
            not isinstance(e, dict)
            or not isinstance(e.get("quote"), str)
            or not isinstance(e.get("url"), str)
        ):
            errors.append("evidence entries need url and quote")
        elif url_key(e["url"]) not in source_keys:
            errors.append(f"evidence url {e['url']} is not one of the item's sources")
        elif not e["quote"].strip() or len(e["quote"]) > QUOTE_MAX:
            errors.append(f"evidence quote must be 1-{QUOTE_MAX} characters")
        else:
            quotes.append(e)
    if errors:
        return errors

    errors += _check_facts(f"{title}\n{summary}", material + [q["quote"] for q in quotes])
    if pages is not None:
        errors += _check_online(urls, quotes, material, pages, report, title)
    return errors


def is_api(digest: dict[str, Any]) -> bool:
    """Written by the API route; digests without a channel come from the Claude route."""
    return digest.get("channel") == "api"


def is_discussion(url: str, c: dict[str, Any] | None) -> bool:
    if c is not None and c.get("discussion_url") and url_key(url) == url_key(c["discussion_url"]):
        return True
    host = urlsplit(url).hostname or ""
    return any(host == h or host.endswith("." + h) for h in DISCUSSION_HOSTS)


def _candidate_text(c: dict[str, Any]) -> list[str]:
    parts = [c.get("title") or "", c.get("summary") or "", c.get("published_at") or ""]
    parts += [str(v) for v in (c.get("signals") or {}).values()]
    parts += [a.get("title") or "" for a in c.get("also_from") or []]
    return parts


def _check_facts(text: str, material: list[str]) -> list[str]:
    blob = "\n".join(material)
    numbers = {_number(n) for n in _NUMBER.findall(blob)}
    words = set(re.findall(r"[a-z]+", blob.lower()))
    numbers |= {str(i) for i, w in enumerate(_NUMBER_WORDS) if w in words}
    squashed = _squash(blob)
    errors = []
    for token in dict.fromkeys(_MIXED.findall(text)):
        if _squash(token) not in squashed:
            errors.append(f"{token!r} does not appear in the cited material")
    for n in dict.fromkeys(_number(n) for n in _NUMBER.findall(text)):
        if n not in numbers:
            errors.append(f"number {n} does not appear in the cited material")
    return errors


def _check_online(
    urls: list[str],
    quotes: list[dict[str, str]],
    material: list[str],
    pages: dict[str, Page],
    report: Report,
    title: str,
) -> list[str]:
    errors = []
    for url in urls:
        page = pages.get(url)
        if page and page.status in (404, 410):
            errors.append(f"broken link ({page.status}): {url}")
        elif page and (page.status is None or page.status >= 400):
            report.warnings.append(f"{title}: could not check {url} ({page.error or page.status})")
    offline = _alnum("\n".join(material))
    for q in quotes:
        quote = _alnum(q["quote"])
        if quote in offline:
            continue
        page = pages.get(q["url"])
        if page and page.text is not None:
            if quote not in _alnum(page.text):
                errors.append(f"evidence quote not found on {q['url']}: {q['quote'][:60]!r}")
        else:
            report.warnings.append(f"{title}: evidence quote unverified ({q['url']})")
    return errors


def _number(value: str) -> str:
    value = value.replace(",", "")
    return value.rstrip(".") if "." in value else value.lstrip("0") or "0"


def _squash(text: str) -> str:
    return re.sub(r"[\s._-]+", "", text.lower())


def _alnum(text: str) -> str:
    return re.sub(r"[^0-9a-z一-鿿]+", "", text.lower())


# --- online checks ---------------------------------------------------------------------------


def digest_urls(digest: dict[str, Any]) -> list[str]:
    urls = published_urls(digest)
    for item in digest.get("items") or []:
        for e in (item.get("evidence") or []) if isinstance(item, dict) else []:
            if isinstance(e, dict) and isinstance(e.get("url"), str):
                urls.append(e["url"])
    return list(dict.fromkeys(urls))


async def check_links(urls: list[str], client: httpx.AsyncClient, concurrency: int = 8) -> dict[str, Page]:
    semaphore = asyncio.Semaphore(concurrency)

    async def one(url: str) -> tuple[str, Page]:
        async with semaphore:
            try:
                response = await client.get(url)
            except httpx.HTTPError as exc:
                return url, Page(None, error=f"{type(exc).__name__}: {exc}"[:200])
        content_type = response.headers.get("content-type", "")
        text = body = None
        if response.status_code < 400 and ("html" in content_type or content_type.startswith("text/")):
            text = page_text(response.text)
            body = max((page_text(m.group(0)) for m in _BODY.finditer(response.text)), key=len, default=None)
        return url, Page(response.status_code, text=text, body=body)

    return dict(await asyncio.gather(*(one(u) for u in urls)))


def page_text(markup: str) -> str:
    return html.unescape(_TAG.sub(" ", _SCRIPT.sub(" ", markup)))


def grep_page(text: str, needles: list[str], context: int = 200) -> str:
    """`daily page`: the page text around each needle, verbatim as validate will match it."""
    text = " ".join(text.split())
    lines = []
    for needle in needles:
        hits = [i for i in range(len(text)) if text.startswith(needle, i)] if needle else []
        lines.append(f"--- {needle!r}: {len(hits)} match(es)")
        for i in hits[:5]:
            lines += [text[max(0, i - context) : i + len(needle) + context], ""]
    return "\n".join(lines)


# --- applying the verdict --------------------------------------------------------------------


def apply_report(digest: dict[str, Any], report: Report, checked_links: bool) -> dict[str, Any]:
    """Drop the invalid items and record why, so the published digest only holds what passed."""
    items = digest["items"]
    result = {**digest, "items": [item for i, item in enumerate(items) if i not in report.item_errors]}
    previous = digest.get("validation") or {}
    result["validation"] = {
        "validated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checked_links": checked_links or previous.get("checked_links", False),
        "dropped": (previous.get("dropped") or [])
        + [
            {"title": items[i].get("title"), "section": items[i].get("section"), "reasons": errors}
            if isinstance(items[i], dict)
            else {"title": None, "section": None, "reasons": errors}
            for i, errors in sorted(report.item_errors.items())
        ],
        "warnings": report.warnings,
    }
    return result
