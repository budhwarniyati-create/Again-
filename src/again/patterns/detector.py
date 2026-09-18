"""Deterministic mistake-pattern detection for Again?."""

from pathlib import Path

from again.db.connection import connect


def detect_repeated_miss_topics(
    db_path: Path | str = "data/user/again.db",
    min_misses: int = 2,
) -> list[dict[str, str | int]]:
    """Find topics where the student has missed multiple questions."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                items.topic AS topic,
                COUNT(*) AS miss_count
            FROM responses
            JOIN items ON items.id = responses.item_id
            WHERE responses.is_correct = 0
              AND items.topic IS NOT NULL
            GROUP BY items.topic
            HAVING COUNT(*) >= ?
            ORDER BY miss_count DESC, items.topic
            """,
            (min_misses,),
        ).fetchall()

    return [
        {
            "topic": row["topic"],
            "miss_count": int(row["miss_count"]),
        }
        for row in rows
    ]

def detect_repeated_miss_topics_across_sittings(
    db_path: Path | str = "data/user/again.db",
) -> list[dict[str, str | int]]:
    """Find topics missed in multiple distinct sittings."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                items.topic AS topic,
                COUNT(DISTINCT sittings.id) AS sitting_count
            FROM responses
            JOIN items ON items.id = responses.item_id
            JOIN sittings ON sittings.id = responses.sitting_id
            WHERE responses.is_correct = 0
              AND items.topic IS NOT NULL
            GROUP BY items.topic
            HAVING COUNT(DISTINCT sittings.id) >= 2
            ORDER BY sitting_count DESC, items.topic
            """
        ).fetchall()

    return [
        {
            "topic": row["topic"],
            "sitting_count": int(row["sitting_count"]),
        }
        for row in rows
    ]
