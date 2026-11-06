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

SCHEMA_VERSION = 1
SCORE_MAX = (3, 3, 2)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def file_name(data: dict[str, Any]) -> str | None:
    """The trace that goes with a digest (or a trace), trace.claude.json or trace.api.<slug>.json;
    None for a route that keeps none (daily.routes)."""
    return routes.trace_name(data)


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
