from datetime import datetime

import pytest

from blockapp import schedule


@pytest.fixture(autouse=True)
def temp_home(tmp_path, monkeypatch):
    monkeypatch.setenv("BLOCKAPP_HOME", str(tmp_path))


def test_parse_days():
    assert schedule.parse_days("weekdays") == ["mon", "tue", "wed", "thu", "fri"]
    assert schedule.parse_days("mon-wed") == ["mon", "tue", "wed"]
    assert schedule.parse_days("fri-mon") == ["mon", "fri", "sat", "sun"]
    assert schedule.parse_days("Monday,Friday") == ["mon", "fri"]
    with pytest.raises(ValueError):
        schedule.parse_days("funday")


# 2026-11-09 is a Monday.
MON_10 = datetime(2026, 11, 9, 10, 0)


def test_active_in_window():
    entry = {"days": ["mon"], "start": "09:00", "end": "12:00"}
    assert schedule.active_until(entry, MON_10) == datetime(2026, 11, 9, 12, 0)
    assert schedule.active_until(entry, datetime(2026, 11, 9, 12, 0)) is None
    assert schedule.active_until(entry, datetime(2026, 11, 10, 10, 0)) is None


def test_overnight_window():
    entry = {"days": ["mon"], "start": "22:00", "end": "06:00"}
    assert schedule.active_until(entry, datetime(2026, 11, 10, 2, 0)) == datetime(2026, 11, 10, 6, 0)
    assert schedule.active_until(entry, datetime(2026, 11, 9, 2, 0)) is None


def test_add_list_remove_and_skip():
    schedule.add_schedule("mon", "09:00", "12:00")
    assert schedule.describe(schedule.schedules()[0]) == "Mondays, 9:00 AM to 12:00 PM"
    assert schedule.skip_current(MON_10) == datetime(2026, 11, 9, 12, 0)
    from blockapp.storage import load_config
    assert schedule.is_skipped(MON_10, load_config())
    assert not schedule.is_skipped(datetime(2026, 11, 9, 12, 0), load_config())
    schedule.remove_schedule(1)
    assert schedule.schedules() == []


def test_start_focus_now_and_skip():
    from blockapp.storage import load_config
    end = schedule.start_focus(25, MON_10)
    assert schedule.session_end(MON_10, load_config()) == end
    assert schedule.skip_current(MON_10) == end
    config = load_config()
    assert "focus_until" not in config and schedule.is_skipped(MON_10, config)
    with pytest.raises(ValueError):
        schedule.start_focus(0, MON_10)
