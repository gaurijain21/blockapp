import pytest

from blockapp import apps
from blockapp.blocker import close_blocked


@pytest.fixture(autouse=True)
def temp_home(tmp_path, monkeypatch):
    monkeypatch.setenv("BLOCKAPP_HOME", str(tmp_path))


def test_normalize():
    assert apps.normalize(" Discord ") == "discord.exe"
    assert apps.normalize("chrome.exe") == "chrome.exe"


def test_add_and_remove():
    assert apps.add_app("Discord") == "discord.exe"
    apps.add_app("discord.exe")
    assert apps.blocked_apps() == ["discord.exe"]
    assert apps.remove_app("discord")
    assert apps.blocked_apps() == []
    assert not apps.remove_app("discord")


def test_cannot_block_windows_processes():
    with pytest.raises(ValueError):
        apps.add_app("explorer")


class FakeProc:
    def __init__(self, name):
        self.info = {"name": name}
        self.terminated = False

    def terminate(self):
        self.terminated = True


def test_close_blocked_only_closes_listed_apps():
    discord, notepad = FakeProc("Discord.exe"), FakeProc("notepad.exe")
    closed = close_blocked(["discord.exe"], [discord, notepad])
    assert closed == ["Discord.exe"]
    assert discord.terminated and not notepad.terminated
