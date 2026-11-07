"""One issue's folder, data/YYYY-MM-DD/: where each of its files is, and reading and writing their JSON.

  candidates.json          what was fetched (daily.pipeline)
  digest.json              the main issue; digest.en.json its English edition
  digest.md                the main issue as it reads on GitHub (daily.render)
  digest.rejected.json     the digest `daily degrade` replaced
  digest.<channel>.<slug>.json, digest.en.<slug>.json
                           a per-model route's digest, kept as a beta, and its English edition
  trace.<key>.json         a route's trace (daily.trace)

How the per-route files are named is up to daily.routes; this module only puts them in the folder.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from daily import routes

CANDIDATES = "candidates.json"
DIGEST = "digest.json"
DIGEST_EN = "digest.en.json"
DIGEST_MD = "digest.md"
REJECTED = "digest.rejected.json"


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_if_exists(path: Path) -> Any:
    """The JSON at path; None if there is no file."""
    return read(path) if path.exists() else None


def try_read(path: Path) -> dict[str, Any] | None:
    """The JSON object at path; None if there is no file, or it is not JSON or not an object."""
    try:
        data = read(path)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


@dataclass(frozen=True)
class IssueDir:
    path: Path

    @classmethod
    def of(cls, data_dir: Path, issue_date: date | str) -> IssueDir:
        return cls(data_dir / str(issue_date))

    @property
    def date(self) -> str:
        return self.path.name

    @property
    def candidates(self) -> Path:
        return self.path / CANDIDATES

    @property
    def digest(self) -> Path:
        return self.path / DIGEST

    @property
    def digest_en(self) -> Path:
        return self.path / DIGEST_EN

    @property
    def markdown(self) -> Path:
        return self.path / DIGEST_MD

    @property
    def rejected(self) -> Path:
        return self.path / REJECTED

    def edition(self, en: bool) -> Path:
        """The main issue, or its English edition."""
        return self.digest_en if en else self.digest

    def beta(self, channel: str, model: str) -> Path:
        return self.path / routes.beta_name(channel, model)

    def beta_en(self, model: str) -> Path:
        return self.path / routes.en_beta_name(model)

    def keyed(self, kind: str, route_key: str) -> Path:
        """A route's own file by its key, digest or trace: trace.claude.json, digest.api.minimax.json."""
        return self.path / routes.file_name(kind, route_key)

    def trace(self, data: Any) -> Path | None:
        """The trace that goes with a digest (or a trace); None for a route without one."""
        name = routes.trace_name(data)
        return self.path / name if name is not None else None

    def route_trace(self, channel: str, model: str | None = None) -> Path:
        """The trace of a route that keeps one, by channel (and model, for a per-model route)."""
        path = self.trace({"channel": channel, "model": model})
        if path is None:
            raise ValueError(f"the {channel} route keeps no trace")
        return path

    def read_candidates(self) -> dict[str, Any]:
        return read(self.candidates)

    def read_digest(self) -> Any:
        """The main issue; None if there is none yet."""
        return read_if_exists(self.digest)
