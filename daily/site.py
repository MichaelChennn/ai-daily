"""The published issues and the full-text RSS feeds (feed.xml, feed.en.xml), for `daily export`.

Only digests that pass `validate` (offline) are published, the same gate the editor and the
fallback go through; items it would drop are left out. Fallback issues carry a visible notice.
The pages themselves are built by the Astro front end (web/) from what `daily export` writes.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from daily import digest as digest_mod
from daily.digest import SECTIONS, is_api
from daily.publish import goes_with
from daily.render import source_labels
from daily.window import PUBLISH_TIME, TIMEZONE, TIMEZONE_LABEL

log = logging.getLogger(__name__)

SITE_TITLE = "AI 科技日报"
SITE_DESCRIPTION = f"每天{TIMEZONE_LABEL} 06:00 更新的中文 AI 技术日报：5 分钟读完，每一条都附一手来源。"
DEFAULT_BASE_URL = "https://michaelchennn.github.io/ai-daily/"
RECENT_DAYS = 30
FALLBACK_NOTICE = "降级版：今天的编辑环节没有按时完成，以下是按热度挑选的候选标题和原始链接，未经编辑。"
FALLBACK_NOTICE_EN = (
    "Fallback edition: today's editing did not finish in time. These are the top candidates by "
    "popularity, with their original titles and links, unedited."
)
SITE_TITLE_EN = "AI Daily"
SITE_DESCRIPTION_EN = (
    "A daily AI tech digest, updated at 06:00 Berlin time: a five-minute read, every story with "
    "first-hand sources."
)
# Section headings on the English site and in its feed.
SECTIONS_EN = {
    "headline": "Headlines",
    "model": "Models",
    "paper": "Papers",
    "tool": "Open source & tools",
    "brief": "Briefs",
}


@dataclass
class Issue:
    date: date
    digest: dict[str, Any]
    candidates: dict[str, Any]
    # API route editions shown beside the main issue: slug (from digest.api.<slug>.json) -> digest.
    betas: dict[str, dict[str, Any]] = field(default_factory=dict)
    # The English edition (digest.en.json), when it was written and passes validate.
    en: dict[str, Any] | None = None

    @property
    def slug(self) -> str:
        return self.date.isoformat()

    @property
    def fallback(self) -> bool:
        return self.digest.get("mode") == "fallback"

    @property
    def by_id(self) -> dict[str, dict[str, Any]]:
        return {c["id"]: c for c in self.candidates.get("candidates", [])}

    def edition(self, lang: str = "zh") -> dict[str, Any]:
        """The digest in one language: in English the English edition, or the main issue without one."""
        return (self.en or self.digest) if lang == "en" else self.digest

    def published_at(self, lang: str = "zh") -> datetime:
        """When that edition was produced; the nominal 06:00 if generated_at is unusable."""
        try:
            value = datetime.fromisoformat(self.edition(lang)["generated_at"])
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError):
            return datetime.combine(self.date, PUBLISH_TIME, TIMEZONE)


def load_issues(data_dir: Path) -> list[Issue]:
    """Every publishable issue under data_dir, newest first, with its publishable betas."""
    issues = []
    for path in sorted(data_dir.glob("*/digest.json"), reverse=True):
        try:
            issue_date = date.fromisoformat(path.parent.name)
        except ValueError:
            continue
        candidates_file = path.parent / "candidates.json"
        if not candidates_file.exists():
            log.warning("skip %s: no candidates.json to validate against", path.parent.name)
            continue
        try:
            candidates = json.loads(candidates_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.warning("skip %s: %s", path.parent.name, exc)
            continue
        data = _publishable(path, candidates)
        if data is None:
            continue
        issue = Issue(issue_date, data, candidates)
        en_path = path.parent / "digest.en.json"
        en = _publishable(en_path, candidates) if en_path.exists() else None
        # Left from the other route, or the main issue fell back: the English site shows titles only.
        if en is not None and en.get("lang") == "en" and goes_with(data, en, candidates) is None:
            issue.en = en
        for beta_path in sorted(path.parent.glob("digest.api.*.json")):
            beta = _publishable(beta_path, candidates)
            # The API edit that became the main issue is not shown again as a beta.
            if beta is not None and not (is_api(data) and beta.get("model") == data.get("model")):
                issue.betas[beta_path.name.removeprefix("digest.api.").removesuffix(".json")] = beta
        issues.append(issue)
    return issues


def _publishable(path: Path, candidates: dict[str, Any]) -> dict[str, Any] | None:
    """The digest at path without the items validate would drop; None if it does not pass."""
    name = f"{path.parent.name}/{path.name}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log.warning("skip %s: %s", name, exc)
        return None
    report = digest_mod.validate(data, candidates)
    if report.errors:
        log.warning("skip %s: %s", name, report.errors[0])
        return None
    if report.item_errors:
        log.warning("%s: leaving out %d invalid items", name, len(report.item_errors))
        kept = [item for i, item in enumerate(data["items"]) if i not in report.item_errors]
        data = {**data, "items": kept}
    return data


def recent(issues: list[Issue]) -> list[Issue]:
    """Issues within RECENT_DAYS of the newest one (issues are newest first)."""
    if not issues:
        return []
    cutoff = issues[0].date - timedelta(days=RECENT_DAYS - 1)
    return [issue for issue in issues if issue.date >= cutoff]


# --- feed --------------------------------------------------------------------------------------


def issue_body(issue: Issue, lang: str = "zh") -> str:
    """The issue's content in one language. Self-contained (absolute links only): it goes into the
    feed. In English, the issue's English edition (or its fallback); tags stay out, they are Chinese."""
    en = lang == "en"
    d, by_id = issue.edition(lang), issue.by_id
    parts = []
    if issue.fallback:
        parts.append(f'<p class="notice">{FALLBACK_NOTICE_EN if en else FALLBACK_NOTICE}</p>')
    if d.get("highlights"):
        lis = "".join(f"<li>{escape(h)}</li>" for h in d["highlights"])
        heading = "Highlights" if en else "今日要点"
        parts.append(f'<section class="highlights"><h2>{heading}</h2><ul>{lis}</ul></section>')
    for section, heading in SECTIONS.items():
        items = [item for item in d["items"] if item["section"] == section]
        if not items:
            continue
        heading = SECTIONS_EN[section] if en else heading
        parts.append(f'<section class="section section-{section}"><h2>{escape(heading)}</h2>')
        short = [i for i in items if section == "brief" or not i.get("summary")]
        for item in items:
            if item not in short:
                parts.append(_item(item, by_id, lang))
        if short:
            briefs = "".join(_brief(item, by_id, lang) for item in short)
            parts.append(f'<ul class="briefs">{briefs}</ul>')
        parts.append("</section>")
    return "".join(parts)


def _item(item: dict[str, Any], by_id: dict[str, dict[str, Any]], lang: str) -> str:
    meta = f'<span class="sources">{"Sources" if lang == "en" else "来源"} {_links(item, by_id, lang)}</span>'
    if item.get("tags") and lang == "zh":
        meta += '<span class="tags">' + " ".join(f"#{escape(t)}" for t in item["tags"]) + "</span>"
    return (
        f'<div class="item"><h3>{escape(item["title"])}</h3>'
        f"<p>{escape(item['summary'])}</p>"
        f'<p class="meta">{meta}</p></div>'
    )


def _brief(item: dict[str, Any], by_id: dict[str, dict[str, Any]], lang: str) -> str:
    summary = f" {escape(item['summary'])}" if item.get("summary") else ""
    links = f'<span class="sources">{_links(item, by_id, lang)}</span>'
    return f"<li><strong>{escape(item['title'])}</strong>{summary} {links}</li>"


def _links(item: dict[str, Any], by_id: dict[str, dict[str, Any]], lang: str) -> str:
    # "HN 讨论" is just "HN" in English, as on the English site.
    return " · ".join(
        f'<a href="{escape(s["url"])}">{escape(label.removesuffix(" 讨论") if lang == "en" else label)}</a>'
        for s, label in source_labels(item["sources"], by_id)
        if urlsplit(s["url"]).scheme in ("http", "https")
    )


def feed(issues: list[Issue], base_url: str, lang: str = "zh") -> str:
    """The feed of the last RECENT_DAYS issues: feed.xml, or in English feed.en.xml, which only
    carries issues whose English edition is written (or fallbacks) and links to the English site."""
    en = lang == "en"
    title_site, description = (SITE_TITLE_EN, SITE_DESCRIPTION_EN) if en else (SITE_TITLE, SITE_DESCRIPTION)
    site_url = f"{base_url}en/" if en else base_url
    shown = [issue for issue in recent(issues) if not en or issue.en or issue.fallback]
    items = []
    for issue in shown:
        d = issue.edition(lang)
        link = f"{site_url}{issue.slug}/"
        title = f"{issue.slug} · {title_site}"
        if issue.fallback:
            title += " (fallback)" if en else "（降级版）"
        notice = FALLBACK_NOTICE_EN if en else FALLBACK_NOTICE
        summary = " ".join(d.get("highlights") or []) or notice
        # The mode is part of the guid: when the edited issue replaces a fallback, readers get it as new.
        items.append(
            "<item>"
            f"<title>{escape(title)}</title>"
            f"<link>{escape(link)}</link>"
            f'<guid isPermaLink="false">{escape(link)}#{escape(str(d.get("mode")))}</guid>'
            f"<pubDate>{format_datetime(issue.published_at(lang).astimezone(timezone.utc))}</pubDate>"
            f"<description>{escape(summary)}</description>"
            f"<content:encoded>{escape(issue_body(issue, lang))}</content:encoded>"
            "</item>"
        )
    updated = max((i.published_at(lang) for i in shown), default=datetime.now(timezone.utc))
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/">\n<channel>'
        f"<title>{title_site}</title><link>{escape(site_url)}</link>"
        f"<description>{escape(description)}</description><language>{'en' if en else 'zh-CN'}</language>"
        f"<lastBuildDate>{format_datetime(updated.astimezone(timezone.utc))}</lastBuildDate>"
        f'<atom:link href="{escape(base_url)}{"feed.en.xml" if en else "feed.xml"}" rel="self" '
        'type="application/rss+xml"/>' + "".join(items) + "</channel>\n</rss>\n"
    )
