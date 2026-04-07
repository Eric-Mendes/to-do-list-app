"""CRUD operations for tags."""

import sqlite3
from typing import Optional


def create_tag(conn: sqlite3.Connection, name: str, color: str = "#6366f1") -> int:
    """Create a tag and return its ID."""
    cur = conn.execute(
        "INSERT INTO tags (name, color) VALUES (?, ?)", (name, color)
    )
    conn.commit()
    return cur.lastrowid


def get_tag(conn: sqlite3.Connection, tag_id: int) -> Optional[sqlite3.Row]:
    """Return a tag by ID, or None if not found."""
    return conn.execute("SELECT * FROM tags WHERE id=?", (tag_id,)).fetchone()


def get_tag_by_name(conn: sqlite3.Connection, name: str) -> Optional[sqlite3.Row]:
    """Return a tag by name, or None if not found."""
    return conn.execute("SELECT * FROM tags WHERE name=?", (name,)).fetchone()


def get_all_tags(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all tags ordered by name."""
    return conn.execute("SELECT * FROM tags ORDER BY name").fetchall()


def update_tag(
    conn: sqlite3.Connection,
    tag_id: int,
    name: Optional[str] = None,
    color: Optional[str] = None,
) -> None:
    """Update tag name and/or color."""
    tag = get_tag(conn, tag_id)
    if tag is None:
        raise ValueError(f"Tag {tag_id} not found")
    new_name = name if name is not None else tag["name"]
    new_color = color if color is not None else tag["color"]
    conn.execute(
        "UPDATE tags SET name=?, color=? WHERE id=?",
        (new_name, new_color, tag_id),
    )
    conn.commit()


def delete_tag(conn: sqlite3.Connection, tag_id: int) -> None:
    """Delete a tag (cascades through list_tags)."""
    conn.execute("DELETE FROM tags WHERE id=?", (tag_id,))
    conn.commit()


def assign_tag_to_list(
    conn: sqlite3.Connection, list_id: int, tag_id: int
) -> None:
    """Assign a tag to a list (no-op if already assigned)."""
    conn.execute(
        "INSERT OR IGNORE INTO list_tags (list_id, tag_id) VALUES (?, ?)",
        (list_id, tag_id),
    )
    conn.commit()


def remove_tag_from_list(
    conn: sqlite3.Connection, list_id: int, tag_id: int
) -> None:
    """Remove a tag assignment from a list."""
    conn.execute(
        "DELETE FROM list_tags WHERE list_id=? AND tag_id=?", (list_id, tag_id)
    )
    conn.commit()


def get_tags_for_list(
    conn: sqlite3.Connection, list_id: int
) -> list[sqlite3.Row]:
    """Return all tags assigned to a list."""
    return conn.execute(
        """
        SELECT t.* FROM tags t
        JOIN list_tags lt ON lt.tag_id = t.id
        WHERE lt.list_id = ?
        ORDER BY t.name
        """,
        (list_id,),
    ).fetchall()
