"""Learning profile and mastery estimates for Again?."""

from dataclasses import dataclass

from again.db.connection import connect


@dataclass(frozen=True)
class MasteryEstimate:
    """Transparent mastery estimate for a single topic."""

    topic: str
    mastery: float
    attempts: int
    correct: int
    confidence: float
    status: str
    recent_accuracy: float | None = None


@dataclass(frozen=True)
class TopicProfile:
    """Learning profile for a single topic."""

    topic: str
    mastery: float
    confidence: float
    status: str
    attempts: int
    correct: int


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

    profile = []

    for row in rows:
        estimate = estimate_mastery(
            topic=row["topic"],
            attempts=int(row["attempts"]),
            correct=int(row["correct"] or 0),
        )

        profile.append(
            MasteryEstimate(
                topic=estimate.topic,
                mastery=estimate.mastery,
                attempts=estimate.attempts,
                correct=estimate.correct,
                confidence=estimate.confidence,
                status=estimate.status,
                recent_accuracy=recent_topic_accuracy(
                    row["topic"],
                    db_path,
                ),
            )
        )

    return profile

def recent_topic_accuracy(
    topic: str,
    db_path: str = "data/user/again.db",
) -> float | None:
    """Return accuracy for a topic in its most recent sitting."""
    with connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                SUM(responses.is_correct) AS correct,
                COUNT(*) AS attempts
            FROM responses
            JOIN items ON items.id = responses.item_id
            JOIN sittings ON sittings.id = responses.sitting_id
            WHERE items.topic = ?
              AND sittings.id = (
                  SELECT sittings.id
                  FROM responses
                  JOIN items ON items.id = responses.item_id
                  JOIN sittings ON sittings.id = responses.sitting_id
                  WHERE items.topic = ?
                  ORDER BY sittings.taken_on DESC, sittings.id DESC
                  LIMIT 1
              )
            """,
            (topic, topic),
        ).fetchone()

    if row["attempts"] == 0:
        return None

    return int(row["correct"] or 0) / int(row["attempts"])