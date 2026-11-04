import copy
import json

import httpx
import pytest

from daily import api_editor, cli, dedup, digest, fallback, render
from daily.digest import Page
from tests.conftest import ISSUE, mock_client

DATE = ISSUE.isoformat()


def _candidate(id_, kind, title, url, summary="", tier=1, **extra):
    return {
        "id": id_,
        "source": extra.pop("source", kind),
        "source_name": extra.pop("source_name", kind.title()),
        "tier": tier,
        "kind": kind,
        "title": title,
        "url": url,
        "summary": summary,
        "published_at": "2026-10-19T12:00:00+00:00",
        "discussion_url": extra.pop("discussion_url", None),
        "signals": extra.pop("signals", {}),
        "tags": [],
        "cluster_id": extra.pop("cluster_id", "k_" + id_),
        "also_from": extra.pop("also_from", []),
        "seen_on": extra.pop("seen_on", []),
        "reported_on": extra.pop("reported_on", []),
    }


CANDIDATES = {
    "date": DATE,
    "candidates": [
        _candidate(
            "c_gpt",
            "blog",
            "Introducing GPT-6",
            "https://openai.com/index/gpt-6/",
            "GPT-6 has a 1M token context window and costs $2 per million input tokens.",
            source_name="OpenAI News",
            also_from=[
                {
                    "source": "hackernews",
                    "url": "https://openai.com/index/gpt-6",
                    "title": "GPT-6",
                    "discussion_url": "https://news.ycombinator.com/item?id=1",
                }
            ],
            signals={"hn_points": 812},
        ),
        _candidate(
            "c_vllm",
            "release",
            "vllm-project/vllm v0.12.0",
            "https://github.com/vllm-project/vllm/releases/tag/v0.12.0",
            "Adds GPT-6 support and speculative decoding for Qwen3.5.",
        ),
        _candidate(
            "c_qwen",
            "model",
            "Qwen/Qwen3.5-72B",
            "https://huggingface.co/Qwen/Qwen3.5-72B",
            "text-generation, transformers, license:apache-2.0",
            signals={"trending_rank": 1},
        ),
        _candidate(
            "c_paper",
            "paper",
            "Scaling Laws for Agents",
            "https://huggingface.co/papers/2610.00001",
            "We study eight agent benchmarks and find a 2.5x gain.",
            signals={"upvotes": 120},
        ),
        _candidate(
            "c_hn",
            "discussion",
            "Ask HN: Is anyone using MCP in prod?",
            "https://news.ycombinator.com/item?id=2",
            tier=2,
            discussion_url="https://news.ycombinator.com/item?id=2",
            signals={"hn_points": 300},
        ),
    ],
}


def _item(section, title, summary, *cids, **extra):
    return {
        "section": section,
        "title": title,
        "summary": summary,
        "sources": [{"candidate_id": c} for c in cids],
        "tags": extra.pop("tags", ["模型"]),
        **extra,
    }


def _digest(**overrides):
    data = {
        "schema_version": 1,
        "date": DATE,
        "mode": "full",
        "highlights": ["OpenAI 发布 GPT-6，上下文达到 1M token。"],
        "items": [
            _item(
                "headline",
                "OpenAI 发布 GPT-6",
                "GPT-6 支持 1M token 上下文，输入价格每百万 token 2 美元。",
                "c_gpt",
            ),
            _item(
                "tool", "vLLM v0.12.0 支持 GPT-6", "新版本加入 GPT-6 支持和 Qwen3.5 的投机解码。", "c_vllm"
            ),
            _item("model", "Qwen3.5-72B 开源", "Apache-2.0 许可，位列 HF 趋势榜第 1。", "c_qwen"),
            _item(
                "paper",
                "智能体的 Scaling Law",
                "在 8 个智能体基准上研究扩展规律，带来 2.5 倍提升。",
                "c_paper",
            ),
        ],
        "research": [],
    }
    data.update(overrides)
    return copy.deepcopy(data)


def _errors(report, index):
    return " | ".join(report.item_errors.get(index, []))


def test_valid_digest_passes_and_fills_in_candidate_urls():
    data = _digest()
    report = digest.validate(data, CANDIDATES)
    assert report.ok, (report.errors, report.item_errors)
    assert data["items"][0]["sources"][0]["url"] == "https://openai.com/index/gpt-6/"
    assert any("items" in w for w in report.warnings)  # 4 items, fewer than the target


def test_unknown_or_foreign_sources_are_rejected():
    data = _digest()
    data["items"][0]["sources"] = [{"candidate_id": "c_nope"}]
    data["items"][1]["sources"] = [{"candidate_id": "c_vllm", "url": "https://example.com/elsewhere"}]
    data["items"][2]["sources"].append({"url": "https://qwenlm.github.io/blog/qwen3.5/"})
    report = digest.validate(data, CANDIDATES)
    assert "unknown candidate_id" in _errors(report, 0)
    assert "not a link of candidate" in _errors(report, 1)
    assert "neither a candidate nor a page recorded as opened" in _errors(report, 2)


def test_opened_pages_and_candidate_urls_count_as_sources():
    data = _digest(research=[{"url": "https://qwenlm.github.io/blog/qwen3.5/", "via": "webfetch"}])
    data["items"][2]["sources"].append({"url": "https://qwenlm.github.io/blog/qwen3.5"})
    data["items"][3]["sources"] = [
        {"url": "https://huggingface.co/papers/2610.00001"}
    ]  # candidate url, no id
    data["items"][0]["sources"].append(
        {"candidate_id": "c_gpt", "url": "https://news.ycombinator.com/item?id=1"}
    )
    assert digest.validate(data, CANDIDATES).ok


def test_discussion_threads_are_not_first_hand():
    data = _digest()
    data["items"].append(_item("brief", "有人在生产环境用 MCP 吗", "HN 上 300 分的讨论。", "c_hn"))
    report = digest.validate(data, CANDIDATES)
    assert "first-hand" in _errors(report, 4)


@pytest.mark.parametrize(
    "summary, problem",
    [
        ("GPT-6 支持 2M token 上下文。", "number 2M"),
        ("GPT-6 支持 1M token 上下文，比 GPT-5.5 快 3 倍。", "GPT-5.5"),
        ("访问 https://openai.com 了解更多。", "URLs"),
    ],
)
def test_facts_must_come_from_the_material(summary, problem):
    data = _digest()
    data["items"][0]["summary"] = summary
    report = digest.validate(data, CANDIDATES)
    errors = _errors(report, 0)
    assert errors
    if problem == "number 2M":
        assert "'2M'" in errors
    elif problem == "GPT-5.5":
        assert "'GPT-5.5'" in errors and "number 3 " in errors + " "
    else:
        assert "URLs" in errors


def test_evidence_quotes_extend_the_material():
    data = _digest()
    data["items"][0]["summary"] = "GPT-6 支持 1M token 上下文，在 SWE-bench 上得分 74.9%。"
    assert "74.9" in _errors(digest.validate(copy.deepcopy(data), CANDIDATES), 0)
    data["items"][0]["evidence"] = [
        {"url": "https://openai.com/index/gpt-6/", "quote": "GPT-6 scores 74.9% on SWE-bench."}
    ]
    assert digest.validate(data, CANDIDATES).ok


def test_evidence_must_cite_one_of_the_item_sources():
    data = _digest()
    data["items"][0]["evidence"] = [{"url": "https://example.com/", "quote": "anything"}]
    assert "not one of the item's sources" in _errors(digest.validate(data, CANDIDATES), 0)


def test_number_words_in_english_count():
    data = _digest()
    assert "8 个" in data["items"][3]["summary"]  # "eight agent benchmarks"
    assert digest.validate(data, CANDIDATES).ok


def test_the_same_candidate_cannot_be_used_twice():
    data = _digest()
    data["items"].append(_item("brief", "GPT-6 上线", "OpenAI 发布 GPT-6。", "c_gpt"))
    report = digest.validate(data, CANDIDATES)
    assert "already used by item 1" in _errors(report, 4)


def test_too_few_surviving_items_fails_the_whole_digest():
    data = _digest()
    for item in data["items"][1:]:
        item["sources"] = [{"candidate_id": "c_nope"}]
    report = digest.validate(data, CANDIDATES)
    assert any("only 1 valid items" in e for e in report.errors)


def test_highlights_may_only_repeat_published_facts():
    data = _digest(highlights=["GPT-6 发布，上下文 1M token，价格降低 50%。"])
    report = digest.validate(data, CANDIDATES)
    assert any("highlight" in e and "50" in e for e in report.errors)


def test_document_level_problems():
    report = digest.validate(_digest(date="2026-01-01", mode="draft"), CANDIDATES)
    joined = " | ".join(report.errors)
    assert "does not match candidates" in joined and "mode" in joined
    assert any("highlights" in e for e in digest.validate(_digest(highlights=[]), CANDIDATES).errors)


def test_online_checks():
    data = _digest()
    data["items"][0]["evidence"] = [
        {"url": "https://openai.com/index/gpt-6/", "quote": "Available today in the API."}
    ]
    data["items"][3]["evidence"] = [
        {"url": "https://huggingface.co/papers/2610.00001", "quote": "A brand new result."}
    ]
    digest.validate(data, CANDIDATES)  # fills in urls
    pages = {
        "https://openai.com/index/gpt-6/": Page(
            200, text=digest.page_text("<p>GPT-6 is <b>available today</b> in the API.</p>")
        ),
        "https://github.com/vllm-project/vllm/releases/tag/v0.12.0": Page(404),
        "https://huggingface.co/Qwen/Qwen3.5-72B": Page(403),
        "https://huggingface.co/papers/2610.00001": Page(200, text="Something else entirely"),
    }
    report = digest.validate(data, CANDIDATES, pages)
    assert 0 not in report.item_errors
    assert "broken link (404)" in _errors(report, 1)
    assert 2 not in report.item_errors and any("could not check" in w for w in report.warnings)
    assert "quote not found" in _errors(report, 3)


async def test_check_links_reads_page_text():
    routes = {
        "a.example/post": httpx.Response(
            200,
            html=(
                "<script>var x = 'hidden';</script><!-- it's a comment -->"
                '<nav>Menu</nav><div data-props="{&quot;t&quot;:&quot;<|im_start|>secret&quot;}"></div>'
                "<main><p>Hello &amp; welcome</p></main><article>Card</article>"
            ),
        ),
        "a.example/paper.pdf": httpx.Response(
            200, content=b"%PDF", headers={"content-type": "application/pdf"}
        ),
    }
    async with mock_client(routes) as client:
        pages = await digest.check_links(
            ["https://a.example/post", "https://a.example/paper.pdf", "https://a.example/gone"], client
        )
    assert "Hello & welcome" in pages["https://a.example/post"].text
    for hidden in ("hidden", "comment", "secret"):  # script, comment, an attribute holding a ">"
        assert hidden not in pages["https://a.example/post"].text
    assert pages["https://a.example/post"].body.strip() == "Hello & welcome"  # the longest main / article
    assert (
        pages["https://a.example/paper.pdf"].status == 200
        and pages["https://a.example/paper.pdf"].text is None
    )
    assert pages["https://a.example/gone"].status == 404


def test_apply_report_drops_and_records():
    data = _digest()
    data["items"][1]["sources"] = [{"candidate_id": "c_nope"}]
    report = digest.validate(data, CANDIDATES)
    result = digest.apply_report(data, report, checked_links=False)
    assert [i["title"] for i in result["items"]] == [
        "OpenAI 发布 GPT-6",
        "Qwen3.5-72B 开源",
        "智能体的 Scaling Law",
    ]
    assert result["validation"]["dropped"][0]["title"] == "vLLM v0.12.0 支持 GPT-6"
    assert digest.validate(result, CANDIDATES).ok  # idempotent


def test_fallback_is_valid_and_skips_reported_and_clustered_candidates():
    candidates = copy.deepcopy(CANDIDATES)
    candidates["candidates"] += [
        _candidate(
            "c_old",
            "paper",
            "Yesterday's paper",
            "https://huggingface.co/papers/2610.00002",
            signals={"upvotes": 999},
            reported_on=[{"date": "2026-10-12", "title": "以前报道过的论文"}],
        ),
        _candidate(
            "c_dup",
            "paper",
            "Scaling Laws for Agents (v2)",
            "https://huggingface.co/papers/2610.00003",
            signals={"upvotes": 50},
            cluster_id="k_c_paper",
        ),
        _candidate(
            "c_p3",
            "paper",
            "Another paper",
            "https://huggingface.co/papers/2610.00004",
            signals={"upvotes": 10},
        ),
    ]
    data = fallback.build_fallback(candidates)
    report = digest.validate(data, candidates)
    assert report.ok, report.item_errors
    papers = [i["sources"][0]["candidate_id"] for i in data["items"] if i["section"] == "paper"]
    assert papers == ["c_paper", "c_p3"]
    assert [i["section"] for i in data["items"]] == [
        "headline",
        "model",
        "paper",
        "paper",
        "tool",
    ]  # Ask HN skipped


def _fallback_papers(*papers):
    candidates = {"date": DATE, "candidates": list(papers)}
    data = fallback.build_fallback(candidates)
    return [i["sources"][0]["candidate_id"] for i in data["items"] if i["section"] == "paper"]


def test_fallback_ranks_by_reported_on_not_seen_on():
    # Listed yesterday but never reported: still news, so its heat decides.
    seen = _candidate(
        "c_seen",
        "paper",
        "Seen paper",
        "https://huggingface.co/papers/2610.00011",
        signals={"upvotes": 99},
        seen_on=["2026-10-19"],
    )
    fresh = _candidate(
        "c_fresh", "paper", "Fresh paper", "https://huggingface.co/papers/2610.00012", signals={"upvotes": 1}
    )
    assert _fallback_papers(fresh, seen) == ["c_seen", "c_fresh"]


def test_fallback_uses_reported_candidates_only_when_nothing_else_is_left():
    reported = _candidate(
        "c_reported",
        "paper",
        "Reported paper",
        "https://huggingface.co/papers/2610.00013",
        signals={"upvotes": 99},
        reported_on=[{"date": "2026-10-12", "title": "以前报道过的论文"}],
    )
    fresh = _candidate(
        "c_fresh", "paper", "Fresh paper", "https://huggingface.co/papers/2610.00014", signals={"upvotes": 1}
    )
    assert _fallback_papers(reported, fresh) == ["c_fresh", "c_reported"]


def test_fallback_reads_candidates_without_reported_on():
    # Issues fetched before reported_on existed don't have the field.
    old = _candidate("c_old", "paper", "Old paper", "https://huggingface.co/papers/2610.00015")
    del old["reported_on"]
    assert _fallback_papers(old) == ["c_old"]


def test_render_markdown():
    data = _digest()
    digest.validate(data, CANDIDATES)
    data["items"][0]["sources"].append(
        {"candidate_id": "c_gpt", "url": "https://news.ycombinator.com/item?id=1"}
    )
    text = render.to_markdown(data, CANDIDATES)
    assert text.startswith(f"# {DATE} · AI 科技日报")
    assert "## 今日要点" in text and "## 🔥 头条" in text and "### OpenAI 发布 GPT-6" in text
    assert (
        "[OpenAI News](https://openai.com/index/gpt-6/) · [HN 讨论](https://news.ycombinator.com/item?id=1)"
        in text
    )
    assert text.index("头条") < text.index("模型") < text.index("论文") < text.index("开源与工具")
    assert "降级版" in render.to_markdown(fallback.build_fallback(CANDIDATES), CANDIDATES)


def test_published_urls_ignore_research():
    data = _digest(research=[{"url": "https://example.com/read-but-not-published", "via": "webfetch"}])
    digest.validate(data, CANDIDATES)
    assert "https://example.com/read-but-not-published" not in digest.published_urls(data)
    assert "https://openai.com/index/gpt-6/" in digest.published_urls(data)


@pytest.fixture
def issue_dir(tmp_path):
    folder = tmp_path / DATE
    folder.mkdir()
    (folder / "candidates.json").write_text(json.dumps(CANDIDATES))
    return folder


def _run(issue_dir, *args):
    return cli.main([*args, "--date", DATE, "--data-dir", str(issue_dir.parent)])


def test_cli_validate_drop_invalid(issue_dir):
    data = _digest()
    data["items"][1]["summary"] = "新版本速度提升 40%。"
    (issue_dir / "digest.json").write_text(json.dumps(data))
    assert _run(issue_dir, "validate") == 1
    assert _run(issue_dir, "validate", "--drop-invalid") == 0
    written = json.loads((issue_dir / "digest.json").read_text())
    assert len(written["items"]) == 3 and written["validation"]["dropped"][0]["reasons"]
    assert _run(issue_dir, "validate") == 0


def test_cli_validate_check_links(issue_dir, monkeypatch):
    (issue_dir / "digest.json").write_text(json.dumps(_digest()))
    routes = {
        "openai.com/index/gpt-6/": "<p>GPT-6</p>",
        "github.com/vllm-project/vllm/releases/tag/v0.12.0": httpx.Response(404),
        "huggingface.co/Qwen/Qwen3.5-72B": "ok",
        "huggingface.co/papers/2610.00001": "ok",
    }
    monkeypatch.setattr(cli.pipeline, "make_client", lambda: mock_client(routes))
    assert _run(issue_dir, "validate", "--check-links", "--drop-invalid") == 0
    written = json.loads((issue_dir / "digest.json").read_text())
    assert written["validation"]["checked_links"] is True
    assert "broken link" in written["validation"]["dropped"][0]["reasons"][0]


def test_cli_degrade(issue_dir):
    path = issue_dir / "digest.json"
    path.write_text(json.dumps(_digest()))
    assert _run(issue_dir, "degrade") == 0
    assert json.loads(path.read_text())["mode"] == "full"  # valid digest is kept

    path.write_text("{not json")
    assert _run(issue_dir, "degrade") == 0
    assert json.loads(path.read_text())["mode"] == "fallback"
    assert (issue_dir / "digest.rejected.json").read_text() == "{not json"

    assert _run(issue_dir, "render") == 0
    assert "降级版" in (issue_dir / "digest.md").read_text()


def test_cli_missing_candidates(tmp_path):
    assert cli.main(["validate", "--date", DATE, "--data-dir", str(tmp_path)]) == 1


def test_history_counts_only_published_items(tmp_path):
    day = tmp_path / "2026-10-19"
    day.mkdir()
    data = _digest(research=[{"url": "https://example.com/background", "via": "webfetch"}])
    digest.validate(data, CANDIDATES)
    (day / "digest.json").write_text(json.dumps(data))
    history = dedup.load_history(tmp_path, ISSUE)
    assert "openai.com/index/gpt-6" in history.published
    assert not any("example.com" in key for key in history.published)


def test_render_labels_repeated_sources_by_candidate_title():
    candidates = copy.deepcopy(CANDIDATES)
    candidates["candidates"].append(
        _candidate(
            "c_qwen2",
            "model",
            "Qwen/Qwen3.5-7B",
            "https://huggingface.co/Qwen/Qwen3.5-7B",
            source_name="Model",
        )
    )
    candidates["candidates"][2]["source_name"] = "Model"
    data = _digest()
    data["items"][2]["sources"].append({"candidate_id": "c_qwen2"})
    digest.validate(data, candidates)
    text = render.to_markdown(data, candidates)
    assert "[Qwen/Qwen3.5-72B](https://huggingface.co/Qwen/Qwen3.5-72B) · [Qwen/Qwen3.5-7B]" in text


def test_cli_page_prints_verbatim_context(monkeypatch, capsys):
    routes = {"a.example/post": httpx.Response(200, html="<p>It <b>achieves</b> sub-500ms   latency.</p>")}
    monkeypatch.setattr(cli.pipeline, "make_client", lambda: mock_client(routes))
    assert cli.main(["page", "https://a.example/post", "--grep", "500ms", "--context", "20"]) == 0
    out = capsys.readouterr().out
    assert "1 match(es)" in out and "It achieves sub-500ms latency." in out
    assert cli.main(["page", "https://a.example/gone", "--grep", "x"]) == 1


# --- #51: the item targets, V1-V3, A7 ---------------------------------------------------------


def _many(count, candidates=None):
    """A digest of count clean brief items, and the candidates behind them."""
    candidates = copy.deepcopy(candidates or CANDIDATES)
    items = []
    for n in range(count):
        cid = f"c_brief{n}"
        url = f"https://example.com/post/{n}"
        candidates["candidates"].append(_candidate(cid, "blog", "A post", url))
        items.append(_item("brief", "一篇文章", "一篇文章。", cid))
    return _digest(items=items, highlights=["今天有一篇文章。"]), candidates


@pytest.mark.parametrize("count, warned", [(7, True), (8, False), (15, False), (18, False), (19, True)])
def test_item_counts_outside_the_target_only_warn(count, warned):
    data, candidates = _many(count)
    report = digest.validate(data, candidates)
    assert not report.item_errors and not report.errors  # nothing is dropped, however many there are
    assert any(w.startswith(f"{count} items") for w in report.warnings) is warned


def test_too_few_items_warns_that_a_source_may_be_missing():
    data, candidates = _many(7)
    (warning,) = [w for w in digest.validate(data, candidates).warnings if w.startswith("7 items")]
    assert "信源漏抓" in warning


def test_targets_match_the_spec():
    assert digest.ITEMS_TARGET == (8, 18) and digest.ITEMS_EXPECTED == 15
    assert digest.SECTION_TARGETS == {"headline": (3, 5), "paper": (2, 4)}  # no limit on briefs
    assert digest.BUDGET == {"webfetch": 30, "websearch": 5}


def test_section_targets_only_warn():
    data = _digest()
    report = digest.validate(data, CANDIDATES)
    assert report.ok
    assert any("headline items" in w for w in report.warnings)  # 1 headline, target 3-5


def test_the_skill_states_the_same_targets():
    skill = api_editor.SKILL_FILE.read_text(encoding="utf-8")
    low, high = digest.ITEMS_TARGET
    assert f"{digest.ITEMS_EXPECTED} 条" in skill and f"{high} 条" in skill and f"{low} 条" in skill
    assert "8–12" not in skill and "12 条" not in skill
    assert f"WebFetch 最多 {digest.BUDGET['webfetch']} 次" in skill
    assert f"{digest.BUDGET['webfetch']} 次的预算" in skill


@pytest.mark.parametrize(
    "url",
    [
        "https://i.redd.it/cdh8dfe7dyyh1.png",
        "https://v.redd.it/6ssijtngz2zh1",
        "https://x.com/someone/status/1",
        "https://twitter.com/someone/status/1",
        "https://www.reddit.com/r/LocalLLaMA/comments/1/x/",
        "https://news.ycombinator.com/item?id=2",
    ],
)
def test_images_videos_and_tweets_are_not_first_hand(url):
    candidates = copy.deepcopy(CANDIDATES)
    candidates["candidates"].append(_candidate("c_post", "discussion", "A post", url, tier=2))
    data = _digest()
    data["items"].append(_item("brief", "一条帖子", "一条帖子。", "c_post"))
    assert "first-hand" in _errors(digest.validate(data, candidates), 4)


def test_hosts_that_merely_end_alike_are_first_hand():
    assert not digest.is_discussion("https://netflix.com/post", None)
    assert not digest.is_discussion("https://github.com/a/b", None)


def _quoted(url_quote, summary="GPT-6 支持 1M token 上下文，在 SWE-bench 上得分 74.9%。"):
    data = _digest()
    data["items"][0]["summary"] = summary
    data["items"][0]["evidence"] = [{"url": url_quote, "quote": "GPT-6 scores 74.9% on SWE-bench."}]
    digest.validate(data, CANDIDATES)  # fills in urls
    return data


@pytest.mark.parametrize(
    "page",
    [Page(403), Page(None, error="ConnectError: refused"), Page(200, text=None)],  # 200: a PDF
    ids=["403", "unreachable", "no text"],
)
def test_quotes_from_a_page_that_cannot_be_read_support_no_facts(page):
    url = "https://openai.com/index/gpt-6/"
    report = digest.validate(_quoted(url), CANDIDATES, {url: page})
    assert "74.9" in _errors(report, 0)
    assert any("unverified" in w for w in report.warnings)


def test_a_fact_from_the_candidate_survives_a_page_that_cannot_be_read():
    url = "https://openai.com/index/gpt-6/"
    data = _quoted(url, summary="GPT-6 支持 1M token 上下文。")  # in the candidate's summary
    assert 0 not in digest.validate(data, CANDIDATES, {url: Page(403)}).item_errors


def test_quotes_found_on_a_readable_page_support_facts():
    url = "https://openai.com/index/gpt-6/"
    page = Page(200, text="Today GPT-6 scores 74.9% on SWE-bench. Try it.")
    assert 0 not in digest.validate(_quoted(url), CANDIDATES, {url: page}).item_errors


def test_offline_validate_still_counts_quotes():
    assert 0 not in digest.validate(_quoted("https://openai.com/index/gpt-6/"), CANDIDATES).item_errors


@pytest.mark.parametrize(
    "text, material, problems",
    [
        ("升级到 PyTorch 2.14", "PyTorch 2.14.0", []),  # a version's prefix
        ("升级到 v2.14", "v2.14.0", []),
        ("版本 1.2.3", "1.2.3.4", []),
        ("提升 2 倍", "PyTorch 2.14.0", ["number 2 "]),  # the prefix is a version, not any number
        ("提升 3 倍", "cost is 3.5 dollars", ["number 3 "]),
        ("版本 2.15", "PyTorch 2.14.0", ["number 2.15"]),
        ("a 763B-parameter model", "763B params", []),
        ("a 6.8T-parameter model", "6.8T params", []),
        ("a 32-bit build", "32 bit", []),
        ("a 764B-parameter model", "763B params", ["'764B'", "number 764"]),
        # Names keep every part: only a leading number is cut from the word after it.
        ("GPT-6", "GPT-5 and 6 others", ["'GPT-6'"]),
        ("DeepSeek-V4-Flash", "DeepSeek-V4-Pro", ["'DeepSeek-V4-Flash'"]),
        ("Qwen3.5-72B", "Qwen3.5-7B and 72 others", ["'Qwen3.5-72B'"]),
    ],
)
def test_fact_tokens(text, material, problems):
    errors = " | ".join(digest._check_facts(text, [material])) + " "
    for problem in problems:
        assert problem in errors
    if not problems:
        assert errors == " "


def _paper_item(cid="c_gpt", **extra):
    return _item("paper", "一篇文章", "一篇文章。", cid, **extra)


@pytest.mark.parametrize(
    "url",
    [
        "https://arxiv.org/abs/2610.00009",
        "https://www.arxiv.org/pdf/2610.00009",
        "https://huggingface.co/papers/2610.00009",
        "https://openreview.net/forum?id=abc",
    ],
)
def test_paper_section_accepts_paper_links_of_any_kind(url):
    candidates = copy.deepcopy(CANDIDATES)
    candidates["candidates"].append(_candidate("c_link", "discussion", "A paper", url, tier=2))
    data = _digest()
    data["items"].append(_paper_item("c_link"))
    assert 4 not in digest.validate(data, candidates).item_errors


def test_paper_section_needs_a_paper_as_its_main_source():
    data = _digest()
    data["items"][3] = _paper_item()  # c_gpt is a blog post
    assert "paper" in _errors(digest.validate(data, CANDIDATES), 3)


def test_paper_section_looks_at_the_main_source_only():
    data = _digest()
    del data["items"][1]
    data["items"][2]["sources"] = [{"candidate_id": "c_vllm"}, {"candidate_id": "c_paper"}]
    assert "paper" in _errors(digest.validate(data, CANDIDATES), 2)
    data = _digest()
    del data["items"][1]  # c_vllm's own item
    data["items"][2]["sources"] = [{"candidate_id": "c_paper"}, {"candidate_id": "c_vllm"}]
    assert 2 not in digest.validate(data, CANDIDATES).item_errors


def test_paper_section_rejects_lookalike_hugging_face_pages():
    candidates = copy.deepcopy(CANDIDATES)
    candidates["candidates"].append(
        _candidate("c_hf", "model", "A model", "https://huggingface.co/acme/papers")
    )
    data = _digest()
    data["items"].append(_paper_item("c_hf"))
    assert "paper" in _errors(digest.validate(data, candidates), 4)


def _trace_file(issue_dir, steps):
    record = {"schema_version": 1, "date": DATE, "channel": "claude", "scores": {}, "steps": steps}
    (issue_dir / "trace.claude.json").write_text(json.dumps(record))


def test_cli_validate_warns_without_a_self_check(issue_dir, capsys):
    (issue_dir / "digest.json").write_text(json.dumps(_digest()))
    assert _run(issue_dir, "validate") == 0
    assert "WARN  no self_check" in capsys.readouterr().err

    _trace_file(issue_dir, [{"step": "self_check", "at": "x", "items": []}])
    assert _run(issue_dir, "validate") == 0
    assert "self_check" not in capsys.readouterr().err  # an empty list counts: it was done


def test_cli_validate_only_asks_the_claude_routes_main_issue_for_a_self_check(issue_dir, capsys):
    (issue_dir / "digest.json").write_text(json.dumps(_digest(channel="api", model="nvidia:a/b")))
    assert _run(issue_dir, "validate") == 0
    assert "self_check" not in capsys.readouterr().err

    (issue_dir / "digest.json").write_text(json.dumps(fallback.build_fallback(CANDIDATES)))
    assert _run(issue_dir, "validate") == 0
    assert "self_check" not in capsys.readouterr().err

    (issue_dir / "digest.en.json").write_text(json.dumps(_digest(lang="en")))
    _run(issue_dir, "validate", "--en")
    assert "self_check" not in capsys.readouterr().err


def test_cli_validate_records_the_self_check_warning(issue_dir):
    (issue_dir / "digest.json").write_text(json.dumps(_digest()))
    assert _run(issue_dir, "validate", "--drop-invalid") == 0
    written = json.loads((issue_dir / "digest.json").read_text())
    assert any("self_check" in w for w in written["validation"]["warnings"])
    record = json.loads((issue_dir / "trace.claude.json").read_text())
    assert any("self_check" in w for w in record["steps"][-1]["warnings"])


def _with_commentary(count=3):
    candidates = copy.deepcopy(CANDIDATES)
    for n in range(count):
        candidates["candidates"].append(
            _candidate(
                f"c_blog{n}",
                "commentary",
                f"Essay number{n}",
                f"https://writer{n}.example/essay",
                tier=2,
            )
        )
    return candidates


def _essay(n, section="brief", **extra):
    return _item(section, f"一篇评论 number{n}", "作者的分析。", f"c_blog{n}", **extra)


@pytest.mark.parametrize("section", ["headline", "model", "tool"])
def test_commentary_outside_the_brief_section_is_dropped(section):
    data = _digest()
    data["items"].append(_essay(0, section))
    report = digest.validate(data, _with_commentary())
    assert "commentary" in _errors(report, 4) and "brief" in _errors(report, 4)


def test_commentary_in_the_brief_section_passes():
    data = _digest()
    data["items"] += [_essay(0), _essay(1)]
    assert digest.validate(data, _with_commentary()).ok


def test_only_the_first_two_commentary_items_are_kept():
    data = _digest()
    data["items"] += [_essay(0), _essay(1), _essay(2)]
    report = digest.validate(data, _with_commentary())
    assert sorted(report.item_errors) == [6]
    assert "at most 2 commentary" in _errors(report, 6)


def test_dropped_commentary_items_do_not_use_up_the_limit():
    data = _digest()
    data["items"] += [
        _essay(0, "tool"),  # wrong section
        _item("brief", "一篇评论 GPT-99", "作者的分析。", "c_blog1"),  # GPT-99 is not in the material
        _essay(2),
        _essay(3),
        _essay(4),
    ]
    report = digest.validate(data, _with_commentary(5))
    assert sorted(report.item_errors) == [4, 5, 8]  # c_blog2 and c_blog3 are the two that count


def test_commentary_rule_looks_at_the_main_source_only():
    candidates = _with_commentary()
    data = _digest()
    data["items"][0]["sources"].append({"candidate_id": "c_blog0"})  # supports an official post
    data["items"] += [_essay(1), _essay(2)]
    assert digest.validate(data, candidates).ok  # c_blog0 is not counted, wherever it sits
    data = _digest()
    data["items"][0]["sources"].insert(0, {"candidate_id": "c_blog0"})
    assert "brief" in _errors(digest.validate(data, candidates), 0)


def test_commentary_main_source_found_by_url():
    data = _digest()
    data["items"].append(
        {
            "section": "tool",
            "title": "一篇评论 number0",
            "summary": "作者的分析。",
            "sources": [{"url": "https://writer0.example/essay"}],
            "tags": [],
        }
    )
    assert "brief" in _errors(digest.validate(data, _with_commentary()), 4)


def test_commentary_rule_applies_to_the_english_edition():
    data = _digest(lang="en")
    data["items"] = [
        _item("headline", "OpenAI ships GPT-6", "GPT-6 has a 1M token context.", "c_gpt"),
        _item("tool", "An essay number0", "The author's analysis.", "c_blog0"),
        _item("brief", "An essay number1", "The author's analysis.", "c_blog1"),
        _item("brief", "An essay number2", "The author's analysis.", "c_blog2"),
        _item("brief", "An essay number3", "The author's analysis.", "c_blog3"),
    ]
    data["highlights"] = ["OpenAI ships GPT-6."]
    report = digest.validate(data, _with_commentary(4))
    assert sorted(report.item_errors) == [1, 4]


def test_fallback_never_breaks_the_commentary_rule():
    candidates = _with_commentary(5)
    assert digest.validate(fallback.build_fallback(candidates), candidates).ok
