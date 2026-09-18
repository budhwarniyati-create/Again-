"""Tests for Again? typed models."""

from dataclasses import FrozenInstanceError

import pytest

from again.models import Attempt, Mistake, Question, Source, Student


def test_student_is_immutable():
    student = Student(id=None, display_name="Test Student")

    with pytest.raises(FrozenInstanceError):
        student.display_name = "Changed"


def test_source_can_be_created():
    source = Source(
        id=None,
        kind="manual",
        uri_or_label="SAT practice test",
        imported_at="2026-09-18T21:00:00+00:00",
    )

    assert source.kind == "manual"
    assert source.notes is None


def test_question_can_be_created():
    question = Question(
        id=None,
        source_id=None,
        subject="Math",
        topic="Linear equations",
        question_label="SAT Q1",
    )

    assert question.subject == "Math"
    assert question.topic == "Linear equations"


def test_attempt_can_be_created():
    attempt = Attempt(
        id=None,
        question_id=1,
        student_id=1,
        is_correct=False,
        attempted_at="2026-09-18T21:15:00+00:00",
        error_type="careless",
    )

    assert attempt.is_correct is False
    assert attempt.error_type == "careless"


def test_mistake_can_be_created():
    mistake = Mistake(
        id=None,
        attempt_id=1,
        category="careless",
        description="Misread the condition",
        severity="low",
    )

    assert mistake.category == "careless"
    assert mistake.severity == "low"
