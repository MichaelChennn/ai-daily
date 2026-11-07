"""生成记录: what the Claude route records through the CLI, what adopt adds, and the process data."""

import io
import json

import pytest

from daily import cli, digest, fallback, ingest, process, trace
from daily.issue import IssueDir
from tests.test_digest import CANDIDATES, DATE, _digest

MODEL = "nvidia:deepseek-ai/deepseek-v4.1-flash"


@pytest.fixture
def issue_dir(tmp_path):
    folder = tmp_path / DATE
    folder.mkdir()
    (folder / "candidates.json").write_text(json.dumps({**CANDIDATES, "clusters": [], "sources": []}))
    return folder


def _cli(issue_dir, *args, stdin=None, monkeypatch=None):
    if stdin is not None:
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(stdin, ensure_ascii=False)))
    return cli.main([*args, "--date", DATE, "--data-dir", str(issue_dir.parent)])


def _trace(issue_dir, name="trace.claude.json"):
    return json.loads((issue_dir / name).read_text())


def _write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False))


def test_the_claude_route_records_scores_self_check_and_every_validate_round(issue_dir, monkeypatch):
    scores = {"c_gpt": [3, 2, 2], "c_vllm": [2, 2, 1], "c_qwen": [3, 3, 3], "c_unknown": [1, 1, 1]}
    assert _cli(issue_dir, "trace", "scores", stdin=scores, monkeypatch=monkeypatch) == 0
    dropped = [{"candidates": ["c_hn"], "title": "有人在生产环境用 MCP 吗", "reason": "只是提问"}]
    assert _cli(issue_dir, "trace", "self-check", stdin=dropped, monkeypatch=monkeypatch) == 0

    data = _digest(model="claude-opus-5-5")
    data["items"][1]["summary"] = "新版本速度提升 40%。"  # not in the material
    _write(issue_dir / "digest.json", data)
    assert _cli(issue_dir, "validate") == 1
    assert _cli(issue_dir, "validate", "--drop-invalid") == 0

    record = _trace(issue_dir)
    assert (record["channel"], record["model"]) == ("claude", "claude-opus-5-5")
    assert record["scores"] == {"c_gpt": [3, 2, 2], "c_vllm": [2, 2, 1]}
    assert [s["step"] for s in record["steps"]] == ["self_check", "check", "final"]
    assert record["steps"][0]["items"] == [{**dropped[0]}]
    final = record["steps"][2]
    assert [i["candidates"] for i in final["items"]] == [["c_gpt"], ["c_vllm"], ["c_qwen"], ["c_paper"]]
    assert final["items"][1]["reasons"] and not final["items"][0]["reasons"]
    validation = json.loads((issue_dir / "digest.json").read_text())["validation"]
    assert validation["dropped"][0]["candidates"] == ["c_vllm"]

    # A new run starts a new trace.
    assert _cli(issue_dir, "trace", "scores", stdin={}, monkeypatch=monkeypatch) == 0
    assert _trace(issue_dir)["steps"] == []


def test_api_and_fallback_digests_add_nothing_to_the_claude_trace(issue_dir):
    _write(issue_dir / "digest.json", _digest(channel="api", model=MODEL))
    assert _cli(issue_dir, "validate") == 0
    _write(issue_dir / "digest.json", fallback.build_fallback(CANDIDATES))
    _cli(issue_dir, "validate")
    assert not (issue_dir / "trace.claude.json").exists()


def test_the_forced_fallback_is_recorded_as_the_claude_route_failing(issue_dir):
    data = _digest(highlights=["OpenAI 发布 GPT-7。"])  # fails the whole issue
    _write(issue_dir / "digest.json", data)
    assert _cli(issue_dir, "validate", "--drop-invalid") == 1
    assert fallback.degrade(IssueDir(issue_dir), force=True)
    failure = _trace(issue_dir)["failure"]
    assert failure["step"] == "final" and "GPT-7" in failure["error"]


def test_a_forced_fallback_brings_the_claude_trace_with_it(issue_dir, tmp_path):
    trace_path, digest_path = tmp_path / "run.trace.json", tmp_path / "run.json"
    failure = {"step": "final", "error": "too few items"}
    _write(trace_path, {"channel": "claude", "steps": [{"step": "final"}], "failure": failure, "adopt": []})
    _write(digest_path, fallback.build_fallback(CANDIDATES))
    assert ingest.adopt(IssueDir(issue_dir), digest_path, trace_path)
    record = _trace(issue_dir)
    assert record["failure"] == failure
    assert [(a["adopted"], a["reason"]) for a in record["adopt"]] == [(True, "no valid digest yet")]


def test_the_trace_follows_the_adopted_digest(issue_dir, tmp_path):
    def run(name, steps, generated_at):
        trace_path, digest_path = tmp_path / f"{name}.trace.json", tmp_path / f"{name}.json"
        _write(trace_path, {"channel": "claude", "started_at": generated_at, "steps": steps, "adopt": []})
        _write(digest_path, _digest(generated_at=generated_at))
        return digest_path, trace_path

    folder = IssueDir(issue_dir)
    first = run("first", [{"step": "final"}], "2026-10-19T21:00:00+00:00")
    assert ingest.adopt(folder, *first)
    record = _trace(issue_dir)
    assert record["steps"] == [{"step": "final"}]
    assert [(a["edition"], a["adopted"]) for a in record["adopt"]] == [("zh", True)]

    older = run("older", [{"step": "precheck"}], "2026-10-19T20:00:00+00:00")
    assert not ingest.adopt(folder, *older)
    record = _trace(issue_dir)
    assert record["steps"] == [{"step": "final"}]  # the adopted run's, kept
    rejected = record["adopt"][-1]
    assert (rejected["adopted"], rejected["run"]) == (False, "2026-10-19T20:00:00+00:00")
    assert rejected["reason"] == "the current edit is newer"

    assert not ingest.adopt(folder, *first)  # unchanged: nothing to note
    assert len(_trace(issue_dir)["adopt"]) == 2


def test_adopt_notes_in_the_api_trace_whether_it_became_the_main_issue(issue_dir, tmp_path):
    _write(issue_dir / "trace.api.deepseek.json", {"channel": "api", "steps": [], "adopt": []})
    incoming = issue_dir / "digest.api.deepseek.json"
    _write(incoming, _digest(channel="api", model=MODEL))
    assert ingest.adopt(IssueDir(issue_dir), incoming)
    (record,) = _trace(issue_dir, "trace.api.deepseek.json")["adopt"]
    assert (record["adopted"], record["reason"]) == (True, "no valid digest yet")


def _process(issue_dir):
    candidates = json.loads((issue_dir / "candidates.json").read_text())
    return process.issue_process(issue_dir, candidates, {})


def test_process_data_follows_each_candidate_through_each_route(issue_dir):
    scores = {"c_gpt": [3, 2, 2], "c_vllm": [2, 2, 1], "c_hn": [1, 1, 1], "c_paper": [1, 1, 0]}
    folder = IssueDir(issue_dir)
    trace.record_scores(folder, "claude", CANDIDATES, scores)
    dropped = [{"candidates": ["c_hn"], "title": "有人在生产环境用 MCP 吗", "reason": "只是提问"}]
    trace.record_self_check(folder, "claude", CANDIDATES, dropped)
    data = _digest()
    data["items"][1]["summary"] = "新版本速度提升 40%。"
    _write(issue_dir / "digest.json", data)
    _cli(issue_dir, "validate", "--drop-invalid")
    # The API route has no trace: its digest's validation is all there is.
    api = _digest(channel="api", model=MODEL)
    _write(
        issue_dir / "digest.api.deepseek.json",
        digest.apply_report(api, digest.validate(api, CANDIDATES), True),
    )

    result = _process(issue_dir)
    assert result["main"] == "claude" and result["filtered"] is None
    claude, deepseek = result["channels"]
    assert (claude["id"], claude["recorded"], claude["scored"]) == ("claude", True, True)
    assert (deepseek["id"], deepseek["label"], deepseek["recorded"]) == ("api.deepseek", "DeepSeek", False)
    assert [f["value"] for f in claude["funnel"]] == [5, 5, 5, 3, 3]
    assert [s["label"] for s in claude["steps"]] == ["自检", "正式校验"]

    rows = {row["id"]: row for row in result["rows"]}
    assert rows["c_gpt"]["cells"]["claude"]["state"] == "published" and not rows["c_gpt"]["differs"]
    hn = rows["c_hn"]["cells"]["claude"]
    assert (hn["state"], hn["step"], hn["reasons"], hn["total"]) == ("dropped", "自检", ["只是提问"], 3)
    vllm = rows["c_vllm"]["cells"]["claude"]
    assert (vllm["state"], vllm["step"]) == ("dropped", "正式校验") and "40" in vllm["reasons"][0]
    assert rows["c_vllm"]["differs"] and rows["c_vllm"]["dropped"] and rows["c_vllm"]["high_unpicked"]
    assert rows["c_hn"]["cells"]["api.deepseek"] == {
        "state": "unpicked",
        "step": None,
        "reasons": [],
        "score": None,
        "total": None,
    }


def test_process_data_lists_the_filtered_items_by_source(issue_dir):
    candidates = {
        **CANDIDATES,
        "sources": [{"id": "hackernews", "status": "ok", "count": 1, "filtered": {"not_ai": 1}}],
        "filtered": [
            {
                "source": "hackernews",
                "title": "SimCity",
                "url": "https://x.com",
                "reason": "not_ai",
                "value": None,
            }
        ],
    }
    result = process.issue_process(issue_dir, candidates, {"hackernews": "Hacker News"})
    assert result["sources"][0]["filtered"] == {"not_ai": 1}
    assert result["filtered"] == [
        {
            "source": "hackernews",
            "name": "Hacker News",
            "items": [{"title": "SimCity", "url": "https://x.com", "reason": "与 AI 无关", "value": None}],
        }
    ]


def test_process_data_puts_each_highlight_error_under_its_highlight(issue_dir):
    trace.record_scores(IssueDir(issue_dir), "claude", CANDIDATES, {})
    data = _digest()
    data["highlights"] = ["OpenAI 发布 GPT-6，上下文达到 1M token。", "vLLM 新版本快了 40%，支持 Qwen9。"]
    _write(issue_dir / "digest.json", data)
    _cli(issue_dir, "validate")
    assert _trace(issue_dir)["steps"][0]["highlights"] == data["highlights"]

    (step,) = _process(issue_dir)["channels"][0]["steps"]
    assert step["highlights"] == [{"text": data["highlights"][1], "missing": ["Qwen9", "40", "9"]}]
    assert [p["title"] for p in step["passed"]] == [item["title"] for item in data["items"]]
    assert all(p["candidates"] for p in step["passed"])
