"""Again? command-line interface."""

import argparse

from again.cli.report import print_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="again")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("report", help="Show the baseline learning report.")

    args = parser.parse_args()

    if args.command == "report":
        print_report()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
