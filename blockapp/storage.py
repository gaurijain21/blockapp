"""Where Blockapp keeps its settings and history.

Data lives in %APPDATA%\\Blockapp on Windows (or ~/.blockapp elsewhere).
Set BLOCKAPP_HOME to use another folder.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path


def data_dir() -> Path:
    override = os.environ.get("BLOCKAPP_HOME")
    if override:
        path = Path(override)
    elif os.environ.get("APPDATA"):
        path = Path(os.environ["APPDATA"]) / "Blockapp"
    else:
        path = Path.home() / ".blockapp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _config_path() -> Path:
    return data_dir() / "config.json"


def load_config() -> dict:
    path = _config_path()
    if not path.exists():
        return {"blocked_apps": []}
    with path.open(encoding="utf-8") as f:
        config = json.load(f)
    config.setdefault("blocked_apps", [])
    return config


def save_config(config: dict) -> None:
    with _config_path().open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def log_event(kind: str, **fields) -> None:
    """Append one event (e.g. a blocked app launch) to events.jsonl."""
    record = {"time": datetime.now().isoformat(timespec="seconds"), "kind": kind, **fields}
    with (data_dir() / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
