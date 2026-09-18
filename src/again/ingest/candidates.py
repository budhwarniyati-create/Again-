"""Candidate records produced by Again?."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseCandidate:
    """A parsed but not yet validated response."""

    source_row_key: str
    sitting_label: str
    section: str
    subject: str
    topic: str | None
    taken_on: str | None = None
    external_ref: str | None = None
    student_answer: str | None = None
    is_correct: bool | None = None
