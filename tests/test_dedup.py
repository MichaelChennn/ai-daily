import json
from datetime import timedelta

import pytest

from daily import dedup
from daily.models import Candidate
from tests.conftest import IN_WINDOW, ISSUE


def make(title, url, source="openai-news", tier=1, kind="blog", **kw) -> Candidate:
    return Candidate(
        source=source,
        source_name=source,
        tier=tier,
        kind=kind,
        title=title,
        url=url,
        published_at=IN_WINDOW,
        **kw,
    )


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("https://openai.com/index/gpt-6/", "http://www.openai.com/index/gpt-6?utm_source=hn#top"),
        ("https://example.com/post?b=2&a=1", "https://example.com/post?a=1&b=2&ref=twitter"),
        ("https://arxiv.org/abs/2610.12345v2", "https://arxiv.org/pdf/2610.12345"),
        ("https://huggingface.co/papers/2610.12345", "https://arxiv.org/abs/2610.12345"),
        ("https://github.com/vLLM-Project/vLLM", "https://github.com/vllm-project/vllm/"),
        ("https://example.com/blog/index.html", "https://example.com/blog"),
    ],
)
def test_same_document_same_key(a, b):
    assert dedup.url_key(a) == dedup.url_key(b)


def test_different_documents_different_keys():
    assert dedup.url_key("https://example.com/a") != dedup.url_key("https://example.com/b")
    assert dedup.url_key("https://news.ycombinator.com/item?id=1") != dedup.url_key(
        "https://news.ycombinator.com/item?id=2"
    )
    # Paths are case-sensitive outside GitHub / Hugging Face.
    assert dedup.url_key("https://example.com/Post") != dedup.url_key("https://example.com/post")


def test_merge_keeps_first_hand_record_and_folds_in_signals():
    official = make("Introducing GPT-6", "https://openai.com/index/gpt-6/", summary="Official post.")
    hn = make(
        "GPT-6",
        "https://openai.com/index/gpt-6?utm_source=hn",
        source="hackernews",
        tier=2,
        kind="discussion",
        discussion_url="https://news.ycombinator.com/item?id=9",
        signals={"hn_points": 812},
    )
    merged = dedup.merge_by_url([hn, official], {"openai-news": 0, "hackernews": 1})
    assert len(merged) == 1
    item = merged[0]
    assert item.source == "openai-news" and item.title == "Introducing GPT-6"
    assert item.signals == {"hn_points": 812}
    assert item.discussion_url == "https://news.ycombinator.com/item?id=9"
    assert item.also_from[0]["source"] == "hackernews"
    assert item.id == dedup.candidate_id(item.key) and item.id.startswith("c_")


def test_merge_respects_source_order_within_a_tier():
    hf = make("Paper", "https://huggingface.co/papers/2610.00001", source="hf-daily-papers", kind="paper")
    arxiv = make("Paper", "https://arxiv.org/abs/2610.00001v1", source="arxiv-cs-cl", kind="paper")
    merged = dedup.merge_by_url([arxiv, hf], {"hf-daily-papers": 0, "arxiv-cs-cl": 1})
    assert [m.source for m in merged] == ["hf-daily-papers"]


def _ids(items):
    for item in items:
        item.key = dedup.url_key(item.url)
        item.id = dedup.candidate_id(item.key)
    return items


def test_clusters_same_event_across_sources():
    items = _ids(
        [
            make("Introducing Qwen3.5-Max", "https://qwen.ai/blog/qwen3.5-max"),
            make(
                "Qwen/Qwen3.5-Max-Instruct", "https://huggingface.co/Qwen/Qwen3.5-Max-Instruct", kind="model"
            ),
            make("Qwen 3.5 Max is out and it beats GPT-6 on SWE-bench", "https://x.com/1", tier=2),
            make("vllm-project/vllm v0.11.0", "https://github.com/vllm-project/vllm/releases/tag/v0.11.0"),
            make(
                "huggingface/transformers v0.11.0",
                "https://github.com/huggingface/transformers/releases/v0.11.0",
            ),
        ]
    )
    clusters = dedup.assign_clusters(items)
    assert len(clusters) == 1
    assert clusters[0]["candidate_ids"] == [items[0].id, items[1].id, items[2].id]
    assert items[3].cluster_id != items[4].cluster_id


def test_unrelated_titles_sharing_a_model_name_stay_apart():
    items = _ids(
        [
            make("GPT-6 system card", "https://openai.com/a"),
            make("Fine-tuning Llama with GPT-6 generated data at scale for medical QA", "https://b.com/x"),
        ]
    )
    assert dedup.assign_clusters(items) == []


def test_entities_ignore_bare_versions():
    assert dedup.title_entities("vllm v0.11.0 release") == {"vllmv0.11.0"}
    assert dedup.title_entities("DeepSeek-V4.1-Flash and Claude Opus 5.5") == {"deepseekv4.1", "opus5.5"}


def _write_day(data_dir, day, candidates=None, digest=None):
    folder = data_dir / day.isoformat()
    folder.mkdir(parents=True)
    if candidates is not None:
        (folder / "candidates.json").write_text(json.dumps({"candidates": candidates}))
    if digest is not None:
        (folder / "digest.json").write_text(json.dumps(digest))


def test_history_drops_published_and_marks_seen(tmp_path):
    yesterday = ISSUE - timedelta(days=1)
    _write_day(
        tmp_path,
        yesterday,
        candidates=[
            {"url": "https://huggingface.co/org/model", "also_from": []},
            {
                "url": "https://openai.com/index/gpt-6",
                "also_from": [{"url": "https://news.ycombinator.com/item?id=9"}],
            },
        ],
        digest={"items": [{"title": "GPT-6", "sources": [{"url": "https://openai.com/index/gpt-6/"}]}]},
    )
    _write_day(tmp_path, ISSUE - timedelta(days=9), candidates=[{"url": "https://old.example/x"}])

    history = dedup.load_history(tmp_path, ISSUE)
    items = dedup.merge_by_url(
        [
            make("GPT-6", "https://openai.com/index/gpt-6?utm_source=x"),
            make("org/model", "https://huggingface.co/Org/Model", kind="model"),
            make("old", "https://old.example/x"),
        ],
        {},
    )
    kept, dropped = dedup.apply_history(items, history)

    assert [d["published_on"] for d in dropped] == [yesterday.isoformat()]
    assert {k.title: k.seen_on for k in kept} == {"org/model": [yesterday.isoformat()], "old": []}
