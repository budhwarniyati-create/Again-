-- Again? SQLite schema
-- Phase 2A: Observation layer

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL,
    uri_or_label TEXT,
    imported_at TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS source_records (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    row_key TEXT NOT NULL,
    raw_payload TEXT,
    imported_at TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE (source_id, row_key)
);

CREATE TABLE IF NOT EXISTS sittings (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    taken_on TEXT NOT NULL,
    label TEXT,
    source_id INTEGER,
    duration_sec INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    external_ref TEXT,
    section TEXT,
    subject TEXT,
    topic TEXT,
    subtopic TEXT,
    difficulty TEXT,
    stem TEXT,
    choices_json TEXT,
    correct_answer TEXT,
    explanation TEXT,
    image_path TEXT,
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_items_source_external_ref
ON items(source_id, external_ref)
WHERE external_ref IS NOT NULL;

CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY,
    sitting_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    student_answer TEXT,
    is_correct INTEGER NOT NULL,
    response_time_ms INTEGER,
    source_id INTEGER,
    source_record_id INTEGER,
    raw_payload_json TEXT,
    FOREIGN KEY (sitting_id) REFERENCES sittings(id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (source_id) REFERENCES sources(id),
    FOREIGN KEY (source_record_id) REFERENCES source_records(id)
);

CREATE TABLE IF NOT EXISTS field_provenance (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    origin TEXT NOT NULL,
    confidence_qualitative TEXT
);
