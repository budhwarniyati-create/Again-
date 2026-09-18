"""Ingestion pipeline for Again?."""

from pathlib import Path

from again.ingest.candidates import ResponseCandidate
from again.ingest.csv import parse_csv
from again.validation.response import validate_response


def ingest_csv(path: Path | str) -> tuple[list[ResponseCandidate], list[tuple[str, list[str]]]]:
    """Parse and validate a CSV without writing to the database."""
    candidates = parse_csv(path)
    valid: list[ResponseCandidate] = []
    rejected: list[tuple[str, list[str]]] = []

    for candidate in candidates:
        errors = validate_response(candidate)

        if errors:
            rejected.append((candidate.source_row_key, errors))
        else:
            valid.append(candidate)

    return valid, rejected
