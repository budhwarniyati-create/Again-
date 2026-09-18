"""Tests for baseline analytics."""

from again.analytics.baseline import accuracy_by_section, accuracy_by_sitting, accuracy_by_topic, accuracy_by_topic_over_time, accuracy_change_by_sitting, overall_accuracy, repeated_misses
from again.db.initialize import initialize_database
from again.ingest.csv import parse_csv
from again.ingest.candidates import ResponseCandidate
from again.ingest.persistence import persist_candidates


def setup_database(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    candidates = parse_csv("data/sample/test_results.csv")
    persist_candidates(candidates, db_path)
    return db_path


def test_overall_accuracy(tmp_path):
    db_path = setup_database(tmp_path)

    result = overall_accuracy(db_path)

    assert result["total"] == 3
    assert result["correct"] == 2
    assert result["incorrect"] == 1
    assert result["accuracy"] == 2 / 3


def test_accuracy_by_section(tmp_path):
    db_path = setup_database(tmp_path)

    result = accuracy_by_section(db_path)

    assert result == [
        {
            "section": "Math",
            "total": 2,
            "correct": 1,
            "incorrect": 1,
            "accuracy": 0.5,
        },
        {
            "section": "Reading and Writing",
            "total": 1,
            "correct": 1,
            "incorrect": 0,
            "accuracy": 1.0,
        },
    ]


def test_accuracy_by_topic(tmp_path):
    db_path = setup_database(tmp_path)

    result = accuracy_by_topic(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "total": 1,
            "correct": 0,
            "incorrect": 1,
            "accuracy": 0.0,
        },
        {
            "topic": "Quadratics",
            "total": 1,
            "correct": 1,
            "incorrect": 0,
            "accuracy": 1.0,
        },
        {
            "topic": "Transitions",
            "total": 1,
            "correct": 1,
            "incorrect": 0,
            "accuracy": 1.0,
        },
    ]
def test_accuracy_by_sitting(tmp_path):
    db_path = setup_database(tmp_path)

    result = accuracy_by_sitting(db_path)

    assert len(result) == 1
    assert result[0]["sitting"] == "SAT Test 1"
    assert result[0]["total"] == 3
    assert result[0]["correct"] == 2
    assert result[0]["incorrect"] == 1
    assert result[0]["accuracy"] == 2 / 3
def test_repeated_misses(tmp_path):
    db_path = setup_database(tmp_path)

    result = repeated_misses(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "misses": 1,
            "status": "Inferred",
        }
    ]
def test_repeated_misses(tmp_path):
    db_path = setup_database(tmp_path)

def test_repeated_misses_detects_repeated_topic(tmp_path):
    db_path = tmp_path / "repeated.db"
    initialize_database(db_path)

    candidates = parse_csv("data/sample/repeated_misses.csv")
    persist_candidates(candidates, db_path)

    result = repeated_misses(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "misses": 2,
            "status": "Inferred",
        }
    ]

def test_accuracy_by_sitting_orders_by_date(tmp_path):
    db_path = tmp_path / "temporal.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-15",
            external_ref="Q2",
            student_answer="A",
            is_correct=True,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q1",
            student_answer="B",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = accuracy_by_sitting(db_path)

    assert [row["taken_on"] for row in result] == [
        "2026-09-01",
        "2026-09-15",
    ]
    assert [row["sitting"] for row in result] == [
        "SAT Test 1",
        "SAT Test 2",
    ]

def test_accuracy_change_by_sitting(tmp_path):
    db_path = tmp_path / "change.db"
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
            topic="Quadratics",
            taken_on="2026-09-01",
            external_ref="Q2",
            student_answer="B",
            is_correct=True,
        ),
        ResponseCandidate(
            source_row_key="row-4",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-15",
            external_ref="Q3",
            student_answer="A",
            is_correct=True,
        ),
        ResponseCandidate(
            source_row_key="row-5",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Quadratics",
            taken_on="2026-09-15",
            external_ref="Q4",
            student_answer="B",
            is_correct=True,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = accuracy_change_by_sitting(db_path)

    assert result[0]["accuracy"] == 0.5
    assert result[0]["accuracy_delta"] is None
    assert result[1]["accuracy"] == 1.0
    assert result[1]["previous_accuracy"] == 0.5
    assert result[1]["accuracy_delta"] == 0.5



def test_accuracy_by_topic_over_time(tmp_path):
    db_path = tmp_path / "topic_time.db"
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
            is_correct=True,
        ),
        ResponseCandidate(
            source_row_key="row-4",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-15",
            external_ref="Q3",
            student_answer="A",
            is_correct=True,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = accuracy_by_topic_over_time(db_path)

    assert result == [
        {
            "sitting": "SAT Test 1",
            "taken_on": "2026-09-01",
            "topic": "Linear equations",
            "total": 2,
            "correct": 1,
            "incorrect": 1,
            "accuracy": 0.5,
        },
        {
            "sitting": "SAT Test 2",
            "taken_on": "2026-09-15",
            "topic": "Linear equations",
            "total": 1,
            "correct": 1,
            "incorrect": 0,
            "accuracy": 1.0,
        },
    ]
