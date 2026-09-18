"""Typed model for an Again? question."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    """A question tracked by Again?."""

    id: int | None
    source_id: int | None
    subject: str
    topic: str | None
    question_label: str | None = None
