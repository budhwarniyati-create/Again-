"""Tests for ingestion persistence."""

from again.db.connection import connect
from again.db.initialize import initialize_database
from again.ingest.candidates import ResponseCandidate
from again.ingest.csv import parse_csv
from again.ingest.persistence import persist_candidates


def test_persist_candidates_deduplicates(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    candidates = parse_csv("data/sample/test_results.csv")

    assert persist_candidates(candidates, db_path) == 3
    assert persist_candidates(candidates, db_path) == 0


def test_external_ref_distinguishes_items(tmp_path):
    db_path = tmp_path / "test.db"
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
            is_correct=True,
        ),
    ]

    assert persist_candidates(candidates, db_path) == 2

    with connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM items"
        ).fetchone()[0]

    assert count == 2


def test_item_provenance_is_recorded(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    candidate = ResponseCandidate(
        source_row_key="row-2",
        sitting_label="SAT Test 1",
        section="Math",
        subject="Math",
        topic="Linear equations",
        external_ref="Q1",
        student_answer="A",
        is_correct=False,
    )

    assert persist_candidates([candidate], db_path) == 1

    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT field_name, origin, confidence_qualitative
            FROM field_provenance
            WHERE entity_type = 'item'
            ORDER BY field_name
            """
        ).fetchall()

    assert [row["field_name"] for row in rows] == [
        "external_ref",
        "section",
        "subject",
        "topic",
    ]
    assert all(row["origin"] == "csv_import" for row in rows)
    assert all(row["confidence_qualitative"] == "direct" for row in rows)
