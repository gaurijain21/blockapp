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


def run_scheduler(on_change: Callable[[str], None] | None = None, stop_after: float | None = None) -> None:
    """Run in the background: block apps and websites whenever focus is on.

    Re-reads settings every tick, so changes in the dashboard or command line
    take effect without restarting. stop_after (seconds) is for testing."""
    from blockapp.catalog import app_label
    from blockapp.schedule import is_skipped, session_end
    from blockapp.storage import load_config
    from blockapp.usage import TabCloser, distraction_in_front

    started = time.monotonic()
    in_session = False
    seen: set = set()
    tabs = TabCloser()
    usage: dict[str, float] = {}
    last_flush = time.monotonic()

    def say(msg: str) -> None:
        if on_change:
            on_change(msg)

    def flush_usage() -> None:
        for app, secs in usage.items():
            log_event("usage", app=app, seconds=round(secs))
        usage.clear()

    while stop_after is None or time.monotonic() - started < stop_after:
        now = datetime.now()
        config = load_config()
        end = session_end(now, config)
        active = end is not None and not is_skipped(now, config)
        if active and not in_session:
            log_event("session_start", apps=config["blocked_apps"], sites=config["blocked_sites"],
                      until=end.isoformat(timespec="seconds"))
            say(f"Focus is on until {end:%H:%M}")
            seen.clear()
        elif not active and in_session:
            log_event("session_end")
            say("Focus is over")
        in_session = active
        if active:
            for name in close_blocked(config["blocked_apps"], already_closed=seen):
                log_event("blocked", app=app_label(name))
                say(f"Closed {app_label(name)}")
            site = tabs.check(config["blocked_sites"])
            if site:
                log_event("blocked", app=site)
                say(f"Closed a {site} tab")
        else:
            thing = distraction_in_front(config["blocked_apps"], config["blocked_sites"])
            if thing:
                usage[thing] = usage.get(thing, 0) + CHECK_EVERY_SECONDS
        if time.monotonic() - last_flush >= 60:
            flush_usage()
            last_flush = time.monotonic()
        time.sleep(CHECK_EVERY_SECONDS)
    flush_usage()
    if in_session:
        log_event("session_end")
