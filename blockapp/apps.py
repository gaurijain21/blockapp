"""Choosing which apps to block."""

from __future__ import annotations

import psutil

from blockapp.storage import load_config, save_config

# Processes Windows needs; never offer or allow blocking these.
PROTECTED = {
    "system", "system idle process", "registry", "smss.exe", "csrss.exe",
    "wininit.exe", "winlogon.exe", "services.exe", "lsass.exe", "svchost.exe",
    "explorer.exe", "dwm.exe", "fontdrvhost.exe", "conhost.exe", "sihost.exe",
    "taskhostw.exe", "ctfmon.exe", "runtimebroker.exe", "searchhost.exe",
    "startmenuexperiencehost.exe", "shellexperiencehost.exe", "taskmgr.exe",
    "python.exe", "pythonw.exe", "py.exe", "cmd.exe", "powershell.exe",
    "pwsh.exe", "windowsterminal.exe", "openconsole.exe",
}


def normalize(name: str) -> str:
    """Lowercase an app name and add .exe if missing: 'Discord' -> 'discord.exe'."""
    name = name.strip().lower()
    if name and not name.endswith(".exe"):
        name += ".exe"
    return name


def is_protected(name: str) -> bool:
    return normalize(name) in PROTECTED


def running_apps() -> list[str]:
    """Names of apps running right now, without duplicates or system processes."""
    names = set()
    for proc in psutil.process_iter(["name"]):
        name = proc.info.get("name")
        if name and not is_protected(name):
            names.add(name)
    return sorted(names, key=str.lower)


def blocked_apps() -> list[str]:
    return load_config()["blocked_apps"]


def add_app(name: str) -> str:
    app = normalize(name)
    if not app:
        raise ValueError("App name is empty.")
    if is_protected(app):
        raise ValueError(f"{app} is part of Windows or Blockapp itself and can't be blocked.")
    config = load_config()
    if app not in config["blocked_apps"]:
        config["blocked_apps"].append(app)
        config["blocked_apps"].sort()
        save_config(config)
    return app


def add_item(text: str) -> tuple[str, str]:
    """Block an app or a website, whichever the text means. Returns (kind, label)."""
    from blockapp.catalog import app_label, classify, site_label

    kind, value = classify(text)
    if kind == "app":
        return "app", app_label(add_app(value))
    config = load_config()
    if value not in config["blocked_sites"]:
        config["blocked_sites"].append(value)
        save_config(config)
    return "site", site_label(value)


def remove_item(kind: str, value: str) -> bool:
    if kind == "site":
        config = load_config()
        if value in config["blocked_sites"]:
            config["blocked_sites"].remove(value)
            save_config(config)
            return True
        return False
    return remove_app(value)


def remove_app(name: str) -> bool:
    app = normalize(name)
    config = load_config()
    if app in config["blocked_apps"]:
        config["blocked_apps"].remove(app)
        save_config(config)
        return True
    return False
