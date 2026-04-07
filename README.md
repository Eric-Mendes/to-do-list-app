# To-Do List App

A single-user to-do list app built with **Streamlit**, **SQLite**, and **Docker**.

## Features

- Create, edit, and delete lists; manage tasks within them
- Organize lists into folders using a tag system
- Calendar/timeline view for tasks with due dates
- Analytics dashboard: completion rates, missed deadlines, streaks, and more

## Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit >= 1.36 |
| Database | SQLite (raw `sqlite3`) |
| Charts | Plotly Express |
| Calendar | streamlit-calendar |
| Container | Docker + docker-compose |
| CI | GitHub Actions |

## Architecture

```
app/
├── main.py              # Streamlit entrypoint (st.navigation)
├── database/            # Connection + schema migrations
├── models/              # CRUD layer (lists, tasks, tags)
├── pages/               # Home, List Detail, Calendar, Analytics
├── components/          # Reusable UI widgets
└── utils/               # Date helpers, CSS injection
tests/
├── unit/                # Model + helper tests
└── integration/         # Multi-model workflow tests
```

## Quick Start

### Local (Python)

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

### Docker

```bash
docker-compose up --build
```

App is available at `http://localhost:8501`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `./data/todo.db` | Path to the SQLite database file |

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

GitHub Actions runs on every push and pull request to `main`:
- Lint (ruff) + format check (black)
- Tests with >= 90% coverage on `app/models/` and `app/database/`
- Docker build smoke test
