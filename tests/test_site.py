import copy
import json
import xml.etree.ElementTree as ET

import pytest

from daily import cli, digest, export, fallback, publish, site
from tests.conftest import source
from tests.test_digest import CANDIDATES, DATE, _digest

NEXT = "2026-10-21"
OLD = "2026-09-01"  # more than 30 days before NEXT


def _candidates(day):
    data = copy.deepcopy(CANDIDATES)
    data["date"] = day
    data["sources"] = [
        {"id": "openai-news", "status": "ok", "count": 1, "seconds": 0.1, "error": None},
        {"id": "reddit", "status": "error", "count": 0, "seconds": 0.1, "error": "HTTPStatusError: 429"},
        {"id": "hf-papers", "status": "disabled", "count": 0, "seconds": 0.0, "error": None},
    ]
    return data


def _write_issue(data_dir, day, digest_data=None):
    folder = data_dir / day
    folder.mkdir(parents=True)
    candidates = _candidates(day)
    (folder / "candidates.json").write_text(json.dumps(candidates))
    if digest_data is None:
        digest_data = fallback.build_fallback(candidates)
    (folder / "digest.json").write_text(json.dumps(digest_data))


@pytest.fixture
def data_dir(tmp_path):
    data = tmp_path / "data"
    _write_issue(data, DATE, _digest(generated_at="2026-10-19T21:40:00+00:00"))
    _write_issue(data, NEXT)  # fallback
    _write_issue(data, OLD, {**_digest(), "date": OLD})
    _write_issue(data, "2026-10-18", {"schema_version": 1, "date": "2026-10-18", "mode": "full"})  # invalid
    return data


SOURCES = [
    source(
        "rss", id_="openai-news", url="https://openai.com/news/rss.xml", homepage="https://openai.com/news/"
    ),
    source("reddit", kind="discussion", tier=2, id_="reddit", subreddit="LocalLLaMA"),
    source("hf_daily_papers", kind="paper", id_="hf-papers"),
]
SOURCES[2].enabled = False


def test_export_writes_the_feed(tmp_path, data_dir):
    public = tmp_path / "public"
    issues = export.export(tmp_path / "data", public, data_dir, SOURCES, "https://example.github.io/ai-daily")
    assert [i.slug for i in issues] == [NEXT, DATE, OLD]  # the invalid issue is left out
    assert (public / ".nojekyll").exists()
    channel = ET.parse(public / "feed.xml").getroot().find("channel")
    items = channel.findall("item")
    assert [i.findtext("link") for i in items] == [  # the last 30 days only
        f"https://example.github.io/ai-daily/{NEXT}/",
        f"https://example.github.io/ai-daily/{DATE}/",
    ]
    assert items[0].findtext("guid").endswith("#fallback") and "降级版" in items[0].findtext("title")
    content = items[1].findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
    assert "<h3>OpenAI 发布 GPT-6</h3>" in content and "GPT-6 支持 1M token 上下文" in content
    assert 'href="https://openai.com/index/gpt-6/"' in content and "#模型" in content
    assert items[1].findtext("pubDate") == "Mon, 19 Oct 2026 21:40:00 +0000"


def test_feed_text_is_escaped(data_dir):
    path = data_dir / DATE / "digest.json"
    data = json.loads(path.read_text())
    data["items"][2]["title"] = "Qwen3.5-72B <script>alert(1)</script>"
    path.write_text(json.dumps(data))
    html = site.issue_body(site.load_issues(data_dir)[1])
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_source_stats(data_dir):
    stats = export.source_stats(SOURCES, data_dir, site.load_issues(data_dir))
    assert (stats["openai-news"].ok, stats["openai-news"].runs) == (4, 4)  # the 4 issues with candidates
    assert stats["reddit"].ok == 0 and stats["hf-papers"].runs == 0  # failed / disabled
    assert stats["openai-news"].picked == 0  # candidates' source is "blog", not a configured id


def test_export_writes_publishable_issues(tmp_path, data_dir):
    out = tmp_path / "web-data"
    (out / "issues").mkdir(parents=True)
    (out / "issues" / "2026-01-01.json").write_text("{}")  # left over from an issue since removed
    export.export(out, tmp_path / "public", data_dir, SOURCES)
    files = sorted(p.name for p in (out / "issues").iterdir())
    assert files == [f"{OLD}.json", f"{DATE}.json", f"{NEXT}.json"]  # not the invalid issue

    issue = json.loads((out / "issues" / f"{DATE}.json").read_text())
    assert not issue["fallback"] and issue["notice"] is None
    assert issue["description"] == "OpenAI 发布 GPT-6，上下文达到 1M token。"
    sections = {s["id"]: s for s in issue["sections"]}
    assert list(sections) == ["headline", "model", "paper", "tool"]
    assert sections["headline"]["label"] == "头条"

    gpt = sections["headline"]["items"][0]
    assert gpt["title"] == "OpenAI 发布 GPT-6" and not gpt["compact"]
    assert gpt["publisher"] == {
        "name": "OpenAI News",
        "icon": "https://www.google.com/s2/favicons?domain=openai.com&sz=64",
        "host": "openai.com",
    }
    assert gpt["published"] == {"iso": "2026-10-19T12:00:00+00:00", "label": "10月19日 14:00"}  # CEST
    assert gpt["sources"] == [
        {"label": "OpenAI News", "url": "https://openai.com/index/gpt-6/", "discussion": False}
    ]
    assert sections["tool"]["items"][0]["publisher"]["icon"] == "https://github.com/vllm-project.png?size=64"
    qwen = sections["model"]["items"][0]["publisher"]
    assert qwen["name"] == "Qwen" and qwen["icon"].startswith(
        "https://huggingface.co/api/organizations/Qwen/"
    )
    assert sections["paper"]["items"][0]["publisher"]["name"] == "Paper"  # huggingface.co/papers: the source

    fallback_issue = json.loads((out / "issues" / f"{NEXT}.json").read_text())
    assert fallback_issue["fallback"] and fallback_issue["notice"] == site.FALLBACK_NOTICE
    assert all(item["compact"] for s in fallback_issue["sections"] for item in s["items"])


def test_export_beta_issues(tmp_path, data_dir):
    def api(model, title):
        data = _digest(channel="api", model=model)
        data["items"][0]["title"] = title
        return data

    folder = data_dir / DATE
    (folder / "digest.api.deepseek.json").write_text(
        json.dumps(api("nvidia:deepseek-ai/deepseek-v4.1-flash", "DeepSeek 写的 GPT-6"))
    )
    (folder / "digest.api.gemini.json").write_text(
        json.dumps(api("gemini:gemini-3.5-flash-lite", "Gemini 写的"))
    )
    (folder / "digest.api.broken.json").write_text(json.dumps({"mode": "full"}))  # fails validate
    # The fallback issue was replaced by the DeepSeek edit: it is the main issue, not a beta.
    deepseek_main = api("nvidia:deepseek-ai/deepseek-v4.1-flash", "DeepSeek 主版")
    (data_dir / NEXT / "digest.json").write_text(json.dumps({**deepseek_main, "date": NEXT}))
    (data_dir / NEXT / "digest.api.deepseek.json").write_text(json.dumps({**deepseek_main, "date": NEXT}))

    out, public = tmp_path / "web-data", tmp_path / "public"
    export.export(out, public, data_dir, SOURCES)

    main = json.loads((out / "issues" / f"{DATE}.json").read_text())
    assert main["editor"] == "Claude" and main["beta"] is None
    assert main["betas"] == [{"slug": "deepseek", "label": "DeepSeek"}, {"slug": "gemini", "label": "Gemini"}]
    beta = json.loads((out / "beta" / DATE / "deepseek.json").read_text())
    assert beta["editor"] == "deepseek-ai/deepseek-v4.1-flash"
    assert beta["beta"] == {"slug": "deepseek", "label": "DeepSeek"} and beta["betas"] == main["betas"]
    assert beta["sections"][0]["items"][0]["title"] == "DeepSeek 写的 GPT-6"
    assert sorted(p.name for p in (out / "beta" / DATE).iterdir()) == ["deepseek.json", "gemini.json"]

    api_main = json.loads((out / "issues" / f"{NEXT}.json").read_text())
    assert api_main["editor"] == "deepseek-ai/deepseek-v4.1-flash" and api_main["betas"] == []
    assert not (out / "beta" / NEXT).exists()
    assert json.loads((out / "issues" / f"{OLD}.json").read_text())["betas"] == []
    assert "写的" not in (public / "feed.xml").read_text()  # the feed only carries main issues


def test_export_english_issues(tmp_path, data_dir):
    en = _digest(lang="en")
    en["items"][0]["title"] = "OpenAI releases GPT-6"
    en["highlights"] = ["OpenAI releases GPT-6 with a 1M-token context."]
    (data_dir / DATE / "digest.en.json").write_text(json.dumps(en))
    (data_dir / DATE / "digest.api.gemini.json").write_text(
        json.dumps(_digest(channel="api", model="gemini:x"))
    )
    out = tmp_path / "web-data"
    export.export(out, tmp_path / "public", data_dir, SOURCES)
    assert sorted(p.name for p in (out / "en" / "issues").iterdir()) == [
        f"{OLD}.json",
        f"{DATE}.json",
        f"{NEXT}.json",
    ]

    issue = json.loads((out / "en" / "issues" / f"{DATE}.json").read_text())
    assert issue["editor"] == "Claude" and issue["notice"] is None and issue["betas"] == []
    assert issue["description"] == "OpenAI releases GPT-6 with a 1M-token context."
    headline = issue["sections"][0]
    assert headline["label"] == "Headlines"
    assert headline["items"][0]["title"] == "OpenAI releases GPT-6"
    assert headline["items"][0]["published"]["label"] == "Oct 19 14:00"
    assert (
        export._item(
            {"title": "t", "sources": [{"url": "https://news.ycombinator.com/item?id=1"}]}, "brief", {}, "en"
        )["sources"][0]["label"]
        == "HN"
    )

    # Not written yet: the main issue's stories under their original titles, no summaries.
    unwritten = json.loads((out / "en" / "issues" / f"{OLD}.json").read_text())
    assert unwritten["editor"] is None and unwritten["notice"] == export.UNWRITTEN_NOTICE_EN
    items = [item for s in unwritten["sections"] for item in s["items"]]
    by_id = {c["id"]: c for c in CANDIDATES["candidates"]}
    assert items[0]["title"] == by_id[_digest()["items"][0]["sources"][0]["candidate_id"]]["title"]
    assert all(item["compact"] and not item["summary"] for item in items)

    fallback_issue = json.loads((out / "en" / "issues" / f"{NEXT}.json").read_text())
    assert fallback_issue["fallback"] and fallback_issue["notice"] == site.FALLBACK_NOTICE_EN


def test_export_sources(tmp_path, data_dir):
    sources = [*SOURCES, source("github_releases", kind="release", id_="gh", repos=["vllm-project/vllm"])]
    export.export(tmp_path, tmp_path / "public", data_dir, sources)
    data = json.loads((tmp_path / "sources.json").read_text())
    assert data["runs"] == 30
    groups = {g["label"]: g["sources"] for g in data["groups"]}
    assert list(groups) == ["官方博客", "论文", "开源", "社区信号"]  # in display order, empty ones left out
    openai = groups["官方博客"][0]
    assert openai["homepage"] == "https://openai.com/news/" and openai["kind"] == "官方博客 · RSS"
    assert openai["stats"] == {"ok": 4, "runs": 4, "candidates": 1.0, "picked": 0}
    assert openai["repos"] == [] and openai["icon"].endswith("domain=openai.com&sz=64")
    assert groups["社区信号"][0]["homepage"] == "https://www.reddit.com/r/LocalLLaMA/"
    assert groups["社区信号"][0]["stats"]["ok"] == 0
    papers = groups["论文"][0]
    assert not papers["enabled"] and papers["stats"] is None
    gh = groups["开源"][0]
    assert gh["repos"] == ["vllm-project/vllm"] and gh["stats"] is None  # never fetched
    assert gh["homepage"] is None and "domain=github.com" in gh["icon"]

    en = json.loads((tmp_path / "en" / "sources.json").read_text())
    assert [g["label"] for g in en["groups"]] == ["Official blogs", "Papers", "Open source", "Community"]
    assert en["groups"][0]["sources"][0]["kind"] == "Official blog · RSS"
    assert en["groups"][0]["sources"][0]["stats"] == openai["stats"]


def test_export_writes_the_english_feed(tmp_path, data_dir):
    en = _en(generated_at="2026-10-19T22:00:00+00:00")
    en["highlights"] = ["OpenAI releases GPT-6 with a 1M-token context."]
    (data_dir / DATE / "digest.en.json").write_text(json.dumps(en))
    _write_issue(data_dir, "2026-10-10", {**_digest(), "date": "2026-10-10"})  # no English edition yet
    public = tmp_path / "public"
    export.export(tmp_path / "data", public, data_dir, SOURCES, "https://example.github.io/ai-daily")
    channel = ET.parse(public / "feed.en.xml").getroot().find("channel")
    assert channel.findtext("language") == "en" and channel.findtext("title") == "AI Daily"
    items = channel.findall("item")
    assert [i.findtext("link") for i in items] == [  # only written editions and fallbacks
        f"https://example.github.io/ai-daily/en/{NEXT}/",
        f"https://example.github.io/ai-daily/en/{DATE}/",
    ]
    assert items[0].findtext("title").endswith("(fallback)")
    assert items[1].findtext("description") == "OpenAI releases GPT-6 with a 1M-token context."
    assert items[1].findtext("pubDate") == "Mon, 19 Oct 2026 22:00:00 +0000"  # the English edition's
    content = items[1].findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
    assert "<h3>OpenAI releases GPT-6</h3>" in content and "<h2>Headlines</h2>" in content
    assert "#" not in content.replace("&#", "")  # no Chinese tags


def test_export_publisher_skips_discussions():
    item = {
        "section": "headline",
        "title": "x",
        "summary": "y",
        "sources": [
            {"candidate_id": "c_hn", "url": "https://news.ycombinator.com/item?id=2"},
            {"url": "https://github.com/owner/repo"},
        ],
    }
    by_id = {c["id"]: c for c in CANDIDATES["candidates"]}
    data = export._item(item, "headline", by_id)
    assert data["publisher"]["name"] == "owner" and data["published"] is None
    assert [s["discussion"] for s in data["sources"]] == [True, False]


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        (None, None),
        ({"kind": "blog", "published_at": None}, None),
        ({"kind": "discussion", "published_at": "2026-10-19T12:00:00+00:00"}, None),  # when it was posted
        ({"kind": "blog", "published_at": "2026-10-19T00:00:00+00:00"}, "10月19日"),  # a date, not midnight
        (
            {"kind": "paper", "published_at": "2026-10-19T00:00:00+00:00", "published_precision": "day"},
            "10月19日",
        ),
        ({"kind": "release", "published_at": "2026-12-01T23:30:00+00:00"}, "12月2日 00:30"),  # CET
    ],
)
def test_export_published(candidate, expected):
    result = export.published(candidate)
    assert (result and result["label"]) == expected


def test_decide():
    full = _digest(generated_at="2026-10-19T21:40:00+00:00")
    newer = _digest(generated_at="2026-10-19T23:00:00+00:00")
    fb = fallback.build_fallback(CANDIDATES)

    def decide(current, incoming):
        data, reason = publish.decide(copy.deepcopy(current), copy.deepcopy(incoming), CANDIDATES)
        return (data or {}).get("generated_at"), reason

    assert decide(None, full) == (full["generated_at"], "no valid digest yet")
    assert decide({"mode": "full"}, fb)[1] == "no valid digest yet"
    assert decide(fb, full)[1] == "replaces the fallback"
    assert decide(full, fb) == (None, "keeping the edited issue over a fallback")
    assert decide(full, newer)[1] == "newer edit"
    assert decide(newer, full) == (None, "the current edit is newer")
    assert decide(full, full) == (None, "unchanged")
    assert decide(full, {**newer, "date": "2026-10-01"})[0] is None
    assert decide(fb, "invalid JSON: ...")[1].startswith("incoming digest is not valid")


def test_decide_ranks_claude_over_the_api_route():
    api = _digest(generated_at="2026-10-19T23:00:00+00:00", channel="api", model="nvidia:deepseek-v4.1")
    other_api = _digest(generated_at="2026-10-19T23:30:00+00:00", channel="api", model="gemini:g-lite")
    claude = _digest(generated_at="2026-10-19T21:40:00+00:00")  # finished before the API edit
    fb = fallback.build_fallback(CANDIDATES)

    def decide(current, incoming):
        data, reason = publish.decide(copy.deepcopy(current), copy.deepcopy(incoming), CANDIDATES)
        return (data or {}).get("model"), reason

    assert decide(fb, api) == ("nvidia:deepseek-v4.1", "replaces the fallback")
    assert decide(api, claude) == (None, "a Claude edit replaces the API edit")
    assert decide(claude, api) == (None, "keeping the edited issue over an API edit")
    assert decide(api, other_api) == (None, "keeping the edited issue over an API edit")


def test_decide_drops_invalid_items():
    incoming = _digest()
    incoming["items"][1]["summary"] = "新版本速度提升 40%。"
    data, _ = publish.decide(None, incoming, CANDIDATES)
    assert len(data["items"]) == 3 and data["validation"]["dropped"][0]["title"].startswith("vLLM")


def test_cli_adopt(tmp_path):
    data_dir = tmp_path / "data"
    _write_issue(data_dir, DATE)  # fallback on main
    incoming = tmp_path / "incoming.json"
    incoming.write_text(json.dumps(_digest()))
    args = ["adopt", "--date", DATE, "--data-dir", str(data_dir), "--from", str(incoming)]
    assert cli.main(args) == 0
    assert json.loads((data_dir / DATE / "digest.json").read_text())["mode"] == "full"
    assert "OpenAI 发布 GPT-6" in (data_dir / DATE / "digest.md").read_text()

    incoming.write_text(json.dumps(fallback.build_fallback(CANDIDATES)))
    assert cli.main(args) == 0
    assert json.loads((data_dir / DATE / "digest.json").read_text())["mode"] == "full"


def _en(**overrides):
    en = _digest(lang="en", **overrides)
    en["items"][0]["title"] = "OpenAI releases GPT-6"
    return en


def test_decide_en_goes_with_the_main_issue():
    claude, api = _digest(), _digest(channel="api", model="gemini:x")
    fb = fallback.build_fallback(CANDIDATES)

    def decide(main, current, incoming):
        data, reason = publish.decide_en(main, current, copy.deepcopy(incoming), CANDIDATES)
        return data is not None, reason

    assert decide(claude, None, _en()) == (True, "English edition of the main issue")
    assert decide(claude, None, _digest()) == (False, "incoming digest is not an English edition")
    assert decide(None, None, _en()) == (False, "no main issue to go with")
    assert decide(fb, None, _en()) == (False, "the main issue is a fallback")
    assert decide(api, None, _en()) == (False, "the main issue comes from the other route")
    assert decide(api, None, _en(channel="api", model="gemini:x"))[0]
    assert decide(api, None, _en(channel="api", model="nvidia:y")) == (
        False,
        "the main issue comes from another model",
    )

    older = _en(generated_at="2026-10-19T21:40:00+00:00")
    newer = _en(generated_at="2026-10-19T22:00:00+00:00")
    assert decide(claude, newer, older) == (False, "the current English edition is newer")
    assert decide(claude, older, newer)[0]
    # The API route's English edition, left after a Claude edit replaced its main issue.
    assert decide(claude, _en(channel="api", model="gemini:x"), older)[0]


def test_english_limits():
    en = _en()
    en["items"][0]["title"] = "OpenAI releases GPT-6, " + "x" * 80  # too long in Chinese, fine in English
    assert digest.validate(en, CANDIDATES).ok
    assert 0 in digest.validate({**en, "lang": "zh"}, CANDIDATES).item_errors
    assert digest.validate({**en, "lang": "fr"}, CANDIDATES).errors == ["lang must be one of ('zh', 'en')"]


def test_cli_adopt_en(tmp_path):
    data_dir = tmp_path / "data"
    _write_issue(data_dir, DATE, _digest())
    incoming = tmp_path / "incoming.json"
    incoming.write_text(json.dumps(_en()))
    args = ["adopt", "--date", DATE, "--data-dir", str(data_dir), "--from", str(incoming), "--en"]
    assert cli.main(args) == 0
    assert json.loads((data_dir / DATE / "digest.en.json").read_text())["lang"] == "en"
    assert (
        json.loads((data_dir / DATE / "digest.json").read_text())["items"][0]["title"] == "OpenAI 发布 GPT-6"
    )

    assert cli.main(["validate", "--date", DATE, "--data-dir", str(data_dir), "--en"]) == 0
    (data_dir / DATE / "digest.en.json").write_text(json.dumps(_digest()))
    assert cli.main(["validate", "--date", DATE, "--data-dir", str(data_dir), "--en"]) == 1


def test_english_edition_of_the_other_route_is_not_shown(data_dir):
    (data_dir / DATE / "digest.en.json").write_text(json.dumps(_en(channel="api", model="gemini:x")))
    issue = next(i for i in site.load_issues(data_dir) if i.slug == DATE)
    assert issue.en is None


def test_cli_export(tmp_path, data_dir, monkeypatch):
    out, public = tmp_path / "data", tmp_path / "public"
    args = ["export", "--data-dir", str(data_dir), "--out", str(out), "--public", str(public)]
    assert cli.main(args) == 0
    assert site.DEFAULT_BASE_URL in (public / "feed.xml").read_text()
    monkeypatch.setenv("SITE_URL", "http://localhost:8000/")
    assert cli.main(args) == 0
    assert f"http://localhost:8000/{NEXT}/" in (public / "feed.xml").read_text()
