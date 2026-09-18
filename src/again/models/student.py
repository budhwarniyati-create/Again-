"""Typed model for a Again? student."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Student:
    """A student tracked by Again?."""

    id: int | None
    display_name: str
