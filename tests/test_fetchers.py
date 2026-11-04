"""Each fetcher against a small canned response (no network)."""

from datetime import datetime, timedelta, timezone

import httpx
import pytest

from daily import pipeline
from daily.config import SourceConfig
from daily.fetchers.base import candidate, collect_filtered, first_hand_links
from daily.fetchers.community import fetch_hackernews, fetch_reddit
from daily.fetchers.feeds import fetch_rss
from daily.fetchers.github import fetch_releases, fetch_trending
from daily.fetchers.html_listing import fetch_html_listing
from daily.fetchers.huggingface import fetch_daily_papers, fetch_trending_models, is_noisy_model
from daily.fetchers.json_api import fetch_json_api
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


# MiniMax: the nav menu links to the newest posts before their dated cards do.
NAV_FIRST = """<html><body><nav><ul>
  <li><a href="/blog/minimax-m3-1-flash">MiniMax M3.1 Flash is here</a></li>
  <li><a href="/blog/minimax-h3">MiniMax H3 is here now</a></li></ul></nav>
<main><div class="grid">
  <div><a href="/blog/minimax-m3-1-flash"><h3>MiniMax M3.1 Flash</h3></a><p>2026-10-19</p>
    <p>A faster model for everyday agents.</p></div>
  <div><a href="/blog/minimax-h3"><h3>MiniMax H3</h3></a><p>2026-07-31</p></div>
</div></main></body></html>"""


async def test_html_listing_takes_the_first_dated_card(window):
    async with mock_client({"www.minimax.io/blog": NAV_FIRST}) as client:
        src = source("html_listing", url="https://www.minimax.io/blog", link_pattern=r"^/blog/[a-z0-9-]+$")
        items = await fetch_html_listing(client, src, window)
    assert [(i.title, i.url, i.summary) for i in items] == [
        (
            "MiniMax M3.1 Flash",
            "https://www.minimax.io/blog/minimax-m3-1-flash",
            "A faster model for everyday agents.",
        )
    ]


# Kimi: each card is an empty overlay link with an aria-label next to the heading and date.
OVERLAY_CARDS = """<html><body><div class="grid">
  <div><a href="/en/blog/kimi-k3-1-pro" aria-label="Kimi K3.1 Pro"></a>
    <div><img src="/cover.png"></div><div><h4>Kimi K3.1 Pro</h4><p>2026-10-19</p></div></div>
  <div><a href="/en/blog/kimi-k3" aria-label="Kimi K3"></a>
    <div><img src="/cover.png"></div><div><h4>Kimi K3</h4><p>2026-07-16</p></div></div>
</div></body></html>"""


async def test_html_listing_accepts_empty_links_with_aria_label(window):
    async with mock_client({"www.kimi.com/en/blog/": OVERLAY_CARDS}) as client:
        src = source(
            "html_listing", url="https://www.kimi.com/en/blog/", link_pattern=r"^/en/blog/[a-z0-9-]+/?$"
        )
        items = await fetch_html_listing(client, src, window)
    assert [(i.title, i.url) for i in items] == [
        ("Kimi K3.1 Pro", "https://www.kimi.com/en/blog/kimi-k3-1-pro")
    ]


# DeepSeek: a docs sidebar whose link texts end in a slash-separated date.
SLASH_DATES = """<html><body><nav class="menu"><ul>
  <li><a href="/news/news261019">DeepSeek-V4.1-Flash-1019 Release 2026/10/19</a></li>
  <li><a href="/news/news250120">DeepSeek-R1 Release 2025/01/20</a></li>
</ul></nav></body></html>"""


async def test_html_listing_reads_slash_dates(window):
    async with mock_client({"api-docs.deepseek.com/news/news250120": SLASH_DATES}) as client:
        src = source(
            "html_listing",
            url="https://api-docs.deepseek.com/news/news250120",
            link_pattern=r"^/news/news[0-9]+/?$",
        )
        items = await fetch_html_listing(client, src, window)
    assert [(i.url, i.published_at.day) for i in items] == [
        ("https://api-docs.deepseek.com/news/news261019", 19)
    ]


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
        _release("v0.10.9", BEFORE_WINDOW - timedelta(days=3)),
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


REDDIT_MULTI = REDDIT.replace(
    "<updated>", '<category term="MachineLearning" label="r/MachineLearning"/><updated>'
)


async def test_reddit_multi_subreddit_feed_keeps_each_entrys_subreddit(window):
    async with mock_client({"www.reddit.com/r/LocalLLaMA+MachineLearning/top/.rss": REDDIT_MULTI}) as client:
        items = await fetch_reddit(
            client, source("reddit", "discussion", tier=2, subreddit="LocalLLaMA+MachineLearning"), window
        )
    assert [i.signals["subreddit"] for i in items] == ["MachineLearning"]


async def test_content_filters_record_what_they_skip(window):
    """过滤 is recorded with its reason and trigger value, for the process page; the window is not."""
    routes = {
        "github.com/trending": TRENDING,
        "huggingface.co/api/daily_papers": PAPERS,
        "huggingface.co/api/models": MODELS,
        "hn.algolia.com/api/v1/search_by_date": HN,
    }
    async with mock_client(routes) as client:
        with collect_filtered() as skipped:
            await fetch_trending(client, source("github_trending", "repo", min_stars_today=50), window)
            await fetch_daily_papers(client, source("hf_daily_papers", "paper", min_upvotes=5), window)
            await fetch_trending_models(client, source("hf_trending_models", "model"), window)
            await fetch_hackernews(client, source("hackernews", "discussion", tier=2), window)
    assert [(f.source, f.title, f.reason, f.value) for f in skipped] == [
        ("github_trending", "acme/css-grid", "not_ai", None),
        ("github_trending", "acme/agent-kit", "min_stars_today", "stars_today 12 < 50"),
        ("hf_daily_papers", "Low interest", "min_upvotes", "upvotes 1 < 5"),
        ("hf_trending_models", "someone/DeepSeek-V4.1-Flash-GGUF", "noisy_model", "repo id contains gguf"),
        ("hf_trending_models", "meta-llama/Llama-3-8B", "max_age_days", "915 days old > 14"),
        ("hackernews", "SimCity, but with permits", "not_ai", None),
        ("hackernews", "Maintaining a legacy codebase", "not_ai", None),
    ]
    assert skipped[0].url == "https://github.com/acme/css-grid"


# ---------------------------------------------------------------- rss: dates and title filter


def _rss(*items: tuple[str, str]) -> str:
    entries = "".join(
        f"<item><title>{title}</title><link>https://example.com/{i}</link><pubDate>{date}</pubDate></item>"
        for i, (title, date) in enumerate(items)
    )
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>B</title>{entries}</channel></rss>'


async def _fetch_feed(body: str, window, **options):
    async with mock_client({"example.com/feed": body}) as client:
        return await fetch_rss(client, source("rss", url="https://example.com/feed", **options), window)


async def test_rss_midnight_means_date_only(window):
    # The issue's window starts 10-19 02:00 UTC, so 10-19 00:00 was out of it as a real timestamp.
    items = await _fetch_feed(_rss(("Date only", "Mon, 19 Oct 2026 00:00:00 GMT")), window)
    assert [(i.title, i.published_precision) for i in items] == [("Date only", "day")]
    assert items[0].published_at == datetime(2026, 10, 19, tzinfo=timezone.utc)


async def test_rss_midnight_is_judged_in_the_feeds_own_timezone(window):
    # Ai2 writes 00:00 Pacific: 08:00 UTC, but still only a date, and the date is the one written.
    pacific = await _fetch_feed(_rss(("Pacific", "Sun, 18 Oct 2026 00:00:00 -0800")), window)
    assert [(i.published_at.day, i.published_precision) for i in pacific] == [(18, "day")]
    # Midnight UTC written from Beijing is a real 08:00 there, a real timestamp.
    beijing = await _fetch_feed(_rss(("Beijing", "Mon, 19 Oct 2026 08:00:00 +0800")), window)
    assert beijing == []  # 00:00 UTC is before the window start


async def test_rss_atom_midnight_with_offset(window):
    atom = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>A</title>
    <entry><title>Ai2 post</title><link href="https://allenai.org/blog/x"/>
    <published>2026-10-19T00:00:00-08:00</published></entry></feed>"""
    items = await _fetch_feed(atom, window)
    assert [(i.published_at.day, i.published_precision) for i in items] == [(19, "day")]


async def test_rss_real_timestamps_keep_second_precision(window):
    items = await _fetch_feed(_rss(("Real", IN_WINDOW.strftime("%a, %d %b %Y %H:%M:%S GMT"))), window)
    assert items[0].published_precision == "second" and items[0].published_at == IN_WINDOW


async def test_rss_exclude_title_pattern_is_recorded_as_filtered(window):
    when = IN_WINDOW.strftime("%a, %d %b %Y %H:%M:%S GMT")
    body = _rss(("[AINews] Daily roundup", when), ("A long essay", when))
    with collect_filtered() as skipped:
        items = await _fetch_feed(body, window, exclude_title_pattern=r"^\[AINews\]")
    assert [i.title for i in items] == ["A long essay"]
    assert [(f.title, f.reason) for f in skipped] == [("[AINews] Daily roundup", "exclude_title")]


async def test_rss_logs_last_build_date_and_entry_count(window, caplog):
    body = _rss(("One", "Mon, 19 Oct 2026 12:00:00 GMT")).replace(
        "<title>B</title>", "<title>B</title><lastBuildDate>Mon, 19 Oct 2026 13:00:00 GMT</lastBuildDate>"
    )
    with caplog.at_level("INFO", logger="daily.fetchers.feeds"):
        await _fetch_feed(body, window)
    assert "Mon, 19 Oct 2026 13:00:00 GMT" in caplog.text and "1 entries" in caplog.text


# ---------------------------------------------------------------- html_listing: titles, diagnostics

# Cohere: the card is a link around title, subtitle, date and reading time, none of them headings.
COHERE_CARDS = """<html><body>
<div><a href="https://cohere.com/blog/rerank-5">Learn more</a></div>
<div><a href="/blog/rerank-5" aria-label="Read full article: Introducing Rerank 5: precise retrieval">
  <div><img src="/x.png"></div></a>
  <a href="/blog/rerank-5"><p>Introducing Rerank 5: precise retrieval</p>
  <p>Give your AI the most relevant context for each request.</p>
  <span><p>Oct 19, 2026</p><div></div><p>8 min read</p></span></a></div>
<div><a href="/blog/embed-5"><div><img src="/x.png"></div><span>Introducing Embed 5: a new family of
  <span>models<i></i></span></span></a>
  <a href="/blog/embed-5"><p>Introducing Embed 5: a new family of models</p>
  <span><p>Oct 20, 2026</p><div></div><p>7 min read</p></span></a></div>
</body></html>"""

# Cursor: date and category first, then the title, then the author and reading time, twice.
CURSOR_CARDS = """<html><body>
<a href="/blog/projects"><article><div><time>Oct 19, 2026</time><span>·</span><span>product</span></div>
  <div><p>Introducing Projects</p></div><div><span>Alexi &amp; Fredrika</span></div><div>5m</div>
  <div><span>Alexi &amp; Fredrika</span><span>·</span><span>5m</span></div></article></a>
<a href="/blog/navan"><div><p>Navan cuts a month-long migration down to a week</p>
  <div><time>Oct 20, 2026</time></div></div><div><div><span></span></div></div></a>
</body></html>"""

# One inline run with nothing separating the title from what follows it.
INLINE_CARD = """<html><body><a href="/blog/inline"><span>A title that runs into its metadata</span>
  <span>Oct 19, 2026</span> · <span>11 min read</span></a></body></html>"""


async def test_html_listing_cohere_title_without_date_or_subtitle(window):
    async with mock_client({"cohere.com/blog": COHERE_CARDS}) as client:
        src = source(
            "html_listing",
            url="https://cohere.com/blog",
            link_pattern=r"^(https://cohere.com)?/blog/[a-z0-9-]+$",
        )
        items = await fetch_html_listing(client, src, window)
    assert [(i.title, i.summary) for i in items] == [
        (
            "Introducing Rerank 5: precise retrieval",
            "Give your AI the most relevant context for each request.",
        ),
        ("Introducing Embed 5: a new family of models", ""),
    ]


async def test_html_listing_cursor_title_without_date_author_or_reading_time(window):
    async with mock_client({"cursor.com/blog": CURSOR_CARDS}) as client:
        src = source("html_listing", url="https://cursor.com/blog", link_pattern=r"^/blog/[a-z0-9-]+$")
        items = await fetch_html_listing(client, src, window)
    assert [i.title for i in items] == [
        "Introducing Projects",
        "Navan cuts a month-long migration down to a week",
    ]


async def test_html_listing_strips_trailing_metadata_from_an_inline_title(window):
    async with mock_client({"x.com/blog": INLINE_CARD}) as client:
        src = source("html_listing", url="https://x.com/blog", link_pattern=r"^/blog/")
        items = await fetch_html_listing(client, src, window)
    assert [i.title for i in items] == ["A title that runs into its metadata"]


async def test_html_listing_failure_says_what_the_runner_actually_got(window):
    page = "<html><body><a href='/x'>one</a><a href='/y'>two</a><p>Verify   you are\nhuman " + "z" * 400
    response = httpx.Response(
        200,
        text=page,
        headers={
            "server": "tencent-cos",
            "content-type": "text/html",
            "eo-cache-status": "MISS",
            "cf-ray": "abc-FRA",
            "x-amz-cf-pop": "IAD12",
            "x-unrelated": "nope",
        },
    )
    async with mock_client({"example.com/blog": response}) as client:
        src = source("html_listing", url="https://example.com/blog", link_pattern="^/blog/")
        report = (await pipeline.run_source(client, src, window))[1]
    error = report.error
    assert "\n" not in error
    for part in (
        "no post links found",
        "status=200",
        "url=https://example.com/blog",
        f"bytes={len(page.encode())}",
        "server=tencent-cos",
        "content-type=text/html",
        "eo-cache-status=MISS",
        "cf-ray=abc-FRA",
        "x-amz-cf-pop=IAD12",
        "links=2",
        "Verify you are human",
    ):
        assert part in error, part
    assert "x-unrelated" not in error
    assert "z" * 260 in error and "z" * 300 not in error  # 300 characters of text, whole message kept


# ---------------------------------------------------------------- github releases: promoted versions


def _ollama_release(tag, published, **kw):
    return {
        "tag_name": tag,
        "name": tag,
        "html_url": f"https://github.com/ollama/ollama/releases/tag/{tag}",
        "published_at": published,
        "draft": False,
        "prerelease": False,
        "body": "",
        **kw,
    }


async def test_github_releases_marks_recent_versions_before_the_window_as_late(window):
    releases = [
        _ollama_release("v3", "2026-10-19T12:00:00Z"),  # in the window
        _ollama_release(
            "v2", "2026-10-18T01:00:00Z"
        ),  # before it, within 3 days of its end: may have been promoted
        _ollama_release("v1", "2026-10-16T03:00:00Z"),  # more than 3 days before the end
        _ollama_release("v0", "2026-10-18T02:00:00Z", prerelease=True),  # still a pre-release
    ]
    urls = []

    async with mock_client({"api.github.com/repos/ollama/ollama/releases": releases}) as client:
        client.event_hooks["request"].append(_record_url(urls))
        items = await fetch_releases(
            client, source("github_releases", "release", repos=["ollama/ollama"]), window
        )
    assert [(i.title, i.signals) for i in items] == [
        ("ollama/ollama v3", {}),
        ("ollama/ollama v2", {"late_release": True}),
    ]
    assert "per_page=30" in urls[0]


def _record_url(urls):
    async def record(request):
        urls.append(str(request.url))

    return record


# ---------------------------------------------------------------- hf_daily_papers: weekly fallback


def _paper(arxiv_id, upvotes):
    return {
        "title": f"Paper {arxiv_id}",
        "paper": {"id": arxiv_id, "title": f"Paper {arxiv_id}", "upvotes": upvotes, "summary": "s"},
    }


def _papers_client(day_list, week_list, requests):
    def handler(request):
        requests.append(dict(request.url.params))
        return httpx.Response(200, json=week_list if "week" in request.url.params else day_list)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_hf_daily_papers_does_not_touch_the_weekly_list_when_the_day_has_papers(window):
    requests = []
    src = source("hf_daily_papers", "paper", week_fallback_limit=10)
    async with _papers_client([_paper("2610.00001", 20)], [_paper("2610.00002", 99)], requests) as client:
        items = await fetch_daily_papers(client, src, window)
    assert [i.title for i in items] == ["Paper 2610.00001"]
    assert "week" not in items[0].signals
    assert len(requests) == 1


async def test_hf_daily_papers_falls_back_to_top_of_the_iso_week(window):
    # Window 10-19 .. 10-20: the list it asks for is 10-19, in ISO week 2026-W43.
    week = [_paper(f"2610.{i:05d}", votes) for i, votes in enumerate([12, 300, 5, 40, 9, 100])]
    requests = []
    src = source("hf_daily_papers", "paper", min_upvotes=10, week_fallback_limit=3)
    with collect_filtered() as skipped:
        async with _papers_client([], week, requests) as client:
            items = await fetch_daily_papers(client, src, window)
    assert [i.signals["upvotes"] for i in items] == [300, 100, 40]
    assert {i.signals["week"] for i in items} == {"2026-W43"}
    assert requests[1]["week"] == "2026-W43"
    assert skipped == []  # the ones below the top 3 were never looked at


async def test_hf_daily_papers_week_fallback_still_applies_min_upvotes(window):
    week = [_paper("2610.00001", 50), _paper("2610.00002", 3)]
    src = source("hf_daily_papers", "paper", min_upvotes=10, week_fallback_limit=10)
    with collect_filtered() as skipped:
        async with _papers_client([], week, []) as client:
            items = await fetch_daily_papers(client, src, window)
    assert [i.signals["upvotes"] for i in items] == [50]
    assert [f.reason for f in skipped] == ["min_upvotes"]


async def test_hf_daily_papers_stays_empty_without_the_option(window):
    requests = []
    async with _papers_client([], [_paper("2610.00001", 50)], requests) as client:
        assert await fetch_daily_papers(client, source("hf_daily_papers", "paper"), window) == []
    assert len(requests) == 1


# ---------------------------------------------------------------- json_api

QWEN = {
    "success": True,
    "data": {
        "articles": [
            {
                "title": "Qwen-Image-3: new &amp; better",
                "path": "qwen-image-3",
                "content": '<meta property="article:published_time" content="2026-10-19T20:00:00+08:00">',
                "extra": {
                    "date": "2026-10-19T20:00:00+08:00",
                    "introduction": "<div>Hello <b>world</b></div>",
                },
            },
            {
                "title": "Old",
                "path": "old",
                "content": '<meta property="article:published_time" content="2026-01-01T20:00:00+08:00">',
                "extra": {"date": "2026-01-01T20:00:00+08:00"},
            },
            {"title": "No date", "path": "no-date", "content": "", "extra": {}},
            {"title": "", "path": "no-title", "extra": {"date": "2026-10-19T20:00:00+08:00"}},
        ]
    },
}
QWEN_OPTIONS = {
    "url": "https://qwen.ai/api/articles",
    "items": "data.articles",
    "title": "title",
    "date": "extra.date",
    "link": "https://qwen.ai/blog?id={path}",
    "summary": "extra.introduction",
}


async def test_json_api_reads_nested_fields(window):
    async with mock_client({"qwen.ai/api/articles": QWEN}) as client:
        items = await fetch_json_api(client, source("json_api", **QWEN_OPTIONS), window)
    assert [(i.title, i.url, i.summary, i.published_precision) for i in items] == [
        ("Qwen-Image-3: new & better", "https://qwen.ai/blog?id=qwen-image-3", "Hello world", "second")
    ]
    assert items[0].published_at == datetime(2026, 10, 19, 12, tzinfo=timezone.utc)


async def test_json_api_date_pattern_takes_the_date_out_of_a_field(window):
    options = {
        **QWEN_OPTIONS,
        "date": "content",
        "date_pattern": r'article:published_time" content="([^"]+)"',
    }
    async with mock_client({"qwen.ai/api/articles": QWEN}) as client:
        items = await fetch_json_api(client, source("json_api", **options), window)
    assert [i.url for i in items] == ["https://qwen.ai/blog?id=qwen-image-3"]
    assert items[0].published_at == datetime(2026, 10, 19, 12, tzinfo=timezone.utc)


def _seed_article(key, millis):
    return {
        "ArticleMeta": {"PublishDate": millis},
        "ArticleSubContentEn": {"Title": f"Seed {key}", "TitleKey": key, "Abstract": "Abstract."},
    }


SEED_OPTIONS = {
    "url": "https://seed.bytedance.com/api/list",
    "items": "sub_article_list",
    "title": "ArticleSubContentEn.Title",
    "date": "ArticleMeta.PublishDate",
    "date_timezone": "Asia/Shanghai",
    "link": "https://seed.bytedance.com/en/blog/{ArticleSubContentEn.TitleKey}",
    "summary": "ArticleSubContentEn.Abstract",
}


async def test_json_api_epoch_millis_as_a_date_in_the_sites_timezone(window):
    # 2026-10-19T16:00Z is midnight on 10-20 in Beijing.
    body = {
        "sub_article_list": [
            _seed_article("recent", 1792425600000),
            _seed_article("old", 1791907200000),
        ]
    }
    async with mock_client({"seed.bytedance.com/api/list": body}) as client:
        items = await fetch_json_api(client, source("json_api", **SEED_OPTIONS), window)
    assert [(i.title, i.url, i.published_precision, i.summary) for i in items] == [
        ("Seed recent", "https://seed.bytedance.com/en/blog/recent", "day", "Abstract.")
    ]
    assert items[0].published_at == datetime(2026, 10, 20, tzinfo=timezone.utc)


@pytest.mark.parametrize("body", [{"sub_article_list": []}, {"other": 1}, {"sub_article_list": {"a": 1}}])
async def test_json_api_fails_loudly_when_the_list_is_gone(window, body):
    async with mock_client({"seed.bytedance.com/api/list": body}) as client:
        with pytest.raises(ValueError, match="sub_article_list"):
            await fetch_json_api(client, source("json_api", **SEED_OPTIONS), window)


async def test_json_api_link_with_a_missing_field_skips_the_item(window):
    article = _seed_article("x", 1792425600000)
    del article["ArticleSubContentEn"]["TitleKey"]
    async with mock_client({"seed.bytedance.com/api/list": {"sub_article_list": [article]}}) as client:
        assert await fetch_json_api(client, source("json_api", **SEED_OPTIONS), window) == []


def test_candidate_urls_have_their_html_entities_decoded():
    source = SourceConfig("s", "rss", "S", 1, "blog")
    item = candidate(
        source,
        title="t",
        url="https://x.example/p?a=1&amp;s=46",
        discussion_url="https://y.example/d?a=1&amp;b=2",
    )
    assert item.url == "https://x.example/p?a=1&s=46"
    assert item.discussion_url == "https://y.example/d?a=1&b=2"
    assert candidate(source, title="t", url="https://x.example/").discussion_url is None


def test_first_hand_links_only_keeps_project_pages_on_the_three_hosts():
    body = (
        '<p>Code: <a href="https://github.com/p-e-w/heretic">repo</a>, '
        "weights https://huggingface.co/acme/model-1.5B, and paper https://arxiv.org/abs/2610.00001.</p>"
        '<a href="https://www.reddit.com/r/x">r/x</a> https://github.com/p-e-w/heretic again, '
        "https://example.com/a/b https://github.com/ https://huggingface.co/models https://notgithub.com/a/b"
    )
    assert first_hand_links(body) == [
        "https://github.com/p-e-w/heretic",
        "https://huggingface.co/acme/model-1.5B",
        "https://arxiv.org/abs/2610.00001",
    ]
    assert first_hand_links("") == [] and first_hand_links(None) == []


def test_first_hand_links_read_escaped_markup():
    # Algolia escapes the slashes in HN's story_text.
    assert first_hand_links('<a href="https:&#x2F;&#x2F;github.com&#x2F;a&#x2F;b">x</a>') == [
        "https://github.com/a/b"
    ]


REDDIT_SELF_POST = (
    """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom"><entry>
  <title>I made a tool</title>
  <link href="https://www.reddit.com/r/LocalLLaMA/comments/abc/tool/" />
  <updated>"""
    + IN_WINDOW.isoformat()
    + """</updated>
  <content type="html">&lt;div&gt;Code at &lt;a href=&quot;https://github.com/a/tool&quot;&gt;here&lt;/a&gt;&lt;/div&gt;
  submitted by &lt;a href=&quot;https://www.reddit.com/user/u&quot;&gt; /u/u &lt;/a&gt;
  &lt;span&gt;&lt;a href=&quot;https://www.reddit.com/r/LocalLLaMA/comments/abc/tool/&quot;&gt;[link]&lt;/a&gt;&lt;/span&gt;</content>
</entry></feed>"""
)


async def test_reddit_keeps_first_hand_links_from_the_post_body(window):
    async with mock_client({"www.reddit.com/r/LocalLLaMA/top/.rss": REDDIT_SELF_POST}) as client:
        items = await fetch_reddit(
            client, source("reddit", "discussion", tier=2, subreddit="LocalLLaMA"), window
        )
    assert items[0].links == ["https://github.com/a/tool"]
    assert "github.com" not in items[0].summary


async def test_hackernews_keeps_first_hand_links_from_the_post_body(window):
    hit = {
        "objectID": "7",
        "title": "Show HN: An AI agent",
        "story_text": 'Repo: <a href="https:&#x2F;&#x2F;github.com&#x2F;a&#x2F;agent">link</a>',
        "created_at_i": int(IN_WINDOW.timestamp()),
        "points": 60,
    }
    routes = {"hn.algolia.com/api/v1/search_by_date": httpx.Response(200, json={"hits": [hit]})}
    async with mock_client(routes) as client:
        items = await fetch_hackernews(client, source("hackernews", "discussion", tier=2), window)
    assert items[0].links == ["https://github.com/a/agent"]
