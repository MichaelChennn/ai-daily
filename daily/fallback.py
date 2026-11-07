"""`daily degrade`: the title + link issue published when the editor did not deliver.

Deterministic, no LLM: official posts first, then the hottest few of each kind by their signals.
Candidates an earlier main digest already reported (`reported_on`) go last.
Items keep their original (English) titles and have no summary.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from typing import Any

from daily import digest, issue, trace
from daily.digest import SCHEMA_VERSION, is_discussion
from daily.issue import IssueDir

# kind -> section, and how many items each section gets (12 in total at most).
SECTION_OF_KIND = {
    "blog": "headline",
    "model": "model",
    "paper": "paper",
    "release": "tool",
    "repo": "tool",
    "discussion": "brief",
    "commentary": "brief",
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
        key=lambda pair: (bool(pair[1].get("reported_on")), pair[1].get("tier", 2), -heat(pair[1]), pair[0]),
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
        "channel": "fallback",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "highlights": [],
        "items": [item for section in SECTION_LIMITS for item in picked[section]],
        "research": [],
    }


def degrade(folder: IssueDir, force: bool = False, channel: str = "claude") -> bool:
    """Writes the fallback as digest.json when there is no valid one (with force: whatever there is),
    keeping the digest it replaces as digest.rejected.json. With force, the editor of the route
    `channel` gave up, which goes into its trace. False if there are no candidates to publish."""
    candidates = folder.read_candidates()
    path = folder.digest
    if path.exists() and not force:
        try:
            report = digest.validate(issue.read(path), candidates)
        except json.JSONDecodeError as exc:
            report = digest.Report(errors=[f"invalid JSON: {exc}"])
        if report.ok:
            print(f"{path} is valid, nothing to do", file=sys.stderr)
            return True
        print(
            f"{path} is not valid ({(report.errors or ['invalid items'])[0]}), replacing it", file=sys.stderr
        )
    if path.exists():
        shutil.copy(path, folder.rejected)
    if force:  # the editor gave up (SKILL.md step 6)
        trace.record_give_up(folder, channel)
    data = build_fallback(candidates)
    if not data["items"]:
        print("no candidates to publish", file=sys.stderr)
        return False
    issue.write(path, digest.apply_report(data, digest.validate(data, candidates), checked_links=False))
    print(path)
    return True
