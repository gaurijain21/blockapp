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
