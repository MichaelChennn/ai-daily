"""`daily export`: the published issues as JSON for the web front end (web/, Astro).

The front end only lays the data out. Everything that decides what gets published stays here:
the same `validate` gate as the feed (site.load_issues), source labels, which link is a
discussion, the item's publisher and whether its publication time is real.

One file per issue, out/issues/YYYY-MM-DD.json, and one per beta (an API route edition beside
the main issue), out/beta/YYYY-MM-DD/<slug>.json:

  date, fallback, notice (the fallback notice, or null), description (highlights, for <meta>)
  editor       who edited it ("Claude", the API route's model), null for a fallback
  betas[]      slug, label: the issue's betas
  beta         {slug, label} on a beta's own page, else null
  sections[]   id, label, items[]
    items[]    title, summary, compact (rendered as a one-line brief),
               publisher {name, icon, host}, published {iso, label} or null,
               sources[] {label, url, discussion}

And out/sources.json, the whitelist for the sources page, in sources.yaml order:

  runs         how many of the latest issues the stats cover
  groups[]     label, sources[]
    sources[]  id, name, kind ("官方博客 · RSS"), homepage or null, icon (the site's favicon) or null,
               enabled, repos[] ("owner/name"),
               stats {ok, runs, candidates (average per run), picked} or null (disabled, never fetched)

And into public/ (web/public, copied as is into the site): feed.xml, the RSS feed with absolute
links under base_url, and .nojekyll.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

from daily.config import SourceConfig
from daily.dedup import url_key
from daily.digest import SECTIONS, is_api
from daily.render import HOST_LABELS, source_labels
from daily.site import DEFAULT_BASE_URL, FALLBACK_NOTICE, RECENT_DAYS, Issue, feed, load_issues
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
# Beta slug (digest.api.<slug>.json) -> its label on the page.
BETA_LABELS = {"deepseek": "DeepSeek", "gemini": "Gemini", "minimax": "MiniMax"}
# Whose icon a source with neither a homepage nor a page url gets.
ICON_HOSTS = {"github_releases": "github.com"}

# sources.yaml kind -> card group on the sources page, in display order.
SOURCE_GROUPS = {
    "blog": "官方博客",
    "paper": "论文",
    "release": "开源",
    "repo": "开源",
    "model": "模型",
    "discussion": "社区信号",
}
KIND_LABELS = {
    "blog": "官方博客",
    "paper": "论文",
    "release": "版本发布",
    "repo": "开源项目",
    "model": "模型",
    "discussion": "社区讨论",
}
TYPE_LABELS = {
    "rss": "RSS",
    "html_listing": "列表页",
    "hf_daily_papers": "API",
    "hf_trending_models": "API",
    "github_releases": "GitHub API",
    "github_trending": "Trending 页",
    "hackernews": "Algolia API",
    "reddit": "RSS",
}
# Where a source's card links to, when sources.yaml has no `homepage` (its `url` is a feed).
TYPE_HOMEPAGES = {
    "hf_daily_papers": "https://huggingface.co/papers",
    "hf_trending_models": "https://huggingface.co/models?sort=trending",
    "github_trending": "https://github.com/trending",
    "hackernews": "https://news.ycombinator.com/",
}


@dataclass
class SourceStats:
    runs: int = 0  # issues in which the source was enabled
    ok: int = 0
    candidates: int = 0
    picked: int = 0  # items of full issues citing one of its candidates


def export(
    out: Path, public: Path, data_dir: Path, sources: list[SourceConfig], base_url: str = DEFAULT_BASE_URL
) -> list[Issue]:
    """Write out/issues/*.json and out/beta/*/*.json for every publishable issue and beta
    (replacing what an earlier export left), out/sources.json, and public/feed.xml and
    public/.nojekyll."""
    folder, beta_folder = out / "issues", out / "beta"
    folder.mkdir(parents=True, exist_ok=True)
    for stale in folder.glob("*.json"):
        stale.unlink()
    shutil.rmtree(beta_folder, ignore_errors=True)
    issues = load_issues(data_dir)
    for issue in issues:
        _write_json(folder / f"{issue.slug}.json", issue_data(issue))
        for slug in issue.betas:
            (beta_folder / issue.slug).mkdir(parents=True, exist_ok=True)
            _write_json(beta_folder / issue.slug / f"{slug}.json", issue_data(issue, slug))
    _write_json(out / "sources.json", sources_data(sources, data_dir, issues))
    public.mkdir(parents=True, exist_ok=True)
    (public / "feed.xml").write_text(feed(issues, base_url.rstrip("/") + "/"), encoding="utf-8")
    (public / ".nojekyll").write_text("", encoding="utf-8")
    return issues


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def sources_data(sources: list[SourceConfig], data_dir: Path, issues: list[Issue]) -> dict[str, Any]:
    stats = source_stats(sources, data_dir, issues)
    groups: dict[str, list[dict[str, Any]]] = {group: [] for group in dict.fromkeys(SOURCE_GROUPS.values())}
    for source in sources:
        s = stats[source.id]
        homepage = source_homepage(source)
        page = homepage or str(source.options.get("url") or "")
        host = (urlsplit(page).hostname or ICON_HOSTS.get(source.type, "")).removeprefix("www.")
        kind = KIND_LABELS.get(source.kind, source.kind)
        groups.setdefault(SOURCE_GROUPS.get(source.kind, "其他"), []).append(
            {
                "id": source.id,
                "name": source.name,
                "kind": f"{kind} · {TYPE_LABELS.get(source.type, source.type)}",
                "homepage": homepage,
                "icon": f"https://www.google.com/s2/favicons?domain={quote(host)}&sz=64" if host else None,
                "enabled": source.enabled,
                "repos": list(source.options.get("repos") or []) if source.type == "github_releases" else [],
                "stats": (
                    {
                        "ok": s.ok,
                        "runs": s.runs,
                        "picked": s.picked,
                        "candidates": round(s.candidates / s.runs, 1),
                    }
                    if source.enabled and s.runs
                    else None
                ),
            }
        )
    return {
        "runs": RECENT_DAYS,
        "groups": [{"label": label, "sources": members} for label, members in groups.items() if members],
    }


def source_stats(sources: list[SourceConfig], data_dir: Path, issues: list[Issue]) -> dict[str, SourceStats]:
    stats = {source.id: SourceStats() for source in sources}
    runs = sorted(data_dir.glob("*/candidates.json"))[-RECENT_DAYS:]
    for path in runs:
        try:
            reports = json.loads(path.read_text(encoding="utf-8")).get("sources", [])
        except json.JSONDecodeError:
            continue
        for report in reports:
            s = stats.get(report.get("id"))
            if s is None or report.get("status") == "disabled":
                continue
            s.runs += 1
            s.ok += report.get("status") == "ok"
            s.candidates += int(report.get("count") or 0)
    run_dates = {path.parent.name for path in runs}
    for issue in issues:
        if issue.fallback or issue.slug not in run_dates:
            continue
        by_id = issue.by_id
        for item in issue.digest["items"]:
            cited = {
                name
                for s in item["sources"]
                if (c := by_id.get(s.get("candidate_id") or ""))
                for name in [c["source"]] + [a.get("source") for a in c.get("also_from") or []]
            }
            for source_id in cited & stats.keys():
                stats[source_id].picked += 1
    return stats


def source_homepage(source: SourceConfig) -> str | None:
    options = source.options
    if options.get("homepage"):
        return str(options["homepage"])
    if source.type == "reddit":
        return f"https://www.reddit.com/r/{options['subreddit']}/"
    if source.type in TYPE_HOMEPAGES:
        return TYPE_HOMEPAGES[source.type]
    return str(options["url"]) if source.type == "html_listing" else None


def issue_data(issue: Issue, beta: str | None = None) -> dict[str, Any]:
    """The main issue's page, or with beta, the page of that beta."""
    digest = issue.betas[beta] if beta else issue.digest
    fallback = digest.get("mode") == "fallback"
    by_id = issue.by_id
    sections = []
    for section, heading in SECTIONS.items():
        items = [item for item in digest["items"] if item["section"] == section]
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
        "fallback": fallback,
        "notice": FALLBACK_NOTICE if fallback else None,
        "description": " ".join(digest.get("highlights") or []),
        "editor": None if fallback else editor(digest),
        "betas": [_beta(slug) for slug in issue.betas],
        "beta": _beta(beta) if beta else None,
        "sections": sections,
    }


def editor(digest: dict[str, Any]) -> str:
    """The API route's model without its provider prefix; a Claude route digest may name its model."""
    model = str(digest.get("model") or "")
    if is_api(digest):
        return model.split(":", 1)[-1]
    return model or "Claude"


def _beta(slug: str) -> dict[str, str]:
    return {"slug": slug, "label": BETA_LABELS.get(slug, slug)}


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
