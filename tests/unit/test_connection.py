"""Tests for the SQLite connection manager."""

import os
import sqlite3

from app.database.connection import get_connection


def test_returns_sqlite_connection(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_row_factory_set(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, val TEXT)")
    conn.execute("INSERT INTO t (val) VALUES ('hello')")
    row = conn.execute("SELECT * FROM t").fetchone()
    assert row["val"] == "hello"
    conn.close()


def test_foreign_keys_enabled(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = get_connection(db_path)
    result = conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1
    conn.close()


def test_reads_db_path_from_env(tmp_path, monkeypatch):
    db_path = str(tmp_path / "env.db")
    monkeypatch.setenv("DB_PATH", db_path)
    conn = get_connection()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()
    assert os.path.exists(db_path)


def test_creates_parent_directory(tmp_path):
    db_path = str(tmp_path / "subdir" / "nested" / "test.db")
    conn = get_connection(db_path)
    assert os.path.exists(db_path)
    conn.close()
