import pytest

from blockapp import apps
from blockapp.catalog import classify, title_matches
from blockapp.storage import load_config, save_config
from blockapp.usage import TabCloser


@pytest.fixture(autouse=True)
def temp_home(tmp_path, monkeypatch):
    monkeypatch.setenv("BLOCKAPP_HOME", str(tmp_path))


def test_classify():
    assert classify("youtube") == ("site", "youtube")
    assert classify("YouTube.exe") == ("site", "youtube")
    assert classify("https://www.youtube.com/watch?v=x") == ("site", "youtube")
    assert classify("example.org") == ("site", "example")
    assert classify("Discord") == ("app", "discord.exe")
    assert classify("notepad") == ("app", "notepad.exe")


@pytest.mark.parametrize("title,expected", [
    ("Lofi beats - YouTube - Google Chrome", "youtube"),
    ("(3) YouTube - Personal - Microsoft​ Edge", "youtube"),
    ("YouTube — Mozilla Firefox", "youtube"),
    ("youtube - Google Search - Google Chrome", None),
    ("How YouTube changed music - Wikipedia - Google Chrome", None),
    ("Instagram - Google Chrome", "instagram"),
    ("Example Domain - example.org - Google Chrome", "example"),
])
def test_title_matches(title, expected):
    assert title_matches(title, ["youtube", "instagram", "example"]) == expected


def test_old_youtube_exe_becomes_website():
    save_config({"blocked_apps": ["youtube.exe", "discord.exe"]})
    config = load_config()
    assert config["blocked_apps"] == ["discord.exe"]
    assert config["blocked_sites"] == ["youtube"]


def test_add_item():
    assert apps.add_item("youtube") == ("site", "YouTube")
    assert apps.add_item("discord") == ("app", "Discord")
    assert load_config()["blocked_sites"] == ["youtube"]
    assert apps.remove_item("site", "youtube")


def test_tab_closer_closes_blocked_tab_once_per_cooldown():
    now = [0.0]
    closed = []
    window = [(1, "chrome.exe", "Cats - YouTube - Google Chrome")]
    tc = TabCloser(get_window=lambda: window[0], close_tab=lambda: closed.append(1), clock=lambda: now[0])
    assert tc.check(["youtube"]) == "YouTube"
    assert tc.check(["youtube"]) is None  # cooling down
    now[0] = 2.0
    assert tc.check(["youtube"]) == "YouTube"
    window[0] = (1, "notepad.exe", "YouTube notes.txt - Notepad")
    now[0] = 5.0
    assert tc.check(["youtube"]) is None  # not a browser
    assert len(closed) == 2
