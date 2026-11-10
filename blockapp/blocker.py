"""Closing blocked apps while blocking is on."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Callable, Iterable

import psutil

from blockapp.apps import normalize
from blockapp.storage import log_event

CHECK_EVERY_SECONDS = 1.0


def close_blocked(blocked: Iterable[str], processes=None, already_closed: set | None = None) -> list[str]:
    """Close every running process on the block list. Returns the names newly closed.

    Process ids in already_closed are closed again if still alive but not
    reported twice, so one launch counts as one blocked attempt."""
    targets = {normalize(b) for b in blocked}
    closed = []
    for proc in processes if processes is not None else psutil.process_iter(["name"]):
        try:
            name = proc.info.get("name") or ""
            if normalize(name) in targets:
                proc.terminate()
                pid = getattr(proc, "pid", None)
                if already_closed is None or pid not in already_closed:
                    closed.append(name)
                if already_closed is not None and pid is not None:
                    already_closed.add(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return closed


def run_blocking(
    blocked: list[str],
    minutes: float | None = None,
    on_close: Callable[[str], None] | None = None,
) -> None:
    """Keep closing blocked apps until time runs out (or forever if minutes is None)."""
    end = datetime.now() + timedelta(minutes=minutes) if minutes else None
    log_event("session_start", apps=blocked, minutes=minutes)
    seen: set = set()
    try:
        while end is None or datetime.now() < end:
            for name in close_blocked(blocked, already_closed=seen):
                log_event("blocked", app=name)
                if on_close:
                    on_close(name)
            time.sleep(CHECK_EVERY_SECONDS)
    finally:
        log_event("session_end")


def run_scheduler(on_change: Callable[[str], None] | None = None, stop_after: float | None = None) -> None:
    """Run in the background: block apps whenever a schedule is on.

    Re-reads settings every tick, so `add`, `schedule add` and `skip` take
    effect without restarting. stop_after (seconds) is for testing."""
    from blockapp.schedule import current_session_end, is_skipped
    from blockapp.storage import load_config

    from blockapp.usage import distracting_app_in_use

    started = time.monotonic()
    in_session = False
    seen: set = set()
    usage: dict[str, float] = {}
    last_flush = time.monotonic()

    def flush_usage() -> None:
        for app, secs in usage.items():
            log_event("usage", app=app, seconds=round(secs))
        usage.clear()

    while stop_after is None or time.monotonic() - started < stop_after:
        now = datetime.now()
        config = load_config()
        end = current_session_end(now, config.get("schedules", []))
        active = end is not None and not is_skipped(now, config)
        if active and not in_session:
            log_event("session_start", apps=config["blocked_apps"], scheduled=True, until=end.isoformat(timespec="seconds"))
            if on_change:
                on_change(f"Focus session on until {end:%H:%M}")
            seen.clear()
        elif not active and in_session:
            log_event("session_end", scheduled=True)
            if on_change:
                on_change("Focus session over")
        in_session = active
        if active:
            for name in close_blocked(config["blocked_apps"], already_closed=seen):
                log_event("blocked", app=name)
                if on_change:
                    on_change(f"Closed {name}")
        else:
            app = distracting_app_in_use(config["blocked_apps"])
            if app:
                usage[app] = usage.get(app, 0) + CHECK_EVERY_SECONDS
        if time.monotonic() - last_flush >= 60:
            flush_usage()
            last_flush = time.monotonic()
        time.sleep(CHECK_EVERY_SECONDS)
    flush_usage()
    if in_session:
        log_event("session_end", scheduled=True)
