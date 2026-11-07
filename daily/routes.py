"""The editor routes: who can write an issue, and what follows from it (docs/adr/0001-two-editor-routes.md).

Every digest names the route that wrote it in its `channel`; a digest without one, or with a channel
not in ROUTES, is not valid. Everything else that depends on the route asks this table: which digest
becomes the main issue (publish), the trace file a route writes and where its betas are (issue, site,
export, process). A new route is a new row here.

  priority  the main issue goes to the route ranked highest: Claude > API > fallback
  redo      a newer digest from the same route replaces the current one (an explicit redo); the
            API route's models do not replace each other, the first one in stays
  per_model one digest per model family, kept as a beta next to the main issue
            (digest.<channel>.<slug>.json) and traced as trace.<channel>.<slug>.json;
            otherwise the route writes digest.json and traces as trace.<channel>.json
  traced    the route records a trace (the fallback does not)
  betas     slug -> the label the site shows for that model family's beta; a slug without a label
            is shown as it is. Kept for families that no longer run, so their old betas still read well.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Route:
    channel: str
    label: str
    mode: str  # the digest mode the route writes
    priority: int
    redo: bool
    per_model: bool
    traced: bool
    # How adopt's reasons name this route's digest (the process page maps the reasons to text).
    noun: str
    a_noun: str
    betas: dict[str, str] = field(default_factory=dict)

    def beta_label(self, slug: str) -> str:
        return self.betas.get(slug, slug)


ROUTES = {
    route.channel: route
    for route in (
        Route("claude", "Claude", "full", 2, redo=True, per_model=False, traced=True,
              noun="Claude edit", a_noun="a Claude edit"),
        Route("api", "API", "full", 1, redo=False, per_model=True, traced=True,
              noun="API edit", a_noun="an API edit",
              # gemini: the Google AI Studio route, removed on 2026-11-05; its betas up to 2026-11-03
              # are still in data/.
              betas={"deepseek": "DeepSeek", "gemini": "Gemini", "minimax": "MiniMax"}),
        Route("fallback", "降级版", "fallback", 0, redo=True, per_model=False, traced=False,
              noun="fallback", a_noun="a fallback"),
    )
}  # fmt: skip


# The routes whose editor works through the CLI by SKILL.md (scores, self-check, validate rounds),
# as the Claude route does; `daily trace` and `daily degrade --force` take one of them.
SKILL_ROUTES = tuple(r.channel for r in ROUTES.values() if r.traced and not r.per_model)


def of(digest: Any) -> Route | None:
    """The route that wrote a digest (or a trace); None if it names none we know."""
    channel = digest.get("channel") if isinstance(digest, dict) else None
    return ROUTES.get(channel) if isinstance(channel, str) else None


def check(digest: dict[str, Any]) -> str | None:
    """Why a digest's channel is not valid; None if it is."""
    route = of(digest)
    if route is None:
        return f"channel {digest.get('channel')!r} is missing or unknown: must be one of {tuple(ROUTES)}"
    if digest.get("mode") != route.mode:
        return f"the {route.channel} route writes mode {route.mode!r}, not {digest.get('mode')!r}"
    if route.per_model and not slug(str(digest.get("model") or "")):
        return f"the {route.channel} route needs the model that wrote it"
    return None


def slug(model: str) -> str:
    """A model family's slug, from the model: nvidia:deepseek-ai/deepseek-v4.1-flash -> deepseek, for
    digest.api.<slug>.json. So EDITOR_API_MODEL holds at most one model per family."""
    return model.partition(":")[2].rsplit("/", 1)[-1].split("-", 1)[0].lower()


def key(digest: Any) -> str | None:
    """Which run of which route: "claude", "api.minimax", "fallback"; None for an unknown route."""
    route = of(digest)
    if route is None:
        return None
    return f"{route.channel}.{slug(str(digest.get('model') or ''))}" if route.per_model else route.channel


def is_api(digest: Any) -> bool:
    """Written by one of the per-model routes, whose model is part of what it is."""
    route = of(digest)
    return route is not None and route.per_model


def file_name(kind: str, route_key: str) -> str:
    """A route's own file, by its key: ("trace", "claude") -> trace.claude.json,
    ("digest", "api.minimax") -> digest.api.minimax.json."""
    return f"{kind}.{route_key}.json"


def trace_name(digest: Any) -> str | None:
    """The trace that goes with a digest (or a trace); None for a route without one."""
    route = of(digest)
    if route is None or not route.traced:
        return None
    return file_name("trace", str(key(digest)))


def beta_name(channel: str, model: str) -> str:
    return file_name("digest", f"{channel}.{slug(model)}")


def en_beta_name(model: str) -> str:
    """The English edition a per-model route writes for its beta, before adopt takes it as
    digest.en.json. Named by the model family alone, as it has been since the first one."""
    return f"digest.en.{slug(model)}.json"


def keyed_files(issue_dir: Path, kind: str) -> dict[str, Path]:
    """The per-model files of an issue, digest or trace, by key ("api.minimax")."""
    found: dict[str, Path] = {}
    for route in ROUTES.values():
        if not route.per_model:
            continue
        for path in sorted(issue_dir.glob(f"{kind}.{route.channel}.*.json")):
            found[path.name.removeprefix(f"{kind}.").removesuffix(".json")] = path
    return found


def route_of_key(route_key: str) -> tuple[Route, str] | None:
    """("api.minimax") -> (the API route, "minimax"); ("claude") -> (the Claude route, "")."""
    channel, _, model_slug = route_key.partition(".")
    route = ROUTES.get(channel)
    return (route, model_slug) if route is not None else None


def label(route_key: str) -> str:
    """What the site calls a route's run: "Claude", "MiniMax"."""
    found = route_of_key(route_key)
    if found is None:
        return route_key
    route, model_slug = found
    return route.beta_label(model_slug) if route.per_model else route.label
