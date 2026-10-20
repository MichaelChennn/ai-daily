"""Hugging Face Daily Papers and Trending Models. Noise filter adapted from Verita."""

from __future__ import annotations

from datetime import timedelta

import httpx

from daily.config import SourceConfig
from daily.fetchers.base import SUMMARY_MAX_CHARS, candidate, get
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


def is_noisy_model(repo_id: str) -> bool:
    normalized = repo_id.lower()
    return any(pattern in normalized for pattern in HF_NOISY_PATTERNS)


async def fetch_daily_papers(
    client: httpx.AsyncClient, source: SourceConfig, window: Window
) -> list[Candidate]:
    """Options: min_upvotes (default 0).

    Takes the Daily Papers list of the UTC day the window ends on, which is nearly complete when
    the ~05:00 Beijing run happens (21:00 UTC).
    """
    min_upvotes = int(source.options.get("min_upvotes", 0))
    day = (window.end - timedelta(minutes=1)).date().isoformat()
    response = await get(
        client, "https://huggingface.co/api/daily_papers", params={"date": day, "limit": 100}
    )

    items: list[Candidate] = []
    for entry in response.json():
        paper = entry.get("paper") or {}
        paper_id = paper.get("id")
        title = clean_title(paper.get("title") or entry.get("title"))
        upvotes = int(paper.get("upvotes") or 0)
        if not paper_id or not title or upvotes < min_upvotes:
            continue
        signals = {"upvotes": upvotes, "comments": int(entry.get("numComments") or 0)}
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
                url=f"https://huggingface.co/papers/{paper_id}",
                summary=truncate(clean_text(paper.get("summary") or entry.get("summary")), SUMMARY_MAX_CHARS),
                published_at=parse_datetime(paper.get("publishedAt")),
                published_precision="day",
                signals=signals,
                tags=[str(k) for k in (paper.get("ai_keywords") or [])][:8],
            )
        )
    return items


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
        if not repo_id or is_noisy_model(repo_id):
            continue
        created = parse_datetime(model.get("createdAt"))
        if created and window.end - created > max_age:
            continue
        tags = model.get("tags") or []
        details = [model.get("pipeline_tag"), model.get("library_name")]
        details += [t for t in tags if t.startswith("license:")]
        items.append(
            candidate(
                source,
                title=clean_title(repo_id),
                url=f"https://huggingface.co/{repo_id}",
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
