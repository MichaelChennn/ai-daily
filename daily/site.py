"""`daily build`: the static site and full-text RSS feed published to GitHub Pages.

Plain Python, no template engine and no JavaScript. Pages:

  index.html            latest issue in full, then the other issues of the last 30 days
  YYYY-MM-DD/           one page per issue, with previous / next links
  archive/              every issue, by month
  sources/              the source whitelist as cards, with fetch and usage stats
  feed.xml              RSS 2.0, the last 30 days, full text in content:encoded

Only digests that pass `validate` (offline) are published, the same gate the editor and the
fallback go through; items it would drop are left out. Fallback issues carry a visible notice.
"""

from __future__ import annotations

import json
import logging
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from html import escape
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from daily import digest as digest_mod
from daily.config import SourceConfig
from daily.digest import SECTIONS
from daily.render import source_labels
from daily.window import BEIJING, PUBLISH_TIME

log = logging.getLogger(__name__)

SITE_TITLE = "AI 科技日报"
SITE_DESCRIPTION = "每天北京时间 06:00 更新的中文 AI 技术日报：5 分钟读完，每一条都附一手来源。"
DEFAULT_BASE_URL = "https://michaelchennn.github.io/ai-daily/"
REPO_URL = "https://github.com/MichaelChennn/ai-daily"
RECENT_DAYS = 30
FALLBACK_NOTICE = "降级版：今天的编辑环节没有按时完成，以下是按热度挑选的候选标题和原始链接，未经编辑。"
WEEKDAYS = "一二三四五六日"

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
TIER_BADGES = {1: '<span class="tier t1">一手</span>', 2: '<span class="tier t2">社区信号</span>'}
# Where a source's card links to, when sources.yaml has no `homepage` (its `url` is a feed).
TYPE_HOMEPAGES = {
    "hf_daily_papers": "https://huggingface.co/papers",
    "hf_trending_models": "https://huggingface.co/models?sort=trending",
    "github_trending": "https://github.com/trending",
    "hackernews": "https://news.ycombinator.com/",
}


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
            return datetime.combine(self.date, PUBLISH_TIME, BEIJING)


@dataclass
class SourceStats:
    runs: int = 0  # issues in which the source was enabled
    ok: int = 0
    candidates: int = 0
    picked: int = 0  # items of full issues citing one of its candidates
    last_status: str | None = None
    last_error: str | None = None


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


def build(
    out: Path, data_dir: Path, sources: list[SourceConfig], base_url: str = DEFAULT_BASE_URL
) -> list[Issue]:
    """Write the whole site to out (replacing what a previous build left there)."""
    if out.exists():
        if any(out.iterdir()) and not (out / "feed.xml").exists():
            raise ValueError(f"{out} is not empty and does not look like a site build; refusing to wipe it")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    base_url = base_url.rstrip("/") + "/"
    issues = load_issues(data_dir)

    _write(out / "index.html", index_page(issues))
    for i, issue in enumerate(issues):
        newer = issues[i - 1] if i > 0 else None
        older = issues[i + 1] if i + 1 < len(issues) else None
        _write(out / issue.slug / "index.html", issue_page(issue, newer, older))
    _write(out / "archive" / "index.html", archive_page(issues))
    _write(out / "sources" / "index.html", sources_page(sources, data_dir, issues))
    # Served for any missing path, so its links are absolute.
    not_found = f'<p>这个页面不存在。<a href="{base_url}">回到首页</a></p>'
    _write(out / "404.html", _layout("找不到页面", not_found, base_url))
    _write(out / "feed.xml", feed(issues, base_url))
    _write(out / "style.css", resources.files("daily").joinpath("static/style.css").read_text("utf-8"))
    (out / ".nojekyll").write_text("", encoding="utf-8")
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# --- pages -----------------------------------------------------------------------------------


def index_page(issues: list[Issue]) -> str:
    if not issues:
        return _layout(SITE_TITLE, "<p>还没有发布任何一期。</p>", "")
    latest, *others = recent(issues)
    body = [f'<article class="issue">{_issue_header(latest, "", link=True)}{issue_body(latest)}</article>']
    if others:
        body.append('<section class="recent"><h2>往期 · 最近 30 天</h2>')
        body.append(_issue_list(others, ""))
        body.append("</section>")
    body.append('<p class="more"><a href="archive/">全部存档 →</a></p>')
    return _layout(SITE_TITLE, "".join(body), "")


def issue_page(issue: Issue, newer: Issue | None, older: Issue | None) -> str:
    nav = ['<nav class="pager">']
    nav.append(f'<a href="../{older.slug}/">← {_short(older.date)}</a>' if older else "<span></span>")
    nav.append('<a href="../archive/">存档</a>')
    nav.append(f'<a href="../{newer.slug}/">{_short(newer.date)} →</a>' if newer else "<span></span>")
    nav.append("</nav>")
    body = f'<article class="issue">{_issue_header(issue, "../")}{issue_body(issue)}</article>{"".join(nav)}'
    title = f"{issue.slug} · {SITE_TITLE}" + ("（降级版）" if issue.fallback else "")
    return _layout(title, body, "../", description=" ".join(issue.digest.get("highlights") or []))


def archive_page(issues: list[Issue]) -> str:
    by_month: dict[str, list[Issue]] = defaultdict(list)
    for issue in issues:
        by_month[f"{issue.date.year} 年 {issue.date.month} 月"].append(issue)
    body = [f'<h1>存档</h1><p class="lede">共 {len(issues)} 期。</p>']
    for month, month_issues in by_month.items():
        body.append(f"<section><h2>{month}</h2>{_issue_list(month_issues, '../')}</section>")
    return _layout(f"存档 · {SITE_TITLE}", "".join(body), "../")


def sources_page(sources: list[SourceConfig], data_dir: Path, issues: list[Issue]) -> str:
    stats = source_stats(sources, data_dir, issues)
    groups: dict[str, list[SourceConfig]] = {group: [] for group in dict.fromkeys(SOURCE_GROUPS.values())}
    for source in sources:
        groups[SOURCE_GROUPS.get(source.kind, "其他")].append(source)
    body = [
        "<h1>信息源</h1>",
        '<p class="lede">日报只从下面这份白名单抓取。<span class="tier t1">一手</span> '
        "是官方博客、论文、Release、模型页，可以作为事实来源；"
        '<span class="tier t2">社区信号</span> 是 HN 和 Reddit，只用来判断热度，'
        "条目必须链接到它们指向的一手页面。统计范围是最近 30 期。</p>",
    ]
    for group, members in groups.items():
        if not members:
            continue
        body.append(f'<section class="source-group"><h2>{group}</h2><div class="cards">')
        body += [_source_card(source, stats[source.id]) for source in members]
        body.append("</div></section>")
    return _layout(f"信息源 · {SITE_TITLE}", "".join(body), "../", wide=True)


def source_stats(sources: list[SourceConfig], data_dir: Path, issues: list[Issue]) -> dict[str, SourceStats]:
    stats = {source.id: SourceStats() for source in sources}
    runs = sorted(data_dir.glob("*/candidates.json"))[-RECENT_DAYS:]
    for path in runs:  # oldest first, so last_status ends up being the latest run's
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
            s.last_status, s.last_error = report.get("status"), report.get("error")
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


def _source_card(source: SourceConfig, s: SourceStats) -> str:
    classes = "card" + ("" if source.enabled else " disabled")
    homepage = _source_homepage(source)
    name = escape(source.name)
    name_html = f'<a href="{escape(homepage)}">{name}</a>' if homepage else name
    tier = TIER_BADGES[source.tier]
    kind = f"{KIND_LABELS.get(source.kind, source.kind)} · {TYPE_LABELS.get(source.type, source.type)}"
    parts = [f'<article class="{classes}"><header><h3>{name_html}</h3>{tier}</header>']
    parts.append(f'<p class="kind">{escape(kind)}</p>')
    if not source.enabled:
        parts.append('<p class="status">已停用</p>')
    elif s.runs:
        parts.append(
            '<dl class="stats">'
            f"<div><dt>抓取成功</dt><dd>{s.ok}/{s.runs}</dd></div>"
            f"<div><dt>平均候选</dt><dd>{s.candidates / s.runs:.1f}</dd></div>"
            f"<div><dt>入选条目</dt><dd>{s.picked}</dd></div>"
            "</dl>"
        )
        if s.last_status == "error":
            error = escape(str(s.last_error or "")[:120])
            parts.append(f'<p class="status error">最近一次抓取失败：{error}</p>')
    else:
        parts.append('<p class="status">还没有抓取记录</p>')
    if source.type == "github_releases":
        repos = "".join(
            f'<li><a href="https://github.com/{escape(r)}">{escape(r.split("/")[-1])}</a></li>'
            for r in source.options.get("repos", [])
        )
        parts.append(f'<ul class="chips">{repos}</ul>')
    parts.append("</article>")
    return "".join(parts)


def _source_homepage(source: SourceConfig) -> str | None:
    options = source.options
    if options.get("homepage"):
        return str(options["homepage"])
    if source.type == "reddit":
        return f"https://www.reddit.com/r/{options['subreddit']}/"
    if source.type in TYPE_HOMEPAGES:
        return TYPE_HOMEPAGES[source.type]
    return str(options["url"]) if source.type == "html_listing" else None


# --- issue fragments -------------------------------------------------------------------------


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


def _issue_header(issue: Issue, prefix: str, link: bool = False) -> str:
    when = issue.published_at.astimezone(BEIJING).strftime("%H:%M")
    title = f"{issue.slug} · 周{WEEKDAYS[issue.date.weekday()]}"
    if link:
        title = f'<a href="{prefix}{issue.slug}/">{title}</a>'
    meta = f"{len(issue.digest['items'])} 条 · 北京时间 {when} " + ("生成" if issue.fallback else "编辑完成")
    badge = ' <span class="badge">降级版</span>' if issue.fallback else ""
    return f'<header class="issue-header"><h1>{title}{badge}</h1><p class="issue-meta">{meta}</p></header>'


def _issue_list(issues: list[Issue], prefix: str) -> str:
    rows = []
    for issue in issues:
        highlights = issue.digest.get("highlights") or []
        items = issue.digest["items"]
        teaser = highlights[0] if highlights else items[0]["title"] if items else ""
        badge = '<span class="badge">降级版</span>' if issue.fallback else ""
        rows.append(
            f'<li><a href="{prefix}{issue.slug}/"><time datetime="{issue.slug}">'
            f"{_short(issue.date)} 周{WEEKDAYS[issue.date.weekday()]}</time>"
            f'<span class="teaser">{escape(teaser)}</span>{badge}</a></li>'
        )
    return f'<ul class="issue-list">{"".join(rows)}</ul>'


def _short(value: date) -> str:
    return value.strftime("%m-%d")


def _layout(title: str, body: str, prefix: str, description: str = "", wide: bool = False) -> str:
    description = escape(description or SITE_DESCRIPTION)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="{prefix}style.css">
<link rel="alternate" type="application/rss+xml" title="{SITE_TITLE}" href="{prefix}feed.xml">
</head>
<body{' class="wide"' if wide else ""}>
<header class="site-header">
<a class="site-title" href="{prefix or "./"}">{SITE_TITLE}</a>
<nav>
<a href="{prefix}archive/">存档</a><a href="{prefix}sources/">信息源</a><a href="{prefix}feed.xml">RSS</a>
</nav>
</header>
<main>
{body}
</main>
<footer class="site-footer">
<p>每天北京时间 06:00 更新 · 抓取与校验是确定性代码，编辑由 Claude 完成，没有人工校对。
<a href="{REPO_URL}">源代码</a></p>
</footer>
</body>
</html>
"""


# --- feed ------------------------------------------------------------------------------------


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
