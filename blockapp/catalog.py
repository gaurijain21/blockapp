"""Popular distractions, so people can type "youtube" or "discord" and have it just work."""

from __future__ import annotations

import re

# Websites: key -> the name the site puts in its browser tab title.
SITES = {
    "youtube": "YouTube",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "netflix": "Netflix",
    "reddit": "Reddit",
    "facebook": "Facebook",
    "twitch": "Twitch",
    "pinterest": "Pinterest",
    "primevideo": "Prime Video",
}

# Desktop apps: key -> (display name, Windows process name).
APPS = {
    "discord": ("Discord", "discord.exe"),
    "steam": ("Steam", "steam.exe"),
    "spotify": ("Spotify", "spotify.exe"),
    "whatsapp": ("WhatsApp", "whatsapp.exe"),
    "telegram": ("Telegram", "telegram.exe"),
    "epicgames": ("Epic Games", "epicgameslauncher.exe"),
    "roblox": ("Roblox", "robloxplayerbeta.exe"),
    "netflixapp": ("Netflix app", "netflix.exe"),
}

# One-tap suggestions shown in the dashboard, in this order.
SUGGESTIONS = [
    ("site", "youtube"), ("site", "instagram"), ("site", "tiktok"), ("app", "discord"),
    ("site", "netflix"), ("site", "reddit"), ("app", "steam"), ("site", "twitch"),
    ("app", "spotify"), ("app", "whatsapp"), ("site", "facebook"), ("app", "roblox"),
]

BROWSERS = {"chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe", "opera_gx.exe", "vivaldi.exe", "arc.exe"}


def _key(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def site_key_from(text: str) -> str | None:
    """'youtube', 'YouTube', 'youtube.com', 'https://www.youtube.com/x' -> 'youtube'."""
    raw = text.strip().lower()
    raw = re.sub(r"^[a-z]+://", "", raw).split("/")[0]
    raw = re.sub(r"^www\.", "", raw)
    if raw.endswith(".exe"):
        raw = raw[:-4]
    if "." in raw:  # a domain like reddit.com or example.org
        base = raw.split(".")[-2] if raw.count(".") >= 1 else raw
        return _key(base) or None
    key = _key(raw)
    return key if key in SITES else None


def classify(text: str) -> tuple[str, str]:
    """Decide whether the user means a website or an app.

    Returns ("site", key) or ("app", process name)."""
    if not text.strip():
        raise ValueError("Type an app or website name.")
    key = _key(text.replace(".exe", ""))
    if key in APPS:
        return "app", APPS[key][1]
    site = site_key_from(text)
    if site:
        return "site", site
    name = text.strip().lower()
    if not name.endswith(".exe"):
        name += ".exe"
    return "app", name


def site_label(key: str) -> str:
    return SITES.get(key, key.capitalize())


def app_label(process: str) -> str:
    for label, exe in APPS.values():
        if exe == process.lower():
            return label
    name = process[:-4] if process.lower().endswith(".exe") else process
    return name[:1].upper() + name[1:]


_SEPARATORS = re.compile(r"\s+[-–—|•·/:]\s+")


def title_matches(title: str, sites: list[str]) -> str | None:
    """If a browser tab title belongs to one of the blocked sites, return that site's key.

    Tab titles look like 'Some video - YouTube - Google Chrome' or '(3) Instagram'.
    Matching whole title parts (not any substring) keeps a Google search for
    "youtube" from counting as being on YouTube."""
    title = re.sub(r"^\(\d+\+?\)\s*", "", title.strip())
    parts = [p.strip() for p in _SEPARATORS.split(title) if p.strip()]
    for key in sites:
        brand = SITES.get(key)
        for part in parts:
            if brand:
                if part == brand or part.startswith(brand + " "):
                    return key
            elif part.lower() in (key, f"{key}.com") or part.lower().startswith(key + ".") :
                return key
    return None
