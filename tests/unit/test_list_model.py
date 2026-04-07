"""Tests for task list model CRUD operations."""

import pytest

from app.models.list_model import (
    create_list,
    delete_list,
    get_all_lists,
    get_list,
    get_lists_by_tag,
    get_task_counts,
    update_list,
)
from app.models.tag_model import assign_tag_to_list, create_tag


def test_create_list_returns_id(db):
    list_id = create_list(db, "Shopping")
    assert isinstance(list_id, int) and list_id > 0


def test_create_list_stores_name_and_description(db):
    list_id = create_list(db, "Work", "Work-related tasks")
    lst = get_list(db, list_id)
    assert lst["name"] == "Work"
    assert lst["description"] == "Work-related tasks"


def test_create_list_no_description(db):
    list_id = create_list(db, "Simple")
    lst = get_list(db, list_id)
    assert lst["description"] is None


def test_get_list_returns_correct_record(db):
    list_id = create_list(db, "My List")
    lst = get_list(db, list_id)
    assert lst["id"] == list_id
    assert lst["name"] == "My List"


def test_get_list_returns_none_for_missing(db):
    assert get_list(db, 9999) is None


def test_get_all_lists_empty(db):
    assert get_all_lists(db) == []


def test_get_all_lists_returns_all_ordered(db):
    create_list(db, "Zeta")
    create_list(db, "Alpha")
    create_list(db, "Milo")
    lists = get_all_lists(db)
    assert [l["name"] for l in lists] == ["Alpha", "Milo", "Zeta"]


def test_update_list_name(db):
    list_id = create_list(db, "Old Name")
    update_list(db, list_id, name="New Name")
    assert get_list(db, list_id)["name"] == "New Name"


def test_update_list_description(db):
    list_id = create_list(db, "My List")
    update_list(db, list_id, description="New desc")
    assert get_list(db, list_id)["description"] == "New desc"


def test_update_list_updated_at_changes(db):
    list_id = create_list(db, "Timely")
    original_ts = get_list(db, list_id)["updated_at"]
    import time; time.sleep(1)
    update_list(db, list_id, name="Timely 2")
    new_ts = get_list(db, list_id)["updated_at"]
    assert new_ts >= original_ts


def test_update_list_raises_for_missing(db):
    with pytest.raises(ValueError):
        update_list(db, 9999, name="x")


def test_delete_list(db):
    list_id = create_list(db, "Doomed")
    delete_list(db, list_id)
    assert get_list(db, list_id) is None


def test_delete_list_cascades_to_tasks(db):
    list_id = create_list(db, "Parent")
    db.execute("INSERT INTO tasks (list_id, title) VALUES (?, ?)", (list_id, "Task"))
    db.commit()
    delete_list(db, list_id)
    tasks = db.execute("SELECT * FROM tasks WHERE list_id=?", (list_id,)).fetchall()
    assert tasks == []


def test_get_lists_by_tag(db):
    t1 = create_list(db, "Work List")
    t2 = create_list(db, "Personal List")
    create_list(db, "Other List")
    tag_id = create_tag(db, "tagged")
    assign_tag_to_list(db, t1, tag_id)
    assign_tag_to_list(db, t2, tag_id)
    result = get_lists_by_tag(db, tag_id)
    assert len(result) == 2
    assert {r["name"] for r in result} == {"Work List", "Personal List"}


def test_get_lists_by_tag_empty(db):
    tag_id = create_tag(db, "empty_tag")
    assert get_lists_by_tag(db, tag_id) == []


def test_get_task_counts_empty(db):
    list_id = create_list(db, "Empty")
    counts = get_task_counts(db, list_id)
    assert counts == {"total": 0, "completed": 0, "overdue": 0}


def test_get_task_counts_with_tasks(db):
    list_id = create_list(db, "Mixed")
    db.execute(
        "INSERT INTO tasks (list_id, title, status, due_date) VALUES (?, ?, 'pending', '2000-01-01')",
        (list_id, "Overdue task"),
    )
    db.execute(
        "INSERT INTO tasks (list_id, title, status) VALUES (?, ?, 'completed')",
        (list_id, "Done task"),
    )
    db.execute(
        "INSERT INTO tasks (list_id, title, status) VALUES (?, ?, 'pending')",
        (list_id, "Normal task"),
    )
    db.commit()
    counts = get_task_counts(db, list_id)
    assert counts["total"] == 3
    assert counts["completed"] == 1
    assert counts["overdue"] == 1
