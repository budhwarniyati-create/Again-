# Again? — Architecture

**Status:** Phase 1 (approved). No application logic in this milestone.

This document is the source of truth for later phases. Do not silently change it. If a better approach appears, propose the change before implementing.

---

## 1. Product

Again? turns item-level academic performance into evidence-bearing claims about recurring learning problems, then tracks what happens after the student changes how they study.

It is **not** a SAT score calculator, error log, generic tutor, chatbot, static dashboard, or LLM wrapper.

**Personality (UI, later):** friendly, curious, slightly cute, calm, encouraging, not preachy. Personality must not weaken analytical language.

**Epistemic rule:** never present an inference as a fact. Claims use:

| Status | Meaning |
| --- | --- |
| Known | Directly present in stored observations |
| Inferred | Derived from evidence, with method recorded |
| Uncertain | Insufficient evidence |

Numeric “calibrated confidence” is deferred until an evaluation set exists. Until then: qualitative status plus sample size.

---

## 2. Design principles (approved)

1. **Item vs response.** An `item` is a reusable question. A `response` is one attempt in one sitting. Scores, dates, and student answers live on responses, not items.
2. **Sitting vs form.** A sitting is one administration. The same official form can be taken more than once.
3. **Missing data is normal.** `items.topic` is nullable. `responses.student_answer` is nullable. Stems, choices, timing, and difficulty are optional.
4. **Validation before analytics.** Parsed input is not an observation until it passes the validation layer. Analytics read only validated observations.
5. **Provenance.** Every imported response is traceable to a source record **and row**. Field-level origin: provided / inferred / extracted.
6. **Source-scoped identity.** `items.external_ref` is unique per `source_id`, not globally unique. The same string from two files is two different items unless we later merge them explicitly.
7. **Raw vs derived.** Observations are append-only facts. Diagnoses, patterns, mastery, rankings, and prose insights are derived and recomputable. Derived data is never written into observation tables.
8. **Baseline before ML.** Deterministic analytics must exist so later models can be compared, not assumed better.
9. **No fake certainty.** Tiny n → “insufficient evidence.” No IRT on n≈1. BKT only if dense per-skill practice logs exist. First mastery model (Phase 8): per-topic Beta–Binomial / empirical Bayes.
10. **Embeddings propose; diagnosis + humans decide.** Semantic similarity ≠ same underlying mistake.
11. **Privacy and copyright.** Local-first. API keys only via environment variables. No College Board (or other copyrighted) stems in git. User data in `data/user/`.
12. **CLI before web.** Two UI levels (student / research) come after the insight objects are trustworthy.

---

## 3. Runtime architecture

```
ingest (CSV / JSON / manual)
        ↓
candidate records
        ↓
validation layer          ← types, required fields, refs, source+row traceability
        ↓
observations (SQLite)     ← students, sittings, items, responses, sources, provenance
        ↓
deterministic analytics   ← counts, rates, trends, thresholded recurrence
        ↓
optional statistical      ← mastery posteriors / intervals (later)
        ↓
optional embeddings       ← candidate links only (later)
        ↓
optional LLM              ← structured hypotheses from structured inputs (later)
        ↓
insights                  ← claim, evidence refs, status, method
        ↓
CLI (then Student view + Research view)
```

**Hard rules**

- Metrics are never computed by an LLM.
- Every stored claim has `status`, `method`, and `evidence_refs`.
- User confirmation is first-class and is not overwritten by a model.
- External LLM calls (if any) are explicit, field-minimized, and keyed from the environment.

### Layer ownership

| Layer | Owns | Does not own |
| --- | --- | --- |
| Deterministic | Accuracy, counts, frequencies, windows, before/after deltas, ranking *inputs*, joins, provenance, insufficient-evidence when n is below threshold | Weakness as identity, causation, OCR as truth |
| Statistical (later) | Per-topic mastery + interval | Population IRT on one student; fake 2-digit % confidence |
| Embeddings (later) | Candidate neighbors / clusters | Pattern identity; diagnosis |
| LLM (later) | Interpreting optional stems, diagnosis hypotheses, prose from structured facts | Counts, percentages, recurrence, eval metrics |
| Human | Confirm / reject / partial; overrides; interventions; experimental hypotheses | Being silently ignored |

---

## 4. Pipeline: ingest → validate → observe → derive

```
source file/row
    → ingest parses bytes into candidates
    → validation accepts or rejects (no partial write of invalid responses)
    → observations stored with source_id + source_row_key
    → analytics / diagnosis / patterns / mastery read observations
    → insights stored in derived tables only
```

Analytics must not query unvalidated staging tables. If we keep a staging area, it is ingest-only and is not part of the observation schema.

---

## 5. Database (Phase 2 will implement)

SQLite, integer PKs, timestamps, nullable where the world is messy. Bold = MVP (Phase 2–3).

### Schema versioning

| Table | Role |
| --- | --- |
| `schema_migrations` | `version` (integer, PK), `applied_at`, `description` |
| `schema_meta` | `key`, `value` — includes current schema version and application compatibility |

Application code records the schema version it expects. Opening a DB with a newer or unknown version is an error, not a silent mismatch. Migrations are ordered, recorded, and never implied by “just CREATE TABLE IF NOT EXISTS” after v1.

### Observations (raw)

- **`students`** — id, display_name
- **`sources`** — id, kind (`manual` / `csv` / `json` / …), uri_or_label, imported_at, notes
- **`source_records`** — id, source_id, row_key (e.g. CSV row number or JSON pointer), raw_payload (optional), imported_at  
  Every imported **response** points at a `source_records` row (or equivalent `source_id` + `source_row_key` unique pair). Manual entry still gets a source of kind `manual` and a record key.
- **`sittings`** — id, student_id, taken_on, label, source_id, duration_sec?
- **`items`** — id, source_id, external_ref?, section, subject, **topic?** (nullable), subtopic?, difficulty?, stem?, choices_json?, correct_answer?, explanation?, image_path?  
  **Uniqueness:** `(source_id, external_ref)` when `external_ref` is present. `external_ref` is **not** globally unique.
- **`responses`** — id, sitting_id, item_id, **student_answer?** (nullable), is_correct, response_time_ms?, source_id, source_record_id (required for imports), raw_payload_json?
- **`field_provenance`** — entity_type, entity_id, field_name, origin (`provided` / `inferred` / `extracted`), confidence_qualitative

`is_correct` may be known even when `student_answer` is missing (e.g. a score report that only marks right/wrong). Conversely an answer may exist before correctness is scored. Validation defines which combinations are allowed.

### Derived (not observations; later phases)

- `diagnoses` — response_id, hypothesis, categories_json (multi-tag; axes may overlap), evidence, status (`inferred` / `user_confirmed` / `rejected`), confidence_qualitative, method (`user` / `rule` / `llm`), model_version?
- `mistake_patterns` — label, lifecycle_state, first_response_id, created_method
- `pattern_members` — pattern_id, response_id, link_status (`candidate` / `confirmed` / `rejected` / `partial`), link_method
- later: `interventions`, `hypotheses`, `insight_runs`, `eval_*`, `embedding_cache`

**Not a table in MVP:** `performance_snapshots`. Compute from `responses`. Persist snapshots only when a model version must be frozen.

**Lifecycle (patterns):**  
`first_observed → diagnosed → repeated → intervention_logged → retested → improving | persistent | resolved | uncertain`  
Transitions need explicit rules (e.g. minimum sittings after intervention).

Diagnosis categories are **multi-tag hypotheses**, not a single exclusive enum. Mechanism, knowledge gap, and context can co-occur.

### What must never happen

- Writing topic accuracy or “recurring” flags onto `responses` or `items`.
- Treating two items as the same because `external_ref` matched across different sources.
- Running analytics on rows that failed validation.
- Storing LLM prose as if it were an observation.

---

## 6. Knowledge model

Versioned taxonomy YAML under `docs/taxonomy/` when Phase 2–3 needs topics (SAT Math / RW domains → topics → optional subtopics). A question may have a null topic. Hierarchical concept graphs wait until there is enough labeled data.

---

## 7. MVP (Phases 2–3)

A user can:

1. Create a local DB (with schema version recorded).
2. Import CSV of item-level results (sitting, section, topic optional, correct/incorrect; stem optional). Each response stores source + row.
3. Run a baseline report: overall / section / topic accuracy; counts; accuracy by sitting; thresholded repeated misses labeled Inferred vs Uncertain.

A user cannot yet diagnose why, cluster semantically, estimate mastery, call an LLM, log interventions, or use a web UI.

---

## 8. Evaluation strategy

Design the protocol now; labels during Phases 4–5; bake-off in Phase 11. Do not wait until after an LLM exists.

Split the research question:

1. Recurring-problem retrieval vs score-only “weakest topic”
2. Diagnosis agreement vs expert
3. Clustering quality (embeddings vs topic+rule baseline)
4. Mastery: interval coverage / ranking vs future accuracy

Gold set: ~30–50 high-quality labeled misses (synthetic or user-owned). Metrics: precision/recall/F1, clustering AMI/ARI if clustering, calibration only if numeric confidence is emitted. Always report n and disagreements.

Repro (later): `eval/runs/` JSON with dataset hash, code version, params, seed, date, metrics.

If a layer does not beat baseline, the README says so and we keep the baseline.

---

## 9. Repository layout

```
again/
  README.md
  pyproject.toml
  .gitignore
  .env.example
  docs/architecture.md          ← this file
  docs/taxonomy/                ← YAML when needed
  src/again/
    db/                         persistence + migrations (Phase 2)
    models/                     typed records
    ingest/                     parse only
    validation/                 gate before observations
    analytics/                  deterministic baseline (Phase 3)
    insights/                   derived claims
    diagnosis/                  Phase 4+
    patterns/                   Phase 5+
    mastery/                    Phase 8+
  tests/
  data/sample/                  synthetic fixtures
  data/user/                    gitignored real history
  eval/                         later
  scripts/                      later reproduce-eval
```

No FastAPI, frontend, embedding, or OCR packages until those milestones.

---

## 10. Risks

| Risk | Mitigation |
| --- | --- |
| IRT/BKT on a few SAT tests | Defer; insufficient-evidence default |
| OCR as the item bank | Phase 14; flag uncertainty |
| SAT stems in git | Forbidden; synthetic samples only |
| Embeddings as identity | Candidate links only |
| Calibrated % | Qualitative status until eval |
| Causal intervention language | Before/after wording only |
| Two UIs too early | CLI until insight objects exist |
| Time-pressure / guessing diagnoses | Require timing or omit/guess flags, else uncertain |

---

## 11. Development order

| # | Milestone | Ships |
| --- | --- | --- |
| **1** | Repo + architecture | This tree |
| **2** | SQLite + ingest + validation | Observations, migrations, CSV/JSON, pytest |
| **3** | Baseline analytics + CLI report | Known / Inferred / Uncertain |
| **4** | Diagnosis (human + optional rules) | Derived `diagnoses`; no LLM |
| **5** | Mistake patterns | Manual + rule grouping; yes/no/partial |
| **6** | Eval skeleton | Label format + baseline metrics |
| **7** | Charts | Only plots that answer a question |
| **8** | Mastery v1 | Beta–Binomial per topic |
| **9** | Embeddings | Candidates vs Phase 5 rules on gold set |
| **10** | LLM diagnosis | Structured; never counters |
| **11** | Interventions + experimental hypotheses | Supported / contradicted / insufficient |
| **12** | Formal eval bake-off | Honest writeup |
| **13** | Web: Student + Research | Same insight objects |
| **14** | OCR ingest | Uncertain extraction flagged |

Phase 2 starts only after this Phase 1 tree is accepted.
