"""Entry point for `python -m blockapp`."""

from blockapp import __version__


def main() -> None:
    print(f"Blockapp {__version__}")
    print("Setup works. App blocking arrives in the next step.")


if __name__ == "__main__":
    main()
