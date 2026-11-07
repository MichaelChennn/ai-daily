"""`daily edit`: one run of the API route on an issue.

Each model edits in turn (daily.api_editor) and leaves its digest as a beta, digest.api.<slug>.json,
with its trace. The one whose digest adopt would make the main issue (publish.main_of) also writes
the English edition, digest.en.<slug>.json. With an out folder, the run is left there for
`daily ingest --from-dir` (ingest.save_run), which adopts it in the publish job.

The functions return the exit status of the command: 0 ok, 1 an edit failed, 2 a model that cannot
run (unknown provider, no key). Every model runs whatever the others did.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from daily import api_editor, ingest, issue, pipeline, publish, trace
from daily.issue import IssueDir
from daily.llm import LLMError, resolve


def run(folder: IssueDir, models: list[str], out: Path | None = None) -> int:
    """Edits with each model in order; the one whose digest adopt would make the main issue also
    writes the English edition."""
    if not folder.candidates.exists():  # fallback.yml alerts
        print(f"::warning::{folder.candidates} is missing: nothing to edit", file=sys.stderr)
        return 0
    candidates = folder.read_candidates()
    status, written = 0, []
    for model in models:
        code, path = _edit_one(folder, candidates, model)
        status = max(status, code)
        if path is not None:
            written.append(path)
    en = None
    found = publish.main_of(folder.read_digest(), [issue.read(p) for p in written], candidates)
    if found is None:
        print("no digest of this run would be the main issue: no English edition", file=sys.stderr)
    else:
        # A failed English edition does not fail the run: the English page shows the original titles.
        en = _write_en(folder, candidates, found[1])
    if out is not None:
        traces = [folder.route_trace(api_editor.CHANNEL, model) for model in models]
        ingest.save_run(out, folder.date, written, en, [t for t in traces if t.exists()])
    return status


def _edit_one(folder: IssueDir, candidates: dict[str, Any], model: str) -> tuple[int, Path | None]:
    trace_path = folder.route_trace(api_editor.CHANNEL, model)
    try:
        resolve(model)
    except LLMError as exc:
        print(exc, file=sys.stderr)
        failed = trace.new(candidates["date"], api_editor.CHANNEL, model)
        trace.save(trace_path, {**failed, "failure": {"step": "setup", "error": str(exc)}})
        return 2, None

    async def edit(editor: api_editor.Editor) -> dict[str, Any]:
        async with editor.client:
            return await editor.run()

    editor = api_editor.Editor(candidates, model, pipeline.make_client())
    try:
        data = asyncio.run(edit(editor))
    except LLMError as exc:
        print(f"::error::{model} did not produce a valid digest: {exc}", file=sys.stderr)
        return 1, None
    finally:
        trace.save(trace_path, editor.trace)  # also when it failed: the trace says where
    path = folder.beta(api_editor.CHANNEL, model)
    issue.write(path, data)
    print(f"{model}: {len(data['items'])} items", file=sys.stderr)
    print(path)
    return 0, path


def write_en_for(folder: IssueDir, source: Path) -> int:
    """`edit --en`: the English edition for one API digest, if adopt would make it the main issue now."""
    candidates = folder.read_candidates()
    adopted, reason = publish.decide(folder.read_digest(), issue.read(source), candidates)
    if adopted is None:
        print(f"{source.name} would not be the main issue ({reason}): no English edition", file=sys.stderr)
        return 0
    try:
        resolve(adopted.get("model") or "")
    except LLMError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0 if _write_en(folder, candidates, adopted) is not None else 1


def _write_en(folder: IssueDir, candidates: dict[str, Any], main: dict[str, Any]) -> Path | None:
    """Writes the English edition of main, the API digest that would be the main issue."""
    model = main.get("model") or ""
    trace_path = folder.trace(main)
    assert trace_path is not None  # the API route keeps a trace
    record = trace.load(trace_path) or trace.new(candidates["date"], api_editor.CHANNEL, model)

    async def write() -> dict[str, Any]:
        async with pipeline.make_client() as client:
            return await api_editor.write_en(main, candidates, model, client, record["steps"])

    try:
        data = asyncio.run(write())
    except LLMError as exc:
        print(f"::warning::{model}: no English edition: {exc}", file=sys.stderr)
        return None
    finally:
        trace.save(trace_path, record)
    path = folder.beta_en(model)
    issue.write(path, data)
    print(f"{model}: {len(data['items'])} items in English", file=sys.stderr)
    print(path)
    return path
