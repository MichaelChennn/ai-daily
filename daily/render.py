"""`daily render`: digest.json -> digest.md, the issue as it reads on GitHub (the site is daily/site.py)."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from daily.dedup import url_key
from daily.digest import SECTIONS

FALLBACK_NOTE = "> 降级版：今天的编辑环节没有完成，以下是按热度挑选的候选标题和原始链接，未经编辑。"
HOST_LABELS = {
    "news.ycombinator.com": "HN 讨论",
    "www.reddit.com": "Reddit 讨论",
    "reddit.com": "Reddit 讨论",
    "github.com": "GitHub",
    "huggingface.co": "Hugging Face",
    "arxiv.org": "arXiv",
}


def to_markdown(digest: dict[str, Any], candidates: dict[str, Any] | None = None) -> str:
    by_id = {c["id"]: c for c in (candidates or {}).get("candidates", [])}
    lines = [f"# {digest['date']} · AI 科技日报", ""]
    if digest.get("mode") == "fallback":
        lines += [FALLBACK_NOTE, ""]
    if digest.get("highlights"):
        lines += ["## 今日要点", ""] + [f"- {h}" for h in digest["highlights"]] + [""]

    for section, heading in SECTIONS.items():
        items = [item for item in digest["items"] if item["section"] == section]
        if not items:
            continue
        lines += [f"## {heading}", ""]
        for item in items:
            links = " · ".join(f"[{label}]({s['url']})" for s, label in source_labels(item["sources"], by_id))
            if section == "brief" or not item.get("summary"):
                lines.append(f"- **{item['title']}** {item.get('summary', '')} {links}".replace("  ", " "))
                continue
            lines += [f"### {item['title']}", "", item["summary"], "", f"来源：{links}"]
            if item.get("tags"):
                lines[-1] += "　" + " ".join(f"`{t}`" for t in item["tags"])
            lines.append("")
        if lines[-1] != "":
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def source_labels(
    sources: list[dict[str, Any]], by_id: dict[str, dict[str, Any]]
) -> list[tuple[dict[str, Any], str]]:
    labels = [_label(s, by_id) for s in sources]
    # Several links from one source (three weight repos, two releases) read better by their own titles.
    return [
        (
            s,
            by_id[s["candidate_id"]]["title"]
            if labels.count(label) > 1 and s.get("candidate_id") in by_id
            else label,
        )
        for s, label in zip(sources, labels, strict=True)
    ]


def _label(source: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> str:
    if source.get("title"):
        return source["title"]
    url = source["url"]
    c = by_id.get(source.get("candidate_id", ""))
    host = urlsplit(url).hostname or url
    if c is not None and url_key(url) == url_key(c["url"]) and c.get("kind") != "discussion":
        return c["source_name"]
    return HOST_LABELS.get(host, host.removeprefix("www."))
