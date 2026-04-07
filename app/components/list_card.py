"""Reusable list card component."""

import sqlite3

import streamlit as st

from app.models.list_model import get_task_counts
from app.models.tag_model import get_tags_for_list
from app.utils.styles import tag_chip


def render_list_card(conn: sqlite3.Connection, lst: sqlite3.Row) -> None:
    """Render a clickable list card with task counts and tag chips.

    Clicking the card sets active_list_id in session state and reruns.
    """
    counts = get_task_counts(conn, lst["id"])
    tags = get_tags_for_list(conn, lst["id"])

    overdue_badge = (
        f'<span class="badge badge-overdue">⚠ {counts["overdue"]} overdue</span> '
        if counts["overdue"] > 0
        else ""
    )
    tag_chips_html = " ".join(tag_chip(t["name"], t["color"]) for t in tags)

    with st.container():
        st.html(f"""
<div class="todo-card">
  <div style="display:flex;justify-content:space-between;align-items:start">
    <div>
      <div style="font-size:1.1rem;font-weight:700;color:#e2e8f0">{lst['name']}</div>
      <div style="font-size:0.85rem;color:#94a3b8;margin-top:2px">{lst['description'] or ''}</div>
    </div>
    <div style="text-align:right;white-space:nowrap">
      <span class="badge badge-pending">{counts['total']} tasks</span>&nbsp;{overdue_badge}
    </div>
  </div>
  <div style="margin-top:8px">{tag_chips_html}</div>
</div>
""")

        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            if st.button(
                "Open →",
                key=f"open_list_{lst['id']}",
                use_container_width=True,
            ):
                st.session_state["active_list_id"] = lst["id"]
                st.session_state["current_page"] = "list_detail"
                st.rerun()
        with col2:
            if st.button("✏️", key=f"edit_list_{lst['id']}", use_container_width=True):
                st.session_state[f"edit_list_{lst['id']}"] = True
                st.rerun()
        with col3:
            if st.button("🗑️", key=f"del_list_{lst['id']}", use_container_width=True):
                st.session_state[f"confirm_del_list_{lst['id']}"] = True
                st.rerun()
