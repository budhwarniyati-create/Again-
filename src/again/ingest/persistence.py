"""Persistence helpers for Again?."""

from datetime import datetime, timezone
from pathlib import Path

from again.db.connection import connect
from again.ingest.candidates import ResponseCandidate


def persist_candidates(
    candidates: list[ResponseCandidate],
    db_path: Path | str = "data/user/again.db",
) -> int:
    """Persist validated response candidates into the database."""
    imported_at = datetime.now(timezone.utc).isoformat()
    persisted = 0

    with connect(db_path) as connection:
        source_id = _get_or_create_source(connection, imported_at)

        for candidate in candidates:
            source_record_id = _get_or_create_source_record(
                connection,
                source_id,
                candidate,
                imported_at,
            )

            existing = connection.execute(
                """
                SELECT id
                FROM responses
                WHERE source_record_id = ?
                """,
                (source_record_id,),
            ).fetchone()

            if existing:
                continue

            student_id = _get_or_create_student(connection, "Default Student")

            sitting_id = _get_or_create_sitting(
                connection,
                student_id,
                source_id,
                candidate,
            )

            item_id = _get_or_create_item(
                connection,
                source_id,
                candidate,
            )

            connection.execute(
                """
                INSERT INTO responses (
                    sitting_id,
                    item_id,
                    student_answer,
                    is_correct,
                    source_id,
                    source_record_id,
                    raw_payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sitting_id,
                    item_id,
                    candidate.student_answer,
                    int(candidate.is_correct),
                    source_id,
                    source_record_id,
                    None,
                ),
            )

            persisted += 1

    return persisted


def _get_or_create_source(connection, imported_at: str) -> int:
    """Create or reuse the CSV ingestion source."""
    row = connection.execute(
        """
        SELECT id
        FROM sources
        WHERE kind = 'csv'
        ORDER BY id
        LIMIT 1
        """
    ).fetchone()

    if row:
        return int(row["id"])

    cursor = connection.execute(
        """
        INSERT INTO sources (kind, uri_or_label, imported_at)
        VALUES ('csv', 'CSV import', ?)
        """,
        (imported_at,),
    )
    return int(cursor.lastrowid)


def _get_or_create_source_record(
    connection,
    source_id: int,
    candidate: ResponseCandidate,
    imported_at: str,
) -> int:
    """Create or reuse a source record."""
    row = connection.execute(
        """
        SELECT id
        FROM source_records
        WHERE source_id = ? AND row_key = ?
        """,
        (source_id, candidate.source_row_key),
    ).fetchone()

    if row:
        return int(row["id"])

    cursor = connection.execute(
        """
        INSERT INTO source_records (
            source_id,
            row_key,
            imported_at
        )
        VALUES (?, ?, ?)
        """,
        (source_id, candidate.source_row_key, imported_at),
    )
    return int(cursor.lastrowid)


def _get_or_create_student(connection, display_name: str) -> int:
    """Create or reuse the default student."""
    row = connection.execute(
        """
        SELECT id
        FROM students
        WHERE display_name = ?
        LIMIT 1
        """,
        (display_name,),
    ).fetchone()

    if row:
        return int(row["id"])

    cursor = connection.execute(
        """
        INSERT INTO students (display_name)
        VALUES (?)
        """,
        (display_name,),
    )
    return int(cursor.lastrowid)


def _get_or_create_sitting(
    connection,
    student_id: int,
    source_id: int,
    candidate: ResponseCandidate,
) -> int:
    """Create or reuse a sitting."""
    row = connection.execute(
        """
        SELECT id
        FROM sittings
        WHERE student_id = ? AND label = ?
        LIMIT 1
        """,
        (student_id, candidate.sitting_label),
    ).fetchone()

    if row:
        return int(row["id"])

    cursor = connection.execute(
        """
        INSERT INTO sittings (
            student_id,
            taken_on,
            label,
            source_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            student_id,
            datetime.now(timezone.utc).date().isoformat(),
            candidate.sitting_label,
            source_id,
        ),
    )
    return int(cursor.lastrowid)


def _get_or_create_item(
    connection,
    source_id: int,
    candidate: ResponseCandidate,
) -> int:
    """Create or reuse an item."""
    row = connection.execute(
        """
        SELECT id
        FROM items
        WHERE source_id = ?
          AND section = ?
          AND subject = ?
          AND topic IS ?
        LIMIT 1
        """,
        (
            source_id,
            candidate.section,
            candidate.subject,
            candidate.topic,
        ),
    ).fetchone()

    if row:
        return int(row["id"])

    cursor = connection.execute(
        """
        INSERT INTO items (
            source_id,
            section,
            subject,
            topic
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            source_id,
            candidate.section,
            candidate.subject,
            candidate.topic,
        ),
    )
    return int(cursor.lastrowid)
