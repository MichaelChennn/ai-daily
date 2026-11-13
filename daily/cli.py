"""Command line entry point: python -m daily <command>."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import date
from pathlib import Path

from daily import (
    dedup,
    digest,
    edit,
    export,
    fallback,
    ingest,
    issue,
    pipeline,
    render,
    routes,
    site,
    trace,
)
from daily.config import DEFAULT_DATA_DIR, DEFAULT_SOURCES_FILE, load_sources
from daily.issue import IssueDir
from daily.window import issue_window, local_today


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m daily", description="AI 晨报流水线")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="抓取信源，去重后写入 data/YYYY-MM-DD/candidates.json")
    fetch.add_argument("--date", type=date.fromisoformat, help="期号日期（柏林时间），默认今天")
    fetch.add_argument("--sources", type=Path, default=DEFAULT_SOURCES_FILE, help="信源配置文件")
    fetch.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="数据目录")
    fetch.add_argument("--only", action="append", metavar="SOURCE_ID", help="只跑指定信源（可重复）")
    fetch.add_argument("--history-days", type=int, default=7, help="跨天去重回看天数")
    fetch.add_argument(
        "--reported-days", type=int, default=dedup.REPORTED_DAYS, help="reported_on 回看的主版天数"
    )

    listing = commands.add_parser("list", help="精简列出候选，给编辑浏览用")
    _issue_args(listing)
    listing.add_argument("--kind", action="append", help="只看某类候选（可重复）")
    listing.add_argument("--summary-chars", type=int, default=160, help="摘要截断长度，0 不显示")

    check = commands.add_parser("validate", help="校验 digest.json（程序闸门）")
    _issue_args(check)
    check.add_argument("--drop-invalid", action="store_true", help="删掉不合格条目并写回 digest.json")
    check.add_argument("--check-links", action="store_true", help="联网检查链接和 evidence 引文")
    check.add_argument("--en", action="store_true", help="校验英文版 digest.en.json")

    degrade = commands.add_parser("degrade", help="digest.json 缺失或不合格时，写入“标题 + 链接”降级版")
    _issue_args(degrade)
    degrade.add_argument("--force", action="store_true", help="无论现有 digest.json 是否合格都覆盖")
    _channel_arg(degrade, "--force 时把放弃记进哪条路线的 trace")

    md = commands.add_parser("render", help="digest.json → digest.md")
    _issue_args(md)

    adopt = commands.add_parser("adopt", help="按规则并入编辑分支推来的 digest.json（ingest 用）")
    _issue_args(adopt)
    adopt.add_argument("--from", dest="source", type=Path, required=True, help="推来的 digest.json")
    adopt.add_argument("--en", action="store_true", help="推来的是英文版，并入 digest.en.json")
    adopt.add_argument("--trace", type=Path, help="推来的那次运行的 trace；采用时替换本期这个通道的 trace")

    pull = commands.add_parser(
        "ingest", help="并入一次运行的全部 digest：编辑分支的提交，或 edit --out 的目录"
    )
    pull.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="数据目录")
    source = pull.add_mutually_exclusive_group(required=True)
    source.add_argument("--ref", help="编辑分支推来的提交（sha 或 FETCH_HEAD）")
    source.add_argument("--from-dir", type=Path, help="edit --out 留下的目录")
    pull.add_argument("--base", default="origin/main", help="--ref 从哪里分出来（默认 origin/main）")

    api = commands.add_parser("edit", help="API 通道：用云端模型编辑，写入 digest.api.<slug>.json")
    _issue_args(api)
    api.add_argument(
        "--model",
        default=os.environ.get("EDITOR_API_MODEL"),
        help="厂商:模型，逗号分隔、按主版优先级排列，如 nvidia:minimaxai/minimax-m3.1-flash"
        "（默认取 EDITOR_API_MODEL）；会成为主版的那份另写英文版",
    )
    api.add_argument(
        "--out", type=Path, help="把这次运行的 digest、英文版和 trace 留在这个目录，给 ingest --from-dir"
    )
    api.add_argument(
        "--en",
        type=Path,
        metavar="API_DIGEST",
        help="为这份 API digest 写英文版 digest.en.<slug>.json（模型取它的 model）；它不会成为主版时跳过",
    )

    data = commands.add_parser("export", help="已发布各期 → JSON 和 RSS，给网页前端（web/）用")
    data.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="数据目录")
    data.add_argument("--sources", type=Path, default=DEFAULT_SOURCES_FILE, help="信源配置文件")
    data.add_argument("--out", type=Path, default=Path("web/data"), help="输出目录")
    data.add_argument("--public", type=Path, default=Path("web/public"), help="feed.xml 和 .nojekyll 的目录")
    data.add_argument(
        "--base-url",
        default=os.environ.get("SITE_URL") or site.DEFAULT_BASE_URL,
        help="网站地址，用于 RSS 里的绝对链接（默认取 SITE_URL）",
    )

    record = commands.add_parser("trace", help="按 SKILL.md 编辑的路线：把打分或自检删掉的条目记进它的 trace")
    record.add_argument("what", choices=["scores", "self-check"], help="scores 开始一次新的记录")
    _issue_args(record)
    _channel_arg(record, "记进哪条路线的 trace")

    page = commands.add_parser("page", help="打印页面里关键词附近的原文，供编辑逐字摘录 evidence")
    page.add_argument("url")
    page.add_argument("--grep", action="append", required=True, metavar="TEXT", help="关键词（可重复）")
    page.add_argument("--context", type=int, default=200, help="关键词前后各显示多少字符")

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
        handlers = {
            "list": _list,
            "validate": _validate,
            "degrade": _degrade,
            "render": _render,
            "adopt": _adopt,
            "ingest": _ingest,
            "edit": _edit,
            "export": _export,
            "page": _page,
            "trace": _trace,
        }
        return handlers[args.command](args)
    except FileNotFoundError as exc:
        print(f"missing {exc.filename}", file=sys.stderr)
        return 1


def _issue_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--date", type=date.fromisoformat, help="期号日期（柏林时间），默认今天")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR, help="数据目录")


def _channel_arg(parser: argparse.ArgumentParser, help_: str) -> None:
    parser.add_argument(
        "--channel", choices=routes.SKILL_ROUTES, default="claude", help=f"{help_}（默认 claude）"
    )


def _issue(args: argparse.Namespace) -> IssueDir:
    return IssueDir.of(args.data_dir, args.date or local_today())


def _fetch(args: argparse.Namespace) -> int:
    sources = load_sources(args.sources)
    if args.only:
        unknown = set(args.only) - {s.id for s in sources}
        if unknown:
            print(f"unknown source id(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        for source in sources:
            source.enabled = source.id in args.only

    window = issue_window(args.date or local_today())
    raw, reports = asyncio.run(pipeline.fetch_all(sources, window))
    history = dedup.load_history(args.data_dir, window.issue_date, args.history_days, args.reported_days)
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
        f"{stats['filtered']} filtered by the fetchers; raw {stats['raw']} "
        f"-> url-merged {stats['after_url_merge']} -> candidates {stats['candidates']} "
        f"({stats['dropped_already_published']} already published, {stats['seen_before']} seen before, "
        f"{stats['reported_before']} reported before, "
        f"{stats['clusters']} clusters)",
        file=sys.stderr,
    )
    print(path)


def _list(args: argparse.Namespace) -> int:
    data = _issue(args).read_candidates()
    print(pipeline.candidate_listing(data, args.kind, args.summary_chars))
    return 0


def _validate(args: argparse.Namespace) -> int:
    folder = _issue(args)
    candidates = folder.read_candidates()
    path = folder.edition(args.en)
    data = issue.read(path)
    if args.en and data.get("lang") != "en":
        print('ERROR digest.en.json needs "lang": "en"', file=sys.stderr)
        return 1
    report = digest.validate(data, candidates)  # also fills in candidate urls the editor left out
    checked_links = args.check_links and not report.errors
    if checked_links:
        client = pipeline.make_client()

        async def check() -> dict[str, digest.Page]:
            async with client:
                return await digest.check_links(digest.digest_urls(data), client)

        report = digest.validate(data, candidates, asyncio.run(check()))
    if not args.en and trace.needs_self_check(folder, data):
        report.warnings.append(
            f"no self_check in {routes.trace_name(data)}: run `daily trace self-check` (SKILL.md 5)"
        )
    step = "en" if args.en else "final" if args.drop_invalid else "precheck" if args.check_links else "check"
    trace.record_validate(folder, data, trace.validate_step(step, data, report, checked_links))

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
        issue.write(path, digest.apply_report(data, report, args.check_links))
        kept = len(data["items"]) - len(report.item_errors)
        print(f"ok: {kept} items kept, {len(report.item_errors)} dropped", file=sys.stderr)
        return 0
    print("ok" if report.ok else f"{len(report.item_errors)} invalid items", file=sys.stderr)
    return 0 if report.ok else 1


def _trace(args: argparse.Namespace) -> int:
    """What an editor working by SKILL.md records itself: its scores (which start the trace of a new
    run) and the items its self-check dropped. The JSON comes on stdin."""
    folder = _issue(args)
    candidates = folder.read_candidates()
    try:
        value = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        print(f"ERROR stdin is not JSON: {exc}", file=sys.stderr)
        return 1
    if args.what == "scores":
        scored, missing = trace.record_scores(folder, args.channel, candidates, value)
        print(f"{scored} candidates scored, {missing} without a score", file=sys.stderr)
        return 0
    try:
        dropped = trace.record_self_check(folder, args.channel, candidates, value)
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    print(f"{dropped} items dropped in the self-check recorded", file=sys.stderr)
    return 0


def _degrade(args: argparse.Namespace) -> int:
    return 0 if fallback.degrade(_issue(args), args.force, args.channel) else 1


def _render(args: argparse.Namespace) -> int:
    folder = _issue(args)
    candidates = issue.read_if_exists(folder.candidates)
    path = folder.markdown
    path.write_text(render.to_markdown(issue.read(folder.digest), candidates), encoding="utf-8")
    print(path)
    return 0


def _adopt(args: argparse.Namespace) -> int:
    ingest.adopt(_issue(args), args.source, args.trace, args.en)
    return 0


def _ingest(args: argparse.Namespace) -> int:
    if args.ref:
        ingest.from_ref(args.data_dir, args.ref, args.base)
    else:
        ingest.from_dir(args.data_dir, args.from_dir)
    return 0


def _edit(args: argparse.Namespace) -> int:
    folder = _issue(args)
    if args.en:
        return edit.write_en_for(folder, args.en)
    models = [m.strip() for m in (args.model or "").split(",") if m.strip()]
    if not models:
        print("no model: pass --model or set EDITOR_API_MODEL", file=sys.stderr)
        return 2
    return edit.run(folder, models, args.out)


def _export(args: argparse.Namespace) -> int:
    issues = export.export(args.out, args.public, args.data_dir, load_sources(args.sources), args.base_url)
    print(f"{len(issues)} issues -> {args.out / 'issues'}", file=sys.stderr)
    return 0


def _page(args: argparse.Namespace) -> int:
    """Same fetch and text extraction as `validate --check-links`, so what is printed here verifies."""

    async def fetch() -> digest.Page:
        async with pipeline.make_client() as client:
            return (await digest.check_links([args.url], client))[args.url]

    page = asyncio.run(fetch())
    if page.text is None:
        print(f"no page text ({page.error or page.status})", file=sys.stderr)
        return 1
    print(digest.grep_page(page.text, args.grep, args.context))
    return 0
