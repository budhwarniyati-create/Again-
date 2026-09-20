"""Command-line baseline report for Again?."""
from again.insights.patterns import get_learning_insights
from again.analytics.baseline import (
    accuracy_by_section,
    accuracy_by_sitting,
    accuracy_by_topic,
    accuracy_by_topic_over_time,
    accuracy_change_by_sitting,
    overall_accuracy,
    repeated_misses,
)
from again.patterns.detector import (
    detect_repeated_miss_topics_across_sittings,
    detect_topic_accuracy_drops,
    detect_topic_regressions,
    detect_section_accuracy_drops,
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

    accuracy_drops = detect_topic_accuracy_drops(db_path)

    print("\nTopic accuracy drops:")
    if not accuracy_drops:
        print("  None detected.")
    else:
        for row in accuracy_drops:
            print(
                f"  {row['topic']}: "
                f"{row['previous_sitting']} {row['previous_accuracy']:.1%} -> "
                f"{row['current_sitting']} {row['current_accuracy']:.1%} "
                f"({row['accuracy_delta']:+.1%})"
            )

        section_drops = detect_section_accuracy_drops(db_path)
    section_drops = detect_section_accuracy_drops(db_path)
    print("\nSection accuracy drops:")
    if not section_drops:
        print("  None detected.")
    else:
        for row in section_drops:
            print(
                f"  {row['section']}: "
                f"{row['previous_sitting']} {row['previous_accuracy']:.1%} -> "
                f"{row['current_sitting']} {row['current_accuracy']:.1%} "
                f"({row['accuracy_delta']:+.1%})"
            )

    regressions = detect_topic_regressions(db_path)


    print("\nTopic regressions:")
    if not regressions:
        print("  None detected.")
    else:
        for row in regressions:
            print(
                f"  {row['topic']}: "
                f"correct before, then missed in {row['current_sitting']}"
            )

    cross_sitting = detect_repeated_miss_topics_across_sittings(db_path)

    print("\nRepeated misses across sittings:")
    if not cross_sitting:
        print("  None detected.")
    else:
        for row in cross_sitting:
            print(
                f"  {row['topic']}: missed in "
                f"{row['sitting_count']} sittings"
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

    insights = get_learning_insights(db_path)

    print("\nLearning insights:")
    if not insights:
        print("  None detected.")
    else:
        for insight in insights:
            print(f"  [{insight.pattern_type}] {insight.message}")