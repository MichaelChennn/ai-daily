"""Command line entry point: python -m daily <command>."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

from daily import api_editor, dedup, digest, export, fallback, pipeline, publish, render, site, trace
from daily.config import DEFAULT_DATA_DIR, DEFAULT_SOURCES_FILE, load_sources
from daily.window import issue_window, local_today


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m daily", description="AI 科技日报流水线")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="抓取信源，去重后写入 data/YYYY-MM-DD/candidates.json")
    fetch.add_argument("--date", type=date.fromisoformat, help="期号日期（柏林时间），默认今天")
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
    check.add_argument("--en", action="store_true", help="校验英文版 digest.en.json")

    degrade = commands.add_parser("degrade", help="digest.json 缺失或不合格时，写入“标题 + 链接”降级版")
    _issue_args(degrade)
    degrade.add_argument("--force", action="store_true", help="无论现有 digest.json 是否合格都覆盖")

    md = commands.add_parser("render", help="digest.json → digest.md")
    _issue_args(md)

    adopt = commands.add_parser("adopt", help="按规则并入编辑分支推来的 digest.json（ingest 用）")
    _issue_args(adopt)
    adopt.add_argument("--from", dest="source", type=Path, required=True, help="推来的 digest.json")
    adopt.add_argument("--en", action="store_true", help="推来的是英文版，并入 digest.en.json")
    adopt.add_argument("--trace", type=Path, help="推来的那次运行的 trace；采用时替换本期这个通道的 trace")

    api = commands.add_parser("edit", help="API 通道：用云端模型编辑，写入 digest.api.<slug>.json")
    _issue_args(api)
    api.add_argument(
        "--model",
        default=os.environ.get("EDITOR_API_MODEL"),
        help="厂商:模型，如 nvidia:deepseek-ai/deepseek-v4.1-flash（默认取 EDITOR_API_MODEL）",
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

    record = commands.add_parser("trace", help="Claude 通道：把打分或自检删掉的条目记进 trace.claude.json")
    record.add_argument("what", choices=["scores", "self-check"], help="scores 开始一次新的记录")
    _issue_args(record)

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


def _issue_dir(args: argparse.Namespace) -> Path:
    return args.data_dir / (args.date or local_today()).isoformat()


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

    window = issue_window(args.date or local_today())
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
        f"{stats['filtered']} filtered by the fetchers; raw {stats['raw']} "
        f"-> url-merged {stats['after_url_merge']} -> candidates {stats['candidates']} "
        f"({stats['dropped_already_published']} already published, {stats['seen_before']} seen before, "
        f"{stats['clusters']} clusters)",
        file=sys.stderr,
    )
    print(path)


def _list(args: argparse.Namespace) -> int:
    data = _read(_issue_dir(args) / "candidates.json")
    print(pipeline.candidate_listing(data, args.kind, args.summary_chars))
    return 0


def _validate(args: argparse.Namespace) -> int:
    issue_dir = _issue_dir(args)
    candidates = _read(issue_dir / "candidates.json")
    path = issue_dir / ("digest.en.json" if args.en else "digest.json")
    data = _read(path)
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
    if not args.en and _needs_self_check(issue_dir, data):
        report.warnings.append(
            "no self_check in trace.claude.json: run `daily trace self-check` (SKILL.md 5)"
        )
    step = "en" if args.en else "final" if args.drop_invalid else "precheck" if args.check_links else "check"
    _trace_claude(issue_dir, data, trace.validate_step(step, data, report, checked_links))

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
        _write(path, digest.apply_report(data, report, args.check_links))
        kept = len(data["items"]) - len(report.item_errors)
        print(f"ok: {kept} items kept, {len(report.item_errors)} dropped", file=sys.stderr)
        return 0
    print("ok" if report.ok else f"{len(report.item_errors)} invalid items", file=sys.stderr)
    return 0 if report.ok else 1


def _needs_self_check(issue_dir: Path, data: Any) -> bool:
    """A Claude route edit whose trace has no self-check, not even an empty one."""
    if not isinstance(data, dict) or digest.is_api(data) or data.get("mode") != "full":
        return False
    record = trace.load(issue_dir / "trace.claude.json")
    return not any(s.get("step") == "self_check" for s in (record or {}).get("steps") or [])


def _trace_claude(issue_dir: Path, data: Any, step: dict[str, Any]) -> None:
    """Add a validate round of the Claude route's edit to its trace; other digests have none."""
    if not isinstance(data, dict) or digest.is_api(data) or data.get("mode") != "full":
        return
    path = issue_dir / "trace.claude.json"
    record = trace.load(path) or trace.new(issue_dir.name, "claude")
    record["model"] = data.get("model") or record.get("model")
    record["steps"].append(step)
    trace.save(path, record)


def _trace(args: argparse.Namespace) -> int:
    """What the Claude editor records itself: its scores (which start the trace of a new run) and
    the items its self-check dropped. The JSON comes on stdin."""
    issue_dir = _issue_dir(args)
    candidates = _read(issue_dir / "candidates.json")
    path = issue_dir / "trace.claude.json"
    try:
        value = json.loads(sys.stdin.read())
    except json.JSONDecodeError as exc:
        print(f"ERROR stdin is not JSON: {exc}", file=sys.stderr)
        return 1
    known = {c["id"] for c in candidates["candidates"]}
    if args.what == "scores":
        record = trace.new(candidates["date"], "claude")
        record["scores"] = trace.scores(value, known)
        missing = len(known - record["scores"].keys())
        trace.save(path, record)
        print(f"{len(record['scores'])} candidates scored, {missing} without a score", file=sys.stderr)
        return 0
    if not isinstance(value, list) or not all(isinstance(v, dict) for v in value):
        print('ERROR self-check takes [{"candidates": [...], "title": ..., "reason": ...}]', file=sys.stderr)
        return 1
    record = trace.load(path) or trace.new(candidates["date"], "claude")
    items = [
        {
            "title": v.get("title"),
            "candidates": [c for c in v.get("candidates") or [] if c in known],
            "reason": v.get("reason"),
        }
        for v in value
    ]
    record["steps"].append({"step": "self_check", "at": trace.now(), "items": items})
    trace.save(path, record)
    print(f"{len(items)} items dropped in the self-check recorded", file=sys.stderr)
    return 0


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
    trace_path = issue_dir / "trace.claude.json"
    if args.force and (record := trace.load(trace_path)):  # the Claude editor gave up (SKILL.md step 6)
        last = record["steps"][-1] if record["steps"] else {}
        error = "; ".join(last.get("errors") or []) or "the editor published the fallback"
        record["failure"] = {"step": last.get("step"), "error": error}
        trace.save(trace_path, record)
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


def _adopt(args: argparse.Namespace) -> int:
    issue_dir = _issue_dir(args)
    candidates = _read(issue_dir / "candidates.json")
    path = issue_dir / ("digest.en.json" if args.en else "digest.json")
    try:
        incoming = _read(args.source)
    except json.JSONDecodeError as exc:
        incoming = f"invalid JSON: {exc}"
    try:
        current = _read(path) if path.exists() else None
    except json.JSONDecodeError:
        current = None
    if args.en:
        main_path = issue_dir / "digest.json"
        main = _read(main_path) if main_path.exists() else None
        data, reason = publish.decide_en(main, current, incoming, candidates)
    else:
        data, reason = publish.decide(current, incoming, candidates)
    print(f"{issue_dir.name}: {'adopted' if data else 'kept'} ({reason})", file=sys.stderr)
    _trace_adopt(issue_dir, incoming, args.trace, data is not None, reason, "en" if args.en else "zh")
    if data is not None:
        _write(path, data)
        if not args.en:
            (issue_dir / "digest.md").write_text(render.to_markdown(data, candidates), encoding="utf-8")
        print(path)
    return 0


def _trace_adopt(
    issue_dir: Path, incoming: Any, source: Path | None, adopted: bool, reason: str, edition: str
) -> None:
    """The trace follows the digest: the trace of an adopted run (source) replaces the route's, and
    a rejected run is noted in the trace already there. Either way the verdict is appended."""
    if not isinstance(incoming, dict) or reason == "unchanged":
        return
    path = issue_dir / trace.file_name(incoming)
    record = trace.load(path)
    run = trace.load(source) if source is not None else None
    if run is not None and edition == "zh" and (adopted or record is None):
        record = run
    if record is None:
        return
    record.setdefault("adopt", []).append(trace.adopt_record(edition, incoming, adopted, reason))
    trace.save(path, record)


def _edit(args: argparse.Namespace) -> int:
    issue_dir = _issue_dir(args)
    candidates = _read(issue_dir / "candidates.json")
    if args.en:
        return _edit_en(args, issue_dir, candidates)
    trace_path = issue_dir / f"trace.api.{digest.slug(args.model or '')}.json"
    try:
        api_editor.resolve(args.model or "")
    except api_editor.EditorError as exc:
        print(exc, file=sys.stderr)
        if args.model:
            failed = trace.new(candidates["date"], "api", args.model)
            trace.save(trace_path, {**failed, "failure": {"step": "setup", "error": str(exc)}})
        return 2

    async def run(editor: api_editor.Editor) -> dict[str, Any]:
        async with editor.client:
            return await editor.run()

    editor = api_editor.Editor(candidates, args.model, pipeline.make_client())
    try:
        data = asyncio.run(run(editor))
    except api_editor.EditorError as exc:
        print(f"{args.model}: {exc}", file=sys.stderr)
        return 1
    finally:
        trace.save(trace_path, editor.trace)  # also when it failed: the trace says where
    path = issue_dir / f"digest.api.{digest.slug(args.model)}.json"
    _write(path, data)
    print(f"{args.model}: {len(data['items'])} items", file=sys.stderr)
    print(path)
    return 0


def _edit_en(args: argparse.Namespace, issue_dir: Path, candidates: dict[str, Any]) -> int:
    """The English edition goes with the main issue, so it is only written for the API digest that
    adopt would make the main issue now; a Claude edit ingested later replaces both."""
    main = _read(args.en)
    current_path = issue_dir / "digest.json"
    current = _read(current_path) if current_path.exists() else None
    adopted, reason = publish.decide(current, main, candidates)
    if adopted is None:
        print(f"{args.en.name} would not be the main issue ({reason}): no English edition", file=sys.stderr)
        return 0
    model = main.get("model") or ""
    try:
        api_editor.resolve(model)
    except api_editor.EditorError as exc:
        print(exc, file=sys.stderr)
        return 2

    trace_path = issue_dir / trace.file_name(main)
    record = trace.load(trace_path) or trace.new(candidates["date"], "api", model)

    async def run() -> dict[str, Any]:
        async with pipeline.make_client() as client:
            return await api_editor.write_en(adopted, candidates, model, client, record["steps"])

    try:
        data = asyncio.run(run())
    except api_editor.EditorError as exc:
        print(f"{model}: no English edition: {exc}", file=sys.stderr)
        return 1
    finally:
        trace.save(trace_path, record)
    path = issue_dir / f"digest.en.{digest.slug(model)}.json"
    _write(path, data)
    print(f"{model}: {len(data['items'])} items in English", file=sys.stderr)
    print(path)
    return 0


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
