"""The 生成记录 (trace) of an editor route: what it did with an issue, step by step.

candidates.json says what was fetched and filtered; the digest says what was published. The trace
holds what happened in between, so the process page (issue #26) can show what each route picked,
what each validate round dropped and why, and #25 can count it across days. One file per route:
data/YYYY-MM-DD/trace.claude.json and trace.api.<slug>.json (daily.routes names them), next to the
digest it explains.

Nothing here decides what gets published; a missing or broken trace only leaves the page with less
to show.

  schema_version, date, channel (a route of daily.routes: "claude" | "api"), model (or null)
  started_at  when the run started
  scores      candidate id -> [重要性 0-3, 实用性 0-3, 新颖性 0-2], the rubric of SKILL.md section 2;
              null when the route did not record them
  steps[]     step, at, and per step:
    no_first_hand    candidates[]: removed before the API route's pick, as discussion threads alone
    pick             groups[]: the API route's picks, candidate ids, main source first
    over_picks       groups[]: picks beyond api_editor.PICKS, cut
    read             pages[] {candidate, url, state ("ok" | "failed" | "no_prose"), status, error,
                     passages}: the pages the API route opened (not on the process page yet)
    skipped          round ("draft" | "fix"), skipped[] {group, candidates[], reason}: picks the API
                     route's model says it did not write, and why (not on the process page yet)
    self_check       items[] {title, candidates[], reason}: what Claude dropped in its self-check
    check, precheck, final, en, draft, fix, highlights
                     one validate round: checked_links, errors[], warnings[], highlights[]
                     (the 今日要点 it checked), items[] {title, section, candidates[], reasons[]}
                     (reasons empty: it passed)
    fix_ignored      error: the API route's fix reply had no items, so the draft went on
    a step may carry an error instead, when the request behind it failed
  failure     {step, error} when the run produced no digest, else null
  adopt[]     at, edition ("zh" | "en"), run (the digest's generated_at), adopted, reason
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from daily import digest, routes
from daily.issue import IssueDir

SCHEMA_VERSION = 1
SCORE_MAX = (3, 3, 2)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new(date: str, channel: str, model: str | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "date": date,
        "channel": channel,
        "model": model,
        "started_at": now(),
        "scores": None,
        "steps": [],
        "failure": None,
        "adopt": [],
    }


def load(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get("steps"), list) else None


def save(path: Path, trace: dict[str, Any]) -> None:
    path.write_text(json.dumps(trace, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def scores(raw: Any, known: set[str]) -> dict[str, list[int]]:
    """The well-formed scores of known candidates; the rest is left out, not guessed."""
    result: dict[str, list[int]] = {}
    for cid, value in raw.items() if isinstance(raw, dict) else []:
        if cid not in known or not isinstance(value, list) or len(value) != len(SCORE_MAX):
            continue
        if all(type(v) is int and 0 <= v <= m for v, m in zip(value, SCORE_MAX, strict=True)):
            result[cid] = value
    return result


def validate_step(step: str, data: Any, report: digest.Report, checked_links: bool) -> dict[str, Any]:
    """One validate round: every item it saw, with the reasons it failed (none: it passed)."""
    items = data.get("items") if isinstance(data, dict) else None
    highlights = data.get("highlights") if isinstance(data, dict) else None
    return {
        "step": step,
        "at": now(),
        "checked_links": checked_links,
        "errors": report.errors,
        "warnings": report.warnings,
        "highlights": [str(h) for h in highlights] if isinstance(highlights, list) else [],
        "items": [
            {
                "title": item.get("title") if isinstance(item, dict) else None,
                "section": item.get("section") if isinstance(item, dict) else None,
                "candidates": digest.source_ids(item),
                "reasons": report.item_errors.get(index, []),
            }
            for index, item in enumerate(items if isinstance(items, list) else [])
        ],
    }


def adopt_record(edition: str, incoming: Any, adopted: bool, reason: str) -> dict[str, Any]:
    run = incoming.get("generated_at") if isinstance(incoming, dict) else None
    return {"at": now(), "edition": edition, "run": run, "adopted": adopted, "reason": reason}


# The routes that work by SKILL.md (the Claude route) record their trace through the CLI, step by step:
# `daily trace scores` starts a run, `daily validate` adds each round, `daily trace self-check` what the
# self-check dropped, and `daily degrade --force` that the editor gave up.


def skill_route(data: Any) -> str | None:
    """The channel of an edit by a route that works by SKILL.md (the Claude route); None otherwise."""
    route = routes.of(data)
    return route.channel if route is not None and route.channel in routes.SKILL_ROUTES else None


def needs_self_check(folder: IssueDir, data: Any) -> bool:
    """An edit by a SKILL.md route whose trace has no self-check, not even an empty one."""
    if (channel := skill_route(data)) is None:
        return False
    record = load(folder.route_trace(channel))
    return not any(s.get("step") == "self_check" for s in (record or {}).get("steps") or [])


def record_validate(folder: IssueDir, data: Any, step: dict[str, Any]) -> None:
    """Add a validate round of a SKILL.md route's edit to its trace; other digests have none."""
    if (channel := skill_route(data)) is None:
        return
    path = folder.route_trace(channel)
    record = load(path) or new(folder.date, channel)
    record["model"] = data.get("model") or record.get("model")
    record["steps"].append(step)
    save(path, record)


def record_scores(folder: IssueDir, channel: str, candidates: dict[str, Any], raw: Any) -> tuple[int, int]:
    """Starts the trace of a new run with the editor's scores: (scored, candidates without a score)."""
    known = {c["id"] for c in candidates["candidates"]}
    record = new(candidates["date"], channel)
    record["scores"] = scores(raw, known)
    save(folder.route_trace(channel), record)
    return len(record["scores"]), len(known - record["scores"].keys())


def record_self_check(folder: IssueDir, channel: str, candidates: dict[str, Any], raw: Any) -> int:
    """Adds the items the editor's self-check dropped; how many. ValueError if raw is not a list of them."""
    if not isinstance(raw, list) or not all(isinstance(v, dict) for v in raw):
        raise ValueError('self-check takes [{"candidates": [...], "title": ..., "reason": ...}]')
    known = {c["id"] for c in candidates["candidates"]}
    path = folder.route_trace(channel)
    record = load(path) or new(candidates["date"], channel)
    items = [
        {
            "title": v.get("title"),
            "candidates": [c for c in v.get("candidates") or [] if c in known],
            "reason": v.get("reason"),
        }
        for v in raw
    ]
    record["steps"].append({"step": "self_check", "at": now(), "items": items})
    save(path, record)
    return len(items)


def record_give_up(folder: IssueDir, channel: str) -> None:
    """The editor gave up and published the fallback (SKILL.md step 6): its last step is the failure."""
    path = folder.route_trace(channel)
    if not (record := load(path)):
        return
    last = record["steps"][-1] if record["steps"] else {}
    error = "; ".join(last.get("errors") or []) or "the editor published the fallback"
    record["failure"] = {"step": last.get("step"), "error": error}
    save(path, record)
