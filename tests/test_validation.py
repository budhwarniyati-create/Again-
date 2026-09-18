"""Tests for ingest validation."""

from again.ingest.candidates import ResponseCandidate
from again.validation.response import validate_response


def test_valid_response_has_no_errors():
    candidate = ResponseCandidate(
        source_row_key="row-1",
        sitting_label="SAT Test 1",
        section="Math",
        subject="Math",
        topic="Linear equations",
        student_answer="B",
        is_correct=False,
    )

    assert validate_response(candidate) == []


def test_missing_required_fields_are_rejected():
    candidate = ResponseCandidate(
        source_row_key="row-1",
        sitting_label="",
        section="Math",
        subject="Math",
        topic=None,
        student_answer=None,
        is_correct=None,
    )

    errors = validate_response(candidate)

    assert "sitting_label is required" in errors
    assert "either is_correct or student_answer must be provided" in errors
