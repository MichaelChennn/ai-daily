import copy
import json

import httpx
import pytest

from daily import cli, dedup, digest, fallback, render
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
    assert any("items" in w for w in report.warnings)  # 4 items, target 8-12


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


def test_fallback_is_valid_and_skips_seen_and_clustered_candidates():
    candidates = copy.deepcopy(CANDIDATES)
    candidates["candidates"] += [
        _candidate(
            "c_old",
            "paper",
            "Yesterday's paper",
            "https://huggingface.co/papers/2610.00002",
            signals={"upvotes": 999},
            seen_on=["2026-10-19"],
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
