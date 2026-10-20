from datetime import date, datetime, timezone

import pytest

from daily.window import beijing_today, issue_window
from tests.conftest import ISSUE


def test_window_covers_26_hours_before_6am_beijing():
    w = issue_window(ISSUE, now=datetime(2026, 10, 21, tzinfo=timezone.utc))
    assert w.start == datetime(2026, 10, 18, 20, 0, tzinfo=timezone.utc)
    assert w.end == datetime(2026, 10, 19, 22, 0, tzinfo=timezone.utc)


def test_window_is_clipped_to_now_for_the_0500_run():
    now = datetime(2026, 10, 19, 21, 7, tzinfo=timezone.utc)  # 05:07 Beijing
    w = issue_window(ISSUE, now=now)
    assert w.end == now
    assert not w.contains(datetime(2026, 10, 19, 21, 45, tzinfo=timezone.utc))


@pytest.mark.parametrize("run_at_utc", [(20, 1), (21, 7), (21, 59)])  # 04:01 .. 05:59 Beijing
def test_consecutive_windows_leave_no_gap_for_any_run_after_0400(run_at_utc):
    hour, minute = run_at_utc
    today = issue_window(ISSUE, now=datetime(2026, 10, 19, hour, minute, tzinfo=timezone.utc))
    tomorrow = issue_window(date(2026, 10, 21), now=datetime(2026, 10, 20, hour, minute, tzinfo=timezone.utc))
    assert tomorrow.start <= today.end


def test_day_precision_matches_calendar_days(window):
    assert window.contains(datetime(2026, 10, 19, tzinfo=timezone.utc), "day")
    assert window.contains(datetime(2026, 10, 20, tzinfo=timezone.utc), "day")  # Beijing date
    assert not window.contains(datetime(2026, 10, 16, tzinfo=timezone.utc), "day")


def test_beijing_today_rolls_over_at_16_utc():
    assert beijing_today(datetime(2026, 10, 20, 15, 59, tzinfo=timezone.utc)) == date(2026, 10, 20)
    assert beijing_today(datetime(2026, 10, 20, 16, 0, tzinfo=timezone.utc)) == date(2026, 10, 21)
