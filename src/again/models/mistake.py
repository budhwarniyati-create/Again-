"""Typed model for an Again? mistake."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Mistake:
    """A mistake pattern identified from a question attempt."""

    id: int | None
    attempt_id: int
    category: str
    description: str
    severity: str | None = None
