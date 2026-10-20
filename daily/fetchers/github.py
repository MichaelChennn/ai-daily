"""GitHub Releases for a watched repo list, and GitHub Trending (AI-related only)."""

from __future__ import annotations

import asyncio
import os
import re

import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, get, is_ai_related
from daily.models import Candidate
from daily.text import clean_text, clean_title, parse_datetime, truncate
from daily.window import Window


def _api_headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def fetch_releases(client: httpx.AsyncClient, source: SourceConfig, window: Window) -> list[Candidate]:
    """Options: repos (list of owner/name); include_prereleases (default false).

    One failing repo fails the whole source, so a renamed repo shows up in the fetch report.
    """
    include_prereleases = bool(source.options.get("include_prereleases", False))
    headers = _api_headers()

    async def one(repo: str) -> list[Candidate]:
        response = await get(
            client, f"https://api.github.com/repos/{repo}/releases", headers=headers, params={"per_page": 10}
        )
        found = []
        for release in response.json():
            if release.get("draft") or (release.get("prerelease") and not include_prereleases):
                continue
            published = parse_datetime(release.get("published_at") or release.get("created_at"))
            if not window.contains(published):
                continue
            name = clean_title(release.get("name") or release.get("tag_name"))
            tag = release.get("tag_name") or ""
            if tag and tag not in name:
                name = f"{name} ({tag})" if name else tag
            found.append(
                candidate(
                    source,
                    title=f"{repo} {name}",
                    url=release["html_url"],
                    summary=truncate(clean_text(release.get("body")), SUMMARY_MAX_CHARS),
                    published_at=published,
                    signals={"prerelease": True} if release.get("prerelease") else {},
                    tags=[repo],
                )
            )
        return found

    results = await asyncio.gather(*(one(repo) for repo in source.options["repos"]))
    return [item for repo_items in results for item in repo_items]


_ROW = re.compile(r"<article\b[^>]*Box-row.*?</article>", re.S)
_REPO_LINK = re.compile(r"<h2\b.*?href=\"/([^/\"]+/[^/\"]+)\"", re.S)
_DESCRIPTION = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S)
_STARS_TODAY = re.compile(r"([\d,]+)\s+stars?\s+(today|this week)")
_TOTAL_STARS = re.compile(r"href=\"/[^\"]+/stargazers\"[^>]*>(.*?)</a>", re.S)
_LANGUAGE = re.compile(r"itemprop=\"programmingLanguage\">([^<]+)<")


async def fetch_trending(client: httpx.AsyncClient, source: SourceConfig, window: Window) -> list[Candidate]:
    """Scrape github.com/trending. Options: since (daily), min_stars_today, extra_keywords.

    Trending has no publish date; the list itself is today's signal, so no window filter.
    """
    since = source.options.get("since", "daily")
    min_stars = int(source.options.get("min_stars_today", 0))
    extra = source.options.get("extra_keywords", [])
    html = (await get(client, "https://github.com/trending", params={"since": since})).text

    rows = _ROW.findall(html)
    if not rows:
        raise ValueError("no trending rows found; page layout may have changed")

    items: list[Candidate] = []
    for rank, row in enumerate(rows, start=1):
        link = _REPO_LINK.search(row)
        if not link:
            continue
        repo = link.group(1)
        desc_match = _DESCRIPTION.search(row)
        description = clean_text(desc_match.group(1)) if desc_match else ""
        if not is_ai_related(repo.replace("/", " ").replace("-", " "), description, extra_keywords=extra):
            continue
        stars_today = _int(_STARS_TODAY.search(row))
        if stars_today < min_stars:
            continue
        signals = {"trending_rank": rank, "stars_today": stars_today}
        if total := _TOTAL_STARS.search(row):
            signals["stars"] = _int_text(clean_text(total.group(1)))
        language = _LANGUAGE.search(row)
        items.append(
            candidate(
                source,
                title=repo,
                url=f"https://github.com/{repo}",
                summary=description,
                signals=signals,
                tags=[language.group(1).strip()] if language else [],
            )
        )
    return items


def _int(match: re.Match[str] | None) -> int:
    return _int_text(match.group(1)) if match else 0


def _int_text(value: str) -> int:
    digits = value.replace(",", "").strip()
    return int(digits) if digits.isdigit() else 0
