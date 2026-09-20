"""Tests for deterministic pattern detection."""
from again.db.connection import connect
from again.insights.patterns import (
    LearningInsight,
    repeated_miss_insights,
    repeated_miss_topic_insights,
    section_accuracy_drop_insights,
    topic_accuracy_drop_insights,
    topic_regression_insights,
    get_learning_insights,
)

from again.insights.patterns import LearningInsight, topic_accuracy_drop_insights
from again.db.initialize import initialize_database
from again.ingest.candidates import ResponseCandidate
from again.ingest.persistence import persist_candidates
from again.patterns.detector import detect_repeated_miss_topics, detect_repeated_miss_topics_across_sittings, detect_topic_accuracy_drops, detect_topic_regressions, detect_section_accuracy_drops


def test_detect_repeated_miss_topics(tmp_path):
    db_path = tmp_path / "patterns.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-4",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Quadratics",
            external_ref="Q3",
            student_answer="C",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "miss_count": 2,
        }
    ]
def test_detect_repeated_miss_topics_across_sittings(tmp_path):
    db_path = tmp_path / "patterns_over_time.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-15",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "miss_count": 2,
        }
    ]
def test_detect_repeated_miss_topics_across_sittings_only(tmp_path):
    db_path = tmp_path / "cross_sitting.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-4",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Quadratics",
            taken_on="2026-09-15",
            external_ref="Q3",
            student_answer="C",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics_across_sittings(db_path)

    assert result == []


def test_detect_repeated_miss_topics_across_sittings_finds_pattern(tmp_path):
    db_path = tmp_path / "cross_sitting_found.db"
    initialize_database(db_path)

    candidates = [
        ResponseCandidate(
            source_row_key="row-2",
            sitting_label="SAT Test 1",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-01",
            external_ref="Q1",
            student_answer="A",
            is_correct=False,
        ),
        ResponseCandidate(
            source_row_key="row-3",
            sitting_label="SAT Test 2",
            section="Math",
            subject="Math",
            topic="Linear equations",
            taken_on="2026-09-15",
            external_ref="Q2",
            student_answer="B",
            is_correct=False,
        ),
    ]

    persist_candidates(candidates, db_path)

    result = detect_repeated_miss_topics_across_sittings(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "sitting_count": 2,
        }
    ]

def test_detect_topic_accuracy_drops(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
        ],
        db_path,
    )

    result = detect_topic_accuracy_drops(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "previous_sitting": "SAT Test 1",
            "current_sitting": "SAT Test 2",
            "previous_accuracy": 1.0,
            "current_accuracy": 0.0,
            "accuracy_delta": -1.0,
        }
    ]

def test_detect_topic_regressions(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
        ],
        db_path,
    )

    result = detect_topic_regressions(db_path)

    assert result == [
        {
            "topic": "Linear equations",
            "current_sitting": "SAT Test 2",
            "current_taken_on": "2026-09-19",
        }
    ]
 
 
def test_detect_section_accuracy_drops(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Quadratics",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-3",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
            ResponseCandidate(
                source_row_key="row-4",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Quadratics",
                taken_on="2026-09-19",
                is_correct=True,
            ),
        ],
        db_path,
    )

    result = detect_section_accuracy_drops(db_path)

    assert result == [
        {
            "section": "Math",
            "previous_sitting": "SAT Test 1",
            "current_sitting": "SAT Test 2",
            "previous_accuracy": 1.0,
            "current_accuracy": 0.5,
            "accuracy_delta": -0.5,
        }
    ]
def test_learning_insight_model():
    insight = LearningInsight(
        pattern_type="topic_accuracy_drop",
        subject="Math",
        topic="Linear equations",
        message="Accuracy decreased on Linear equations.",
        evidence={
            "previous_accuracy": 1.0,
            "current_accuracy": 0.5,
            "accuracy_delta": -0.5,
        },
    )

    assert insight.pattern_type == "topic_accuracy_drop"
    assert insight.subject == "Math"
    assert insight.topic == "Linear equations"
    assert insight.evidence["accuracy_delta"] == -0.5

def test_topic_accuracy_drop_insights(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
        ],
        db_path,
    )

    insights = topic_accuracy_drop_insights(db_path)

    assert len(insights) == 1
    assert insights[0].pattern_type == "topic_accuracy_drop"
    assert insights[0].topic == "Linear equations"
    assert insights[0].evidence["accuracy_delta"] == -1.0

def test_repeated_miss_insights(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=False,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
        ],
        db_path,
    )

    insights = repeated_miss_insights(db_path)

    assert len(insights) == 1
    assert insights[0].pattern_type == "repeated_miss_across_sittings"
    assert insights[0].topic == "Linear equations"
    assert insights[0].evidence["sitting_count"] == 2

def test_topic_regression_insights(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
        ],
        db_path,
    )

    insights = topic_regression_insights(db_path)

    assert len(insights) == 1
    assert insights[0].pattern_type == "topic_regression"
    assert insights[0].topic == "Linear equations"
    assert insights[0].evidence["current_sitting"] == "SAT Test 2"

def test_section_accuracy_drop_insights(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    persist_candidates(
        [
            ResponseCandidate(
                source_row_key="row-1",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-2",
                sitting_label="SAT Test 1",
                section="Math",
                subject="Math",
                topic="Quadratics",
                taken_on="2026-09-18",
                is_correct=True,
            ),
            ResponseCandidate(
                source_row_key="row-3",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Linear equations",
                taken_on="2026-09-19",
                is_correct=False,
            ),
            ResponseCandidate(
                source_row_key="row-4",
                sitting_label="SAT Test 2",
                section="Math",
                subject="Math",
                topic="Quadratics",
                taken_on="2026-09-19",
                is_correct=True,
            ),
        ],
        db_path,
    )

    insights = section_accuracy_drop_insights(db_path)

    assert len(insights) == 1
    assert insights[0].pattern_type == "section_accuracy_drop"
    assert insights[0].subject == "Math"
    assert insights[0].evidence["accuracy_delta"] == -0.5

def test_repeated_miss_topic_insights(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    with connect(db_path) as connection:
        connection.execute(
            "INSERT INTO students (id, display_name) VALUES (1, 'Test Student')"
        )
        connection.execute(
            """
            INSERT INTO sources (id, kind, uri_or_label, imported_at)
            VALUES (1, 'test', 'test', '2026-09-18T00:00:00')
            """
        )
        connection.execute(
            """
            INSERT INTO sittings (id, student_id, taken_on, label)
            VALUES (1, 1, '2026-09-18', 'SAT Test 1')
            """
        )
        connection.execute(
            """
            INSERT INTO items
                (id, source_id, external_ref, section, subject, topic)
            VALUES
                (1, 1, 'q1', 'Math', 'Math', 'Linear equations'),
                (2, 1, 'q2', 'Math', 'Math', 'Linear equations')
            """
        )
        connection.execute(
            """
            INSERT INTO responses
                (id, sitting_id, item_id, student_answer, is_correct)
            VALUES
                (1, 1, 1, 'A', 0),
                (2, 1, 2, 'B', 0)
            """
        )

    insights = repeated_miss_topic_insights(db_path)

    assert len(insights) == 1
    assert insights[0].pattern_type == "repeated_miss_topic"
    assert insights[0].topic == "Linear equations"
    assert insights[0].evidence["miss_count"] == 2

def test_get_learning_insights(tmp_path):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    with connect(db_path) as connection:
        connection.execute(
            "INSERT INTO students (id, display_name) VALUES (1, 'Test Student')"
        )
        connection.execute(
            """
            INSERT INTO sources (id, kind, uri_or_label, imported_at)
            VALUES (1, 'test', 'test', '2026-09-18T00:00:00')
            """
        )
        connection.execute(
            """
            INSERT INTO sittings (id, student_id, taken_on, label)
            VALUES
                (1, 1, '2026-09-18', 'SAT Test 1'),
                (2, 1, '2026-09-19', 'SAT Test 2')
            """
        )
        connection.execute(
            """
            INSERT INTO items
                (id, source_id, external_ref, section, subject, topic)
            VALUES
                (1, 1, 'q1', 'Math', 'Math', 'Linear equations'),
                (2, 1, 'q2', 'Math', 'Math', 'Linear equations')
            """
        )
        connection.execute(
            """
            INSERT INTO responses
                (id, sitting_id, item_id, student_answer, is_correct)
            VALUES
                (1, 1, 1, 'A', 1),
                (2, 2, 2, 'B', 0)
            """
        )

    insights = get_learning_insights(db_path)

    assert len(insights) >= 2
    assert any(
        insight.pattern_type == "topic_accuracy_drop"
        for insight in insights
    )
    assert any(
        insight.pattern_type == "topic_regression"
        for insight in insights
    )