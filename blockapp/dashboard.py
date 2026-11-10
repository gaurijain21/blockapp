"""A small dashboard in your browser: python -m blockapp dashboard

Uses only Python's standard library. Listens on 127.0.0.1, so only your own
computer can open it. While it's open, it also does the blocking
(the same as `blockapp run`)."""

from __future__ import annotations

import json
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

from blockapp import apps, schedule, score
from blockapp.catalog import APPS, SITES, SUGGESTIONS, app_label, site_label
from blockapp.storage import load_config


def _clock(t: datetime) -> str:
    return t.strftime("%I:%M %p").lstrip("0")


def state() -> dict:
    now = datetime.now()
    config = load_config()
    events = score.load_events()
    today = score.daily_stats(events, score.last_days(1))[0]
    history = score.daily_stats(events, score.last_days(7))
    end = schedule.session_end(now, config)
    active = end is not None and not schedule.is_skipped(now, config)
    entries = config.get("schedules", [])
    nxt = schedule.next_start(now, entries)

    blocked = [{"kind": "site", "value": k, "label": site_label(k)} for k in config["blocked_sites"]]
    blocked += [{"kind": "app", "value": a, "label": app_label(a)} for a in config["blocked_apps"]]
    blocked_keys = {(b["kind"], b["value"]) for b in blocked}
    suggestions = []
    for kind, key in SUGGESTIONS:
        value = key if kind == "site" else APPS[key][1]
        label = SITES[key] if kind == "site" else APPS[key][0]
        suggestions.append({"kind": kind, "value": value, "label": label, "on": (kind, value) in blocked_keys})
    suggested = {(s["kind"], s["value"]) for s in suggestions}

    names = sorted(
        set(today.by_app) | set(today.attempts_by_app),
        key=lambda a: -(today.by_app.get(a, 0) / 60 + today.attempts_by_app.get(a, 0)),
    )
    return {
        "score": today.score,
        "label": score.label(today.score),
        "breakdown": {
            "attempts": today.attempts,
            "skips": today.skips,
            "minutes": round(today.distracted_minutes),
            "penalties": {k: round(v) for k, v in today.penalties.items()},
        },
        "distractions": [
            {"name": n, "minutes": round(today.by_app.get(n, 0) / 60), "opens": today.attempts_by_app.get(n, 0)}
            for n in names[:5]
        ],
        "history": [{"day": s.day.strftime("%a"), "date": s.day.isoformat(), "score": s.score} for s in history],
        "blocked": blocked,
        "suggestions": suggestions,
        "custom": [b for b in blocked if (b["kind"], b["value"]) not in suggested],
        "schedules": [
            {"number": i, "text": schedule.describe(e)} for i, e in enumerate(entries, 1)
        ],
        "session": {
            "active": active,
            "until": _clock(end) if active else None,
            "seconds_left": int((end - now).total_seconds()) if active else 0,
        },
        "next": schedule.friendly_when(nxt, now) if nxt and not active else None,
        "running": sorted({app_label(a) for a in apps.running_apps()}),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the terminal quiet
        pass

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data, status: int = 200) -> None:
        self._send(status, json.dumps(data).encode(), "application/json")

    def do_GET(self):
        if self.path == "/":
            html = resources.files("blockapp").joinpath("dashboard.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
        elif self.path == "/api/state":
            self._json(state())
        else:
            self._send(404, b"Not found", "text/plain")

    def do_POST(self):
        # Only accept requests from this dashboard's own page.
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{self.headers.get('Host')}":
            return self._send(403, b"Forbidden", "text/plain")
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/api/block":
                if body.get("kind") == "site":
                    apps.add_item(body["value"])
                elif body.get("kind") == "app":
                    apps.add_app(body["value"])
                else:
                    apps.add_item(body.get("name", ""))
            elif self.path == "/api/unblock":
                apps.remove_item(body.get("kind", ""), body.get("value", ""))
            elif self.path == "/api/schedules/add":
                schedule.add_schedule(body.get("days") or [], body.get("start", ""), body.get("end", ""))
            elif self.path == "/api/schedules/remove":
                schedule.remove_schedule(int(body.get("number", 0)))
            elif self.path == "/api/focus":
                schedule.start_focus(float(body.get("minutes", 25)))
            elif self.path == "/api/skip":
                schedule.skip_current()
            else:
                return self._send(404, b"Not found", "text/plain")
        except ValueError as e:
            return self._json({"error": str(e)}, 400)
        self._json(state())


def serve(port: int = 8765, open_browser: bool = True, follow_schedules: bool = True) -> None:
    if follow_schedules:
        from blockapp.blocker import run_scheduler
        threading.Thread(target=run_scheduler, daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://localhost:{port}"
    print(f"Blockapp dashboard: {url}  (keep this window open; Ctrl+C stops it)")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
