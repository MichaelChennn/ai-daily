"""Fetcher registry: sources.yaml `type` -> fetch function."""

from daily.fetchers.base import Fetcher
from daily.fetchers.community import fetch_hackernews, fetch_reddit
from daily.fetchers.feeds import fetch_rss
from daily.fetchers.github import fetch_releases, fetch_trending
from daily.fetchers.html_listing import fetch_html_listing
from daily.fetchers.huggingface import fetch_daily_papers, fetch_trending_models

FETCHERS: dict[str, Fetcher] = {
    "rss": fetch_rss,
    "html_listing": fetch_html_listing,
    "github_releases": fetch_releases,
    "github_trending": fetch_trending,
    "hf_daily_papers": fetch_daily_papers,
    "hf_trending_models": fetch_trending_models,
    "hackernews": fetch_hackernews,
    "reddit": fetch_reddit,
}
