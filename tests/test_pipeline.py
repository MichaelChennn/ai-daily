import json
from datetime import timedelta

import pytest

from daily import cli, dedup, pipeline
from daily.config import DEFAULT_SOURCES_FILE, load_sources
from daily.fetchers import FETCHERS
from daily.models import Candidate
from tests.conftest import IN_WINDOW, ISSUE, mock_client, source
from tests.test_fetchers import HN, RSS


def test_every_configured_source_has_a_fetcher():
    sources = load_sources(DEFAULT_SOURCES_FILE)
    assert sources
    assert {s.type for s in sources} <= set(FETCHERS)


async def test_one_failing_source_does_not_stop_the_others(window):
    sources = [
        source("rss", id_="openai-news", url="https://openai.com/news/rss.xml"),
        source("rss", id_="broken", url="https://broken.example/feed"),
        source("hackernews", "discussion", tier=2, id_="hackernews"),
    ]
    routes = {
        "openai.com/news/rss.xml": RSS,
        "broken.example/feed": ConnectionError("boom"),
        "hn.algolia.com/api/v1/search_by_date": HN,
    }
    async with mock_client(routes) as client:
        raw, reports = await pipeline.fetch_all(sources, window, client)

    assert {r.id: r.status for r in reports} == {"openai-news": "ok", "broken": "error", "hackernews": "ok"}
    assert "boom" in next(r.error for r in reports if r.id == "broken")
    assert len(raw) == 3  # 1 blog post + 2 HN stories


def test_build_candidates_merges_hn_into_official_post(window):
    sources = [source("rss", id_="openai-news"), source("hackernews", "discussion", tier=2, id_="hackernews")]
    blog = Candidate(
        source="openai-news",
        source_name="OpenAI",
        tier=1,
        kind="blog",
        title="Introducing GPT-6",
        url="https://openai.com/index/gpt-6/",
        published_at=IN_WINDOW,
    )
    hn = Candidate(
        source="hackernews",
        source_name="HN",
        tier=2,
        kind="discussion",
        title="GPT-6",
        url="https://openai.com/index/gpt-6",
        published_at=IN_WINDOW,
        signals={"hn_points": 900},
    )
    data = pipeline.build_candidates([hn, blog], sources, window, [], dedup.History({}, {}))
    assert data["stats"]["raw"] == 2 and data["stats"]["candidates"] == 1
    (item,) = data["candidates"]
    assert item["source"] == "openai-news" and item["signals"] == {"hn_points": 900}
    assert item["published_at"] == IN_WINDOW.isoformat()
    json.dumps(data)  # serializable


def test_cli_fetch_writes_candidates_json(tmp_path, monkeypatch, capsys):
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text(
        """
sources:
  - {id: openai-news, name: OpenAI, type: rss, tier: 1, kind: blog, url: "https://openai.com/news/rss.xml"}
  - {id: hackernews, name: HN, type: hackernews, tier: 2, kind: discussion, min_points: 50}
  - {id: paused, name: Paused, type: rss, tier: 1, kind: blog, enabled: false, url: "https://off.example/"}
"""
    )
    data_dir = tmp_path / "data"
    yesterday = data_dir / (ISSUE - timedelta(days=1)).isoformat()
    yesterday.mkdir(parents=True)
    (yesterday / "digest.json").write_text(json.dumps({"items": [{"url": "https://openai.com/index/gpt-6"}]}))

    routes = {"openai.com/news/rss.xml": RSS, "hn.algolia.com/api/v1/search_by_date": HN}
    monkeypatch.setattr(pipeline, "make_client", lambda: mock_client(routes))

    code = cli.main(
        ["fetch", "--date", ISSUE.isoformat(), "--sources", str(sources_file), "--data-dir", str(data_dir)]
    )

    assert code == 0
    out = data_dir / ISSUE.isoformat() / "candidates.json"
    assert capsys.readouterr().out.strip() == str(out)
    data = json.loads(out.read_text())
    assert data["date"] == ISSUE.isoformat()
    assert [d["url"] for d in data["dropped"]] == ["https://openai.com/index/gpt-6/"]
    assert {s["id"]: s["status"] for s in data["sources"]} == {
        "openai-news": "ok",
        "hackernews": "ok",
        "paused": "disabled",
    }
    assert [c["source"] for c in data["candidates"]] == ["hackernews", "hackernews"]


def test_cli_fetch_fails_when_nothing_was_fetched(tmp_path, monkeypatch):
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text(
        'sources:\n  - {id: a, name: A, type: rss, tier: 1, kind: blog, url: "https://a.example/"}\n'
    )
    monkeypatch.setattr(pipeline, "make_client", lambda: mock_client({}))
    code = cli.main(["fetch", "--sources", str(sources_file), "--data-dir", str(tmp_path / "data")])
    assert code == 1


def test_source_ids_must_be_strings(tmp_path):
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text("sources:\n  - {id: off, name: A, type: rss, tier: 1, kind: blog}\n")
    with pytest.raises(ValueError, match="must be a string"):
        load_sources(sources_file)


def test_cli_rejects_unknown_only(tmp_path):
    assert cli.main(["fetch", "--only", "nope", "--data-dir", str(tmp_path)]) == 2
