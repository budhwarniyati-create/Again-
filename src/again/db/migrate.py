"""Schema migration runner for Again?."""

from datetime import datetime, timezone
from pathlib import Path

from .connection import connect


MIGRATIONS_DIR = Path(__file__).with_name("migrations")


def _migration_files() -> list[Path]:
    """Return migration files in version order."""
    return sorted(MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql"))


def _ensure_migration_table(connection) -> None:
    """Create the migration tracking table if needed."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )


def current_version(connection) -> int:
    """Return the highest migration version already applied."""
    row = connection.execute(
        "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
    ).fetchone()
    return int(row["version"])


def migrate(db_path) -> int:
    """Apply all pending migrations and return the resulting version."""
    with connect(db_path) as connection:
        _ensure_migration_table(connection)

        applied = current_version(connection)

        for migration in _migration_files():
            version = int(migration.name[:3])

            if version <= applied:
                continue

            sql = migration.read_text(encoding="utf-8")

            with connection:
                connection.executescript(sql)
                connection.execute(
                    """
                    INSERT INTO schema_migrations
                        (version, applied_at, description)
                    VALUES (?, ?, ?)
                    """,
                    (
                        version,
                        datetime.now(timezone.utc).isoformat(),
                        migration.stem[4:].replace("_", " "),
                    ),
                )

            applied = version

        connection.execute(
            """
            INSERT INTO schema_meta (key, value)
            VALUES ('current_schema_version', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (str(applied),),
        )

        return applied
