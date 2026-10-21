"""`daily adopt`: decide whether a digest pushed from an editor branch replaces the one on main.

The Claude editor runs in a cloud session that can only push to its own claude/ branch;
.github/workflows/ingest.yml hands each digest.json it pushes to `adopt`. The rules match the
skill's: an edited issue is never replaced by a fallback, a fallback is replaced by any valid
digest (the editor finishing after the 06:30 fallback), and an edited issue is only replaced by
a newer edit (an explicit redo).
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
    if _time(incoming) > _time(current):
        return incoming, "newer edit"
    return None, "the current edit is newer"


def _time(data: dict[str, Any]) -> datetime:
    try:
        value = datetime.fromisoformat(data["generated_at"])
    except (KeyError, TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
