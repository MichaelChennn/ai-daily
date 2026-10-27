"""`daily adopt`: decide whether a digest from an editor route replaces the one on main.

The Claude editor runs in a cloud session that can only push to its own claude/ branch;
.github/workflows/ingest.yml hands each digest.json it pushes to `adopt`. The rules match the
skill's: an edited issue is never replaced by a fallback, a fallback is replaced by any valid
digest (the editor finishing after the 06:30 fallback), and an edited issue is only replaced by
a newer edit (an explicit redo).

The API route (.github/workflows/editor-api.yml, daily.api_editor) hands its digests here too,
so the main issue goes Claude route > API route > fallback: a Claude edit always replaces an API
edit, and an API edit never replaces any edit, whichever was written first.

The English edition (digest.en.json, `daily adopt --en`) goes with the main issue: it is written
by the route that wrote the main issue (docs/adr/0001-two-editor-routes.md), so one from the other
route, or for a fallback, is not taken.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from daily import digest


def decide(current: Any, incoming: Any, candidates: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    """Returns (digest to write, reason); None leaves the current digest as it is."""
    report = digest.validate(incoming, candidates)
    if report.errors:
        return None, f"incoming digest is not valid: {report.errors[0]}"
    if report.item_errors:  # the editor skipped --drop-invalid: drop the items it would have
        incoming = digest.apply_report(incoming, report, checked_links=False)
    # Validating also fills in the candidate urls an editor left out, so compare after it.
    current_ok = current is not None and digest.validate(current, candidates).ok
    if current == incoming:
        return None, "unchanged"
    if not current_ok:
        return incoming, "no valid digest yet"
    if current.get("mode") == "fallback":
        return incoming, "replaces the fallback"
    if incoming.get("mode") == "fallback":
        return None, "keeping the edited issue over a fallback"
    if digest.is_api(current) and not digest.is_api(incoming):
        return incoming, "a Claude edit replaces the API edit"
    if digest.is_api(incoming):
        return None, "keeping the edited issue over an API edit"
    if _time(incoming) > _time(current):
        return incoming, "newer edit"
    return None, "the current edit is newer"


def decide_en(
    main: Any, current: Any, incoming: Any, candidates: dict[str, Any]
) -> tuple[dict[str, Any] | None, str]:
    """Like decide(), for the English edition of the main issue `main`."""
    if not isinstance(incoming, dict) or incoming.get("lang") != "en":
        return None, "incoming digest is not an English edition"
    report = digest.validate(incoming, candidates)
    if report.errors:
        return None, f"incoming digest is not valid: {report.errors[0]}"
    if report.item_errors:
        incoming = digest.apply_report(incoming, report, checked_links=False)
    if (mismatch := goes_with(main, incoming, candidates)) is not None:
        return None, mismatch
    if current == incoming:
        return None, "unchanged"
    if (
        isinstance(current, dict)
        and current.get("lang") == "en"
        and goes_with(main, current, candidates) is None
        and digest.validate(current, candidates).ok
        and _time(current) >= _time(incoming)
    ):
        return None, "the current English edition is newer"
    return incoming, "English edition of the main issue"


def goes_with(main: Any, en: dict[str, Any], candidates: dict[str, Any]) -> str | None:
    """Why the English edition en cannot go with the main issue; None if it can."""
    if not isinstance(main, dict) or digest.validate(main, candidates).errors:
        return "no main issue to go with"
    if main.get("mode") != "full":
        return "the main issue is a fallback"
    if digest.is_api(main) != digest.is_api(en):
        return "the main issue comes from the other route"
    return None


def _time(data: dict[str, Any]) -> datetime:
    try:
        value = datetime.fromisoformat(data["generated_at"])
    except (KeyError, TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
