"""`daily degrade`: the title + link issue published when the editor did not deliver.

Deterministic, no LLM: official posts first, then the hottest few of each kind by their signals.
Items keep their original (English) titles and have no summary.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from daily.digest import SCHEMA_VERSION, is_discussion

# kind -> section, and how many items each section gets (12 in total at most).
SECTION_OF_KIND = {
    "blog": "headline",
    "model": "model",
    "paper": "paper",
    "release": "tool",
    "repo": "tool",
    "discussion": "brief",
}
SECTION_LIMITS = {"headline": 4, "model": 2, "paper": 2, "tool": 2, "brief": 2}


def heat(candidate: dict[str, Any]) -> float:
    s = candidate.get("signals") or {}
    score = float(s.get("hn_points", 0)) + 10 * float(s.get("upvotes", 0)) + float(s.get("stars_today", 0))
    for rank_signal in ("trending_rank", "reddit_rank"):
        if rank_signal in s:
            score += max(0, 50 - int(s[rank_signal])) * 10
    return score + 100 * len(candidate.get("also_from") or [])  # picked up by more than one source


def build_fallback(candidates: dict[str, Any]) -> dict[str, Any]:
    # Ties keep candidates.json order, which follows sources.yaml (labs' own blogs first).
    ranked = sorted(
        enumerate(candidates.get("candidates", [])),
        key=lambda pair: (bool(pair[1].get("seen_on")), pair[1].get("tier", 2), -heat(pair[1]), pair[0]),
    )
    picked: dict[str, list[dict[str, Any]]] = {section: [] for section in SECTION_LIMITS}
    clusters_used: set[str] = set()
    for _, c in ranked:
        section = SECTION_OF_KIND.get(c.get("kind"), "brief")
        if len(picked[section]) >= SECTION_LIMITS[section] or c.get("cluster_id") in clusters_used:
            continue
        if is_discussion(c["url"], c):  # Ask HN / Reddit self posts: no first-hand page to link
            continue
        clusters_used.add(c.get("cluster_id"))
        picked[section].append(
            {
                "section": section,
                "title": c["title"],
                "summary": "",
                "sources": [{"candidate_id": c["id"], "url": c["url"]}],
                "tags": [],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "date": candidates["date"],
        "mode": "fallback",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "highlights": [],
        "items": [item for section in SECTION_LIMITS for item in picked[section]],
        "research": [],
    }
