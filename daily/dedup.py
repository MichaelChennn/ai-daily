"""Dedup in three layers.

1. Same thing, different URL spelling: URLs are reduced to a canonical key (tracking params,
   www., trailing slashes, arXiv abs/pdf/versions, HF paper pages...). Candidates sharing a key
   are merged into one; the best-tier record wins and the others are kept in `also_from`, with
   their signals (HN points, upvotes...) folded in.
2. Same event, different pages: titles are compared (token overlap + shared model names) and
   similar candidates get the same `cluster_id`. Clusters are hints for the editor, not merges.
3. Across days: keys seen in the last N days of candidates are recorded in `seen_on`; keys that
   were already published in a digest are dropped.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from daily.models import Candidate

# ---------------------------------------------------------------- 1. URL keys

TRACKING_PARAMS = {
    "ref",
    "ref_src",
    "ref_url",
    "source",
    "src",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "igshid",
    "s",
    "si",
    "trk",
    "cmpid",
    "_hsenc",
    "_hsmi",
    "mkt_tok",
    "spm",
    "share",
    "from",
}
_ARXIV_ID = r"(\d{4}\.\d{4,5})(?:v\d+)?"
_ARXIV_PATH = re.compile(rf"^/(?:abs|pdf|html)/{_ARXIV_ID}(?:\.pdf)?/?$")
_HF_PAPER_PATH = re.compile(rf"^/papers/{_ARXIV_ID}/?$")


def canonical_url(url: str) -> str:
    """Normalized URL suitable for display and comparison."""
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    for prefix in ("www.", "m.", "mobile."):
        if host.startswith(prefix):
            host = host[len(prefix) :]
    if parts.port and parts.port not in (80, 443):
        host = f"{host}:{parts.port}"
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    path = re.sub(r"/index\.html?$", "/", path)
    if len(path) > 1:
        path = path.rstrip("/")
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.lower().startswith("utm_") and k.lower() not in TRACKING_PARAMS
    ]
    return urlunsplit(("https", host, path, urlencode(sorted(query)), ""))


def url_key(url: str) -> str:
    """Identity key: different URLs for the same document map to the same key."""
    canonical = canonical_url(url)
    parts = urlsplit(canonical)
    host, path = parts.hostname or "", parts.path
    if host in ("arxiv.org", "export.arxiv.org") and (m := _ARXIV_PATH.match(path)):
        return f"arxiv:{m.group(1)}"
    if host == "huggingface.co" and (m := _HF_PAPER_PATH.match(path)):
        return f"arxiv:{m.group(1)}"
    if host in ("github.com", "huggingface.co"):
        # Repo and model ids are case-insensitive.
        path = path.lower()
    return f"{host}{path}" + (f"?{parts.query}" if parts.query else "")


def candidate_id(key: str) -> str:
    return "c_" + hashlib.sha1(key.encode()).hexdigest()[:10]


def merge_by_url(items: Iterable[Candidate], source_order: dict[str, int]) -> list[Candidate]:
    groups: dict[str, list[Candidate]] = {}
    for item in items:
        groups.setdefault(url_key(item.url), []).append(item)

    merged: list[Candidate] = []
    for key, group in groups.items():
        group.sort(
            key=lambda c: (c.tier, c.kind == "discussion", source_order.get(c.source, 999), -len(c.summary))
        )
        primary, rest = group[0], group[1:]
        primary.key = key
        primary.id = candidate_id(key)
        primary.url = canonical_url(primary.url) if key.startswith("arxiv:") else primary.url
        for other in rest:
            primary.also_from.append(
                {
                    "source": other.source,
                    "source_name": other.source_name,
                    "title": other.title,
                    "url": other.url,
                    **({"discussion_url": other.discussion_url} if other.discussion_url else {}),
                }
            )
            for name, value in other.signals.items():
                primary.signals.setdefault(name, value)
            if not primary.discussion_url and other.discussion_url:
                primary.discussion_url = other.discussion_url
            if not primary.summary and other.summary:
                primary.summary = other.summary
            if primary.published_at is None and other.published_at is not None:
                primary.published_at = other.published_at
                primary.published_precision = other.published_precision
            primary.tags.extend(t for t in other.tags if t not in primary.tags)
        merged.append(primary)
    return merged


# ---------------------------------------------------------------- 2. title clusters

STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "of",
    "for",
    "to",
    "in",
    "on",
    "with",
    "by",
    "at",
    "from",
    "via",
    "is",
    "are",
    "be",
    "as",
    "its",
    "it",
    "this",
    "that",
    "new",
    "now",
    "our",
    "we",
    "you",
    "your",
    "how",
    "what",
    "why",
    "introducing",
    "announcing",
    "launch",
    "launches",
    "released",
    "release",
    "releases",
    "available",
    "today",
    "show",
    "hn",
    "ask",
    "vs",
    "using",
    "use",
    "towards",
    "toward",
}
_TOKEN = re.compile(r"[a-z0-9]+(?:\.[0-9]+)*|[\u4e00-\u9fff]+")
# Model / product names with a version: gpt-6, qwen3.5, deepseek-v4.1, llama 4, claude opus 5.5.
_ENTITY = re.compile(r"\b([a-z]{2,})[\s-]?(v?\d+(?:\.\d+)*[a-z]?)\b")
_YEAR = re.compile(r"^(19|20)\d\d$")

JACCARD_ALONE = 0.5
JACCARD_WITH_ENTITY = 0.2


def _entity(match: re.Match[str]) -> str | None:
    name, version = match.groups()
    if name in STOPWORDS or _YEAR.match(version):
        return None
    return name + version


def _join_entities(title: str) -> str:
    """'GPT-6' / 'Qwen 3.5' -> 'gpt6' / 'qwen3.5', so a name and its version form one token."""
    return _ENTITY.sub(lambda m: _entity(m) or m.group(0), title.lower())


def title_tokens(title: str) -> set[str]:
    tokens: set[str] = set()
    for token in _TOKEN.findall(_join_entities(title)):
        if "\u4e00" <= token[0] <= "\u9fff":
            tokens.update(token[i : i + 2] for i in range(max(1, len(token) - 1)))
        elif token not in STOPWORDS and (len(token) > 1 or token.isdigit()):
            tokens.add(token)
    return tokens


def title_entities(title: str) -> set[str]:
    return {e for m in _ENTITY.finditer(title.lower()) if (e := _entity(m))}


def similar(a: Candidate, b: Candidate) -> bool:
    ta, tb = title_tokens(a.title), title_tokens(b.title)
    if not ta or not tb:
        return False
    jaccard = len(ta & tb) / len(ta | tb)
    if jaccard >= JACCARD_ALONE:
        return True
    return jaccard >= JACCARD_WITH_ENTITY and bool(title_entities(a.title) & title_entities(b.title))


def assign_clusters(items: list[Candidate]) -> list[dict[str, Any]]:
    """Set cluster_id on every candidate; return the multi-member clusters."""
    parent = list(range(len(items)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if find(i) != find(j) and similar(items[i], items[j]):
                parent[find(j)] = find(i)

    members: dict[int, list[Candidate]] = {}
    for i, item in enumerate(items):
        members.setdefault(find(i), []).append(item)

    clusters = []
    for group in members.values():
        group.sort(key=lambda c: (c.tier, c.kind == "discussion"))
        cluster_id = "k_" + group[0].id.removeprefix("c_")
        for item in group:
            item.cluster_id = cluster_id
        if len(group) > 1:
            clusters.append(
                {"id": cluster_id, "title": group[0].title, "candidate_ids": [c.id for c in group]}
            )
    return clusters


# ---------------------------------------------------------------- 3. history


@dataclass
class History:
    seen: dict[str, list[str]]  # key -> dates it appeared as a candidate
    published: dict[str, str]  # key -> date it was published in a digest


def load_history(data_dir: Path, issue_date: date, days: int = 7) -> History:
    seen: dict[str, list[str]] = {}
    published: dict[str, str] = {}
    for offset in range(days, 0, -1):
        day = (issue_date - timedelta(days=offset)).isoformat()
        day_dir = data_dir / day
        candidates_file = day_dir / "candidates.json"
        if candidates_file.exists():
            for item in json.loads(candidates_file.read_text(encoding="utf-8")).get("candidates", []):
                for url in [item.get("url"), *(a.get("url") for a in item.get("also_from", []))]:
                    if url:
                        seen.setdefault(url_key(url), []).append(day)
        digest_file = day_dir / "digest.json"
        if digest_file.exists():
            from daily.digest import published_urls  # deferred: digest imports dedup

            for url in published_urls(json.loads(digest_file.read_text(encoding="utf-8"))):
                published.setdefault(url_key(url), day)
    return History(seen={k: sorted(set(v)) for k, v in seen.items()}, published=published)


def apply_history(items: list[Candidate], history: History) -> tuple[list[Candidate], list[dict[str, str]]]:
    """Drop already-published candidates; annotate the rest with the days they were seen."""
    kept: list[Candidate] = []
    dropped: list[dict[str, str]] = []
    for item in items:
        keys = [item.key, *(url_key(a["url"]) for a in item.also_from)]
        published_on = next((history.published[k] for k in keys if k in history.published), None)
        if published_on:
            dropped.append(
                {"id": item.id, "title": item.title, "url": item.url, "published_on": published_on}
            )
            continue
        item.seen_on = sorted({d for k in keys for d in history.seen.get(k, [])})
        kept.append(item)
    return kept, dropped
