"""Deterministic diagnosis of recurring learning patterns."""

from dataclasses import dataclass
from pathlib import Path

from again.insights.patterns import LearningInsight, get_learning_insights


@dataclass(frozen=True)
class Diagnosis:
    """A deterministic, evidence-backed diagnosis."""

    diagnosis_type: str
    subject: str | None
    section: str | None
    topic: str | None
    message: str
    confidence: str
    evidence: dict[str, str | int | float]


_PRIORITY = {
    "repeated_miss_across_sittings": 5,
    "topic_accuracy_drop": 4,
    "section_accuracy_drop": 3,
    "topic_regression": 2,
    "repeated_miss_topic": 1,
    "mastery_status": 0,
}


def diagnose_learning_insights(
    insights: list[LearningInsight],
) -> list[Diagnosis]:
    """Aggregate overlapping insights into consolidated diagnoses."""

    grouped: dict[
        tuple[str | None, str | None, str | None], list[LearningInsight]
    ] = {}

    for insight in insights:
        key = (insight.subject, insight.section, insight.topic)
        grouped.setdefault(key, []).append(insight)

    diagnoses: list[Diagnosis] = []

    for (subject, section, topic), topic_insights in grouped.items():
        topic_insights = sorted(
            topic_insights,
            key=lambda insight: _PRIORITY.get(insight.pattern_type, 0),
            reverse=True,
        )

        label = topic or section or subject or "overall performance"

        evidence: dict[str, str | int | float] = {}
        pattern_types: list[str] = []

        for insight in topic_insights:
            pattern_types.append(insight.pattern_type)

            for key, value in insight.evidence.items():
                evidence[f"{insight.pattern_type}.{key}"] = value

        has_recurring = "repeated_miss_across_sittings" in pattern_types
        has_decline = (
            "topic_accuracy_drop" in pattern_types
            or "section_accuracy_drop" in pattern_types
        )
        has_regression = "topic_regression" in pattern_types
        has_repeated_misses = "repeated_miss_topic" in pattern_types

        if has_recurring and has_decline:
            diagnosis_type = "recurring_decline"
            confidence = "high"
            message = (
                f"{label} shows a recurring performance issue "
                "across multiple observations, including a recent decline."
            )
        elif has_recurring:
            diagnosis_type = "recurring_pattern"
            confidence = "high"
            message = (
                f"{label} shows a recurring performance issue "
                "across multiple sittings."
            )
        elif has_decline:
            diagnosis_type = "recent_decline"
            confidence = "high"
            message = (
                f"{label} shows a recent performance decline."
            )
        elif has_regression:
            diagnosis_type = "regression"
            confidence = "medium"
            message = (
                f"{label} shows evidence of regression after "
                "previously correct performance."
            )
        elif has_repeated_misses:
            diagnosis_type = "repeated_topic_misses"
            confidence = "high"
            message = (
                f"{label} has repeated incorrect responses."
            )
        else:
            continue

        evidence["supporting_patterns"] = len(pattern_types)

        diagnoses.append(
            Diagnosis(
                diagnosis_type=diagnosis_type,
                subject=subject,
                section=section,
                topic=topic,
                message=message,
                confidence=confidence,
                evidence=evidence,
            )
        )

    diagnoses.sort(
        key=lambda diagnosis: (
            diagnosis.topic
            or diagnosis.section
            or diagnosis.subject
            or "",
            diagnosis.diagnosis_type,
        )
    )

    return diagnoses


def build_diagnoses(
    db_path: Path | str = "data/user/again.db",
) -> list[Diagnosis]:
    """Build consolidated diagnoses from the current database."""
    insights = get_learning_insights(db_path)
    return diagnose_learning_insights(insights)
