"""Demo seed data for development and demos."""

import sqlite3
from datetime import date, timedelta


def seed_demo_data(conn: sqlite3.Connection) -> None:
    """Insert realistic demo data into the database.

    Safe to call multiple times — clears existing data first.
    """
    today = date.today()

    conn.executescript("""
        DELETE FROM list_tags;
        DELETE FROM tasks;
        DELETE FROM task_lists;
        DELETE FROM tags;
        """)

    # Tags / folders
    conn.execute("INSERT INTO tags (name, color) VALUES ('Work', '#6366f1')")
    conn.execute("INSERT INTO tags (name, color) VALUES ('Personal', '#22c55e')")
    conn.execute("INSERT INTO tags (name, color) VALUES ('Health', '#f59e0b')")
    work_tag = conn.execute("SELECT id FROM tags WHERE name='Work'").fetchone()[0]
    personal_tag = conn.execute("SELECT id FROM tags WHERE name='Personal'").fetchone()[
        0
    ]
    health_tag = conn.execute("SELECT id FROM tags WHERE name='Health'").fetchone()[0]

    # Lists
    def make_list(name, description=None):
        cur = conn.execute(
            "INSERT INTO task_lists (name, description) VALUES (?, ?)",
            (name, description),
        )
        return cur.lastrowid

    l_project = make_list("Q2 Project", "Main work deliverables for Q2")
    l_errands = make_list("Errands", "Things to get done around the house")
    l_fitness = make_list("Fitness Goals", "Health and exercise tracking")
    l_learning = make_list("Learning", "Books and courses to complete")

    # Tag assignments
    conn.execute("INSERT INTO list_tags VALUES (?, ?)", (l_project, work_tag))
    conn.execute("INSERT INTO list_tags VALUES (?, ?)", (l_errands, personal_tag))
    conn.execute("INSERT INTO list_tags VALUES (?, ?)", (l_fitness, health_tag))
    conn.execute("INSERT INTO list_tags VALUES (?, ?)", (l_fitness, personal_tag))
    conn.execute("INSERT INTO list_tags VALUES (?, ?)", (l_learning, personal_tag))

    # Tasks helper
    def task(
        list_id, title, status="pending", priority="medium", days=None, completed=False
    ):
        due = (today + timedelta(days=days)).isoformat() if days is not None else None
        cur = conn.execute(
            """INSERT INTO tasks (list_id, title, status, priority, due_date,
               completed_at, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?,
               CASE WHEN ? THEN datetime('now', '-1 day') ELSE NULL END,
               datetime('now', ? || ' days'), datetime('now'))""",
            (list_id, title, status, priority, due, completed, str(-abs(days or 5))),
        )
        return cur.lastrowid

    # Q2 Project tasks
    task(
        l_project, "Define project scope", "completed", "high", days=-10, completed=True
    )
    task(l_project, "Set up repo and CI", "completed", "high", days=-8, completed=True)
    task(
        l_project,
        "Design database schema",
        "completed",
        "medium",
        days=-5,
        completed=True,
    )
    task(l_project, "Implement API endpoints", "in_progress", "high", days=3)
    task(l_project, "Write unit tests", "pending", "high", days=7)
    task(l_project, "Code review", "pending", "medium", days=10)
    task(l_project, "Deploy to staging", "pending", "high", days=14)
    task(l_project, "Stakeholder demo", "pending", "high", days=18)

    # Errands
    task(l_errands, "Buy groceries", "completed", "medium", days=-2, completed=True)
    task(l_errands, "Pay utility bills", "pending", "high", days=-1)  # overdue
    task(l_errands, "Schedule dentist appointment", "pending", "medium", days=5)
    task(l_errands, "Renew car insurance", "pending", "high", days=7)
    task(l_errands, "Clean garage", "pending", "low", days=14)

    # Fitness
    task(
        l_fitness,
        "30-min run on Monday",
        "completed",
        "medium",
        days=-3,
        completed=True,
    )
    task(
        l_fitness,
        "30-min run on Wednesday",
        "completed",
        "medium",
        days=-1,
        completed=True,
    )
    task(l_fitness, "30-min run on Friday", "pending", "medium", days=1)
    task(l_fitness, "Gym — upper body", "pending", "medium", days=2)
    task(l_fitness, "Gym — lower body", "pending", "medium", days=4)
    task(l_fitness, "Meal prep Sunday", "pending", "low", days=6)

    # Learning
    task(
        l_learning,
        "Finish 'Designing Data-Intensive Applications'",
        "in_progress",
        "medium",
        days=30,
    )
    task(
        l_learning,
        "Complete Streamlit advanced tutorial",
        "completed",
        "low",
        days=-4,
        completed=True,
    )
    task(l_learning, "Watch Docker deep-dive series", "pending", "low", days=21)

    conn.commit()
