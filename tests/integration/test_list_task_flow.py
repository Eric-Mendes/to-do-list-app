"""Integration tests for list + task CRUD workflows."""

from app.models.list_model import create_list, delete_list, get_list, get_task_counts
from app.models.task_model import (
    complete_task,
    create_task,
    delete_task,
    get_task,
    get_tasks_for_list,
)


def test_full_list_task_cycle(db):
    """Create a list, add 3 tasks, complete 1, delete 1, assert counts."""
    list_id = create_list(db, "Project Alpha", "Main project tasks")
    assert get_list(db, list_id) is not None

    t1 = create_task(db, list_id, "Design", priority="high")
    create_task(db, list_id, "Implement", priority="high")
    t3 = create_task(db, list_id, "Test", priority="medium")

    assert len(get_tasks_for_list(db, list_id)) == 3

    complete_task(db, t1)
    assert get_task(db, t1)["status"] == "completed"

    delete_task(db, t3)
    assert get_task(db, t3) is None

    remaining = get_tasks_for_list(db, list_id)
    assert len(remaining) == 2
    titles = {t["title"] for t in remaining}
    assert titles == {"Design", "Implement"}

    counts = get_task_counts(db, list_id)
    assert counts["total"] == 2
    assert counts["completed"] == 1


def test_delete_list_cascades_all_tasks(db):
    """Deleting a list removes all its tasks."""
    list_id = create_list(db, "Doomed List")
    ids = [create_task(db, list_id, f"Task {i}") for i in range(5)]

    delete_list(db, list_id)

    assert get_list(db, list_id) is None
    for task_id in ids:
        assert get_task(db, task_id) is None


def test_multiple_lists_isolated(db):
    """Tasks in one list do not appear in another."""
    l1 = create_list(db, "List 1")
    l2 = create_list(db, "List 2")

    create_task(db, l1, "L1 Task")
    create_task(db, l2, "L2 Task")

    assert len(get_tasks_for_list(db, l1)) == 1
    assert get_tasks_for_list(db, l1)[0]["title"] == "L1 Task"
    assert len(get_tasks_for_list(db, l2)) == 1
    assert get_tasks_for_list(db, l2)[0]["title"] == "L2 Task"
