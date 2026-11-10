"""The Focus Score: how distracted you were on a given day, from 0 to 100.

Start at 100, then lose points for:
- each time a blocked app was opened during a focus session: 5 points (up to 40)
- each focus session you ended early with `skip`: 10 points (up to 20)
- each minute spent in your distracting apps outside sessions: 0.5 points (up to 40)
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from blockapp.storage import data_dir

ATTEMPT_POINTS, ATTEMPT_CAP = 5, 40
SKIP_POINTS, SKIP_CAP = 10, 20
MINUTE_POINTS, MINUTE_CAP = 0.5, 40


@dataclass
class DayStats:
    day: date
    attempts: int = 0
    skips: int = 0
    distracted_seconds: float = 0
    by_app: dict = field(default_factory=lambda: defaultdict(float))
    attempts_by_app: dict = field(default_factory=lambda: defaultdict(int))

    @property
    def distracted_minutes(self) -> float:
        return self.distracted_seconds / 60

    @property
    def penalties(self) -> dict:
        return {
            "attempts": min(ATTEMPT_CAP, self.attempts * ATTEMPT_POINTS),
            "skips": min(SKIP_CAP, self.skips * SKIP_POINTS),
            "time": min(MINUTE_CAP, self.distracted_minutes * MINUTE_POINTS),
        }

    @property
    def score(self) -> int:
        return max(0, round(100 - sum(self.penalties.values())))


def load_events() -> list[dict]:
    path = data_dir() / "events.jsonl"
    if not path.exists():
        return []
    events = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def daily_stats(events: list[dict], days: list[date]) -> list[DayStats]:
    stats = {d: DayStats(d) for d in days}
    for ev in events:
        try:
            d = datetime.fromisoformat(ev["time"]).date()
        except (KeyError, ValueError):
            continue
        s = stats.get(d)
        if s is None:
            continue
        kind = ev.get("kind")
        if kind == "blocked":
            s.attempts += 1
            s.attempts_by_app[ev.get("app", "?")] += 1
        elif kind == "skip":
            s.skips += 1
        elif kind == "usage":
            secs = float(ev.get("seconds", 0))
            s.distracted_seconds += secs
            s.by_app[ev.get("app", "?")] += secs
    return [stats[d] for d in days]


def last_days(n: int, today: date | None = None) -> list[date]:
    today = today or date.today()
    return [today - timedelta(days=i) for i in range(n - 1, -1, -1)]


def label(score: int) -> str:
    if score >= 90:
        return "Locked in"
    if score >= 70:
        return "Mostly focused"
    if score >= 50:
        return "Easily distracted"
    return "Very distracted"


def report_today(s: DayStats) -> str:
    p = s.penalties
    lines = [
        f"Focus Score today: {s.score}/100 ({label(s.score)})",
        "",
        f"  Tried to open blocked apps:  {s.attempts:>4}   -{p['attempts']:.0f}",
        f"  Sessions ended early:        {s.skips:>4}   -{p['skips']:.0f}",
        f"  Minutes in distracting apps: {s.distracted_minutes:>4.0f}   -{p['time']:.0f}",
    ]
    apps = set(s.by_app) | set(s.attempts_by_app)
    if apps:
        lines.append("")
        lines.append("  Biggest distractions:")
        ranked = sorted(apps, key=lambda a: -(s.by_app.get(a, 0) / 60 + s.attempts_by_app.get(a, 0)))
        for app in ranked[:5]:
            lines.append(f"    {app}: {s.by_app.get(app, 0) / 60:.0f} min, {s.attempts_by_app.get(app, 0)} blocked opens")
    return "\n".join(lines)


def report_history(stats: list[DayStats]) -> str:
    lines = ["Focus Score, last %d days:" % len(stats), ""]
    for s in stats:
        bar = "#" * (s.score // 5)
        lines.append(f"  {s.day:%a %d %b}  {s.score:>3}  {bar}")
    avg = sum(s.score for s in stats) / len(stats)
    lines += ["", f"  Average: {avg:.0f}"]
    return "\n".join(lines)
