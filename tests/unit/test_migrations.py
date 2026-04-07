"""Tests for database schema migrations."""

import sqlite3

from app.database.migrations import run_migrations


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


def test_all_tables_created(db):
    for table in ("tags", "task_lists", "list_tags", "tasks"):
        assert _table_exists(db, table), f"Table '{table}' was not created"


def test_migrations_are_idempotent(db):
    run_migrations(db)
    run_migrations(db)
    for table in ("tags", "task_lists", "list_tags", "tasks"):
        assert _table_exists(db, table)


def test_tags_columns(db):
    cols = _columns(db, "tags")
    assert {"id", "name", "color", "created_at"}.issubset(cols)


def test_task_lists_columns(db):
    cols = _columns(db, "task_lists")
    assert {"id", "name", "description", "created_at", "updated_at"}.issubset(cols)


def test_list_tags_columns(db):
    cols = _columns(db, "list_tags")
    assert {"list_id", "tag_id"}.issubset(cols)


def test_tasks_columns(db):
    cols = _columns(db, "tasks")
    assert {
        "id", "list_id", "title", "description", "status",
        "priority", "due_date", "completed_at", "created_at", "updated_at",
    }.issubset(cols)


def test_tasks_cascade_delete(db):
    db.execute("INSERT INTO task_lists (name) VALUES ('My List')")
    list_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute("INSERT INTO tasks (list_id, title) VALUES (?, 'Task 1')", (list_id,))
    db.commit()

    db.execute("DELETE FROM task_lists WHERE id=?", (list_id,))
    db.commit()

    tasks = db.execute("SELECT * FROM tasks WHERE list_id=?", (list_id,)).fetchall()
    assert tasks == []


def test_list_tags_cascade_delete_on_list(db):
    db.execute("INSERT INTO tags (name) VALUES ('work')")
    tag_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute("INSERT INTO task_lists (name) VALUES ('My List')")
    list_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute("INSERT INTO list_tags (list_id, tag_id) VALUES (?, ?)", (list_id, tag_id))
    db.commit()

    db.execute("DELETE FROM task_lists WHERE id=?", (list_id,))
    db.commit()

    rows = db.execute("SELECT * FROM list_tags WHERE list_id=?", (list_id,)).fetchall()
    assert rows == []
