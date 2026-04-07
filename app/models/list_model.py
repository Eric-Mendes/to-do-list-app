"""CRUD operations for task lists."""

import sqlite3
from typing import Optional


def create_list(
    conn: sqlite3.Connection, name: str, description: Optional[str] = None
) -> int:
    """Create a task list and return its ID."""
    cur = conn.execute(
        "INSERT INTO task_lists (name, description) VALUES (?, ?)",
        (name, description),
    )
    conn.commit()
    return cur.lastrowid


def get_list(conn: sqlite3.Connection, list_id: int) -> Optional[sqlite3.Row]:
    """Return a task list by ID, or None if not found."""
    return conn.execute("SELECT * FROM task_lists WHERE id=?", (list_id,)).fetchone()


def get_all_lists(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all task lists ordered by name."""
    return conn.execute("SELECT * FROM task_lists ORDER BY name").fetchall()


def get_lists_by_tag(conn: sqlite3.Connection, tag_id: int) -> list[sqlite3.Row]:
    """Return all lists that have a given tag assigned."""
    return conn.execute(
        """
        SELECT tl.* FROM task_lists tl
        JOIN list_tags lt ON lt.list_id = tl.id
        WHERE lt.tag_id = ?
        ORDER BY tl.name
        """,
        (tag_id,),
    ).fetchall()


def update_list(
    conn: sqlite3.Connection,
    list_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> None:
    """Update a list's name and/or description."""
    lst = get_list(conn, list_id)
    if lst is None:
        raise ValueError(f"List {list_id} not found")
    new_name = name if name is not None else lst["name"]
    new_desc = description if description is not None else lst["description"]
    conn.execute(
        """
        UPDATE task_lists
        SET name=?, description=?, updated_at=datetime('now')
        WHERE id=?
        """,
        (new_name, new_desc, list_id),
    )
    conn.commit()


def delete_list(conn: sqlite3.Connection, list_id: int) -> None:
    """Delete a list (cascades to tasks and list_tags)."""
    conn.execute("DELETE FROM task_lists WHERE id=?", (list_id,))
    conn.commit()


def get_task_counts(conn: sqlite3.Connection, list_id: int) -> dict:
    """Return task counts for a list: total, completed, overdue."""
    row = conn.execute(
        """
        SELECT
            COUNT(*)                                                   AS total,
            SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END)       AS completed,
            SUM(
                CASE WHEN due_date < date('now')
                          AND status NOT IN ('completed', 'cancelled')
                THEN 1 ELSE 0 END
            )                                                          AS overdue
        FROM tasks
        WHERE list_id=?
        """,
        (list_id,),
    ).fetchone()
    return {
        "total": row["total"] or 0,
        "completed": row["completed"] or 0,
        "overdue": row["overdue"] or 0,
    }
