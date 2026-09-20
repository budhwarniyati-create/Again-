"""Structured learning insights derived from detected patterns."""

from dataclasses import dataclass
from pathlib import Path

from again.patterns.detector import (
    detect_repeated_miss_topics_across_sittings,
    detect_topic_accuracy_drops,
)


@dataclass(frozen=True)
class LearningInsight:
    """A structured observation about a student's performance."""

    pattern_type: str
    subject: str | None
    topic: str | None
    message: str
    evidence: dict[str, str | int | float]


def topic_accuracy_drop_insights(
    db_path: Path | str = "data/user/again.db",
) -> list[LearningInsight]:
    """Convert topic accuracy drops into structured learning insights."""
    drops = detect_topic_accuracy_drops(db_path)

    return [
        LearningInsight(
            pattern_type="topic_accuracy_drop",
            subject=None,
            topic=row["topic"],
            message=(
                f"Accuracy decreased for {row['topic']} from "
                f"{float(row['previous_accuracy']):.1%} to "
                f"{float(row['current_accuracy']):.1%}."
            ),
            evidence={
                "previous_sitting": row["previous_sitting"],
                "current_sitting": row["current_sitting"],
                "previous_accuracy": row["previous_accuracy"],
                "current_accuracy": row["current_accuracy"],
                "accuracy_delta": row["accuracy_delta"],
            },
        )
        for row in drops
    ]


def repeated_miss_insights(
    db_path: Path | str = "data/user/again.db",
) -> list[LearningInsight]:
    """Convert repeated misses across sittings into structured insights."""
    misses = detect_repeated_miss_topics_across_sittings(db_path)

    return [
        LearningInsight(
            pattern_type="repeated_miss_across_sittings",
            subject=None,
            topic=row["topic"],
            message=(
                f"{row['topic']} was missed across "
                f"{row['sitting_count']} different sittings."
            ),
            evidence={
                "sitting_count": row["sitting_count"],
            },
        )
        for row in misses
    ]

def topic_regression_insights(
    db_path: Path | str = "data/user/again.db",
) -> list[LearningInsight]:
    """Convert topic regressions into structured learning insights."""
    from again.patterns.detector import detect_topic_regressions

    regressions = detect_topic_regressions(db_path)

    return [
        LearningInsight(
            pattern_type="topic_regression",
            subject=None,
            topic=row["topic"],
            message=(
                f"{row['topic']} was answered correctly previously "
                f"but was missed in {row['current_sitting']}."
            ),
            evidence={
                "current_sitting": row["current_sitting"],
                "current_taken_on": row["current_taken_on"],
            },
        )
        for row in regressions
    ]

def section_accuracy_drop_insights(
    db_path: Path | str = "data/user/again.db",
) -> list[LearningInsight]:
    """Convert section accuracy drops into structured learning insights."""
    from again.patterns.detector import detect_section_accuracy_drops

    drops = detect_section_accuracy_drops(db_path)

    return [
        LearningInsight(
            pattern_type="section_accuracy_drop",
            subject=row["section"],
            topic=None,
            message=(
                f"{row['section']} accuracy decreased from "
                f"{float(row['previous_accuracy']):.1%} to "
                f"{float(row['current_accuracy']):.1%}."
            ),
            evidence={
                "previous_sitting": row["previous_sitting"],
                "current_sitting": row["current_sitting"],
                "previous_accuracy": row["previous_accuracy"],
                "current_accuracy": row["current_accuracy"],
                "accuracy_delta": row["accuracy_delta"],
            },
        )
        for row in drops
    ]

def repeated_miss_topic_insights(
    db_path: Path | str = "data/user/again.db",
) -> list[LearningInsight]:
    """Convert repeated misses within topics into structured insights."""
    from again.patterns.detector import detect_repeated_miss_topics

    misses = detect_repeated_miss_topics(db_path)

    return [
        LearningInsight(
            pattern_type="repeated_miss_topic",
            subject=None,
            topic=row["topic"],
            message=(
                f"{row['topic']} was missed "
                f"{row['miss_count']} times."
            ),
            evidence={
                "miss_count": row["miss_count"],
            },
        )
        for row in misses
    ]

def get_learning_insights(
    db_path: Path | str = "data/user/again.db",
) -> list[LearningInsight]:
    """Return all structured learning insights for a database."""
    insights: list[LearningInsight] = []

    insights.extend(topic_accuracy_drop_insights(db_path))
    insights.extend(repeated_miss_insights(db_path))
    insights.extend(repeated_miss_topic_insights(db_path))
    insights.extend(topic_regression_insights(db_path))
    insights.extend(section_accuracy_drop_insights(db_path))

    return insights