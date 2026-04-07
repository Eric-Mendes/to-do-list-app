"""CRUD operations for tasks."""

import sqlite3
from typing import Optional


def create_task(
    conn: sqlite3.Connection,
    list_id: int,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> int:
    """Create a task and return its ID."""
    cur = conn.execute(
        """
        INSERT INTO tasks (list_id, title, description, priority, due_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (list_id, title, description, priority, due_date),
    )
    conn.commit()
    return cur.lastrowid


def get_task(conn: sqlite3.Connection, task_id: int) -> Optional[sqlite3.Row]:
    """Return a task by ID, or None if not found."""
    return conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()


def get_tasks_for_list(
    conn: sqlite3.Connection,
    list_id: int,
    status: Optional[str] = None,
) -> list[sqlite3.Row]:
    """Return tasks for a list, optionally filtered by status.

    Ordered by: status (pending first), due_date (nulls last), priority (high first).
    """
    priority_order = "CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END"
    status_order = (
        "CASE status WHEN 'in_progress' THEN 0 WHEN 'pending' THEN 1 "
        "WHEN 'completed' THEN 2 ELSE 3 END"
    )
    if status:
        return conn.execute(
            f"""
            SELECT * FROM tasks
            WHERE list_id=? AND status=?
            ORDER BY {status_order}, due_date ASC NULLS LAST, {priority_order}
            """,
            (list_id, status),
        ).fetchall()
    return conn.execute(
        f"""
        SELECT * FROM tasks
        WHERE list_id=?
        ORDER BY {status_order}, due_date ASC NULLS LAST, {priority_order}
        """,
        (list_id,),
    ).fetchall()


def update_task(
    conn: sqlite3.Connection,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    list_id: Optional[int] = None,
) -> None:
    """Update one or more fields of a task."""
    task = get_task(conn, task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found")

    new_title = title if title is not None else task["title"]
    new_desc = description if description is not None else task["description"]
    new_status = status if status is not None else task["status"]
    new_priority = priority if priority is not None else task["priority"]
    new_due_date = due_date if due_date is not None else task["due_date"]
    new_list_id = list_id if list_id is not None else task["list_id"]

    conn.execute(
        """
        UPDATE tasks
        SET title=?, description=?, status=?, priority=?, due_date=?,
            list_id=?, updated_at=datetime('now')
        WHERE id=?
        """,
        (new_title, new_desc, new_status, new_priority, new_due_date, new_list_id, task_id),
    )
    conn.commit()


def complete_task(conn: sqlite3.Connection, task_id: int) -> None:
    """Mark a task as completed and record completed_at."""
    task = get_task(conn, task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found")
    conn.execute(
        """
        UPDATE tasks
        SET status='completed', completed_at=datetime('now'), updated_at=datetime('now')
        WHERE id=?
        """,
        (task_id,),
    )
    conn.commit()


def uncomplete_task(conn: sqlite3.Connection, task_id: int) -> None:
    """Revert a completed task back to pending."""
    task = get_task(conn, task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found")
    conn.execute(
        """
        UPDATE tasks
        SET status='pending', completed_at=NULL, updated_at=datetime('now')
        WHERE id=?
        """,
        (task_id,),
    )
    conn.commit()


def delete_task(conn: sqlite3.Connection, task_id: int) -> None:
    """Delete a task."""
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()


def get_tasks_with_due_date(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all non-cancelled tasks that have a due date set."""
    return conn.execute(
        """
        SELECT t.*, tl.name AS list_name
        FROM tasks t
        JOIN task_lists tl ON tl.id = t.list_id
        WHERE t.due_date IS NOT NULL AND t.status != 'cancelled'
        ORDER BY t.due_date
        """
    ).fetchall()


def get_overdue_tasks(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return tasks past their due date that are not completed or cancelled."""
    return conn.execute(
        """
        SELECT * FROM tasks
        WHERE due_date < date('now')
          AND status NOT IN ('completed', 'cancelled')
        ORDER BY due_date
        """
    ).fetchall()


# ---------------------------------------------------------------------------
# Analytics queries
# ---------------------------------------------------------------------------


def get_tasks_in_period(
    conn: sqlite3.Connection, start: str, end: str
) -> list[sqlite3.Row]:
    """Return tasks created between start and end (inclusive, ISO-8601 dates)."""
    return conn.execute(
        "SELECT * FROM tasks WHERE date(created_at) BETWEEN ? AND ?",
        (start, end),
    ).fetchall()


def get_completion_stats(
    conn: sqlite3.Connection, start: str, end: str
) -> dict:
    """Return created, completed, planned, and missed counts for a period."""
    created = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE date(created_at) BETWEEN ? AND ?",
        (start, end),
    ).fetchone()[0]

    completed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='completed' AND date(completed_at) BETWEEN ? AND ?",
        (start, end),
    ).fetchone()[0]

    planned = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='pending' AND due_date >= date('now')",
    ).fetchone()[0]

    missed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE due_date < date('now') AND status NOT IN ('completed','cancelled')",
    ).fetchone()[0]

    return {
        "created": created,
        "completed": completed,
        "planned": planned,
        "missed": missed,
    }


def get_tasks_by_status(conn: sqlite3.Connection) -> dict[str, int]:
    """Return count of tasks grouped by status."""
    rows = conn.execute(
        "SELECT status, COUNT(*) AS cnt FROM tasks GROUP BY status"
    ).fetchall()
    return {row["status"]: row["cnt"] for row in rows}


def get_completion_rate_by_list(conn: sqlite3.Connection) -> list[dict]:
    """Return completion rate per list as a list of dicts."""
    rows = conn.execute(
        """
        SELECT
            tl.name,
            COUNT(*) AS total,
            SUM(CASE WHEN t.status='completed' THEN 1 ELSE 0 END) AS completed
        FROM task_lists tl
        JOIN tasks t ON t.list_id = tl.id
        GROUP BY tl.id, tl.name
        ORDER BY tl.name
        """
    ).fetchall()
    return [
        {
            "list": row["name"],
            "total": row["total"],
            "completed": row["completed"],
            "rate": round(row["completed"] / row["total"] * 100, 1) if row["total"] else 0,
        }
        for row in rows
    ]


def get_completion_streak(conn: sqlite3.Connection) -> int:
    """Return the current streak of consecutive days with at least one completed task."""
    rows = conn.execute(
        """
        SELECT DISTINCT date(completed_at) AS day
        FROM tasks
        WHERE status='completed' AND completed_at IS NOT NULL
        ORDER BY day DESC
        """
    ).fetchall()
    if not rows:
        return 0

    from datetime import date, timedelta

    today = date.today()
    streak = 0
    for row in rows:
        expected = today - timedelta(days=streak)
        if row["day"] == expected.isoformat():
            streak += 1
        else:
            break
    return streak
