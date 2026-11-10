"""Command line for Blockapp: `python -m blockapp <command>`."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from blockapp import __version__
from blockapp import apps
from blockapp import schedule, score, startup
from blockapp.blocker import run_blocking, run_scheduler


def cmd_running(args) -> int:
    print("Apps running right now:")
    for name in apps.running_apps():
        print(f"  {name}")
    print("\nAdd one with: python -m blockapp add <name>")
    return 0


def cmd_list(args) -> int:
    blocked = apps.blocked_apps()
    if not blocked:
        print("No apps blocked yet. Add one with: python -m blockapp add <name>")
    for name in blocked:
        print(f"  {name}")
    return 0


def cmd_add(args) -> int:
    for name in args.names:
        try:
            print(f"Added {apps.add_app(name)}")
        except ValueError as e:
            print(e)
            return 1
    return 0


def cmd_remove(args) -> int:
    for name in args.names:
        if apps.remove_app(name):
            print(f"Removed {apps.normalize(name)}")
        else:
            print(f"{apps.normalize(name)} wasn't on the list")
    return 0


def cmd_block(args) -> int:
    blocked = apps.blocked_apps()
    if not blocked:
        print("Nothing to block. Add apps first with: python -m blockapp add <name>")
        return 1
    length = f"for {args.minutes:g} minutes" if args.minutes else "until you press Ctrl+C"
    print(f"Blocking {', '.join(blocked)} {length}.")

    def on_close(name: str) -> None:
        print(f"[{datetime.now():%H:%M:%S}] Closed {name}")

    try:
        run_blocking(blocked, args.minutes, on_close)
        print("Focus session finished.")
    except KeyboardInterrupt:
        print("\nBlocking stopped.")
    return 0


def cmd_schedule_add(args) -> int:
    try:
        entry = schedule.add_schedule(args.days, args.start, args.end)
    except ValueError as e:
        print(e)
        return 1
    print(f"Added: {schedule.describe(entry)}")
    print("Blocking follows your schedules while `python -m blockapp run` is running.")
    return 0


def cmd_schedule_list(args) -> int:
    items = schedule.schedules()
    if not items:
        print("No schedules yet. Add one with: python -m blockapp schedule add --days weekdays --start 09:00 --end 12:00")
    for i, entry in enumerate(items, 1):
        print(f"  {i}. {schedule.describe(entry)}")
    return 0


def cmd_schedule_remove(args) -> int:
    try:
        print(f"Removed: {schedule.describe(schedule.remove_schedule(args.number))}")
    except ValueError as e:
        print(e)
        return 1
    return 0


def cmd_skip(args) -> int:
    end = schedule.skip_current()
    if end:
        print(f"Ended this focus session early. Blocking resumes with your next session after {end:%H:%M}.")
    else:
        print("No scheduled session is on right now.")
    return 0


def cmd_run(args) -> int:
    print("Blockapp is following your schedules. Leave this window open, or turn on `startup on`.")
    try:
        run_scheduler(lambda msg: print(f"[{datetime.now():%H:%M:%S}] {msg}"))
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def cmd_startup(args) -> int:
    try:
        print(startup.enable() if args.state == "on" else startup.disable())
    except RuntimeError as e:
        print(e)
        return 1
    return 0


def cmd_score(args) -> int:
    events = score.load_events()
    if args.days > 1:
        print(score.report_history(score.daily_stats(events, score.last_days(args.days))))
    else:
        print(score.report_today(score.daily_stats(events, score.last_days(1))[0]))
    return 0


def cmd_dashboard(args) -> int:
    from blockapp.dashboard import serve
    serve(port=args.port, open_browser=not args.no_browser)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blockapp", description="Block the apps you can't stop opening.")
    parser.add_argument("--version", action="version", version=f"Blockapp {__version__}")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("running", help="show apps running now").set_defaults(func=cmd_running)
    sub.add_parser("list", help="show your blocked apps").set_defaults(func=cmd_list)
    p = sub.add_parser("add", help="block one or more apps, e.g. add discord chrome")
    p.add_argument("names", nargs="+")
    p.set_defaults(func=cmd_add)
    p = sub.add_parser("remove", help="unblock one or more apps")
    p.add_argument("names", nargs="+")
    p.set_defaults(func=cmd_remove)
    p = sub.add_parser("block", help="start blocking now")
    p.add_argument("--minutes", type=float, help="stop after this many minutes")
    p.set_defaults(func=cmd_block)

    p = sub.add_parser("schedule", help="manage recurring focus sessions")
    ssub = p.add_subparsers(dest="schedule_command", required=True)
    q = ssub.add_parser("add", help="e.g. --days weekdays --start 09:00 --end 12:00")
    q.add_argument("--days", default="weekdays", help="weekdays, weekends, everyday, mon-fri, or mon,wed,fri")
    q.add_argument("--start", required=True, help="24-hour time, e.g. 09:00")
    q.add_argument("--end", required=True, help="24-hour time, e.g. 12:00")
    q.set_defaults(func=cmd_schedule_add)
    ssub.add_parser("list", help="show your schedules").set_defaults(func=cmd_schedule_list)
    q = ssub.add_parser("remove", help="remove a schedule by its number from `schedule list`")
    q.add_argument("number", type=int)
    q.set_defaults(func=cmd_schedule_remove)

    sub.add_parser("skip", help="end the current scheduled session early").set_defaults(func=cmd_skip)
    sub.add_parser("run", help="follow your schedules (keep running)").set_defaults(func=cmd_run)
    p = sub.add_parser("startup", help="start Blockapp automatically when you sign in to Windows")
    p.add_argument("state", choices=["on", "off"])
    p.set_defaults(func=cmd_startup)
    p = sub.add_parser("dashboard", help="open the dashboard in your browser")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-browser", action="store_true", help="don't open a browser window")
    p.set_defaults(func=cmd_dashboard)
    p = sub.add_parser("score", help="show your Focus Score")
    p.add_argument("--days", type=int, default=1, help="show a history, e.g. --days 7")
    p.set_defaults(func=cmd_score)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
