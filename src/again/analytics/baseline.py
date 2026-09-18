"""Baseline analytics for Again?."""

from pathlib import Path

from again.db.connection import connect


def overall_accuracy(
    db_path: Path | str = "data/user/again.db",
) -> dict[str, int | float | None]:
    """Calculate overall response accuracy."""
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(is_correct) AS correct
            FROM responses
            """
        ).fetchone()

    total = int(row["total"])
    correct = int(row["correct"] or 0)

    return {
        "total": total,
        "correct": correct,
        "incorrect": total - correct,
        "accuracy": (correct / total) if total else None,
    }
def accuracy_by_section(
    db_path: Path | str = "data/user/again.db",
) -> list[dict[str, int | float]]:
    """Calculate accuracy for each section."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                section,
                COUNT(*) AS total,
                SUM(is_correct) AS correct
            FROM responses
            JOIN items ON items.id = responses.item_id
            GROUP BY section
            ORDER BY section
            """
        ).fetchall()

    return [
        {
            "section": row["section"],
            "total": int(row["total"]),
            "correct": int(row["correct"] or 0),
            "incorrect": int(row["total"]) - int(row["correct"] or 0),
            "accuracy": int(row["correct"] or 0) / int(row["total"]),
        }
        for row in rows
    ]
def accuracy_by_topic(
    db_path: Path | str = "data/user/again.db",
) -> list[dict[str, str | int | float]]:
    """Calculate accuracy for each topic."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                topic,
                COUNT(*) AS total,
                SUM(is_correct) AS correct
            FROM responses
            JOIN items ON items.id = responses.item_id
            WHERE topic IS NOT NULL
            GROUP BY topic
            ORDER BY topic
            """
        ).fetchall()

    return [
        {
            "topic": row["topic"],
            "total": int(row["total"]),
            "correct": int(row["correct"] or 0),
            "incorrect": int(row["total"]) - int(row["correct"] or 0),
            "accuracy": int(row["correct"] or 0) / int(row["total"]),
        }
        for row in rows
    ]
def accuracy_by_sitting(
    db_path: Path | str = "data/user/again.db",
) -> list[dict[str, str | int | float]]:
    """Calculate accuracy for each sitting."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                sittings.label AS sitting,
                sittings.taken_on,
                COUNT(*) AS total,
                SUM(responses.is_correct) AS correct
            FROM responses
            JOIN sittings ON sittings.id = responses.sitting_id
            GROUP BY sittings.id
            ORDER BY sittings.taken_on, sittings.id
            """
        ).fetchall()

    return [
        {
            "sitting": row["sitting"],
            "taken_on": row["taken_on"],
            "total": int(row["total"]),
            "correct": int(row["correct"] or 0),
            "incorrect": int(row["total"]) - int(row["correct"] or 0),
            "accuracy": int(row["correct"] or 0) / int(row["total"]),
        }
        for row in rows
    ]
def repeated_misses(
    db_path: Path | str = "data/user/again.db",
    minimum_misses: int = 2,
) -> list[dict[str, str | int]]:
    """Find topics with at least the requested number of incorrect responses."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                items.topic AS topic,
                COUNT(*) AS misses
            FROM responses
            JOIN items ON items.id = responses.item_id
            WHERE responses.is_correct = 0
              AND items.topic IS NOT NULL
            GROUP BY items.topic
            HAVING COUNT(*) >= ?
            ORDER BY misses DESC, topic
            """,
            (minimum_misses,),
        ).fetchall()

    return [
        {
            "topic": row["topic"],
            "misses": int(row["misses"]),
            "status": "Inferred",
        }
        for row in rows
    ]

def accuracy_change_by_sitting(
    db_path: Path | str = "data/user/again.db",
) -> list[dict[str, str | int | float | None]]:
    """Calculate accuracy change from each sitting to the previous sitting."""
    sittings = accuracy_by_sitting(db_path)

    results: list[dict[str, str | int | float | None]] = []

    for index, current in enumerate(sittings):
        previous = sittings[index - 1] if index > 0 else None

        results.append(
            {
                "sitting": current["sitting"],
                "taken_on": current["taken_on"],
                "accuracy": current["accuracy"],
                "previous_accuracy": (
                    previous["accuracy"] if previous else None
                ),
                "accuracy_delta": (
                    current["accuracy"] - previous["accuracy"]
                    if previous
                    else None
                ),
            }
        )

    return results

def accuracy_by_topic_over_time(
    db_path: Path | str = "data/user/again.db",
) -> list[dict[str, str | int | float]]:
    """Calculate topic accuracy for each sitting in chronological order."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
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

    return [
        {
            "sitting": row["sitting"],
            "taken_on": row["taken_on"],
            "topic": row["topic"],
            "total": int(row["total"]),
            "correct": int(row["correct"] or 0),
            "incorrect": int(row["total"]) - int(row["correct"] or 0),
            "accuracy": int(row["correct"] or 0) / int(row["total"]),
        }
        for row in rows
    ]
