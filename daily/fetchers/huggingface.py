"""Hugging Face Daily Papers and Trending Models. Noise filter adapted from Verita."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, filtered, get
from daily.models import Candidate
from daily.text import clean_text, clean_title, parse_datetime, truncate
from daily.window import Window

# Derivative uploads (quantizations, merges, adapters) that rarely deserve a digest slot.
HF_NOISY_PATTERNS = [
    "gguf",
    "quantized",
    "awq",
    "gptq",
    "lora",
    "adapter",
    "merge",
    "fp16",
    "fp8",
    "fp4",  # also matches nvfp4 / mxfp4
    "int4",
    "int8",
    "4bit",
    "8bit",
    "mlx",
    "exl2",
    "bnb",
    "abliterated",
    "uncensored",
]


def noisy_pattern(repo_id: str) -> str | None:
    """The first noise pattern in the repo id, if any."""
    normalized = repo_id.lower()
    return next((pattern for pattern in HF_NOISY_PATTERNS if pattern in normalized), None)


def is_noisy_model(repo_id: str) -> bool:
    return noisy_pattern(repo_id) is not None


async def fetch_daily_papers(
    client: httpx.AsyncClient, source: SourceConfig, window: Window
) -> list[Candidate]:
    """Options: min_upvotes (default 0); week_fallback_limit (default none).

    Takes the Daily Papers list of the last UTC day that is complete, or nearly so, when the
    window ends: the 05:07 Berlin run happens at 03:07 / 04:07 UTC, so that is the day before.
    Papers listed later on the same UTC day are picked up by the next issue.

    HF lists nothing on weekends and some holidays. For such a day, week_fallback_limit takes that
    many of the highest-voted papers of its ISO week instead, marked with `signals.week`; the ones
    an issue already published are dropped by dedup, so the next empty day gets the next ones.
    """
    min_upvotes = int(source.options.get("min_upvotes", 0))
    day = (window.end - timedelta(hours=12)).date()
    response = await get(
        client, "https://huggingface.co/api/daily_papers", params={"date": day.isoformat(), "limit": 100}
    )
    entries = response.json()

    week: str | None = None
    if not entries and (week_limit := source.options.get("week_fallback_limit")):
        year, number, _ = day.isocalendar()
        week = f"{year}-W{number:02d}"
        response = await get(
            client, "https://huggingface.co/api/daily_papers", params={"week": week, "limit": 100}
        )
        entries = sorted(response.json(), key=_upvotes, reverse=True)[: int(week_limit)]

    items: list[Candidate] = []
    for entry in entries:
        paper = entry.get("paper") or {}
        paper_id = paper.get("id")
        title = clean_title(paper.get("title") or entry.get("title"))
        upvotes = _upvotes(entry)
        if not paper_id or not title:
            continue
        url = f"https://huggingface.co/papers/{paper_id}"
        if upvotes < min_upvotes:
            filtered(source, "min_upvotes", title, url, f"upvotes {upvotes} < {min_upvotes}")
            continue
        signals = {"upvotes": upvotes, "comments": int(entry.get("numComments") or 0)}
        if week:
            signals["week"] = week
        if paper.get("githubRepo"):
            signals["github_repo"] = paper["githubRepo"]
            signals["github_stars"] = int(paper.get("githubStars") or 0)
        org = (paper.get("organization") or entry.get("organization") or {}).get("fullname")
        if org:
            signals["organization"] = org
        items.append(
            candidate(
                source,
                title=title,
                url=url,
                summary=truncate(clean_text(paper.get("summary") or entry.get("summary")), SUMMARY_MAX_CHARS),
                published_at=parse_datetime(paper.get("publishedAt")),
                published_precision="day",
                signals=signals,
                tags=[str(k) for k in (paper.get("ai_keywords") or [])][:8],
            )
        )
    return items


def _upvotes(entry: dict[str, Any]) -> int:
    return int((entry.get("paper") or {}).get("upvotes") or 0)


async def fetch_trending_models(
    client: httpx.AsyncClient, source: SourceConfig, window: Window
) -> list[Candidate]:
    """Options: limit (default 50), max_age_days (default 14; older models still trending are skipped)."""
    limit = int(source.options.get("limit", 50))
    max_age = timedelta(days=int(source.options.get("max_age_days", 14)))
    response = await get(
        client, "https://huggingface.co/api/models", params={"sort": "trendingScore", "limit": limit}
    )

    items: list[Candidate] = []
    for rank, model in enumerate(response.json(), start=1):
        repo_id = model.get("id") or model.get("modelId")
        if not repo_id:
            continue
        url = f"https://huggingface.co/{repo_id}"
        if noise := noisy_pattern(repo_id):
            filtered(source, "noisy_model", repo_id, url, f"repo id contains {noise}")
            continue
        created = parse_datetime(model.get("createdAt"))
        if created and window.end - created > max_age:
            age = (window.end - created).days
            filtered(source, "max_age_days", repo_id, url, f"{age} days old > {max_age.days}")
            continue
        tags = model.get("tags") or []
        details = [model.get("pipeline_tag"), model.get("library_name")]
        details += [t for t in tags if t.startswith("license:")]
        items.append(
            candidate(
                source,
                title=clean_title(repo_id),
                url=url,
                summary=", ".join(d for d in details if d),
                published_at=created,
                signals={
                    "trending_rank": rank,
                    "trending_score": model.get("trendingScore"),
                    "likes": model.get("likes"),
                    "downloads": model.get("downloads"),
                },
                tags=[repo_id.split("/", 1)[0]],
            )
        )
    return items
