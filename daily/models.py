"""Data model shared by fetchers, dedup and the candidates.json writer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

# What kind of thing a candidate is; the editor uses it to pick a digest section.
KINDS = {"blog", "paper", "release", "model", "repo", "discussion"}


@dataclass
class Candidate:
    """One normalized item from one source. Fetchers produce these; dedup merges them."""

    source: str  # source id from sources.yaml, e.g. "openai-blog"
    source_name: str
    tier: int  # 1 = first-hand, 2 = community signal
    kind: str
    title: str
    url: str
    summary: str = ""
    published_at: datetime | None = None
    # "second" for real timestamps; "day" when the source only gives a calendar date.
    published_precision: str = "second"
    discussion_url: str | None = None
    signals: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    # Filled in by dedup.
    id: str = ""
    key: str = ""
    cluster_id: str = ""
    also_from: list[dict[str, Any]] = field(default_factory=list)
    seen_on: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["published_at"] = self.published_at.isoformat() if self.published_at else None
        return data


@dataclass
class FetchError:
    source: str
    message: str


@dataclass
class SourceResult:
    source: str
    items: list[Candidate]
    error: FetchError | None = None
