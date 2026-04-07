"""Reusable task card component."""

import sqlite3

import streamlit as st

from app.models.task_model import complete_task, uncomplete_task
from app.utils.date_helpers import format_due_date_label, is_overdue
from app.utils.styles import priority_badge, status_badge


def render_task_card(conn: sqlite3.Connection, task: sqlite3.Row) -> None:
    """Render a task card with checkbox, badges, due date, and action buttons."""
    is_done = task["status"] == "completed"
    due_label = format_due_date_label(task["due_date"])
    overdue = is_overdue(task["due_date"]) and not is_done

    due_color = "#ef4444" if overdue else "#94a3b8"
    title_style = (
        "text-decoration:line-through;color:#64748b" if is_done else "color:#e2e8f0"
    )

    with st.container():
        col_check, col_content, col_actions = st.columns([1, 8, 2])

        with col_check:
            checked = st.checkbox(
                "",
                value=is_done,
                key=f"check_{task['id']}",
                label_visibility="collapsed",
            )
            if checked != is_done:
                if checked:
                    complete_task(conn, task["id"])
                else:
                    uncomplete_task(conn, task["id"])
                st.rerun()

        with col_content:
            priority_html = priority_badge(task["priority"])
            status_html = status_badge(task["status"])
            due_html = (
                f'<span style="font-size:0.75rem;color:{due_color}">📅 {due_label}</span>'
                if task["due_date"]
                else ""
            )
            st.html(f"""
<div style="padding:4px 0">
  <span style="font-size:1rem;font-weight:600;{title_style}">{task['title']}</span>
  &nbsp;&nbsp;{priority_html}&nbsp;{status_html}
  <br>
  <span style="font-size:0.82rem;color:#94a3b8">{task['description'] or ''}</span>
  &nbsp;&nbsp;{due_html}
</div>
""")

        with col_actions:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✏️", key=f"edit_task_{task['id']}", help="Edit"):
                    st.session_state[f"edit_task_{task['id']}"] = True
                    st.rerun()
            with c2:
                if st.button("🗑️", key=f"del_task_{task['id']}", help="Delete"):
                    st.session_state[f"del_task_{task['id']}"] = True
                    st.rerun()

        st.html('<hr style="margin:4px 0;border-color:#1e293b">')
