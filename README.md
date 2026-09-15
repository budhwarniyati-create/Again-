# Again?

**Why did I get this wrong... again?**

Again? is an evidence-driven personal learning intelligence system. The first use case is SAT preparation. The architecture is meant to grow to other academic domains without becoming a score calculator, a chatbot, or an LLM wrapper.

```
raw performance data
        ↓
question-level analysis
        ↓
pattern detection
        ↓
learning profile
        ↓
intervention
        ↓
new performance
        ↓
measure change
```

The product should feel like a smart friend who has studied your history: curious, calm, encouraging. Personality never replaces rigor. Every important conclusion is **known**, **inferred**, or **uncertain**.

---

## Problem

A total score, or even a section score, does not answer:

- What keeps going wrong?
- Is this actually a recurring problem?
- How confident are we about the diagnosis?
- Is the problem improving?
- What should I prioritize next?
- Did the intervention actually help?

## Motivation

The research question the system is built to *test*, not assume:

> Can combining longitudinal performance data, statistical mastery estimation, semantic similarity, and AI-assisted diagnosis identify recurring learning problems more effectively than simple score-based analysis?

If sophisticated layers do not beat a transparent baseline, we keep the baseline.

## Current status

**Phase 1 — repository and architecture only.** There is no database, ingest pipeline, or analytics yet.

| Phase | Status |
| --- | --- |
| 1 Architecture + repo | This milestone |
| 2 Data model + SQLite | Next |
| 3 Baseline analytics | Planned |
| 4–14 Diagnosis through polish | Planned; see [docs/architecture.md](docs/architecture.md) |

## Architecture (summary)

- **Local-first Python library**, SQLite as system of record, CLI first, web later.
- **Observations vs derived data are strictly separated.** Analytics never writes back into raw responses.
- **Ingest → validation → observations → analytics → (later) statistical / ML / LLM insights.**
- Metrics are computed in code. LLMs, when used, only synthesize structured inputs.
- Question **stems are optional**. Metadata-only history is valid.
- Real SAT / copyrighted stems stay in `data/user/` (gitignored). Sample data is synthetic.

Full design, schema, evaluation plan, and risks: **[docs/architecture.md](docs/architecture.md)**.

## Methodology (planned)

1. Transparent baseline (counts, rates, recurrence thresholds).
2. Human- and rule-based diagnosis, then pattern grouping.
3. Evaluation skeleton with expert labels.
4. Per-topic Bayesian mastery only when n is large enough; otherwise “insufficient evidence.”
5. Embeddings as *candidate* similarity, not identity.
6. Optional LLM hypotheses, never for arithmetic.
7. Intervention and n-of-1 hypothesis tracking without causal overclaim.

## Evaluation (planned)

Compare baseline vs embeddings vs LLM-assisted diagnosis on a small gold set. Report n, disagreement examples, and (only if we emit numeric confidence) calibration. Details in the architecture doc.

## Limitations (now)

- No running application.
- No labeled evaluation data yet.
- One-student longitudinal data cannot support population IRT.
- Copyrighted question text will never be committed to this repository.

## Future work

See the phase list in [docs/architecture.md](docs/architecture.md). Do not implement later phases until the previous milestone is accepted.

## Setup

Requires Python 3.11+.

```bash
cd again
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -e ".[dev]"
pytest
```

Phase 1 only asserts that the `again` package imports. There is no CLI and no database.

## License

MIT (see `pyproject.toml`). User data in `data/user/` is not part of the public project.
