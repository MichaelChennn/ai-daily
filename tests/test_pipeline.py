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
    (yesterday / "digest.json").write_text(
        json.dumps({"items": [{"sources": [{"url": "https://openai.com/index/gpt-6"}]}]})
    )

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


async def test_filtered_items_are_counted_per_source_and_listed(window):
    sources = [source("hackernews", "discussion", tier=2, id_="hackernews")]
    async with mock_client({"hn.algolia.com/api/v1/search_by_date": HN}) as client:
        raw, reports = await pipeline.fetch_all(sources, window, client)
    data = pipeline.build_candidates(raw, sources, window, reports, dedup.History({}, {}))
    assert data["stats"]["filtered"] == 2
    assert data["sources"][0]["filtered"] == {"not_ai": 2} and data["sources"][0]["count"] == 2
    assert data["filtered"][0] == {
        "source": "hackernews",
        "title": "SimCity, but with permits",
        "url": "https://x.com",
        "reason": "not_ai",
        "value": None,
    }
    json.dumps(data)


def _release(version, signals=None):
    return Candidate(
        source="github-releases",
        source_name="GitHub Releases",
        tier=1,
        kind="release",
        title=f"ollama/ollama {version}",
        url=f"https://github.com/ollama/ollama/releases/tag/{version}",
        published_at=IN_WINDOW,
        signals=signals or {},
    )


def test_late_release_only_stays_if_no_earlier_candidate_had_it(window):
    sources = [source("github_releases", "release", id_="github-releases")]
    seen = dedup.url_key("https://github.com/ollama/ollama/releases/tag/v2")
    history = dedup.History({seen: ["2026-10-19"]}, {})
    raw = [
        _release("v1", {"late_release": True}),  # first time we see it: was a pre-release until now
        _release("v2", {"late_release": True}),  # an earlier issue already had it
        _release("v3"),
    ]
    data = pipeline.build_candidates(raw, sources, window, [], history)
    assert [c["title"] for c in data["candidates"]] == [
        "ollama/ollama v1",
        "ollama/ollama v3",
    ]
    assert data["stats"]["seen_before"] == 0


def test_shipped_sources_are_the_agreed_list():
    sources = {s.id: s for s in load_sources(DEFAULT_SOURCES_FILE)}
    commentary = {s.id for s in sources.values() if s.kind == "commentary"}
    assert len(commentary) == 13
    assert all(sources[i].tier == 2 and sources[i].type == "rss" for i in commentary)
    assert all(sources[i].options.get("homepage") for i in commentary)  # the sources page links to them
    assert sources["latent-space"].options["exclude_title_pattern"] == r"^\[AINews\]"
    assert sources["simon-willison"].options["url"].endswith("/atom/entries/")
    assert {"qwen-blog", "seed-blog"} <= {s.id for s in sources.values() if s.type == "json_api"}
    assert sources["hf-daily-papers"].options["week_fallback_limit"] == 10
    assert sources["minimax-blog"].options["link_pattern"] == "^/(blog|news)/[a-z0-9-]+$"
    # Every existing source is still there, and still on.
    existing = {
        "openai-news", "anthropic-news", "anthropic-research", "deepmind-blog", "google-ai-blog", "mistral-news",
        "huggingface-blog", "meta-ai-news", "minimax-blog", "kimi-blog", "deepseek-news", "hf-daily-papers",
        "github-releases", "github-trending", "hf-trending-models", "hackernews", "reddit-ai",
    }  # fmt: skip
    assert existing <= sources.keys()
    assert all(sources[i].enabled for i in existing)
    assert len(sources) == 46
