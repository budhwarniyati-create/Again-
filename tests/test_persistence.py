"""Tests for ingestion persistence."""

from again.db.initialize import initialize_database
from again.ingest.csv import parse_csv
from again.ingest.persistence import persist_candidates


def test_persist_candidates_deduplicates(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    candidates = parse_csv("data/sample/test_results.csv")

    assert persist_candidates(candidates, db_path) == 3
    assert persist_candidates(candidates, db_path) == 0
