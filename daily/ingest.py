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

from daily import publish, render, routes, trace

# In a run folder: {"date", "digests": [file names, in priority order], "en": file name | null}.
RUN = "run.json"


def adopt(issue_dir: Path, source: Path, run_trace: Path | None = None, en: bool = False) -> bool:
    """Adopts the digest at source into the issue if publish says so. True if it was adopted."""
    candidates = _read(issue_dir / "candidates.json")
    path = issue_dir / ("digest.en.json" if en else "digest.json")
    try:
        incoming = _read(source)
    except json.JSONDecodeError as exc:
        incoming = f"invalid JSON: {exc}"
    try:
        current = _read(path) if path.exists() else None
    except json.JSONDecodeError:
        current = None
    if en:
        main_path = issue_dir / "digest.json"
        main = _read(main_path) if main_path.exists() else None
        data, reason = publish.decide_en(main, current, incoming, candidates)
    else:
        data, reason = publish.decide(current, incoming, candidates)
    print(f"{issue_dir.name}: {'adopted' if data else 'kept'} ({reason})", file=sys.stderr)
    _trace_adopt(issue_dir, incoming, run_trace, data is not None, reason, "en" if en else "zh")
    if data is None:
        return False
    _write(path, data)
    if not en:
        (issue_dir / "digest.md").write_text(render.to_markdown(data, candidates), encoding="utf-8")
    print(path)
    return True


def _trace_adopt(
    issue_dir: Path, incoming: Any, source: Path | None, adopted: bool, reason: str, edition: str
) -> None:
    """The trace follows the digest: the trace of an adopted run (source) replaces the route's, and
    a rejected run is noted in the trace already there. Either way the verdict is appended."""
    if not isinstance(incoming, dict) or reason == "unchanged":
        return
    run = trace.load(source) if source is not None else None
    # A run's trace names its route: a fallback the Claude editor wrote when it gave up
    # (`degrade --force`) goes with trace.claude.json, though the fallback route keeps none.
    name = trace.file_name(run if run is not None else incoming)
    if name is None:
        return
    path = issue_dir / name
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
        for path in changed("digest.json") + changed("digest.en.json"):
            en = path.endswith(".en.json")
            date = path.split("/")[-2]
            issue_dir = data_dir / date
            if not (issue_dir / "candidates.json").exists():
                print(f"::warning::{path}: main has no {date}/candidates.json, skipped", file=sys.stderr)
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
            adopt(issue_dir, incoming, run_trace, en)


def _branch_refuses(incoming: Path) -> str | None:
    """A branch carries the runs of the routes that edit by SKILL.md (and the fallback such an editor
    writes when it gives up); a per-model route publishes through its own workflow."""
    try:
        route = routes.of(_read(incoming))
    except json.JSONDecodeError:
        return None  # adopt reports it
    if route is not None and route.per_model:
        return f"the {route.channel} route does not come in through a branch"
    return None


def _branch_trace(root: Path, sha: str, issue: str, incoming: Path, out: Path) -> Path | None:
    """The trace of the run on the branch: its route's, or for a fallback the editor wrote when it gave
    up, that of the SKILL.md route whose trace the branch carries."""
    try:
        data = _read(incoming)
    except json.JSONDecodeError:
        return None
    route = routes.of(data)
    if route is not None and route.channel in routes.SKILL_ROUTES:
        names = [str(routes.trace_name(data))]
    else:
        names = [str(routes.trace_name({"channel": channel})) for channel in routes.SKILL_ROUTES]
    for name in names:
        try:
            out.write_text(_git(root, "show", f"{sha}:{issue}/{name}"), encoding="utf-8")
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
    _write(folder / RUN, manifest)


def from_dir(data_dir: Path, folder: Path) -> None:
    """Adopts a run left by save_run. The traces go in first, for adopt to note in each whether its
    digest became the main issue; each digest stays as a beta next to the main issue."""
    if not (folder / RUN).exists():
        print(f"{folder}: no run to adopt", file=sys.stderr)
        return
    run = _read(folder / RUN)
    issue_dir = data_dir / run["date"]
    for path in sorted(folder.glob("trace.*.json")):
        shutil.copy(path, issue_dir / path.name)
    for name in run["digests"]:
        shutil.copy(folder / name, issue_dir / name)
        adopt(issue_dir, issue_dir / name)
    if run.get("en"):  # taken only when its digest did become the main issue (publish.goes_with)
        adopt(issue_dir, folder / run["en"], en=True)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
