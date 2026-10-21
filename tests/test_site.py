import copy
import json
import xml.etree.ElementTree as ET

import pytest

from daily import cli, fallback, publish, site
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
        {"id": "arxiv", "status": "disabled", "count": 0, "seconds": 0.0, "error": None},
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
    source("rss", kind="paper", id_="arxiv", url="https://rss.arxiv.org/rss/cs.CL"),
]
SOURCES[2].enabled = False


def test_build_writes_the_whole_site(tmp_path, data_dir):
    out = tmp_path / "site"
    issues = site.build(out, data_dir, SOURCES, "https://example.github.io/ai-daily")
    assert [i.slug for i in issues] == [NEXT, DATE, OLD]  # the invalid issue is left out
    for page in ["index.html", f"{DATE}/index.html", f"{NEXT}/index.html", "archive/index.html"]:
        assert (out / page).exists(), page
    assert (out / "sources/index.html").exists() and (out / "style.css").read_text()

    index = (out / "index.html").read_text()
    assert "降级版" in index and site.FALLBACK_NOTICE in index  # latest issue, in full
    assert f'href="{DATE}/"' in index and OLD not in index  # last 30 days only
    assert f'href="../{OLD}/"' in (out / "archive/index.html").read_text()

    page = (out / DATE / "index.html").read_text()
    assert "OpenAI 发布 GPT-6" in page and 'href="https://openai.com/index/gpt-6/"' in page
    assert f'href="../{NEXT}/"' in page and f'href="../{OLD}/"' in page  # newer / older
    assert "降级版" not in page and "#模型" in page

    with pytest.raises(ValueError):
        site.build(data_dir, data_dir, SOURCES)  # never wipes a directory that is not a site build
    site.build(out, data_dir, SOURCES)  # rebuilding over the previous build is fine


def test_feed_has_full_text_and_mode_in_guid(tmp_path, data_dir):
    out = tmp_path / "site"
    site.build(out, data_dir, SOURCES, "https://example.github.io/ai-daily/")
    channel = ET.parse(out / "feed.xml").getroot().find("channel")
    items = channel.findall("item")
    assert [i.findtext("link") for i in items] == [
        f"https://example.github.io/ai-daily/{NEXT}/",
        f"https://example.github.io/ai-daily/{DATE}/",
    ]
    assert items[0].findtext("guid").endswith("#fallback") and "降级版" in items[0].findtext("title")
    content = items[1].findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
    assert "<h3>OpenAI 发布 GPT-6</h3>" in content and "GPT-6 支持 1M token 上下文" in content
    assert items[1].findtext("pubDate") == "Mon, 19 Oct 2026 21:40:00 +0000"


def test_text_is_escaped(tmp_path, data_dir):
    path = data_dir / DATE / "digest.json"
    data = json.loads(path.read_text())
    data["items"][2]["title"] = "Qwen3.5-72B <script>alert(1)</script>"
    path.write_text(json.dumps(data))
    html = site.issue_page(site.load_issues(data_dir)[1], None, None)
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_sources_page_cards(data_dir):
    html = site.sources_page(SOURCES, data_dir, site.load_issues(data_dir))
    assert '<a href="https://openai.com/news/">openai-news</a>' in html
    assert 'href="https://www.reddit.com/r/LocalLLaMA/"' in html
    assert "<dd>4/4</dd>" in html  # openai-news ran in the 4 issues with candidates
    assert "最近一次抓取失败：HTTPStatusError: 429" in html
    assert 'class="card disabled"' in html and "已停用" in html
    stats = site.source_stats(SOURCES, data_dir, site.load_issues(data_dir))
    assert stats["openai-news"].picked == 0  # candidates' source is "blog", not a configured id


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


def test_cli_build(tmp_path, data_dir):
    out = tmp_path / "out"
    assert cli.main(["build", "--data-dir", str(data_dir), "--out", str(out)]) == 0
    assert site.DEFAULT_BASE_URL in (out / "feed.xml").read_text()
