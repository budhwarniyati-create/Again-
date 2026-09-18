"""Typed model for an Again? data source."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    """A source from which Again? imported or received data."""

    id: int | None
    kind: str
    uri_or_label: str | None
    imported_at: str
    notes: str | None = None
