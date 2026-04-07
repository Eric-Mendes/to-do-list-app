"""Integration tests for analytics query functions."""

from datetime import date, timedelta

from app.models.list_model import create_list
from app.models.task_model import (
    complete_task,
    create_task,
    get_completion_rate_by_list,
    get_completion_stats,
    get_completion_streak,
    get_tasks_by_status,
    get_tasks_in_period,
    get_tasks_with_due_date,
    update_task,
)


def _today(delta: int = 0) -> str:
    return (date.today() + timedelta(days=delta)).isoformat()


def test_get_tasks_in_period(db):
    lst = create_list(db, "L")
    t1 = create_task(db, lst, "T1")
    t2 = create_task(db, lst, "T2")
    create_task(db, lst, "T3")

    # Manually backdate created_at for two tasks
    yesterday = _today(-1)
    db.execute("UPDATE tasks SET created_at=? WHERE id=?", (yesterday, t1))
    db.execute("UPDATE tasks SET created_at=? WHERE id=?", (yesterday, t2))
    db.commit()

    results = get_tasks_in_period(db, yesterday, yesterday)
    assert len(results) == 2

    results_today = get_tasks_in_period(db, _today(), _today())
    assert len(results_today) == 1


def test_get_completion_stats(db):
    lst = create_list(db, "Stats List")
    t1 = create_task(db, lst, "Done 1")
    t2 = create_task(db, lst, "Done 2")
    create_task(db, lst, "Pending future", due_date=_today(10))
    create_task(db, lst, "Overdue task", due_date=_today(-5))

    complete_task(db, t1)
    complete_task(db, t2)

    stats = get_completion_stats(db, _today(-1), _today(1))
    assert stats["created"] == 4
    assert stats["completed"] == 2
    assert stats["planned"] >= 1
    assert stats["missed"] >= 1


def test_get_tasks_by_status(db):
    lst = create_list(db, "Status List")
    t1 = create_task(db, lst, "T1")
    t2 = create_task(db, lst, "T2")
    create_task(db, lst, "T3")
    complete_task(db, t1)
    update_task(db, t2, status="cancelled")

    counts = get_tasks_by_status(db)
    assert counts.get("completed", 0) >= 1
    assert counts.get("cancelled", 0) >= 1
    assert counts.get("pending", 0) >= 1


def test_get_completion_rate_by_list(db):
    l1 = create_list(db, "A List")
    l2 = create_list(db, "B List")

    t1 = create_task(db, l1, "Done")
    create_task(db, l1, "Not done")
    complete_task(db, t1)

    t2 = create_task(db, l2, "All done")
    complete_task(db, t2)

    rates = get_completion_rate_by_list(db)
    rate_map = {r["list"]: r for r in rates}

    assert rate_map["A List"]["rate"] == 50.0
    assert rate_map["B List"]["rate"] == 100.0


def test_get_tasks_with_due_date_excludes_cancelled(db):
    lst = create_list(db, "L")
    create_task(db, lst, "Keep", due_date=_today(5))
    cancel_id = create_task(db, lst, "Cancel", due_date=_today(5))
    update_task(db, cancel_id, status="cancelled")

    result = get_tasks_with_due_date(db)
    titles = [t["title"] for t in result]
    assert "Keep" in titles
    assert "Cancel" not in titles


def test_get_completion_streak_no_completions(db):
    assert get_completion_streak(db) == 0


def test_get_completion_streak_with_today(db):
    lst = create_list(db, "L")
    t1 = create_task(db, lst, "Today task")
    complete_task(db, t1)
    streak = get_completion_streak(db)
    assert streak >= 1
