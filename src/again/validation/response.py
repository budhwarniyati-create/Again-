"""Validation for Again? ingest candidates."""

from again.ingest.candidates import ResponseCandidate


def validate_response(candidate: ResponseCandidate) -> list[str]:
    """Return validation errors. An empty list means valid."""
    errors: list[str] = []

    if not candidate.source_row_key.strip():
        errors.append("source_row_key is required")

    if not candidate.sitting_label.strip():
        errors.append("sitting_label is required")

    if not candidate.section.strip():
        errors.append("section is required")

    if not candidate.subject.strip():
        errors.append("subject is required")

    if candidate.is_correct is None and candidate.student_answer is None:
        errors.append("either is_correct or student_answer must be provided")

    if candidate.is_correct is not None and not isinstance(candidate.is_correct, bool):
        errors.append("is_correct must be a boolean or None")

    return errors
