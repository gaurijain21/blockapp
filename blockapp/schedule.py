"""Recurring focus sessions, e.g. weekdays 09:00-12:00."""

from __future__ import annotations

from datetime import datetime, time, timedelta

from blockapp.storage import load_config, log_event, save_config

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
    day_list = parse_days(days) if isinstance(days, str) else [d for d in DAYS if d in days]
    if not day_list:
        raise ValueError("Pick at least one day.")
    entry = {"days": day_list, "start": s.strftime("%H:%M"), "end": e.strftime("%H:%M")}
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


def _clock(hhmm: str) -> str:
    t = parse_time(hhmm)
    return t.strftime("%I:%M %p").lstrip("0")


def days_label(days: list[str]) -> str:
    if days == DAYS[:5]:
        label = "Weekdays"
    elif len(days) == 1:
        label = {"mon": "Mondays", "tue": "Tuesdays", "wed": "Wednesdays", "thu": "Thursdays",
                 "fri": "Fridays", "sat": "Saturdays", "sun": "Sundays"}[days[0]]
    elif days == DAYS:
        label = "Every day"
    elif days == DAYS[5:]:
        label = "Weekends"
    else:
        label = ", ".join(d.capitalize() for d in days)
    return label


def describe(entry: dict) -> str:
    return f"{days_label(entry['days'])}, {_clock(entry['start'])} to {_clock(entry['end'])}"


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


def session_end(now: datetime, config: dict) -> datetime | None:
    """When the current focus session ends (scheduled or started now), or None."""
    ends = []
    sched = current_session_end(now, config.get("schedules", []))
    if sched:
        ends.append(sched)
    manual = config.get("focus_until")
    if manual and now < datetime.fromisoformat(manual):
        ends.append(datetime.fromisoformat(manual))
    return max(ends) if ends else None


def start_focus(minutes: float, now: datetime | None = None) -> datetime:
    """Start a focus session right now for this many minutes."""
    if not 1 <= minutes <= 24 * 60:
        raise ValueError("Pick between 1 minute and 24 hours.")
    now = now or datetime.now()
    end = now + timedelta(minutes=minutes)
    config = load_config()
    config["focus_until"] = end.isoformat(timespec="seconds")
    if config.get("skip_until") and datetime.fromisoformat(config["skip_until"]) > now:
        config.pop("skip_until")
    save_config(config)
    log_event("focus_now", minutes=minutes)
    return end


def skip_current(now: datetime | None = None) -> datetime | None:
    """End the current focus session early. Returns when it would have ended."""
    now = now or datetime.now()
    config = load_config()
    end = session_end(now, config)
    if end:
        config.pop("focus_until", None)
        config["skip_until"] = end.isoformat(timespec="seconds")
        save_config(config)
        log_event("skip", until=config["skip_until"])
    return end


def is_skipped(now: datetime, config: dict) -> bool:
    skip = config.get("skip_until")
    return bool(skip) and now < datetime.fromisoformat(skip)


def next_start(now: datetime, entries: list[dict]) -> datetime | None:
    """When the next automatic focus time begins, looking a week ahead."""
    best = None
    for entry in entries:
        s = parse_time(entry["start"])
        for offset in range(8):
            day = (now + timedelta(days=offset)).date()
            if DAYS[day.weekday()] not in entry["days"]:
                continue
            start = datetime.combine(day, s)
            if start > now:
                if best is None or start < best:
                    best = start
                break
    return best


def friendly_when(when: datetime, now: datetime) -> str:
    """'today at 9:00 AM', 'tomorrow at 9:00 AM', 'Thursday at 9:00 AM'."""
    clock = when.strftime("%I:%M %p").lstrip("0")
    delta = (when.date() - now.date()).days
    if delta == 0:
        return f"today at {clock}"
    if delta == 1:
        return f"tomorrow at {clock}"
    return f"{when:%A} at {clock}"
