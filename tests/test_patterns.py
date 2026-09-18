"""Tests for deterministic pattern detection."""

from again.db.initialize import initialize_database
from again.ingest.candidates import ResponseCandidate
from again.ingest.persistence import persist_candidates
from again.patterns.detector import detect_repeated_miss_topics, detect_repeated_miss_topics_across_sittings, detect_topic_accuracy_drops, detect_topic_accuracy_drops


def test_detect_repeated_miss_topics(tmp_path):
    db_path = tmp_path / "patterns.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-4",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Quadratics",
            external_ref="Q3",
            student_answer="C",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "miss_count": 2,
        }
    ]
def test_detect_repeated_miss_topics_across_sittings(tmp_path):
    db_path = tmp_path / "patterns_over_time.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-15",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "miss_count": 2,
        }
    ]
def test_detect_repeated_miss_topics_across_sittings_only(tmp_path):
    db_path = tmp_path / "cross_sitting.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-4",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Quadratics",
            taken_on="2026-09-15",
            external_ref="Q3",
            student_answer="C",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics_across_sittings(db_path)

    assert result == []


def test_detect_repeated_miss_topics_across_sittings_finds_pattern(tmp_path):
    db_path = tmp_path / "cross_sitting_found.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-15",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics_across_sittings(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "sitting_count": 2,
        }
    ]

def test_detect_topic_accuracy_drops(tmp_path):
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
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
        ],
        db_path,
    )

    result = detect_topic_accuracy_drops(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "previous_sitting": "SAT Test 1",
            "current_sitting": "SAT Test 2",
            "previous_accuracy": 1.0,
            "current_accuracy": 0.0,
            "accuracy_delta": -1.0,
        }
    ]
