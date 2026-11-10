"""What you're looking at right now: the app in front, and the browser tab title."""

from __future__ import annotations

import os
import time

import psutil

from blockapp.apps import normalize
from blockapp.catalog import BROWSERS, app_label, site_label, title_matches

IS_WINDOWS = os.name == "nt"


def foreground_window() -> tuple[int, str, str] | None:
    """(window handle, process name, window title) of the window in front. Windows only."""
    if not IS_WINDOWS:
        return None
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    length = user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buf, length + 1)
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    try:
        name = psutil.Process(pid.value).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None
    return hwnd, name, buf.value


def _press_ctrl_w() -> None:
    """Close the current browser tab, the same as pressing Ctrl+W."""
    import ctypes

    user32 = ctypes.windll.user32
    VK_CONTROL, VK_W, KEYUP = 0x11, 0x57, 0x0002
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_W, 0, 0, 0)
    user32.keybd_event(VK_W, 0, KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYUP, 0)


class TabCloser:
    """Closes the browser tab in front when it's on a blocked website."""

    COOLDOWN = 1.5  # seconds; gives the browser time to switch tabs before checking again

    def __init__(self, get_window=foreground_window, close_tab=_press_ctrl_w, clock=time.monotonic):
        self.get_window, self.close_tab, self.clock = get_window, close_tab, clock
        self.last_close = -1e9

    def check(self, sites: list[str]) -> str | None:
        """Close the tab if needed. Returns the blocked site's label, or None."""
        if not sites or self.clock() - self.last_close < self.COOLDOWN:
            return None
        win = self.get_window()
        if not win:
            return None
        _, process, title = win
        if normalize(process) not in BROWSERS:
            return None
        key = title_matches(title, sites)
        if not key:
            return None
        self.close_tab()
        self.last_close = self.clock()
        return site_label(key)


def distraction_in_front(apps: list[str], sites: list[str]) -> str | None:
    """The blocked app or website you're looking at now, if any.

    On Windows this is the window in front. Elsewhere (for testing) it's any
    blocked app that's running."""
    targets = {normalize(b) for b in apps}
    if IS_WINDOWS:
        win = foreground_window()
        if not win:
            return None
        _, process, title = win
        if normalize(process) in targets:
            return app_label(process)
        if normalize(process) in BROWSERS:
            key = title_matches(title, sites)
            return site_label(key) if key else None
        return None
    for proc in psutil.process_iter(["name"]):
        name = proc.info.get("name") or ""
        if normalize(name) in targets:
            return app_label(name)
    return None
