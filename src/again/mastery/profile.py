"""Learning profile and mastery estimates for Again?."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MasteryEstimate:
    """Transparent mastery estimate for a single topic."""

    topic: str
    mastery: float
    attempts: int
    correct: int
    confidence: float
    status: str

def estimate_mastery(
    topic: str,
    attempts: int,
    correct: int,
) -> MasteryEstimate:
    """Estimate mastery from observed correct and incorrect attempts."""
    if attempts <= 0:
        raise ValueError("attempts must be greater than 0")

    if not 0 <= correct <= attempts:
        raise ValueError("correct must be between 0 and attempts")

    mastery = (correct + 1) / (attempts + 2)
    confidence = 1 - (1 / (attempts + 1))

    if mastery < 0.5:
        status = "developing"
    elif mastery < 0.75:
        status = "established"
    else:
        status = "strong"

    return MasteryEstimate(
        topic=topic,
        mastery=mastery,
        attempts=attempts,
        correct=correct,
        confidence=confidence,
        status=status,
    )
from again.db.connection import connect


def build_mastery_profile(
    db_path: str = "data/user/again.db",
) -> list[MasteryEstimate]:
    """Build mastery estimates for every topic in the database."""
    with connect(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                items.topic AS topic,
                COUNT(*) AS attempts,
                SUM(responses.is_correct) AS correct
            FROM responses
            JOIN items ON items.id = responses.item_id
            WHERE items.topic IS NOT NULL
            GROUP BY items.topic
            ORDER BY items.topic
            """
        ).fetchall()

    return [
        estimate_mastery(
            topic=row["topic"],
            attempts=int(row["attempts"]),
            correct=int(row["correct"] or 0),
        )
        for row in rows
    ]