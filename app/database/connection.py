"""SQLite connection management."""

import os
import sqlite3

_DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "todo.db"
)


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Return a configured SQLite connection.

    Reads DB_PATH from the environment if db_path is not provided.
    Enables WAL journal mode and foreign key enforcement.
    Sets row_factory to sqlite3.Row for dict-like access.
    """
    path = db_path or os.environ.get("DB_PATH", _DEFAULT_DB_PATH)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.commit()
    return conn
