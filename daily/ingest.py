"""`daily adopt` and `daily ingest`: bring an editor route's digests into the issues on main.

publish decides whether a digest becomes the main issue; this module does the reading and writing
around it: the digest, its trace, digest.md. The routes deliver their runs in two ways:

  a branch (from_ref)  the Claude editor runs in a cloud session that can only push to its own
                       claude/ branch; .github/workflows/ingest.yml passes the commit it pushed.
                       Every data/*/digest.json and digest.en.json the branch changed is adopted,
                       the main issues first (an English edition is adopted only to go with one),
                       with the run's trace. Nothing else on the branch reaches main.
  a run folder (from_dir)
                       the API route (.github/workflows/editor-api.yml) edits in one job and
                       publishes in another; `daily edit --out` leaves its digests, English edition
                       and traces in a folder, with run.json saying in which order to adopt them.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from daily import issue, publish, render, routes, trace
from daily.issue import IssueDir

# In a run folder: {"date", "digests": [file names, in priority order], "en": file name | null}.
RUN = "run.json"


def adopt(folder: IssueDir, source: Path, run_trace: Path | None = None, en: bool = False) -> bool:
    """Adopts the digest at source into the issue if publish says so. True if it was adopted."""
    candidates = folder.read_candidates()
    path = folder.edition(en)
    try:
        incoming = issue.read(source)
    except json.JSONDecodeError as exc:
        incoming = f"invalid JSON: {exc}"
    try:
        current = issue.read_if_exists(path)
    except json.JSONDecodeError:
        current = None
    if en:
        data, reason = publish.decide_en(folder.read_digest(), current, incoming, candidates)
    else:
        data, reason = publish.decide(current, incoming, candidates)
    print(f"{folder.date}: {'adopted' if data else 'kept'} ({reason})", file=sys.stderr)
    _trace_adopt(folder, incoming, run_trace, data is not None, reason, "en" if en else "zh")
    if data is None:
        return False
    issue.write(path, data)
    if not en:
        folder.markdown.write_text(render.to_markdown(data, candidates), encoding="utf-8")
    print(path)
    return True


def _trace_adopt(
    folder: IssueDir, incoming: Any, source: Path | None, adopted: bool, reason: str, edition: str
) -> None:
    """The trace follows the digest: the trace of an adopted run (source) replaces the route's, and
    a rejected run is noted in the trace already there. Either way the verdict is appended."""
    if not isinstance(incoming, dict) or reason == "unchanged":
        return
    run = trace.load(source) if source is not None else None
    # A run's trace names its route: a fallback the Claude editor wrote when it gave up
    # (`degrade --force`) goes with trace.claude.json, though the fallback route keeps none.
    path = folder.trace(run if run is not None else incoming)
    if path is None:
        return
    record = trace.load(path)
    if run is not None and edition == "zh" and (adopted or record is None):
        record = run
    if record is None:
        return
    record.setdefault("adopt", []).append(trace.adopt_record(edition, incoming, adopted, reason))
    trace.save(path, record)


def from_ref(data_dir: Path, ref: str, base: str = "origin/main") -> None:
    """Adopts the digests a branch's commit ref changed since it left base."""
    root = Path(_git(data_dir, "rev-parse", "--show-toplevel").strip())
    data = data_dir.resolve().relative_to(root).as_posix()
    sha = _git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    since = _git(root, "merge-base", base, sha).strip()

    def changed(name: str) -> list[str]:
        paths = _git(root, "diff", "--name-only", "--diff-filter=AM", since, sha, "--", f"{data}/*/{name}")
        return paths.split()

    with tempfile.TemporaryDirectory() as tmp:
        for path in changed(issue.DIGEST) + changed(issue.DIGEST_EN):
            en = path.endswith(".en.json")
            date = path.split("/")[-2]
            folder = IssueDir.of(data_dir, date)
            if not folder.candidates.exists():
                print(f"::warning::{path}: main has no {date}/{issue.CANDIDATES}, skipped", file=sys.stderr)
                continue
            incoming = Path(tmp) / f"{date}.{'en' if en else 'zh'}.json"
            incoming.write_text(_git(root, "show", f"{sha}:{path}"), encoding="utf-8")
            run_trace = None
            if not en:
                if (refused := _branch_refuses(incoming)) is not None:
                    print(f"{date}: kept ({refused})", file=sys.stderr)
                    continue
                saved = Path(tmp) / f"{date}.trace.json"
                run_trace = _branch_trace(root, sha, f"{data}/{date}", incoming, saved)
            adopt(folder, incoming, run_trace, en)


def _branch_refuses(incoming: Path) -> str | None:
    """A branch carries the runs of the routes that edit by SKILL.md (and the fallback such an editor
    writes when it gives up); a per-model route publishes through its own workflow."""
    try:
        route = routes.of(issue.read(incoming))
    except json.JSONDecodeError:
        return None  # adopt reports it
    if route is not None and route.per_model:
        return f"the {route.channel} route does not come in through a branch"
    return None


def _branch_trace(root: Path, sha: str, issue_path: str, incoming: Path, out: Path) -> Path | None:
    """The trace of the run on the branch: its route's, or for a fallback the editor wrote when it gave
    up, that of the SKILL.md route whose trace the branch carries."""
    try:
        data = issue.read(incoming)
    except json.JSONDecodeError:
        return None
    route = routes.of(data)
    if route is not None and route.channel in routes.SKILL_ROUTES:
        names = [str(routes.trace_name(data))]
    else:
        names = [str(routes.trace_name({"channel": channel})) for channel in routes.SKILL_ROUTES]
    for name in names:
        try:
            out.write_text(_git(root, "show", f"{sha}:{issue_path}/{name}"), encoding="utf-8")
        except subprocess.CalledProcessError:
            continue
        return out
    return None


def save_run(folder: Path, date: str, digests: list[Path], en: Path | None, traces: list[Path]) -> None:
    """Leaves a run of the API route in folder for from_dir: digests in priority order."""
    folder.mkdir(parents=True, exist_ok=True)
    for path in [*digests, *traces, *([en] if en else [])]:
        shutil.copy(path, folder / path.name)
    manifest = {"date": date, "digests": [p.name for p in digests], "en": en.name if en else None}
    issue.write(folder / RUN, manifest)


def from_dir(data_dir: Path, folder: Path) -> None:
    """Adopts a run left by save_run. The traces go in first, for adopt to note in each whether its
    digest became the main issue; each digest stays as a beta next to the main issue."""
    if not (folder / RUN).exists():
        print(f"{folder}: no run to adopt", file=sys.stderr)
        return
    run = issue.read(folder / RUN)
    target = IssueDir.of(data_dir, run["date"])
    for path in sorted(folder.glob("trace.*.json")):
        shutil.copy(path, target.path / path.name)
    for name in run["digests"]:
        shutil.copy(folder / name, target.path / name)
        adopt(target, target.path / name)
    if run.get("en"):  # taken only when its digest did become the main issue (publish.goes_with)
        adopt(target, folder / run["en"], en=True)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout
