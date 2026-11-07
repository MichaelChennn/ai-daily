"""`daily ingest`: a Claude branch's commit, or the folder an API run left, adopted into main's issues."""

import json
import subprocess

import pytest

from daily import cli, edit, fallback, pipeline
from daily.issue import IssueDir
from tests.test_api_editor import ENGLISH, MODEL, FakeWeb, _picks, _reply, _written
from tests.test_digest import CANDIDATES, DATE, _digest
from tests.test_site import _en

MINIMAX = "nvidia:minimaxai/minimax-m3.1-flash"


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def _put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """main with today's candidates; the editor's branch starts from it."""
    for key in ("AUTHOR", "COMMITTER"):
        monkeypatch.setenv(f"GIT_{key}_NAME", "test")
        monkeypatch.setenv(f"GIT_{key}_EMAIL", "test@example.com")
    root = tmp_path / "repo"
    _put(root / "data" / DATE / "candidates.json", {**CANDIDATES, "clusters": [], "sources": []})
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "candidates")
    _git(root, "switch", "-qc", "claude/today")
    return root


def _push(root, files):
    """A commit on the editor's branch, then back to main, as the ingest workflow checks it out."""
    for name, data in files.items():
        _put(root / "data" / DATE / name, data)
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "edit")
    _git(root, "switch", "-q", "main")


def _ingest(root):
    data_dir = root / "data"
    assert cli.main(["ingest", "--ref", "claude/today", "--base", "main", "--data-dir", str(data_dir)]) == 0
    return data_dir / DATE


def _read(path):
    return json.loads(path.read_text())


def test_a_branch_brings_its_digests_and_trace_and_nothing_else(repo):
    run = {"channel": "claude", "steps": [{"step": "final"}], "adopt": []}
    _push(
        repo,
        {
            "digest.json": _digest(),
            "digest.en.json": _en(),
            "trace.claude.json": run,
            "candidates.json": {**CANDIDATES, "candidates": []},  # not the editor's to change
        },
    )
    issue = _ingest(repo)
    assert _read(issue / "digest.json")["channel"] == "claude"
    assert _read(issue / "digest.en.json")["lang"] == "en"  # after its main issue, though it sorts first
    assert (issue / "digest.md").exists()
    assert len(_read(issue / "candidates.json")["candidates"]) == len(CANDIDATES["candidates"])
    trace = _read(issue / "trace.claude.json")
    assert trace["steps"] == run["steps"]
    assert [(a["edition"], a["adopted"]) for a in trace["adopt"]] == [("zh", True), ("en", True)]


def test_a_fallback_the_editor_gave_up_with_brings_its_trace(repo):
    failure = {"step": "final", "error": "too few items"}
    _push(
        repo,
        {
            "digest.json": fallback.build_fallback(CANDIDATES),
            "trace.claude.json": {"channel": "claude", "steps": [], "failure": failure, "adopt": []},
        },
    )
    issue = _ingest(repo)
    assert _read(issue / "digest.json")["mode"] == "fallback"
    assert _read(issue / "trace.claude.json")["failure"] == failure


def test_a_branch_does_not_bring_an_api_digest(repo, capsys):
    _push(repo, {"digest.json": _digest(channel="api", model=MODEL)})
    issue = _ingest(repo)
    assert not (issue / "digest.json").exists()
    assert "the api route does not come in through a branch" in capsys.readouterr().err


@pytest.fixture
def issue_dir(tmp_path, monkeypatch):
    folder = tmp_path / "runner" / DATE
    folder.mkdir(parents=True)
    (folder / "candidates.json").write_text(json.dumps({**CANDIDATES, "clusters": [], "sources": []}))
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test")
    monkeypatch.setattr("daily.llm._sleep", _no_sleep)
    return folder


async def _no_sleep(_):
    pass


def test_edit_runs_every_model_and_the_one_that_would_be_the_main_issue_writes_english(
    issue_dir, tmp_path, monkeypatch
):
    web = FakeWeb([_picks(), _written(), _picks(), _written(), _reply(json.dumps(ENGLISH))])
    monkeypatch.setattr(pipeline, "make_client", web.client)
    out = tmp_path / "run"
    models = f"{MODEL},acme:x/broken-1,{MINIMAX}"
    args = ["edit", "--date", DATE, "--data-dir", str(issue_dir.parent), "--model", models, "--out", str(out)]
    assert cli.main(args) == 2  # one model failed: the job fails, after the others ran

    assert json.loads(web.chats[-1].content)["model"] == "deepseek-ai/deepseek-v4.1-flash"  # the first
    run = _read(out / "run.json")
    assert run == {
        "date": DATE,
        "digests": ["digest.api.deepseek.json", "digest.api.minimax.json"],
        "en": "digest.en.deepseek.json",
    }
    assert sorted(p.name for p in out.glob("trace.*")) == [
        "trace.api.broken.json",
        "trace.api.deepseek.json",
        "trace.api.minimax.json",
    ]

    # The publish job, on main: the traces and betas go in, and the first model's digest leads.
    main = tmp_path / "main" / DATE
    main.mkdir(parents=True)
    (main / "candidates.json").write_text((issue_dir / "candidates.json").read_text())
    assert cli.main(["ingest", "--from-dir", str(out), "--data-dir", str(main.parent)]) == 0
    assert _read(main / "digest.json")["model"] == MODEL
    assert _read(main / "digest.en.json")["model"] == MODEL
    assert (main / "digest.api.minimax.json").exists()
    assert _read(main / "trace.api.broken.json")["failure"]["step"] == "setup"
    adopted = {
        name: _read(main / name)["adopt"] for name in ("trace.api.deepseek.json", "trace.api.minimax.json")
    }
    assert [a["adopted"] for a in adopted["trace.api.deepseek.json"]] == [True, True]  # zh, en
    assert [a["reason"] for a in adopted["trace.api.minimax.json"]] == [
        "keeping the edited issue over an API edit"
    ]


def test_edit_writes_no_english_when_a_claude_edit_leads(issue_dir, tmp_path, monkeypatch):
    (issue_dir / "digest.json").write_text(json.dumps(_digest(), ensure_ascii=False))
    web = FakeWeb([_picks(), _written()])
    monkeypatch.setattr(pipeline, "make_client", web.client)
    out = tmp_path / "run"
    assert edit.run(IssueDir(issue_dir), [MODEL], out) == 0
    assert _read(out / "run.json")["en"] is None and len(web.chats) == 2


def test_ingest_without_a_run_does_nothing(tmp_path):
    assert cli.main(["ingest", "--from-dir", str(tmp_path / "none"), "--data-dir", str(tmp_path)]) == 0
