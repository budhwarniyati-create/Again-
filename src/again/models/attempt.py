"""Typed model for an Again? question attempt."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Attempt:
    """A student's attempt at a question."""

    id: int | None
    question_id: int
    student_id: int
    is_correct: bool
    attempted_at: str
    error_type: str | None = None
    notes: str | None = None
