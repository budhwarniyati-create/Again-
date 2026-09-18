"""Candidate records produced by Again? ingestion."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseCandidate:
    """A parsed but not yet validated response."""

    source_row_key: str
    sitting_label: str
    section: str
    subject: str
    topic: str | None
    student_answer: str | None
    is_correct: bool | None
