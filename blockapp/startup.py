"""Start `blockapp run` quietly when you sign in to Windows."""

from __future__ import annotations

import os
import sys
from pathlib import Path

FILE_NAME = "Blockapp.vbs"


def _startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if os.name != "nt" or not appdata:
        raise RuntimeError("Starting automatically only works on Windows.")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _pythonw() -> str:
    exe = Path(sys.executable)
    quiet = exe.with_name("pythonw.exe")
    return str(quiet if quiet.exists() else exe)


def enable() -> str:
    project = Path(__file__).resolve().parent.parent
    # A tiny VBScript runs Blockapp with no console window.
    script = (
        'Set shell = CreateObject("WScript.Shell")\r\n'
        f'shell.CurrentDirectory = "{project}"\r\n'
        f'shell.Run """{_pythonw()}"" -m blockapp run", 0, False\r\n'
    )
    path = _startup_dir() / FILE_NAME
    path.write_text(script, encoding="utf-8")
    return f"Blockapp will start when you sign in. (Created {path})"


def disable() -> str:
    path = _startup_dir() / FILE_NAME
    if path.exists():
        path.unlink()
        return "Blockapp won't start automatically any more."
    return "Automatic start was already off."
