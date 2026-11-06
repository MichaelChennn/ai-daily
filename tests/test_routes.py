"""The route table: a digest's channel decides whether it is valid, whether it becomes the main issue,
and where its trace and beta go."""

import copy
import json

import pytest

from daily import digest, fallback, process, publish, routes, site
from tests.test_digest import CANDIDATES, DATE, _digest

MODEL = "nvidia:minimaxai/minimax-m3.1-flash"


@pytest.mark.parametrize(
    ("overrides", "problem"),
    [
        ({"channel": None}, "channel None is missing or unknown"),
        ({"channel": "jules"}, "channel 'jules' is missing or unknown"),
        ({"channel": "fallback"}, "the fallback route writes mode 'fallback'"),
        ({"channel": "api"}, "the api route needs the model"),
    ],
)
def test_a_digest_must_name_a_known_route(overrides, problem):
    data = _digest(**overrides)
    if overrides["channel"] is None:
        del data["channel"]
    errors = digest.validate(data, CANDIDATES).errors
    assert any(problem in e for e in errors), errors


def test_files_and_labels_come_from_the_table():
    api = {"channel": "api", "model": MODEL}
    assert routes.key(api) == "api.minimax"
    assert routes.trace_name(api) == "trace.api.minimax.json"
    assert routes.trace_name({"channel": "claude"}) == "trace.claude.json"
    assert routes.trace_name({"channel": "fallback", "mode": "fallback"}) is None
    assert routes.beta_name("api", MODEL) == "digest.api.minimax.json"
    assert (routes.label("claude"), routes.label("api.minimax"), routes.label("api.qwen")) == (
        "Claude",
        "MiniMax",
        "qwen",  # no label yet: shown as it is
    )


def test_an_older_fallback_does_not_replace_a_newer_one():
    newer = fallback.build_fallback(CANDIDATES)
    older = {**newer, "generated_at": "2026-10-19T00:00:00+00:00"}
    assert publish.decide(copy.deepcopy(newer), copy.deepcopy(older), CANDIDATES) == (
        None,
        "the current edit is newer",
    )


@pytest.fixture
def jules(monkeypatch):
    """A new route is a new row: a per-model agent route ranked above Claude."""
    table = {
        **routes.ROUTES,
        "jules": routes.Route(
            "jules", "Jules", "full", 3, redo=True, per_model=True, traced=True,
            noun="Jules edit", a_noun="a Jules edit", betas={"gemini": "Jules (Gemini)"},
        ),
    }  # fmt: skip
    monkeypatch.setattr(routes, "ROUTES", table)


def test_a_new_route_takes_its_place_by_priority(jules):
    claude = _digest(generated_at="2026-10-19T23:00:00+00:00")
    new = _digest(channel="jules", model="google:gemini-3-pro", generated_at="2026-10-19T21:00:00+00:00")
    assert publish.decide(copy.deepcopy(claude), copy.deepcopy(new), CANDIDATES)[1] == (
        "a Jules edit replaces the Claude edit"
    )
    assert publish.decide(copy.deepcopy(new), copy.deepcopy(claude), CANDIDATES) == (
        None,
        "keeping the edited issue over a Claude edit",
    )


def test_a_new_routes_betas_are_found_and_labelled(jules, tmp_path):
    issue_dir = tmp_path / DATE
    issue_dir.mkdir()
    (issue_dir / "candidates.json").write_text(json.dumps({**CANDIDATES, "clusters": [], "sources": []}))
    (issue_dir / "digest.json").write_text(json.dumps(_digest()))
    beta = _digest(channel="jules", model="google:gemini-3-pro")
    (issue_dir / "digest.jules.gemini.json").write_text(json.dumps(beta))

    (issue,) = site.load_issues(tmp_path)
    assert list(issue.betas) == ["gemini"]
    channels = process.issue_process(issue_dir, CANDIDATES, {})["channels"]
    assert [(c["id"], c["label"]) for c in channels] == [
        ("claude", "Claude"),
        ("jules.gemini", "Jules (Gemini)"),
    ]
