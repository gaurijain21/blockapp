"""Recurring focus sessions, e.g. weekdays 09:00-12:00."""

from __future__ import annotations

from datetime import datetime, time, timedelta

from blockapp.storage import load_config, save_config

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_GROUPS = {"weekdays": DAYS[:5], "weekends": DAYS[5:], "everyday": DAYS, "daily": DAYS}


def parse_days(text: str) -> list[str]:
    """'mon-fri', 'weekdays', 'mon,wed,fri' or 'sat-sun' -> list of day codes."""
    text = text.strip().lower()
    if text in DAY_GROUPS:
        return list(DAY_GROUPS[text])
    days: list[str] = []
    for part in text.split(","):
        part = part.strip()[:7]
        if "-" in part:
            a, b = (p.strip()[:3] for p in part.split("-", 1))
            i, j = DAYS.index(a), DAYS.index(b)
            span = DAYS[i:j + 1] if i <= j else DAYS[i:] + DAYS[:j + 1]
            days.extend(span)
        else:
            if part[:3] not in DAYS:
                raise ValueError(f"Unknown day: {part}")
            days.append(part[:3])
    return [d for d in DAYS if d in days]


def parse_time(text: str) -> time:
    try:
        return datetime.strptime(text.strip(), "%H:%M").time()
    except ValueError:
        raise ValueError(f"Use 24-hour HH:MM times, like 09:00 or 17:30 (got {text!r}).")


def add_schedule(days: str, start: str, end: str) -> dict:
    s, e = parse_time(start), parse_time(end)
    if s == e:
        raise ValueError("Start and end can't be the same time.")
    entry = {"days": parse_days(days), "start": s.strftime("%H:%M"), "end": e.strftime("%H:%M")}
    config = load_config()
    config.setdefault("schedules", []).append(entry)
    save_config(config)
    return entry


def schedules() -> list[dict]:
    return load_config().get("schedules", [])


def remove_schedule(number: int) -> dict:
    config = load_config()
    items = config.get("schedules", [])
    if not 1 <= number <= len(items):
        raise ValueError(f"There's no schedule number {number}.")
    removed = items.pop(number - 1)
    save_config(config)
    return removed


def describe(entry: dict) -> str:
    days = entry["days"]
    if days == DAYS[:5]:
        label = "Weekdays"
    elif days == DAYS:
        label = "Every day"
    elif days == DAYS[5:]:
        label = "Weekends"
    else:
        label = ", ".join(d.capitalize() for d in days)
    return f"{label} {entry['start']}-{entry['end']}"


def active_until(entry: dict, now: datetime) -> datetime | None:
    """If this schedule is on at `now`, return when it ends; otherwise None.

    A window that crosses midnight (22:00-06:00) belongs to the day it starts."""
    s, e = parse_time(entry["start"]), parse_time(entry["end"])
    for offset in (0, -1):  # today's window, or yesterday's overnight window
        day = (now + timedelta(days=offset)).date()
        if DAYS[day.weekday()] not in entry["days"]:
            continue
        start = datetime.combine(day, s)
        end = datetime.combine(day if e > s else day + timedelta(days=1), e)
        if start <= now < end:
            return end
    return None


def current_session_end(now: datetime, entries: list[dict] | None = None) -> datetime | None:
    """Latest end time of any schedule that's on right now, or None."""
    ends = [t for t in (active_until(x, now) for x in (entries if entries is not None else schedules())) if t]
    return max(ends) if ends else None


def skip_current(now: datetime | None = None) -> datetime | None:
    """End the current scheduled session early. Returns when it would have ended."""
    now = now or datetime.now()
    end = current_session_end(now)
    if end:
        config = load_config()
        config["skip_until"] = end.isoformat(timespec="seconds")
        save_config(config)
    return end


def is_skipped(now: datetime, config: dict) -> bool:
    skip = config.get("skip_until")
    return bool(skip) and now < datetime.fromisoformat(skip)
