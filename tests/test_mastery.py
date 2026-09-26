from again.mastery.profile import (
    MasteryEstimate,
    build_mastery_profile,
    estimate_mastery,
    recent_topic_accuracy,
)


def test_estimate_mastery():
    result = estimate_mastery(
        topic="Linear equations",
        attempts=10,
        correct=8,
    )

    assert isinstance(result, MasteryEstimate)
    assert result.topic == "Linear equations"
    assert result.mastery == 0.75
    assert result.attempts == 10
    assert result.correct == 8
    assert result.confidence == 10 / 11
    assert result.status == "strong"

def test_estimate_mastery_with_less_evidence():
    result = estimate_mastery(
        topic="Quadratics",
        attempts=3,
        correct=2,
    )

    assert result.mastery == 0.6
    assert result.confidence == 0.75
    assert result.status == "established"
def test_build_mastery_profile():
    profile = build_mastery_profile()

    topics = {estimate.topic: estimate for estimate in profile}

    assert "Linear equations" in topics
    assert topics["Linear equations"].attempts >= 1

import pytest


def test_estimate_mastery_rejects_zero_attempts():
    with pytest.raises(ValueError):
        estimate_mastery(
            topic="Geometry",
            attempts=0,
            correct=0,
        )


def test_estimate_mastery_rejects_invalid_correct_count():
    with pytest.raises(ValueError):
        estimate_mastery(
            topic="Geometry",
            attempts=3,
            correct=4,
        )

def test_recent_topic_accuracy():
    accuracy = recent_topic_accuracy("Linear equations")

    assert accuracy == 0.0

def test_topic_mastery_trend():
    from again.mastery.profile import topic_mastery_trend

    trend = topic_mastery_trend("Linear equations")

    assert trend == "stable"