"""Command-line baseline report for Again?."""

from again.analytics.baseline import (
    accuracy_by_section,
    accuracy_by_sitting,
    accuracy_by_topic,
    accuracy_by_topic_over_time,
    accuracy_change_by_sitting,
    overall_accuracy,
    repeated_misses,
)


def print_report(db_path="data/user/again.db") -> None:
    """Print the baseline analytics report."""
    overall = overall_accuracy(db_path)

    print("=== Again? Baseline Report ===")
    print(
        f"\nOverall: {overall['correct']}/{overall['total']} correct "
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

    print("\nAccuracy change:")
    for row in accuracy_change_by_sitting(db_path):
        if row["accuracy_delta"] is None:
            print(
                f"  {row['sitting']} ({row['taken_on']}): "
                f"{row['accuracy']:.1%} (baseline)"
            )
        else:
            print(
                f"  {row['sitting']} ({row['taken_on']}): "
                f"{row['accuracy']:.1%} "
                f"({row['accuracy_delta']:+.1%})"
            )

    print("\nTopic accuracy over time:")
    for row in accuracy_by_topic_over_time(db_path):
        print(
            f"  {row['sitting']} ({row['taken_on']}) - "
            f"{row['topic']}: {row['accuracy']:.1%} "
            f"({row['correct']}/{row['total']})"
        )

    misses = repeated_misses(db_path)

    print("\nRepeated misses:")
    if not misses:
        print("  None detected.")
    else:
        for row in misses:
            print(
                f"  {row['topic']}: "
                f"{row['miss_count']} misses"
            )
