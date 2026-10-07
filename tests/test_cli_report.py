"""Focused tests for the `report` command's diagnosis output."""

from again.cli.report import print_report
from again.db.initialize import initialize_database
from again.ingest.candidates import ResponseCandidate
from again.ingest.persistence import persist_candidates


def seed_decline_dataset(db_path) -> None:
    """Insert enough response data to produce a deterministic diagnosis."""
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


def diagnosis_section(output: str) -> str:
    """Return the report text printed under the Diagnoses header."""
    return output.split("Diagnoses:", 1)[1].split("\n\n", 1)[0]


def test_report_includes_diagnosis_output(tmp_path, capsys):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)
    seed_decline_dataset(db_path)

    print_report(db_path)

    output = capsys.readouterr().out

    assert "Diagnoses:" in output

    section = diagnosis_section(output)

    assert (
        "[recent_decline | high] Linear equations shows a recent "
        "performance decline."
    ) in section
    assert (
        "[recent_decline | high] Math shows a recent performance decline."
    ) in section


def test_report_prints_none_when_no_diagnoses(tmp_path, capsys):
    db_path = tmp_path / "again.db"
    initialize_database(db_path)

    # A single all-correct sitting yields no diagnosable patterns.
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
        ],
        db_path,
    )

    print_report(db_path)

    output = capsys.readouterr().out

    assert "Diagnoses:" in output

    section = diagnosis_section(output)

    assert "None detected." in section
    assert "[recent_decline" not in section
