"""Streamlit application entrypoint."""

import os

import streamlit as st

from app.database.connection import get_connection
from app.database.migrations import run_migrations

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="To-Do App",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Database ─────────────────────────────────────────────────────────────────
@st.cache_resource
def _get_db():
    db_path = os.environ.get("DB_PATH", "data/todo.db")
    conn = get_connection(db_path)
    run_migrations(conn)
    return conn


conn = _get_db()

# Store connection in session state so pages can access it
if "conn" not in st.session_state:
    st.session_state["conn"] = conn
if "active_tag" not in st.session_state:
    st.session_state["active_tag"] = None
if "active_list_id" not in st.session_state:
    st.session_state["active_list_id"] = None

# ── Sidebar ──────────────────────────────────────────────────────────────────
from app.components.sidebar import render_sidebar  # noqa: E402

render_sidebar(conn)

# ── Navigation ───────────────────────────────────────────────────────────────
_pages_dir = os.path.join(os.path.dirname(__file__), "pages")
pages = [
    st.Page(
        os.path.join(_pages_dir, "home.py"), title="My Lists", icon="📋", default=True
    ),
    st.Page(os.path.join(_pages_dir, "list_detail.py"), title="List Detail", icon="📝"),
    st.Page(os.path.join(_pages_dir, "calendar_view.py"), title="Calendar", icon="📅"),
    st.Page(os.path.join(_pages_dir, "analytics.py"), title="Analytics", icon="📊"),
]

pg = st.navigation(pages, position="sidebar")
pg.run()
