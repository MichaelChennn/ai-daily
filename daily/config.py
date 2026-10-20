"""Load the source whitelist (sources.yaml)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from daily.models import KINDS

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES_FILE = ROOT / "sources.yaml"
DEFAULT_DATA_DIR = ROOT / "data"


@dataclass
class SourceConfig:
    id: str
    type: str
    name: str
    tier: int
    kind: str
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)


def load_sources(path: Path = DEFAULT_SOURCES_FILE) -> list[SourceConfig]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources: list[SourceConfig] = []
    seen: set[str] = set()
    for entry in raw.get("sources", []):
        entry = dict(entry)
        try:
            source = SourceConfig(
                id=entry.pop("id"),
                type=entry.pop("type"),
                name=entry.pop("name"),
                tier=int(entry.pop("tier")),
                kind=entry.pop("kind"),
                enabled=bool(entry.pop("enabled", True)),
                options=entry,
            )
        except KeyError as exc:
            raise ValueError(f"{path}: source entry missing field {exc}: {entry}") from exc
        if not isinstance(source.id, str):
            raise ValueError(f"{path}: source id {source.id!r} must be a string (quote it)")
        if source.id in seen:
            raise ValueError(f"{path}: duplicate source id {source.id!r}")
        if source.kind not in KINDS:
            raise ValueError(f"{path}: source {source.id!r} has unknown kind {source.kind!r}")
        if source.tier not in (1, 2):
            raise ValueError(f"{path}: source {source.id!r} tier must be 1 or 2")
        seen.add(source.id)
        sources.append(source)
    return sources
