"""Command-line baseline report for Again?."""

from again.analytics.baseline import (
    accuracy_by_section,
    accuracy_by_sitting,
    accuracy_by_topic,
    overall_accuracy,
    repeated_misses,
)


def print_report(db_path="data/user/again.db") -> None:
    """Print a readable baseline report."""
    overall = overall_accuracy(db_path)

    print("\n=== Again? Baseline Report ===\n")

    print(
        f"Overall: {overall['correct']}/{overall['total']} correct "
        f"({overall['accuracy']:.1%})"
    )

    print("\nBy section:")
    for row in accuracy_by_section(db_path):
        print(
            f"  {row['section']}: "
            f"{row['correct']}/{row['total']} "
            f"({row['accuracy']:.1%})"
        )

    print("\nBy topic:")
    for row in accuracy_by_topic(db_path):
        print(
            f"  {row['topic']}: "
            f"{row['correct']}/{row['total']} "
            f"({row['accuracy']:.1%})"
        )

    print("\nBy sitting:")
    for row in accuracy_by_sitting(db_path):
        print(
            f"  {row['sitting']}: "
            f"{row['correct']}/{row['total']} "
            f"({row['accuracy']:.1%})"
        )

    misses = repeated_misses(db_path)

    print("\nRepeated misses:")
    if not misses:
        print("  None detected.")
    else:
        for row in misses:
            print(
                f"  {row['topic']}: "
                f"{row['misses']} misses [{row['status']}]"
            )


if __name__ == "__main__":
    print_report()
