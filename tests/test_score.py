from datetime import date

from blockapp import score

DAY = date(2026, 11, 9)


def ev(kind, **kw):
    return {"time": "2026-11-09T10:00:00", "kind": kind, **kw}


def stats(events):
    return score.daily_stats(events, [DAY])[0]


def test_perfect_day():
    assert stats([]).score == 100


def test_penalties_and_caps():
    s = stats([ev("blocked", app="discord.exe")] * 3 + [ev("skip")] + [ev("usage", app="discord.exe", seconds=1200)])
    # 3 attempts = -15, 1 skip = -10, 20 minutes = -10
    assert s.score == 65
    worst = stats([ev("blocked", app="x")] * 50 + [ev("skip")] * 5 + [ev("usage", app="x", seconds=99999)])
    assert worst.score == 0


def test_other_days_ignored():
    other = {"time": "2026-11-08T10:00:00", "kind": "blocked", "app": "x"}
    assert stats([other]).score == 100


def test_reports_render():
    s = stats([ev("usage", app="discord.exe", seconds=600)])
    assert "discord.exe: 10 min, 0 blocked opens" in score.report_today(s)
    assert "Average" in score.report_history([s])
