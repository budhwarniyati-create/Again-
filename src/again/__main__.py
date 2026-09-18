"""Again? command-line interface."""

import argparse

from again.cli.report import print_report
from again.ingest.pipeline import ingest_csv
from again.ingest.persistence import persist_candidates


def main() -> None:
    parser = argparse.ArgumentParser(prog="again")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("report", help="Show the baseline learning report.")

    import_parser = subparsers.add_parser(
        "import",
        help="Import a CSV response dataset.",
    )
    import_parser.add_argument("path", help="Path to the CSV file.")

    args = parser.parse_args()

    if args.command == "report":
        print_report()
    elif args.command == "import":
        valid, rejected = ingest_csv(args.path)
        persisted = persist_candidates(valid, source_label=args.path)

        print(f"Valid rows: {len(valid)}")
        print(f"Rejected rows: {len(rejected)}")
        print(f"Imported rows: {persisted}")

        if rejected:
            print("\nRejected:")
            for row_key, errors in rejected:
                print(f"  {row_key}: {'; '.join(errors)}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
