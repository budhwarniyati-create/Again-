"""Database initialization for Again?."""

from pathlib import Path

from .migrate import migrate


DEFAULT_DB_PATH = Path("data/user/again.db")


def initialize_database(db_path: Path | str = DEFAULT_DB_PATH) -> int:
    """Initialize or upgrade the database using migrations."""
    return migrate(db_path)
