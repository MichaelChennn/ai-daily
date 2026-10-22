"""`daily export`: the published issues as JSON for the web front end (web/, Astro).

The front end only lays the data out. Everything that decides what gets published stays here:
the same `validate` gate as `daily build` (via site.load_issues), source labels, which link is a
discussion, the item's publisher and whether its publication time is real.

One file per issue, out/issues/YYYY-MM-DD.json:

  date, fallback, notice (the fallback notice, or null), description (highlights, for <meta>)
  sections[]   id, label, items[]
    items[]    title, summary, compact (rendered as a one-line brief),
               publisher {name, icon, host}, published {iso, label} or null,
               sources[] {label, url, discussion}
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

from daily.dedup import url_key
from daily.digest import SECTIONS
from daily.render import HOST_LABELS, source_labels
from daily.site import FALLBACK_NOTICE, Issue, load_issues
from daily.window import TIMEZONE

DISCUSSION_HOSTS = {"news.ycombinator.com", "reddit.com", "old.reddit.com"}
# huggingface.co/<first path segment> that is a site section, not a user or organization.
HF_SECTIONS = {
    "blog",
    "papers",
    "docs",
    "learn",
    "collections",
    "models",
    "posts",
    "tasks",
    "spaces",
    "datasets",
}


def export(out: Path, data_dir: Path) -> list[Issue]:
    """Write out/issues/*.json for every publishable issue (replacing what an earlier export left)."""
    folder = out / "issues"
    folder.mkdir(parents=True, exist_ok=True)
    for stale in folder.glob("*.json"):
        stale.unlink()
    issues = load_issues(data_dir)
    for issue in issues:
        text = json.dumps(issue_data(issue), ensure_ascii=False, indent=1)
        (folder / f"{issue.slug}.json").write_text(text + "\n", encoding="utf-8")
    return issues


def issue_data(issue: Issue) -> dict[str, Any]:
    by_id = issue.by_id
    sections = []
    for section, heading in SECTIONS.items():
        items = [item for item in issue.digest["items"] if item["section"] == section]
        if not items:
            continue
        sections.append(
            {
                "id": section,
                "label": heading.split(" ", 1)[-1],  # without the emoji
                "items": [_item(item, section, by_id) for item in items],
            }
        )
    return {
        "date": issue.slug,
        "fallback": issue.fallback,
        "notice": FALLBACK_NOTICE if issue.fallback else None,
        "description": " ".join(issue.digest.get("highlights") or []),
        "sections": sections,
    }


def _item(item: dict[str, Any], section: str, by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sources = [
        {"label": label, "url": s["url"], "discussion": _is_discussion(s["url"])}
        for s, label in source_labels(item["sources"], by_id)
        if urlsplit(s["url"]).scheme in ("http", "https")
    ]
    primary = next((s for s in item["sources"] if not _is_discussion(s["url"])), item["sources"][0])
    candidate = by_id.get(primary.get("candidate_id") or "")
    return {
        "title": item["title"],
        "summary": item.get("summary") or "",
        "compact": section == "brief" or not item.get("summary"),
        "publisher": publisher(primary["url"], candidate),
        "published": published(candidate),
        "sources": sources,
    }


def publisher(url: str, candidate: dict[str, Any] | None) -> dict[str, str]:
    """Who published the page at url: the GitHub / Hugging Face owner, else the source or the site."""
    parts = urlsplit(url)
    host = (parts.hostname or "").removeprefix("www.")
    path = [p for p in parts.path.split("/") if p]
    if host == "github.com" and path:
        owner = path[0]
        return {"name": owner, "icon": f"https://github.com/{quote(owner)}.png?size=64", "host": host}
    if host == "huggingface.co" and path and path[0] not in HF_SECTIONS:
        owner = path[0]
        # Organizations only: a user account 404s here and the page falls back to a monogram.
        icon = f"https://huggingface.co/api/organizations/{quote(owner)}/avatar?redirect=true"
        return {"name": owner, "icon": icon, "host": host}
    own_page = candidate is not None and url_key(url) == url_key(candidate["url"])
    if own_page and candidate.get("kind") != "discussion":
        name = candidate["source_name"]
    else:
        name = HOST_LABELS.get(parts.hostname or "", host)
    icon = f"https://www.google.com/s2/favicons?domain={quote(host)}&sz=64"
    return {"name": name, "icon": icon, "host": host}


def published(candidate: dict[str, Any] | None) -> dict[str, str] | None:
    """The candidate's publication time, or None when there is no real one.

    A discussion's time is when it was posted, not when the thing it links to was published.
    Sources that only give a date (and feeds that publish at exactly midnight UTC) get the date only.
    """
    if candidate is None or candidate.get("kind") == "discussion" or not candidate.get("published_at"):
        return None
    try:
        value = datetime.fromisoformat(candidate["published_at"])
    except (TypeError, ValueError):
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    utc = value.astimezone(timezone.utc)
    if candidate.get("published_precision") == "day" or (utc.hour, utc.minute, utc.second) == (0, 0, 0):
        return {"iso": utc.date().isoformat(), "label": f"{utc.month}月{utc.day}日"}
    local = value.astimezone(TIMEZONE)
    return {"iso": utc.isoformat(), "label": f"{local.month}月{local.day}日 {local:%H:%M}"}


def _is_discussion(url: str) -> bool:
    host = (urlsplit(url).hostname or "").removeprefix("www.")
    return host in DISCUSSION_HOSTS
