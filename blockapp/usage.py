"""Which app you're using right now, for counting distracted time."""

from __future__ import annotations

import os

import psutil

from blockapp.apps import normalize


def foreground_app() -> str | None:
    """Name of the app in the window you're looking at (Windows only)."""
    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        return psutil.Process(pid.value).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def distracting_app_in_use(blocked: list[str]) -> str | None:
    """The blocked app you're using now, if any.

    On Windows this is the app in front. Elsewhere (for testing) it's any
    blocked app that's running."""
    targets = {normalize(b) for b in blocked}
    if os.name == "nt":
        app = foreground_app()
        return app if app and normalize(app) in targets else None
    for proc in psutil.process_iter(["name"]):
        name = proc.info.get("name") or ""
        if normalize(name) in targets:
            return name
    return None
