"""Tests for deterministic diagnosis aggregation."""

from again.db.initialize import initialize_database
from again.diagnosis import build_diagnoses, diagnose_learning_insights
from again.ingest.candidates import ResponseCandidate
from again.ingest.persistence import persist_candidates
from again.insights.patterns import LearningInsight


def make_insight(
    pattern_type,
    *,
    subject=None,
    section=None,
    topic=None,
    evidence=None,
):
    return LearningInsight(
        pattern_type=pattern_type,
        subject=subject,
        section=section,
        topic=topic,
        message=f"{pattern_type} observation.",
        evidence=evidence if evidence is not None else {},
    )


def test_topic_diagnosis():
    diagnoses = diagnose_learning_insights(
        [
            make_insight(
                "topic_accuracy_drop",
                topic="Linear equations",
                evidence={"accuracy_delta": -0.5},
            )
        ]
    )

    assert len(diagnoses) == 1

    diagnosis = diagnoses[0]

    assert diagnosis.diagnosis_type == "recent_decline"
    assert diagnosis.confidence == "high"
    assert diagnosis.topic == "Linear equations"
    assert diagnosis.section is None
    assert diagnosis.subject is None
    assert "Linear equations" in diagnosis.message
    assert "None" not in diagnosis.message


def test_section_diagnosis():
    diagnoses = diagnose_learning_insights(
        [
            make_insight(
                "section_accuracy_drop",
                section="Math",
                evidence={"accuracy_delta": -0.5},
            )
        ]
    )

    assert len(diagnoses) == 1

    diagnosis = diagnoses[0]

    assert diagnosis.diagnosis_type == "recent_decline"
    assert diagnosis.confidence == "high"
    assert diagnosis.section == "Math"
    assert diagnosis.subject is None
    assert diagnosis.topic is None
    assert "Math" in diagnosis.message
    assert "None" not in diagnosis.message


def test_different_sections_stay_separate():
    math = make_insight(
        "section_accuracy_drop",
        section="Math",
        evidence={"accuracy_delta": -0.5},
    )
    reading = make_insight(
        "section_accuracy_drop",
        section="Reading",
        evidence={"accuracy_delta": -0.4},
    )

    diagnoses = diagnose_learning_insights([math, reading])

    assert len(diagnoses) == 2
    assert {diagnosis.section for diagnosis in diagnoses} == {
        "Math",
        "Reading",
    }

    for diagnosis in diagnoses:
        assert diagnosis.diagnosis_type == "recent_decline"
        assert "None" not in diagnosis.message


def test_recurring_and_decline_produce_recurring_decline():
    topic = "Linear equations"

    diagnoses = diagnose_learning_insights(
        [
            make_insight(
                "topic_accuracy_drop",
                topic=topic,
                evidence={"accuracy_delta": -0.5},
            ),
            make_insight(
                "repeated_miss_across_sittings",
                topic=topic,
                evidence={"sitting_count": 2},
            ),
        ]
    )

    assert len(diagnoses) == 1

    diagnosis = diagnoses[0]

    assert diagnosis.diagnosis_type == "recurring_decline"
    assert diagnosis.confidence == "high"
    assert diagnosis.topic == topic
    assert diagnosis.evidence["supporting_patterns"] == 2
    assert (
        diagnosis.evidence["repeated_miss_across_sittings.sitting_count"] == 2
    )
    assert diagnosis.evidence["topic_accuracy_drop.accuracy_delta"] == -0.5


def test_evidence_preserved_without_cross_section_overwrite():
    math = make_insight(
        "section_accuracy_drop",
        section="Math",
        evidence={"accuracy_delta": -0.5},
    )
    reading = make_insight(
        "section_accuracy_drop",
        section="Reading",
        evidence={"accuracy_delta": -0.4},
    )

    diagnoses = diagnose_learning_insights([math, reading])
    by_section = {diagnosis.section: diagnosis for diagnosis in diagnoses}

    assert set(by_section) == {"Math", "Reading"}
    assert (
        by_section["Math"].evidence["section_accuracy_drop.accuracy_delta"]
        == -0.5
    )
    assert (
        by_section["Reading"].evidence[
            "section_accuracy_drop.accuracy_delta"
        ]
        == -0.4
    )
    assert by_section["Math"].evidence["supporting_patterns"] == 1
    assert by_section["Reading"].evidence["supporting_patterns"] == 1


def test_build_diagnoses_from_database(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Quadratics",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-3",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
            ResponseCandidate(
                source_row_key="row-4",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Quadratics",
                taken_on="2026-09-19",
                is_correct=True,
            ),
        ],
        db_path,
    )

    diagnoses = build_diagnoses(db_path)

    section_diagnoses = [
        diagnosis for diagnosis in diagnoses if diagnosis.section == "Math"
    ]

    assert len(section_diagnoses) == 1
    assert section_diagnoses[0].diagnosis_type == "recent_decline"
    assert section_diagnoses[0].subject is None
    assert "Math" in section_diagnoses[0].message
    assert "None" not in section_diagnoses[0].message

    topic_diagnoses = [
        diagnosis
        for diagnosis in diagnoses
        if diagnosis.topic == "Linear equations"
    ]

    assert len(topic_diagnoses) == 1
    assert topic_diagnoses[0].section is None
    assert topic_diagnoses[0].diagnosis_type == "recent_decline"
