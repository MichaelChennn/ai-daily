"""Each fetcher against a small canned response (no network)."""

import pytest

from daily.fetchers.community import fetch_hackernews, fetch_reddit
from daily.fetchers.feeds import fetch_rss
from daily.fetchers.github import fetch_releases, fetch_trending
from daily.fetchers.html_listing import fetch_html_listing
from daily.fetchers.huggingface import fetch_daily_papers, fetch_trending_models, is_noisy_model
from tests.conftest import BEFORE_WINDOW, IN_WINDOW, mock_client, source

RSS = f"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Blog</title>
<item><title>Introducing GPT-6</title><link>https://openai.com/index/gpt-6/</link>
  <pubDate>{IN_WINDOW.strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>
  <description>&lt;p&gt;Our &lt;b&gt;best&lt;/b&gt; model.&lt;/p&gt;</description><category>Product</category></item>
<item><title>Old post</title><link>https://openai.com/index/old/</link>
  <pubDate>{BEFORE_WINDOW.strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate></item>
</channel></rss>"""


async def test_rss_keeps_only_window_items(window):
    async with mock_client({"openai.com/news/rss.xml": RSS}) as client:
        items = await fetch_rss(client, source("rss", url="https://openai.com/news/rss.xml"), window)
    assert [(i.title, i.url, i.summary, i.tags) for i in items] == [
        ("Introducing GPT-6", "https://openai.com/index/gpt-6/", "Our best model.", ["Product"])
    ]
    assert items[0].published_at == IN_WINDOW


ARXIV = """<?xml version="1.0"?>
<rss xmlns:arxiv="http://arxiv.org/schemas/atom" version="2.0"><channel><title>cs.CL</title>
<item><title>New paper</title><link>https://arxiv.org/abs/2610.00001</link>
  <pubDate>Mon, 19 Oct 2026 04:00:00 -0400</pubDate><arxiv:announce_type>new</arxiv:announce_type></item>
<item><title>Revised paper</title><link>https://arxiv.org/abs/2601.00001</link>
  <pubDate>Mon, 19 Oct 2026 04:00:00 -0400</pubDate><arxiv:announce_type>replace</arxiv:announce_type></item>
</channel></rss>"""


async def test_rss_arxiv_announce_type_filter(window):
    async with mock_client({"rss.arxiv.org/rss/cs.CL": ARXIV}) as client:
        src = source("rss", "paper", url="https://rss.arxiv.org/rss/cs.CL", arxiv_announce_types=["new"])
        items = await fetch_rss(client, src, window)
    assert [i.title for i in items] == ["New paper"]


# Mixes the layouts seen in the wild: cards with the date before the link next to a featured
# card that points outside the pattern (Anthropic), table rows with the date after the link,
# and category chips that match the link pattern.
LISTING = """<html><body><article><h1>News</h1>
<div class="grid">
  <div><time>Sep 1, 2026</time><a href="/featured-elsewhere"><h2>Featured post outside the pattern</h2></a></div>
  <div><header><a href="/news/announcements">Announcements</a><time>Oct 19, 2026</time></header>
    <a href="/news/claude-feature"><h2>Claude gets a feature</h2><p>Long description of the feature.</p></a></div>
</div>
<article><header><time>Oct 1, 2026</time></header>
  <a href="/news/old-thing"><h2>Something from earlier</h2></a></article>
<div class="row"><a href="/news/table-post"><span>A post shown in the table view</span></a>
  <a href="/news/announcements">Announcements</a><time>Oct 20, 2026</time></div>
<a href="/careers">Careers at the company</a>
</article><script>var x = "<a href='/news/fake'>not a post at all</a> Oct 19, 2026";</script></body></html>"""


async def test_html_listing(window):
    async with mock_client({"www.anthropic.com/news": LISTING}) as client:
        src = source("html_listing", url="https://www.anthropic.com/news", link_pattern=r"^/news/[a-z0-9-]+$")
        items = await fetch_html_listing(client, src, window)
    assert [(i.title, i.url, i.published_at.day, i.published_precision) for i in items] == [
        ("Claude gets a feature", "https://www.anthropic.com/news/claude-feature", 19, "day"),
        ("A post shown in the table view", "https://www.anthropic.com/news/table-post", 20, "day"),
    ]
    assert items[0].summary == "Long description of the feature."


async def test_html_listing_fails_loudly_when_layout_changes(window):
    async with mock_client({"example.com/blog": "<html>nothing here</html>"}) as client:
        src = source("html_listing", url="https://example.com/blog", link_pattern="^/blog/")
        with pytest.raises(ValueError, match="layout"):
            await fetch_html_listing(client, src, window)


def _release(tag, when, **kw):
    return {
        "tag_name": tag,
        "name": kw.pop("name", tag),
        "html_url": f"https://github.com/vllm-project/vllm/releases/tag/{tag}",
        "published_at": when.isoformat().replace("+00:00", "Z"),
        "body": "## Highlights\n* faster",
        "draft": False,
        "prerelease": False,
        **kw,
    }


async def test_github_releases(window):
    releases = [
        _release("v0.11.0", IN_WINDOW),
        _release("v0.11.0rc1", IN_WINDOW, prerelease=True),
        _release("v0.10.9", BEFORE_WINDOW),
    ]
    async with mock_client({"api.github.com/repos/vllm-project/vllm/releases": releases}) as client:
        items = await fetch_releases(
            client, source("github_releases", "release", repos=["vllm-project/vllm"]), window
        )
    assert [(i.title, i.summary) for i in items] == [("vllm-project/vllm v0.11.0", "Highlights faster")]


async def test_github_releases_one_bad_repo_fails_the_source(window):
    async with mock_client({"api.github.com/repos/a/b/releases": []}) as client:
        with pytest.raises(Exception, match="404"):
            await fetch_releases(
                client, source("github_releases", "release", repos=["a/b", "gone/repo"]), window
            )


TRENDING = """<main>
<article class="Box-row"><h2 class="h3"><a href="/acme/tiny-llm-server">acme / tiny-llm-server</a></h2>
  <p class="col-9">Serve LLMs on a Raspberry Pi</p><span itemprop="programmingLanguage">Rust</span>
  <a href="/acme/tiny-llm-server/stargazers">1,204</a><span>312 stars today</span></article>
<article class="Box-row"><h2 class="h3"><a href="/acme/css-grid">acme / css-grid</a></h2>
  <p class="col-9">A CSS grid framework that is maintained daily</p><span>900 stars today</span></article>
<article class="Box-row"><h2 class="h3"><a href="/acme/agent-kit">acme / agent-kit</a></h2>
  <p class="col-9">Build agents</p><span>12 stars today</span></article>
</main>"""


async def test_github_trending_keeps_ai_repos_above_threshold(window):
    async with mock_client({"github.com/trending": TRENDING}) as client:
        items = await fetch_trending(client, source("github_trending", "repo", min_stars_today=50), window)
    assert [(i.title, i.signals, i.tags) for i in items] == [
        ("acme/tiny-llm-server", {"trending_rank": 1, "stars_today": 312, "stars": 1204}, ["Rust"])
    ]


PAPERS = [
    {
        "paper": {
            "id": "2610.20424",
            "title": "BizBench: Long-Horizon Agents",
            "summary": "We introduce BizBench.",
            "upvotes": 454,
            "publishedAt": "2026-10-14T00:00:00.000Z",
            "githubRepo": "https://github.com/ant-intl/BizAgentBench",
            "githubStars": 17,
            "ai_keywords": ["BizBench", "agents"],
            "organization": {"fullname": "ant-international"},
        },
        "numComments": 3,
    },
    {"paper": {"id": "2610.00002", "title": "Low interest", "summary": "x", "upvotes": 1}},
]


async def test_hf_daily_papers(window):
    async with mock_client({"huggingface.co/api/daily_papers": PAPERS}) as client:
        items = await fetch_daily_papers(client, source("hf_daily_papers", "paper", min_upvotes=5), window)
    assert len(items) == 1
    paper = items[0]
    assert paper.url == "https://huggingface.co/papers/2610.20424"
    assert paper.signals == {
        "upvotes": 454,
        "comments": 3,
        "github_repo": "https://github.com/ant-intl/BizAgentBench",
        "github_stars": 17,
        "organization": "ant-international",
    }
    assert paper.tags == ["BizBench", "agents"]


MODELS = [
    {
        "id": "deepseek-ai/DeepSeek-V4.1-Flash",
        "createdAt": IN_WINDOW.isoformat(),
        "likes": 1926,
        "downloads": 27737,
        "trendingScore": 1726,
        "pipeline_tag": "text-generation",
        "library_name": "transformers",
        "tags": ["fp8", "license:mit"],
    },
    {"id": "someone/DeepSeek-V4.1-Flash-GGUF", "createdAt": IN_WINDOW.isoformat()},
    {"id": "meta-llama/Llama-3-8B", "createdAt": "2024-04-18T00:00:00Z"},
]


async def test_hf_trending_models_filters_noise_and_old_models(window):
    async with mock_client({"huggingface.co/api/models": MODELS}) as client:
        items = await fetch_trending_models(client, source("hf_trending_models", "model"), window)
    assert [(i.title, i.summary, i.signals["trending_rank"]) for i in items] == [
        ("deepseek-ai/DeepSeek-V4.1-Flash", "text-generation, transformers, license:mit", 1)
    ]


def test_noise_filter_checks_repo_id_only():
    assert is_noisy_model("bartowski/Qwen3-8B-GGUF")
    assert is_noisy_model("x/Model-AWQ")
    assert is_noisy_model("nvidia/Nemotron-3.5-Super-120B-NVFP4")
    assert not is_noisy_model("deepseek-ai/DeepSeek-V4.1-Flash")


HN = {
    "hits": [
        {
            "objectID": "101",
            "title": "Claude Opus 5.5 is out",
            "url": "https://www.anthropic.com/news/claude-opus-5-5",
            "points": 900,
            "num_comments": 400,
            "created_at_i": int(IN_WINDOW.timestamp()),
        },
        {
            "objectID": "102",
            "title": "Ask HN: Best way to learn AI agents?",
            "points": 120,
            "created_at_i": 1,
        },
        {"objectID": "103", "title": "SimCity, but with permits", "url": "https://x.com", "points": 500},
        {"objectID": "104", "title": "Maintaining a legacy codebase", "url": "https://y.com", "points": 300},
    ]
}


async def test_hackernews_keeps_ai_stories(window):
    async with mock_client({"hn.algolia.com/api/v1/search_by_date": HN}) as client:
        items = await fetch_hackernews(client, source("hackernews", "discussion", tier=2), window)
    assert [(i.title, i.url, i.discussion_url) for i in items] == [
        (
            "Claude Opus 5.5 is out",
            "https://www.anthropic.com/news/claude-opus-5-5",
            "https://news.ycombinator.com/item?id=101",
        ),
        (
            "Ask HN: Best way to learn AI agents?",
            "https://news.ycombinator.com/item?id=102",
            "https://news.ycombinator.com/item?id=102",
        ),
    ]
    assert items[0].signals == {"hn_points": 900, "hn_comments": 400}


REDDIT = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>top scoring links : LocalLLaMA</title>
<entry><title>New 8B model beats 70B</title>
  <link href="https://www.reddit.com/r/LocalLLaMA/comments/abc/new_8b/" />
  <updated>{IN_WINDOW.isoformat()}</updated><published>{IN_WINDOW.isoformat()}</published>
  <content type="html">&lt;div&gt;Benchmarks inside&lt;/div&gt; submitted by &lt;a href=&quot;https://www.reddit.com/user/u&quot;&gt; /u/u &lt;/a&gt;
  &lt;br/&gt; &lt;span&gt;&lt;a href=&quot;https://huggingface.co/org/model-8b&quot;&gt;[link]&lt;/a&gt;&lt;/span&gt;
  &lt;span&gt;&lt;a href=&quot;https://www.reddit.com/r/LocalLLaMA/comments/abc/new_8b/&quot;&gt;[comments]&lt;/a&gt;&lt;/span&gt;</content>
</entry></feed>"""


async def test_reddit_extracts_external_link(window):
    async with mock_client({"www.reddit.com/r/LocalLLaMA/top/.rss": REDDIT}) as client:
        items = await fetch_reddit(
            client, source("reddit", "discussion", tier=2, subreddit="LocalLLaMA"), window
        )
    assert [(i.url, i.discussion_url, i.summary) for i in items] == [
        (
            "https://huggingface.co/org/model-8b",
            "https://www.reddit.com/r/LocalLLaMA/comments/abc/new_8b/",
            "Benchmarks inside",
        )
    ]
    assert items[0].signals == {"reddit_rank": 1, "subreddit": "LocalLLaMA"}
