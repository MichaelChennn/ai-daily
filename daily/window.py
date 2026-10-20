"""The time window an issue covers.

Issue D is published at 06:00 Beijing time and covers the 24 hours before that. Fetch runs at
05:30, so the window is extended one hour backwards to catch what the previous run could not see
yet (published 05:30-06:00); the overlap is harmless because cross-day dedup marks repeats.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

BEIJING = timezone(timedelta(hours=8), "Asia/Shanghai")
PUBLISH_TIME = time(6, 0)
COVERAGE = timedelta(hours=24)
OVERLAP = timedelta(hours=1)


@dataclass(frozen=True)
class Window:
    issue_date: date
    start: datetime  # UTC, inclusive
    end: datetime  # UTC, exclusive

    def contains(self, value: datetime | None, precision: str = "second") -> bool:
        if value is None:
            return False
        if precision == "day":
            # Day-precision dates (e.g. "Oct 6, 2026") have no timezone; accept any calendar day
            # the window touches, in either UTC or Beijing time.
            day = value.date()
            days = {
                self.start.date(),
                self.end.date(),
                self.start.astimezone(BEIJING).date(),
                self.end.astimezone(BEIJING).date(),
            }
            return day in days
        return self.start <= value < self.end


def beijing_today(now: datetime | None = None) -> date:
    return (now or datetime.now(timezone.utc)).astimezone(BEIJING).date()


def issue_window(issue_date: date, now: datetime | None = None) -> Window:
    publish_at = datetime.combine(issue_date, PUBLISH_TIME, BEIJING).astimezone(timezone.utc)
    end = min(publish_at, (now or datetime.now(timezone.utc)).astimezone(timezone.utc))
    start = publish_at - COVERAGE - OVERLAP
    return Window(issue_date=issue_date, start=start, end=end)
