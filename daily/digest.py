"""digest.json, the issue the editor writes, and `daily validate`, the program gate it must pass.

The editor (Claude, .claude/skills/daily-editor) only writes; this module decides what may be
published. Item-level failures drop the item and are never "fixed" (charter, principle 5):

- every source is a candidate from candidates.json, or a page the editor recorded as opened;
- every item has at least one first-hand source, not just a HN / Reddit thread, image or tweet;
- an item in the paper section has a paper as its main source;
- an item whose main source is commentary sits in the brief section, at most COMMENTARY_MAX per issue;
- numbers and model names / versions in the text (Chinese, or English in digest.en.json) appear
  in the cited material (candidate title and summary, or a verbatim evidence quote);
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

from daily import routes
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
# How many items an issue should have. Outside the target is a warning: no padding, and items that
# were written and passed are not cut.
ITEMS_TARGET = (8, 18)
ITEMS_EXPECTED = 15
MIN_ITEMS = 3  # fewer surviving items in a full digest means the edit failed: publish the fallback
SECTION_TARGETS = {"headline": (3, 5), "paper": (2, 4)}
COMMENTARY_MAX = 2  # items whose main source is a writer's or newsletter's post; over it they are dropped
HIGHLIGHTS_MAX = 3
# The main issue is Chinese; the English edition (digest.en.json, "lang": "en") has the same
# schema, and English takes about twice the characters.
LANGS = ("zh", "en")
TITLE_MAX = {"full": 60, "fallback": 200}  # fallback keeps the original English titles
TITLE_MAX_EN = 120
SUMMARY_MAX = {"zh": {"brief": 120}, "en": {"brief": 250}}
SUMMARY_MAX_DEFAULT = {"zh": 400, "en": 800}
QUOTE_MAX = 300  # evidence, not reprints
TAGS_MAX = 5
# Daily budget for the editor (charter open item 2); exceeding it is a warning, not a failure.
BUDGET = {"webfetch": 30, "websearch": 5}
# Not first-hand: threads, and posts whose text cannot be downloaded and quoted (images, videos, tweets).
DISCUSSION_HOSTS = ("news.ycombinator.com", "reddit.com", "redd.it", "x.com", "twitter.com")
PAPER_HOSTS = ("arxiv.org", "openreview.net")

_URL_IN_TEXT = re.compile(r"https?://|www\.", re.I)
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
# Tokens mixing letters and digits: model names and versions (GPT-6, Qwen3.5, v2.1.305, 128K, H100).
_MIXED = re.compile(
    r"(?<![A-Za-z0-9])(?=[A-Za-z0-9._-]*[A-Za-z])(?=[A-Za-z0-9._-]*\d)[A-Za-z0-9][A-Za-z0-9._-]*"
)
# A number with a word hyphenated to it ("763B-parameter", "32-bit"): the number is the fact. Names
# start with letters or carry digits in more parts ("GPT-6", "Qwen3.5-72B") and are checked whole.
_NUMBER_AND_WORD = re.compile(r"^(\d[A-Za-z0-9.]*)(?:-[A-Za-z]+)+$")
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
    elif (problem := routes.check(digest)) is not None:
        report.errors.append(problem)
    lang = digest.get("lang", "zh")
    if lang not in LANGS:
        report.errors.append(f"lang must be one of {LANGS}")
        return report
    _check_highlights(digest.get("highlights"), mode, report)
    items = digest.get("items")
    if not isinstance(items, list) or not items:
        report.errors.append("items must be a non-empty list")
        return report

    context = _Context(candidates, digest.get("research"), report)
    cited: dict[str, int] = {}
    commentary = 0  # items kept so far with commentary as their main source
    for index, item in enumerate(items):
        errors = _check_item(item, mode, lang, context, pages, report)
        for cid in _cited_ids(item, context) if not errors else []:
            if cid in cited:
                errors.append(f"candidate {cid} is already used by item {cited[cid] + 1}")
            cited.setdefault(cid, index)
        if not errors and _main_kind(item, context) == "commentary":
            if item["section"] != "brief":
                errors.append(f"a commentary item belongs in the brief section, not {item['section']}")
            elif commentary >= COMMENTARY_MAX:
                errors.append(f"at most {COMMENTARY_MAX} commentary items per issue")
            else:
                commentary += 1
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
    urls += c.get("links") or []  # last: only used when there is no first-hand page before them
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
    count = len(items)
    if count < low:
        report.warnings.append(f"{count} items, fewer than {low}: 这一期可能有信源漏抓了")
    elif count > high:
        report.warnings.append(f"{count} items, more than {high} (expected about {ITEMS_EXPECTED})")
    for section, (low, high) in SECTION_TARGETS.items():
        count = sum(1 for item in items if item["section"] == section)
        if not low <= count <= high:
            report.warnings.append(f"{count} {section} items (target {low}-{high})")


def _source_id(source: dict[str, Any], context: _Context) -> str | None:
    return source.get("candidate_id") or context.by_key.get(url_key(source["url"]))


def _cited_ids(item: dict[str, Any], context: _Context) -> list[str]:
    ids = []
    for s in item["sources"]:
        cid = _source_id(s, context)
        if cid and cid not in ids:
            ids.append(cid)
    return ids


def _main_kind(item: dict[str, Any], context: _Context) -> str | None:
    """The kind of the candidate behind the first source; a page the editor opened has none."""
    c = context.by_id.get(_source_id(item["sources"][0], context) or "")
    return c.get("kind") if c else None


def _check_item(
    item: Any, mode: Any, lang: str, context: _Context, pages: dict[str, Page] | None, report: Report
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
    elif len(title) > (title_max := _title_max(mode, lang)):
        errors.append(f"title longer than {title_max} characters")
    if not isinstance(summary, str) or (mode == "full" and not summary.strip()):
        errors.append("summary is empty")
    elif len(summary) > (summary_max := SUMMARY_MAX[lang].get(section, SUMMARY_MAX_DEFAULT[lang])):
        errors.append(f"summary longer than {summary_max} characters")
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
    main: dict[str, Any] | None = None  # the candidate of the first source
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
        if not urls:
            main = c
        urls.append(url)
        if not is_discussion(url, c):
            first_hand = True
    if errors:
        return errors
    if not first_hand:
        errors.append("needs a first-hand source, not only a discussion thread")
    if section == "paper" and not _is_paper(urls[0], main):
        errors.append(f"the paper section needs a paper as its main source, not {urls[0]}")

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

    # A quote from a page that cannot be read is unchecked (see _check_online): it supports nothing.
    checked = [q["quote"] for q in quotes if pages is None or _readable(pages.get(q["url"]))]
    errors += _check_facts(f"{title}\n{summary}", material + checked)
    if pages is not None:
        errors += _check_online(urls, quotes, material, pages, report, title)
    return errors


def _title_max(mode: Any, lang: str) -> int:
    if mode == "full" and lang == "en":
        return TITLE_MAX_EN
    return TITLE_MAX.get(mode, TITLE_MAX["full"])


def is_discussion(url: str, c: dict[str, Any] | None) -> bool:
    if c is not None and c.get("discussion_url") and url_key(url) == url_key(c["discussion_url"]):
        return True
    host = urlsplit(url).hostname or ""
    return any(host == h or host.endswith("." + h) for h in DISCUSSION_HOSTS)


def _is_paper(url: str, c: dict[str, Any] | None) -> bool:
    if c is not None and c.get("kind") == "paper":
        return True
    parts = urlsplit(url)
    host = parts.hostname or ""
    if host == "huggingface.co":
        return parts.path.startswith("/papers/")
    return any(host == h or host.endswith("." + h) for h in PAPER_HOSTS)


def _readable(page: Page | None) -> bool:
    return page is not None and page.text is not None


def _candidate_text(c: dict[str, Any]) -> list[str]:
    parts = [c.get("title") or "", c.get("summary") or "", c.get("published_at") or ""]
    parts += [str(v) for v in (c.get("signals") or {}).values()]
    parts += [a.get("title") or "" for a in c.get("also_from") or []]
    return parts


def _check_facts(text: str, material: list[str]) -> list[str]:
    blob = "\n".join(material)
    numbers = {v for n in _NUMBER.findall(blob) for v in _number_forms(_number(n))}
    words = set(re.findall(r"[a-z]+", blob.lower()))
    numbers |= {str(i) for i, w in enumerate(_NUMBER_WORDS) if w in words}
    squashed = _squash(blob)
    errors = []
    for token in dict.fromkeys(_fact_token(t) for t in _MIXED.findall(text)):
        if _squash(token) not in squashed:
            errors.append(f"{token!r} does not appear in the cited material")
    for n in dict.fromkeys(_number(n) for n in _NUMBER.findall(text)):
        if n not in numbers:
            errors.append(f"number {n} does not appear in the cited material")
    return errors


def _fact_token(token: str) -> str:
    match = _NUMBER_AND_WORD.match(token)
    return match.group(1) if match else token


def _number_forms(number: str) -> list[str]:
    """A number and, for a version like 2.14.0, its prefixes down to two parts: 2.14 but not 2."""
    parts = number.split(".")
    return [number] + [".".join(parts[:n]) for n in range(2, len(parts))]


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
            {
                "title": items[i].get("title"),
                "section": items[i].get("section"),
                "candidates": source_ids(items[i]),
                "reasons": errors,
            }
            if isinstance(items[i], dict)
            else {"title": None, "section": None, "candidates": [], "reasons": errors}
            for i, errors in sorted(report.item_errors.items())
        ],
        "warnings": report.warnings,
    }
    return result


def source_ids(item: Any) -> list[str]:
    """The candidate ids an item cites, main source first."""
    if not isinstance(item, dict):
        return []
    ids = [s.get("candidate_id") for s in item.get("sources") or [] if isinstance(s, dict)]
    return list(dict.fromkeys(i for i in ids if isinstance(i, str)))
