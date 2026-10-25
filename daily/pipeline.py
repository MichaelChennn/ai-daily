"""`daily fetch`: run every enabled source, dedupe, and write data/YYYY-MM-DD/candidates.json."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from daily import __version__, dedup
from daily.config import SourceConfig
from daily.fetchers import FETCHERS
from daily.models import Candidate
from daily.throttle import PoliteTransport
from daily.window import Window

logger = logging.getLogger(__name__)

USER_AGENT = f"ai-daily/{__version__} (+https://github.com/MichaelChennn/ai-daily)"
SOURCE_TIMEOUT_SECONDS = 60


@dataclass
class SourceReport:
    id: str
    status: str  # ok | error | disabled
    count: int = 0
    seconds: float = 0.0
    error: str | None = None


def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(20.0),
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
        transport=PoliteTransport(httpx.AsyncHTTPTransport(retries=2)),
    )


async def run_source(
    client: httpx.AsyncClient, source: SourceConfig, window: Window
) -> tuple[list[Candidate], SourceReport]:
    """Run one fetcher in isolation: any failure becomes a report entry, never an exception."""
    started = time.monotonic()
    try:
        fetcher = FETCHERS[source.type]
        items = await asyncio.wait_for(fetcher(client, source, window), SOURCE_TIMEOUT_SECONDS)
    except Exception as exc:  # noqa: BLE001 - isolation is the point
        detail = str(exc).splitlines()[0] if str(exc) else ""
        message = f"{type(exc).__name__}: {detail}" if detail else type(exc).__name__
        logger.warning("source %s failed: %s", source.id, message)
        return [], SourceReport(source.id, "error", seconds=time.monotonic() - started, error=message[:500])
    logger.info("source %s: %d items", source.id, len(items))
    return items, SourceReport(source.id, "ok", count=len(items), seconds=time.monotonic() - started)


async def fetch_all(
    sources: list[SourceConfig], window: Window, client: httpx.AsyncClient | None = None
) -> tuple[list[Candidate], list[SourceReport]]:
    enabled = [s for s in sources if s.enabled]
    reports = [SourceReport(s.id, "disabled") for s in sources if not s.enabled]
    owns_client = client is None
    client = client or make_client()
    try:
        results = await asyncio.gather(*(run_source(client, s, window) for s in enabled))
    finally:
        if owns_client:
            await client.aclose()
    items = [item for source_items, _ in results for item in source_items]
    return items, [report for _, report in results] + reports


def build_candidates(
    raw: list[Candidate],
    sources: list[SourceConfig],
    window: Window,
    reports: list[SourceReport],
    history: dedup.History,
    now: datetime | None = None,
) -> dict[str, Any]:
    source_order = {s.id: i for i, s in enumerate(sources)}
    merged = dedup.merge_by_url(raw, source_order)
    kept, dropped = dedup.apply_history(merged, history)
    kept.sort(
        key=lambda c: (
            c.tier,
            source_order.get(c.source, 999),
            -(c.published_at.timestamp() if c.published_at else 0),
        )
    )
    clusters = dedup.assign_clusters(kept)

    return {
        "schema_version": 1,
        "date": window.issue_date.isoformat(),
        "generated_at": (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat(),
        "window": {"start": window.start.isoformat(), "end": window.end.isoformat()},
        "stats": {
            "raw": len(raw),
            "after_url_merge": len(merged),
            "dropped_already_published": len(dropped),
            "candidates": len(kept),
            "clusters": len(clusters),
            "seen_before": sum(1 for c in kept if c.seen_on),
        },
        "sources": [report.__dict__ for report in sorted(reports, key=lambda r: source_order.get(r.id, 999))],
        "clusters": clusters,
        "dropped": dropped,
        "candidates": [c.to_json() for c in kept],
    }


def candidate_listing(data: dict[str, Any], kinds: list[str] | None = None, summary_chars: int = 160) -> str:
    """`daily list`: one line per candidate for the editor to browse, its summary below."""
    clusters = {c["id"]: len(c["candidate_ids"]) for c in data["clusters"]}
    failed = [r["id"] for r in data["sources"] if r["status"] == "error"]
    count = len(data["candidates"])
    lines = [f"issue {data['date']}: {count} candidates; failed sources: {failed or 'none'}"]
    for c in data["candidates"]:
        if kinds and c["kind"] not in kinds:
            continue
        notes = [f"{k}={v}" for k, v in c["signals"].items() if k not in ("subreddit", "organization")]
        notes += [f"+{a['source']}" for a in c["also_from"]]
        if c["cluster_id"] in clusters:
            notes.append(f"cluster {c['cluster_id']}({clusters[c['cluster_id']]})")
        if c["seen_on"]:
            notes.append(f"seen {','.join(c['seen_on'])}")
        head = f"{c['id']} {c['kind']:<10} T{c['tier']} [{c['source']}] {c['title']}"
        lines.append(f"{head}  | {' '.join(notes)}")
        if summary_chars and c["summary"]:
            summary = " ".join(c["summary"].split())
            lines.append(f"    {summary[:summary_chars]}{'…' if len(summary) > summary_chars else ''}")
    return "\n".join(lines)


def write_candidates(data: dict[str, Any], data_dir: Path) -> Path:
    out_dir = data_dir / data["date"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "candidates.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
