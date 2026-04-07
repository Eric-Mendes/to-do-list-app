"""Tests for task model CRUD and analytics operations."""

import pytest

from app.models.list_model import create_list
from app.models.task_model import (
    complete_task,
    create_task,
    delete_task,
    get_overdue_tasks,
    get_task,
    get_tasks_for_list,
    get_tasks_with_due_date,
    uncomplete_task,
    update_task,
)


@pytest.fixture
def lst(db):
    return create_list(db, "Test List")


def test_create_task_returns_id(db, lst):
    task_id = create_task(db, lst, "My Task")
    assert isinstance(task_id, int) and task_id > 0


def test_create_task_defaults(db, lst):
    task_id = create_task(db, lst, "Default Task")
    task = get_task(db, task_id)
    assert task["status"] == "pending"
    assert task["priority"] == "medium"
    assert task["due_date"] is None
    assert task["completed_at"] is None


def test_create_task_with_all_fields(db, lst):
    task_id = create_task(
        db, lst, "Full Task", description="Desc", priority="high", due_date="2030-12-31"
    )
    task = get_task(db, task_id)
    assert task["title"] == "Full Task"
    assert task["description"] == "Desc"
    assert task["priority"] == "high"
    assert task["due_date"] == "2030-12-31"


def test_get_task_returns_none_for_missing(db):
    assert get_task(db, 9999) is None


def test_get_tasks_for_list_returns_only_list_tasks(db):
    l1 = create_list(db, "L1")
    l2 = create_list(db, "L2")
    create_task(db, l1, "T1")
    create_task(db, l2, "T2")
    tasks = get_tasks_for_list(db, l1)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "T1"


def test_get_tasks_for_list_empty(db, lst):
    assert get_tasks_for_list(db, lst) == []


def test_get_tasks_for_list_status_filter(db, lst):
    create_task(db, lst, "Pending")
    t_id = create_task(db, lst, "Done")
    complete_task(db, t_id)
    pending = get_tasks_for_list(db, lst, status="pending")
    assert len(pending) == 1
    assert pending[0]["title"] == "Pending"


def test_update_task_title(db, lst):
    task_id = create_task(db, lst, "Old")
    update_task(db, task_id, title="New")
    assert get_task(db, task_id)["title"] == "New"


def test_update_task_priority(db, lst):
    task_id = create_task(db, lst, "Task")
    update_task(db, task_id, priority="high")
    assert get_task(db, task_id)["priority"] == "high"


def test_update_task_due_date(db, lst):
    task_id = create_task(db, lst, "Task")
    update_task(db, task_id, due_date="2025-06-15")
    assert get_task(db, task_id)["due_date"] == "2025-06-15"


def test_update_task_raises_for_missing(db):
    with pytest.raises(ValueError):
        update_task(db, 9999, title="x")


def test_complete_task(db, lst):
    task_id = create_task(db, lst, "Task")
    complete_task(db, task_id)
    task = get_task(db, task_id)
    assert task["status"] == "completed"
    assert task["completed_at"] is not None


def test_complete_task_raises_for_missing(db):
    with pytest.raises(ValueError):
        complete_task(db, 9999)


def test_uncomplete_task(db, lst):
    task_id = create_task(db, lst, "Task")
    complete_task(db, task_id)
    uncomplete_task(db, task_id)
    task = get_task(db, task_id)
    assert task["status"] == "pending"
    assert task["completed_at"] is None


def test_uncomplete_task_raises_for_missing(db):
    with pytest.raises(ValueError):
        uncomplete_task(db, 9999)


def test_delete_task(db, lst):
    task_id = create_task(db, lst, "Delete me")
    delete_task(db, task_id)
    assert get_task(db, task_id) is None


def test_get_tasks_with_due_date(db):
    l1 = create_list(db, "L1")
    create_task(db, l1, "No due")
    create_task(db, l1, "Has due", due_date="2030-01-01")
    result = get_tasks_with_due_date(db)
    assert len(result) == 1
    assert result[0]["title"] == "Has due"
    assert result[0]["list_name"] == "L1"


def test_get_overdue_tasks(db, lst):
    create_task(db, lst, "Future", due_date="2099-01-01")
    overdue_id = create_task(db, lst, "Overdue", due_date="2000-01-01")
    complete_id = create_task(db, lst, "Completed overdue", due_date="2000-01-01")
    complete_task(db, complete_id)

    overdue = get_overdue_tasks(db)
    titles = [t["title"] for t in overdue]
    assert "Overdue" in titles
    assert "Future" not in titles
    assert "Completed overdue" not in titles
