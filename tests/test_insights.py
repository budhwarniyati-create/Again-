from again.insights.patterns import LearningInsight


def test_mastery_insight_is_structured():
    insight = LearningInsight(
        pattern_type="mastery_status",
        subject=None,
        section=None,
        topic="Linear equations",
        message="Linear equations mastery is established.",
        evidence={
            "mastery": 0.68,
            "confidence": 0.8,
            "status": "established",
            "recent_accuracy": 0.8,
            "trend": "improving",
        },
    )

    assert insight.pattern_type == "mastery_status"
    assert insight.topic == "Linear equations"
    assert insight.evidence["mastery"] == 0.68
    assert insight.evidence["trend"] == "improving"
from again.insights.patterns import mastery_status_insights


def test_mastery_status_insights():
    insights = mastery_status_insights()

    assert isinstance(insights, list)

    linear = [
        insight
        for insight in insights
        if insight.topic == "Linear equations"
    ]

    assert linear

    insight = linear[0]

    assert insight.pattern_type == "mastery_status"
    assert "mastery" in insight.evidence
    assert "confidence" in insight.evidence
    assert "trend" in insight.evidence
