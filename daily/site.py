"""The published issues and the full-text RSS feed (feed.xml), for `daily export`.

Only digests that pass `validate` (offline) are published, the same gate the editor and the
fallback go through; items it would drop are left out. Fallback issues carry a visible notice.
The pages themselves are built by the Astro front end (web/) from what `daily export` writes.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from daily import digest as digest_mod
from daily.digest import SECTIONS
from daily.render import source_labels
from daily.window import PUBLISH_TIME, TIMEZONE, TIMEZONE_LABEL

log = logging.getLogger(__name__)

SITE_TITLE = "AI 科技日报"
SITE_DESCRIPTION = f"每天{TIMEZONE_LABEL} 06:00 更新的中文 AI 技术日报：5 分钟读完，每一条都附一手来源。"
DEFAULT_BASE_URL = "https://michaelchennn.github.io/ai-daily/"
RECENT_DAYS = 30
FALLBACK_NOTICE = "降级版：今天的编辑环节没有按时完成，以下是按热度挑选的候选标题和原始链接，未经编辑。"


@dataclass
class Issue:
    date: date
    digest: dict[str, Any]
    candidates: dict[str, Any]

    @property
    def slug(self) -> str:
        return self.date.isoformat()

    @property
    def fallback(self) -> bool:
        return self.digest.get("mode") == "fallback"

    @property
    def by_id(self) -> dict[str, dict[str, Any]]:
        return {c["id"]: c for c in self.candidates.get("candidates", [])}

    @property
    def published_at(self) -> datetime:
        """When the issue's content was produced; the nominal 06:00 if generated_at is unusable."""
        try:
            value = datetime.fromisoformat(self.digest["generated_at"])
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError):
            return datetime.combine(self.date, PUBLISH_TIME, TIMEZONE)


def load_issues(data_dir: Path) -> list[Issue]:
    """Every publishable issue under data_dir, newest first."""
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
            data = json.loads(path.read_text(encoding="utf-8"))
            candidates = json.loads(candidates_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log.warning("skip %s: %s", path.parent.name, exc)
            continue
        report = digest_mod.validate(data, candidates)
        if report.errors:
            log.warning("skip %s: %s", path.parent.name, report.errors[0])
            continue
        if report.item_errors:
            log.warning("%s: leaving out %d invalid items", path.parent.name, len(report.item_errors))
            kept = [item for i, item in enumerate(data["items"]) if i not in report.item_errors]
            data = {**data, "items": kept}
        issues.append(Issue(issue_date, data, candidates))
    return issues


def recent(issues: list[Issue]) -> list[Issue]:
    """Issues within RECENT_DAYS of the newest one (issues are newest first)."""
    if not issues:
        return []
    cutoff = issues[0].date - timedelta(days=RECENT_DAYS - 1)
    return [issue for issue in issues if issue.date >= cutoff]


# --- feed --------------------------------------------------------------------------------------


def issue_body(issue: Issue) -> str:
    """The issue's content. Self-contained (absolute links only): it also goes into the feed."""
    d, by_id = issue.digest, issue.by_id
    parts = []
    if issue.fallback:
        parts.append(f'<p class="notice">{FALLBACK_NOTICE}</p>')
    if d.get("highlights"):
        lis = "".join(f"<li>{escape(h)}</li>" for h in d["highlights"])
        parts.append(f'<section class="highlights"><h2>今日要点</h2><ul>{lis}</ul></section>')
    for section, heading in SECTIONS.items():
        items = [item for item in d["items"] if item["section"] == section]
        if not items:
            continue
        parts.append(f'<section class="section section-{section}"><h2>{escape(heading)}</h2>')
        short = [i for i in items if section == "brief" or not i.get("summary")]
        for item in items:
            if item not in short:
                parts.append(_item(item, by_id))
        if short:
            parts.append('<ul class="briefs">' + "".join(_brief(item, by_id) for item in short) + "</ul>")
        parts.append("</section>")
    return "".join(parts)


def _item(item: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> str:
    meta = f'<span class="sources">来源 {_links(item, by_id)}</span>'
    if item.get("tags"):
        meta += '<span class="tags">' + " ".join(f"#{escape(t)}" for t in item["tags"]) + "</span>"
    return (
        f'<div class="item"><h3>{escape(item["title"])}</h3>'
        f"<p>{escape(item['summary'])}</p>"
        f'<p class="meta">{meta}</p></div>'
    )


def _brief(item: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> str:
    summary = f" {escape(item['summary'])}" if item.get("summary") else ""
    links = f'<span class="sources">{_links(item, by_id)}</span>'
    return f"<li><strong>{escape(item['title'])}</strong>{summary} {links}</li>"


def _links(item: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> str:
    return " · ".join(
        f'<a href="{escape(s["url"])}">{escape(label)}</a>'
        for s, label in source_labels(item["sources"], by_id)
        if urlsplit(s["url"]).scheme in ("http", "https")
    )


def feed(issues: list[Issue], base_url: str) -> str:
    items = []
    for issue in recent(issues):
        link = f"{base_url}{issue.slug}/"
        title = f"{issue.slug} · {SITE_TITLE}" + ("（降级版）" if issue.fallback else "")
        summary = " ".join(issue.digest.get("highlights") or []) or FALLBACK_NOTICE
        # The mode is part of the guid: when the edited issue replaces a fallback, readers get it as new.
        items.append(
            "<item>"
            f"<title>{escape(title)}</title>"
            f"<link>{escape(link)}</link>"
            f'<guid isPermaLink="false">{escape(link)}#{escape(str(issue.digest.get("mode")))}</guid>'
            f"<pubDate>{format_datetime(issue.published_at.astimezone(timezone.utc))}</pubDate>"
            f"<description>{escape(summary)}</description>"
            f"<content:encoded>{escape(issue_body(issue))}</content:encoded>"
            "</item>"
        )
    updated = max((i.published_at for i in issues), default=datetime.now(timezone.utc))
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:content="http://purl.org/rss/1.0/modules/content/">\n<channel>'
        f"<title>{SITE_TITLE}</title><link>{escape(base_url)}</link>"
        f"<description>{escape(SITE_DESCRIPTION)}</description><language>zh-CN</language>"
        f"<lastBuildDate>{format_datetime(updated.astimezone(timezone.utc))}</lastBuildDate>"
        f'<atom:link href="{escape(base_url)}feed.xml" rel="self" type="application/rss+xml"/>'
        + "".join(items)
        + "</channel>\n</rss>\n"
    )
