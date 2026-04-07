# To-Do List App

A single-user to-do list app built with **Streamlit**, **SQLite**, and **Docker**.

## Features

- **Lists** — Create, edit, and delete task lists; manage tasks within them
- **Folders** — Organize lists into folders using a tag system (multi-tag support)
- **Tasks** — Full CRUD with priority levels, due dates, and status tracking
- **Calendar** — Timeline view for tasks with due dates, color-coded by status
- **Analytics** — Completion rates, overdue counts, streaks, and Plotly charts
- **Demo Data** — One-click sample data to explore the app

## Stack

| Layer     | Technology                   |
|-----------|------------------------------|
| UI        | Streamlit >= 1.36             |
| Database  | SQLite (raw `sqlite3`)        |
| Charts    | Plotly Express               |
| Calendar  | streamlit-calendar            |
| Container | Docker + docker-compose       |
| CI        | GitHub Actions                |

## Architecture

```
app/
├── main.py              # Streamlit entrypoint (st.navigation)
├── database/
│   ├── connection.py    # SQLite connection (WAL mode, FK enforcement)
│   ├── migrations.py    # Idempotent schema creation
│   └── seed.py          # Demo data loader
├── models/
│   ├── list_model.py    # Task list CRUD + tag filtering + counts
│   ├── task_model.py    # Task CRUD + analytics queries
│   └── tag_model.py     # Tag CRUD + list assignment
├── pages/
│   ├── home.py          # Lists grid with tag folder filter
│   ├── list_detail.py   # Tasks inside a list
│   ├── calendar_view.py # FullCalendar timeline view
│   └── analytics.py     # KPI metrics and charts
├── components/
│   ├── sidebar.py       # Tag folder tree + demo data button
│   ├── list_card.py     # List card widget
│   ├── task_card.py     # Task row with checkbox, badges, actions
│   ├── modals.py        # @st.dialog create/edit/delete dialogs
│   └── charts.py        # Plotly wrappers
└── utils/
    ├── date_helpers.py  # is_overdue, days_until_due, format labels
    └── styles.py        # CSS injection + badge/chip HTML helpers
tests/
├── conftest.py          # In-memory SQLite fixture
├── unit/                # Model + helper tests
└── integration/         # Multi-model workflow + analytics tests
```

## Database Schema

```
tags         (id, name UNIQUE, color, created_at)
task_lists   (id, name, description, created_at, updated_at)
list_tags    (list_id →task_lists, tag_id →tags)   -- folders via tagging
tasks        (id, list_id →task_lists, title, description,
              status, priority, due_date, completed_at,
              created_at, updated_at)
```

Foreign keys cascade on delete. Dates stored as ISO-8601 strings.

## Quick Start

### Local (Python + venv)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .          # makes the app package importable
streamlit run app/main.py
```

### Docker (recommended)

```bash
docker-compose up --build
```

App is available at **http://localhost:8501**.

Click **Demo Data** in the sidebar to load sample lists, tasks, and tags.

## Environment Variables

| Variable | Default          | Description                       |
|----------|------------------|-----------------------------------|
| `DB_PATH`| `./data/todo.db` | Path to the SQLite database file  |

## Development

```bash
pip install -r requirements.txt -r requirements-dev.txt

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Lint
ruff check app/ tests/

# Format
black app/ tests/
```

## CI/CD

GitHub Actions runs on every push and PR to `main`:

1. **test** (Python 3.11 & 3.12) — ruff lint, black format check, pytest with ≥ 90% coverage
2. **docker-build** (after tests) — `docker build` + health endpoint smoke test
