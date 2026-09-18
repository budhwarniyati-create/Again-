"""Tests for the CSV ingestion pipeline."""

from again.ingest.pipeline import ingest_csv


def test_ingest_csv_accepts_valid_rows():
    valid, rejected = ingest_csv("data/sample/test_results.csv")

    assert len(valid) == 3
    assert rejected == []


def test_ingest_csv_rejects_invalid_rows():
    valid, rejected = ingest_csv("data/sample/invalid_test_results.csv")

    assert len(valid) == 1
    assert len(rejected) == 1
    assert rejected[0][0] == "row-3"
    assert "section is required" in rejected[0][1]
