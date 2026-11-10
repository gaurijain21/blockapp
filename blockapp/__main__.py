"""Command line for Blockapp: `python -m blockapp <command>`."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from blockapp import __version__
from blockapp import apps
from blockapp.blocker import run_blocking


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
