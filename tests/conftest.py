"""Shared pytest fixtures."""

import sqlite3

import pytest

from app.database.migrations import run_migrations


@pytest.fixture
def db() -> sqlite3.Connection:
    """In-memory SQLite connection with schema applied."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    run_migrations(conn)
    yield conn
    conn.close()
