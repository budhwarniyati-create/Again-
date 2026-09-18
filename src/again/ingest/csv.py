"""CSV ingestion for Again?."""

import csv
from pathlib import Path

from again.ingest.candidates import ResponseCandidate


def parse_csv(path: Path | str) -> list[ResponseCandidate]:
    """Parse an item-level CSV into response candidates."""
    candidates: list[ResponseCandidate] = []

    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            candidates.append(
                ResponseCandidate(
                    source_row_key=f"row-{row_number}",
                    sitting_label=(row.get("sitting") or "").strip(),
                    section=(row.get("section") or "").strip(),
                    subject=(row.get("subject") or "").strip(),
                    topic=(row.get("topic") or "").strip() or None,
                    external_ref=(row.get("external_ref") or "").strip() or None,
                    student_answer=(row.get("student_answer") or "").strip() or None,
                    is_correct=_parse_bool(row.get("is_correct")),
                )
            )

    return candidates


def _parse_bool(value: str | None) -> bool | None:
    """Convert common CSV boolean values into bool or None."""
    if value is None or not value.strip():
        return None

    normalized = value.strip().lower()

    if normalized in {"true", "1", "yes", "correct"}:
        return True

    if normalized in {"false", "0", "no", "incorrect"}:
        return False

    return None
