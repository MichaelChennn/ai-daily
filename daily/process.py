"""The 生成过程 page's data (issue #26): how one issue was made, from the fetch to what each editor
route published. `daily export` writes it to out/process/YYYY-MM-DD.json; the page only lays it out.

It reads candidates.json, the digests and the traces (daily/trace.py). An issue from before the
traces, or a route without one, shows what its digest's validation still says, and recorded is
false: the page marks the rest 当时未记录.

  date
  main         the route whose digest is the main issue: "claude", "api.<slug>", or "fallback"
  funnel       filtered (null: not recorded), raw, after_url_merge, already_published, candidates
  sources[]    id, name, status, count, error, filtered {reason: count} or null
  filtered[]   source, name, items[] {title, url, reason, value}: the fetchers' 过滤, by source;
               null when not recorded
  channels[]   id ("claude", "api.<slug>"), label, model, main, recorded, scored,
               failure {step, label, error} or null,
               funnel[] {label, value}, adopt[],
               steps[] {step, label, at, kept, passed[], dropped[], highlights[], errors[]}
    passed[]   title, candidates[]
    dropped[]  title, candidates[], reasons[]
    highlights[]
               text (a 日报简介 sentence; null if unknown), missing[]: its words that no passing item has
  rows[]       one per candidate: id, title, url, source, kind, cells {channel id: cell},
               differs (the routes did not treat it alike), dropped (a route dropped it),
               high_unpicked (scored >= HIGH_SCORE by a route that did not publish it)
    cell       state ("unpicked" | "dropped" | "published"), step (label) or null, reasons[],
               score [重要性, 实用性, 新颖性] or null, total or null
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from daily import digest, trace
from daily.site import publishable

HIGH_SCORE = 5  # SKILL.md section 2: a total of about 5 qualifies
STEP_LABELS = {
    "setup": "配置",
    "no_first_hand": "无一手来源，预先去掉",
    "pick": "挑选",
    "over_picks": "超出挑选上限，截掉",
    "read": "打开原文",
    "self_check": "自检",
    "check": "校验",
    "precheck": "预检",
    "draft": "第一稿校验",
    "fix": "修改稿校验",
    "highlights": "要点改用标题后校验",
    "final": "正式校验",
    "en": "英文版校验",
    "en_highlights": "英文版要点改用标题后校验",
}
EN_STEPS = {"en", "en_highlights"}
VALIDATE_STEPS = {"check", "precheck", "draft", "fix", "highlights", "final"}
FILTER_REASONS = {
    "not_ai": "与 AI 无关",
    "min_stars_today": "今日 star 不够",
    "min_upvotes": "点赞不够",
    "max_age_days": "模型发布太久",
    "noisy_model": "衍生权重",
}


def issue_process(
    issue_dir: Path, candidates: dict[str, Any], source_names: dict[str, str], labels: dict[str, str]
) -> dict[str, Any]:
    """labels: API slug -> its name on the page."""
    stats = candidates.get("stats") or {}
    main = _read(issue_dir / "digest.json")
    channels = [_channel(issue_dir, cid, candidates, main, labels) for cid in _channel_ids(issue_dir, main)]
    channels = [c for c in channels if c is not None]
    recorded = "filtered" in candidates
    return {
        "date": candidates["date"],
        "main": _main_id(main),
        "funnel": {
            "filtered": stats.get("filtered") if recorded else None,
            "raw": stats.get("raw"),
            "after_url_merge": stats.get("after_url_merge"),
            "already_published": stats.get("dropped_already_published"),
            "candidates": stats.get("candidates"),
        },
        "sources": [
            {
                "id": s["id"],
                "name": source_names.get(s["id"], s["id"]),
                "status": s.get("status"),
                "count": s.get("count"),
                "error": s.get("error"),
                "filtered": s.get("filtered") if recorded else None,
            }
            for s in candidates.get("sources") or []
            if s.get("status") != "disabled"
        ],
        "filtered": _filtered(candidates, source_names) if recorded else None,
        "channels": [{k: v for k, v in c.items() if k != "cells"} for c in channels],
        "rows": _rows(candidates, channels),
    }


def _read(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _main_id(main: dict[str, Any] | None) -> str | None:
    if main is None:
        return None
    if main.get("mode") == "fallback":
        return "fallback"
    return "api." + digest.slug(main.get("model") or "") if digest.is_api(main) else "claude"


def _channel_ids(issue_dir: Path, main: dict[str, Any] | None) -> list[str]:
    ids = ["claude"] if (issue_dir / "trace.claude.json").exists() or _main_id(main) == "claude" else []
    slugs = {
        p.name.split(".")[2]
        for pattern in ("digest.api.*.json", "trace.api.*.json")
        for p in issue_dir.glob(pattern)
    }
    return ids + [f"api.{slug}" for slug in sorted(slugs)]


def _channel(
    issue_dir: Path,
    cid: str,
    candidates: dict[str, Any],
    main: dict[str, Any] | None,
    labels: dict[str, str],
) -> dict[str, Any] | None:
    api = cid.startswith("api.")
    record = trace.load(issue_dir / f"trace.{cid}.json")
    digest_path = issue_dir / (f"digest.{cid}.json" if api else "digest.json")
    raw = _read(digest_path)
    if not api and raw is not None and (digest.is_api(raw) or raw.get("mode") != "full"):
        raw = None  # the main issue is not the Claude route's
    published = publishable(digest_path, candidates) if raw is not None else None
    if record is None and raw is None:
        return None
    steps = record["steps"] if record else _steps_from_validation(raw)
    model = (record or {}).get("model") or (raw or {}).get("model")
    failure = (record or {}).get("failure")
    return {
        "id": cid,
        "label": labels.get(cid[4:], cid[4:]) if api else "Claude",
        "model": model,
        "main": _main_id(main) == cid,
        "recorded": record is not None,
        "scored": bool(record and record.get("scores")),
        "failure": {**failure, "label": STEP_LABELS.get(failure.get("step"), failure.get("step"))}
        if failure
        else None,
        "funnel": _funnel(candidates, steps, published),
        "steps": [_step(s, (raw or {}).get("highlights") or []) for s in steps],
        "adopt": (record or {}).get("adopt") or [],
        "cells": _cells(candidates, steps, published, (record or {}).get("scores") or {}),
    }


def _steps_from_validation(data: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Without a trace, the digest's validation: one round, its kept and dropped items."""
    if data is None:
        return []
    validation = data.get("validation") or {}
    kept = [
        {
            "title": i.get("title"),
            "section": i.get("section"),
            "candidates": digest.source_ids(i),
            "reasons": [],
        }
        for i in data.get("items") or []
        if isinstance(i, dict)
    ]
    dropped = [{**d, "candidates": d.get("candidates") or []} for d in validation.get("dropped") or []]
    return [{"step": "final", "at": validation.get("validated_at"), "errors": [], "items": dropped + kept}]


def _zh_rounds(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [s for s in steps if s.get("step") in VALIDATE_STEPS and "items" in s]


def _funnel(
    candidates: dict[str, Any], steps: list[dict[str, Any]], published: dict[str, Any] | None
) -> list[dict[str, Any]]:
    rounds = _zh_rounds(steps)
    checked = [s for s in steps if s.get("step") == "self_check"]
    picked: set[str] = set()
    for s in steps:
        if s.get("step") == "pick":
            picked.update(cid for group in s.get("groups") or [] for cid in group)
        for item in s.get("items") or [] if s.get("step") not in EN_STEPS else []:
            picked.update(item.get("candidates") or [])
    written = sum(len(s.get("items") or []) for s in checked) + (len(rounds[0]["items"]) if rounds else 0)
    passed = sum(1 for item in rounds[-1]["items"] if not item.get("reasons")) if rounds else 0
    return [
        {"label": "候选", "value": len(candidates.get("candidates") or [])},
        {"label": "挑中的候选", "value": len(picked)},
        {"label": "写成条目", "value": written},
        {"label": "通过校验", "value": passed},
        {"label": "发布", "value": len(published["items"]) if published else 0},
    ]


def _step(s: dict[str, Any], highlights: list[str]) -> dict[str, Any]:
    name = s.get("step")
    result: dict[str, Any] = {"step": name, "label": STEP_LABELS.get(name, name), "at": s.get("at")}
    if "items" in s and name == "self_check":
        result.update(kept=None, dropped=[{**i, "reasons": [i.get("reason")]} for i in s["items"]])
    elif "items" in s:
        items = s["items"]
        result.update(
            kept=sum(1 for i in items if not i.get("reasons")),
            passed=[
                {"title": i.get("title"), "candidates": i.get("candidates") or []}
                for i in items
                if not i.get("reasons")
            ],
            dropped=[
                {"title": i.get("title"), "candidates": i.get("candidates") or [], "reasons": i["reasons"]}
                for i in items
                if i.get("reasons")
            ],
        )
        errors = s.get("errors") or []
        if "highlights" in s:
            result["highlights"], result["errors"] = _highlight_errors(errors, s["highlights"])
        else:
            # Older traces did not keep the 今日要点 the round checked. The digest's own are a
            # guess, used only when every missing word is found in them.
            guess = _highlight_errors(errors, [] if name in EN_STEPS else highlights)
            if any(h["text"] is None for h in guess[0]):
                guess = _highlight_errors(errors, [])
            result["highlights"], result["errors"] = guess
    elif "groups" in s:
        result.update(kept=len(s["groups"]) if name == "pick" else 0, groups=s["groups"])
    elif "candidates" in s:
        result.update(kept=None, candidates=s["candidates"])
    if s.get("error"):
        result["error"] = s["error"]
    return result


HIGHLIGHT_ERROR = re.compile(r"^highlight: (?:'(.+)'|number (.+)) does not appear in the published items$")


def _highlight_errors(errors: list[str], highlights: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    """The 今日要点 with words no passing item has, each with those words; and the other errors.
    Words found in no highlight go under text None."""
    missing: dict[str | None, list[str]] = {}
    other = []
    for error in errors:
        m = HIGHLIGHT_ERROR.match(error)
        if not m:
            other.append(error)
            continue
        word = m[1] or m[2]
        pattern = re.escape(word) if m[1] else rf"(?<![\d.]){re.escape(word)}(?![\d])"
        text = next((h for h in highlights if re.search(pattern, str(h))), None)
        missing.setdefault(text, []).append(word)
    order = [h for h in highlights if h in missing] + ([None] if None in missing else [])
    return [{"text": text, "missing": missing[text]} for text in order], other


def _cells(
    candidates: dict[str, Any],
    steps: list[dict[str, Any]],
    published: dict[str, Any] | None,
    scores: dict[str, list[int]],
) -> dict[str, dict[str, Any]]:
    """Each candidate's fate in one route: published, or the last step that dropped it."""
    out = {cid for item in (published or {}).get("items") or [] for cid in digest.source_ids(item)}
    fates: dict[str, tuple[str, str | None, list[str]]] = {}  # candidate -> (state, step, reasons)
    previous: set[str] = set()  # in the last validate round's draft
    for s in steps:
        name = s.get("step")
        label = STEP_LABELS.get(name, name)
        if name == "no_first_hand":
            for cid in s.get("candidates") or []:
                fates[cid] = ("unpicked", label, [])
        elif name in ("pick", "over_picks"):
            reason = "挑选后没有写" if name == "pick" else "超出挑选上限"
            for cid in (c for group in s.get("groups") or [] for c in group):
                fates[cid] = ("dropped", label, [reason])
        elif name == "self_check":
            for item in s.get("items") or []:
                for cid in item.get("candidates") or []:
                    fates[cid] = ("dropped", label, [item.get("reason") or ""])
        elif name in VALIDATE_STEPS:
            present: set[str] = set()
            for item in s.get("items") or []:
                for cid in item.get("candidates") or []:
                    present.add(cid)
                    fates[cid] = (
                        ("dropped", label, item["reasons"]) if item.get("reasons") else ("passed", label, [])
                    )
            for cid in previous - present:
                if fates[cid][0] == "passed":
                    fates[cid] = ("dropped", label, ["这一轮的稿子里已经删掉"])
            previous = present
    cells = {}
    for c in candidates.get("candidates") or []:
        cid = c["id"]
        state, step, reasons = (
            ("published", None, []) if cid in out else fates.get(cid, ("unpicked", None, []))
        )
        if state == "passed":  # passed validate, but its digest was not published
            state, step, reasons = "dropped", "未发布", []
        score = scores.get(cid)
        cells[cid] = {
            "state": state,
            "step": step,
            "reasons": reasons,
            "score": score,
            "total": sum(score) if score else None,
        }
    return cells


def _rows(candidates: dict[str, Any], channels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for c in candidates.get("candidates") or []:
        cells = {ch["id"]: ch["cells"][c["id"]] for ch in channels}
        states = {cell["state"] for cell in cells.values()}
        rows.append(
            {
                "id": c["id"],
                "title": c["title"],
                "url": c["url"],
                "source": c.get("source_name") or c["source"],
                "kind": c["kind"],
                "cells": cells,
                "differs": len(states) > 1,
                "dropped": "dropped" in states,
                "high_unpicked": any(
                    (cell["total"] or 0) >= HIGH_SCORE and cell["state"] != "published"
                    for cell in cells.values()
                ),
            }
        )
    return rows


def _filtered(candidates: dict[str, Any], source_names: dict[str, str]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for f in candidates.get("filtered") or []:
        groups.setdefault(f["source"], []).append(
            {
                "title": f["title"],
                "url": f["url"],
                "reason": FILTER_REASONS.get(f["reason"], f["reason"]),
                "value": f.get("value"),
            }
        )
    return [
        {"source": sid, "name": source_names.get(sid, sid), "items": items} for sid, items in groups.items()
    ]
