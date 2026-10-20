"""Command line entry point: python -m daily <command>."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

from daily import dedup, digest, fallback, pipeline, render
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

    listing = commands.add_parser("list", help="精简列出候选，给编辑浏览用")
    _issue_args(listing)
    listing.add_argument("--kind", action="append", help="只看某类候选（可重复）")
    listing.add_argument("--summary-chars", type=int, default=160, help="摘要截断长度，0 不显示")

    check = commands.add_parser("validate", help="校验 digest.json（程序闸门）")
    _issue_args(check)
    check.add_argument("--drop-invalid", action="store_true", help="删掉不合格条目并写回 digest.json")
    check.add_argument("--check-links", action="store_true", help="联网检查链接和 evidence 引文")

    degrade = commands.add_parser("degrade", help="digest.json 缺失或不合格时，写入“标题 + 链接”降级版")
    _issue_args(degrade)
    degrade.add_argument("--force", action="store_true", help="无论现有 digest.json 是否合格都覆盖")

    md = commands.add_parser("render", help="digest.json → digest.md")
    _issue_args(md)

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger("httpx").setLevel(logging.INFO if args.verbose else logging.WARNING)

    if args.command == "fetch":
        return _fetch(args)
    try:
        return {"list": _list, "validate": _validate, "degrade": _degrade, "render": _render}[args.command](
            args
        )
    except FileNotFoundError as exc:
        print(f"missing {exc.filename}", file=sys.stderr)
        return 1


def _issue_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--date", type=date.fromisoformat, help="期号日期（北京时间），默认今天")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="数据目录")


def _issue_dir(args: argparse.Namespace) -> Path:
    return args.data_dir / (args.date or beijing_today()).isoformat()


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def _list(args: argparse.Namespace) -> int:
    data = _read(_issue_dir(args) / "candidates.json")
    clusters = {c["id"]: len(c["candidate_ids"]) for c in data["clusters"]}
    failed = [r["id"] for r in data["sources"] if r["status"] == "error"]
    print(f"issue {data['date']}: {len(data['candidates'])} candidates; failed sources: {failed or 'none'}")
    for c in data["candidates"]:
        if args.kind and c["kind"] not in args.kind:
            continue
        notes = [f"{k}={v}" for k, v in c["signals"].items() if k not in ("subreddit", "organization")]
        notes += [f"+{a['source']}" for a in c["also_from"]]
        if c["cluster_id"] in clusters:
            notes.append(f"cluster {c['cluster_id']}({clusters[c['cluster_id']]})")
        if c["seen_on"]:
            notes.append(f"seen {','.join(c['seen_on'])}")
        print(f"{c['id']} {c['kind']:<10} T{c['tier']} [{c['source']}] {c['title']}  | {' '.join(notes)}")
        if args.summary_chars and c["summary"]:
            summary = " ".join(c["summary"].split())
            print(f"    {summary[: args.summary_chars]}{'…' if len(summary) > args.summary_chars else ''}")
    return 0


def _validate(args: argparse.Namespace) -> int:
    issue_dir = _issue_dir(args)
    candidates = _read(issue_dir / "candidates.json")
    data = _read(issue_dir / "digest.json")
    report = digest.validate(data, candidates)  # also fills in candidate urls the editor left out
    if args.check_links and not report.errors:
        client = pipeline.make_client()

        async def check() -> dict[str, digest.Page]:
            async with client:
                return await digest.check_links(digest.digest_urls(data), client)

        report = digest.validate(data, candidates, asyncio.run(check()))

    for error in report.errors:
        print(f"ERROR {error}", file=sys.stderr)
    for index, errors in sorted(report.item_errors.items()):
        title = data["items"][index].get("title") if isinstance(data["items"][index], dict) else None
        print(f"DROP  item {index + 1} {title!r}: {'; '.join(errors)}", file=sys.stderr)
    for warning in report.warnings:
        print(f"WARN  {warning}", file=sys.stderr)
    if report.errors:
        return 1
    if args.drop_invalid:
        _write(issue_dir / "digest.json", digest.apply_report(data, report, args.check_links))
        kept = len(data["items"]) - len(report.item_errors)
        print(f"ok: {kept} items kept, {len(report.item_errors)} dropped", file=sys.stderr)
        return 0
    print("ok" if report.ok else f"{len(report.item_errors)} invalid items", file=sys.stderr)
    return 0 if report.ok else 1


def _degrade(args: argparse.Namespace) -> int:
    issue_dir = _issue_dir(args)
    candidates = _read(issue_dir / "candidates.json")
    path = issue_dir / "digest.json"
    if path.exists() and not args.force:
        try:
            report = digest.validate(_read(path), candidates)
        except json.JSONDecodeError as exc:
            report = digest.Report(errors=[f"invalid JSON: {exc}"])
        if report.ok:
            print(f"{path} is valid, nothing to do", file=sys.stderr)
            return 0
        print(
            f"{path} is not valid ({(report.errors or ['invalid items'])[0]}), replacing it", file=sys.stderr
        )
    if path.exists():
        shutil.copy(path, issue_dir / "digest.rejected.json")
    data = fallback.build_fallback(candidates)
    if not data["items"]:
        print("no candidates to publish", file=sys.stderr)
        return 1
    _write(path, digest.apply_report(data, digest.validate(data, candidates), checked_links=False))
    print(path)
    return 0


def _render(args: argparse.Namespace) -> int:
    issue_dir = _issue_dir(args)
    candidates_file = issue_dir / "candidates.json"
    candidates = _read(candidates_file) if candidates_file.exists() else None
    path = issue_dir / "digest.md"
    path.write_text(render.to_markdown(_read(issue_dir / "digest.json"), candidates), encoding="utf-8")
    print(path)
    return 0
