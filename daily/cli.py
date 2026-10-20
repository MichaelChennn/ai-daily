"""Command line entry point: python -m daily <command>."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

from daily import dedup, pipeline
from daily.config import DEFAULT_DATA_DIR, DEFAULT_SOURCES_FILE, load_sources
from daily.window import beijing_today, issue_window


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m daily", description="AI 科技日报流水线")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="抓取信源，去重后写入 data/YYYY-MM-DD/candidates.json")
    fetch.add_argument("--date", type=date.fromisoformat, help="期号日期（北京时间），默认今天")
    fetch.add_argument("--sources", type=Path, default=DEFAULT_SOURCES_FILE, help="信源配置文件")
    fetch.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="数据目录")
    fetch.add_argument("--only", action="append", metavar="SOURCE_ID", help="只跑指定信源（可重复）")
    fetch.add_argument("--history-days", type=int, default=7, help="跨天去重回看天数")

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger("httpx").setLevel(logging.INFO if args.verbose else logging.WARNING)

    if args.command == "fetch":
        return _fetch(args)
    return 2


def _fetch(args: argparse.Namespace) -> int:
    sources = load_sources(args.sources)
    if args.only:
        unknown = set(args.only) - {s.id for s in sources}
        if unknown:
            print(f"unknown source id(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        for source in sources:
            source.enabled = source.id in args.only

    window = issue_window(args.date or beijing_today())
    raw, reports = asyncio.run(pipeline.fetch_all(sources, window))
    history = dedup.load_history(args.data_dir, window.issue_date, args.history_days)
    data = pipeline.build_candidates(raw, sources, window, reports, history)
    path = pipeline.write_candidates(data, args.data_dir)

    _print_report(data, path)
    # Single-source failures are recorded in candidates.json and do not fail the run.
    if not data["candidates"]:
        print("no candidates at all - treat as a failed run", file=sys.stderr)
        return 1
    return 0


def _print_report(data: dict, path: Path) -> None:
    window = data["window"]
    print(f"issue {data['date']}  window {window['start']} .. {window['end']}", file=sys.stderr)
    for report in data["sources"]:
        if report["status"] == "disabled":
            continue
        detail = f"{report['count']:>4} items" if report["status"] == "ok" else f"ERROR {report['error']}"
        print(f"  {report['id']:<24} {detail}  ({report['seconds']:.1f}s)", file=sys.stderr)
    stats = data["stats"]
    print(
        f"raw {stats['raw']} -> url-merged {stats['after_url_merge']} -> candidates {stats['candidates']} "
        f"({stats['dropped_already_published']} already published, {stats['seen_before']} seen before, "
        f"{stats['clusters']} clusters)",
        file=sys.stderr,
    )
    print(path)
