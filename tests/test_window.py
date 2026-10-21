from datetime import date, datetime, timezone

import pytest

from daily.window import issue_window, local_today
from tests.conftest import ISSUE


def test_window_covers_26_hours_before_6am_berlin():
    w = issue_window(ISSUE, now=datetime(2026, 10, 21, tzinfo=timezone.utc))
    assert w.start == datetime(2026, 10, 19, 2, 0, tzinfo=timezone.utc)  # 04:00 CEST the day before
    assert w.end == datetime(2026, 10, 20, 4, 0, tzinfo=timezone.utc)  # 06:00 CEST


def test_window_follows_daylight_saving():
    # 2026-10-25: CEST ends. Issue 10-26 is published at 06:00 CET = 05:00 UTC.
    w = issue_window(date(2026, 10, 26), now=datetime(2026, 10, 27, tzinfo=timezone.utc))
    assert w.end == datetime(2026, 10, 26, 5, 0, tzinfo=timezone.utc)
    assert w.start == datetime(2026, 10, 25, 3, 0, tzinfo=timezone.utc)  # 04:00 CET


def test_window_is_clipped_to_now_for_the_0500_run():
    now = datetime(2026, 10, 20, 3, 7, tzinfo=timezone.utc)  # 05:07 Berlin
    w = issue_window(ISSUE, now=now)
    assert w.end == now
    assert not w.contains(datetime(2026, 10, 20, 3, 45, tzinfo=timezone.utc))


@pytest.mark.parametrize("run_at_utc", [(2, 1), (3, 7), (3, 59)])  # 04:01 .. 05:59 Berlin
def test_consecutive_windows_leave_no_gap_for_any_run_after_0400(run_at_utc):
    hour, minute = run_at_utc
    today = issue_window(ISSUE, now=datetime(2026, 10, 20, hour, minute, tzinfo=timezone.utc))
    tomorrow = issue_window(date(2026, 10, 21), now=datetime(2026, 10, 21, hour, minute, tzinfo=timezone.utc))
    assert tomorrow.start <= today.end


def test_day_precision_matches_calendar_days(window):
    assert window.contains(datetime(2026, 10, 19, tzinfo=timezone.utc), "day")
    assert window.contains(datetime(2026, 10, 20, tzinfo=timezone.utc), "day")
    assert not window.contains(datetime(2026, 10, 16, tzinfo=timezone.utc), "day")


def test_local_today_rolls_over_at_berlin_midnight():
    assert local_today(datetime(2026, 10, 20, 21, 59, tzinfo=timezone.utc)) == date(2026, 10, 20)  # CEST
    assert local_today(datetime(2026, 10, 20, 22, 0, tzinfo=timezone.utc)) == date(2026, 10, 21)
    assert local_today(datetime(2026, 12, 20, 22, 59, tzinfo=timezone.utc)) == date(2026, 12, 20)  # CET
