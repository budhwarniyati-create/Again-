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

def detect_topic_accuracy_drops(
    db_path: Path | str = "data/user/again.db",
) -> list[dict[str, str | int | float]]:
    """Find topics where accuracy decreased between consecutive sittings."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                sittings.id AS sitting_id,
                sittings.label AS sitting,
                sittings.taken_on,
                items.topic AS topic,
                COUNT(*) AS total,
                SUM(responses.is_correct) AS correct
            FROM responses
            JOIN sittings ON sittings.id = responses.sitting_id
            JOIN items ON items.id = responses.item_id
            WHERE items.topic IS NOT NULL
            GROUP BY sittings.id, items.topic
            ORDER BY sittings.taken_on, sittings.id, items.topic
            """
        ).fetchall()

    by_topic: dict[str, list[dict[str, str | int | float]]] = {}

    for row in rows:
        total = int(row["total"])
        correct = int(row["correct"] or 0)
        accuracy = correct / total

        by_topic.setdefault(row["topic"], []).append(
            {
                "sitting": row["sitting"],
                "taken_on": row["taken_on"],
                "accuracy": accuracy,
            }
        )

    results: list[dict[str, str | int | float]] = []

    for topic, sittings in by_topic.items():
        for previous, current in zip(sittings, sittings[1:]):
            delta = float(current["accuracy"]) - float(previous["accuracy"])

            if delta < 0:
                results.append(
                    {
                        "topic": topic,
                        "previous_sitting": previous["sitting"],
                        "current_sitting": current["sitting"],
                        "previous_accuracy": previous["accuracy"],
                        "current_accuracy": current["accuracy"],
                        "accuracy_delta": delta,
                    }
                )

    return results
