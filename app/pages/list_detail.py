"""List detail page — tasks inside a list."""

import streamlit as st

from app.components.modals import (
    create_task_dialog,
    delete_task_dialog,
    edit_list_dialog,
    edit_task_dialog,
)
from app.components.task_card import render_task_card
from app.models.list_model import get_list, get_task_counts
from app.models.tag_model import get_tags_for_list
from app.models.task_model import get_tasks_for_list
from app.utils.styles import inject_css, tag_chip

inject_css()

conn = st.session_state.get("conn")
if conn is None:
    st.error("Database not initialised.")
    st.stop()

list_id = st.session_state.get("active_list_id")
if list_id is None:
    st.info("No list selected. Go back to My Lists.")
    if st.button("← My Lists"):
        st.switch_page("app/pages/home.py")
    st.stop()

lst = get_list(conn, list_id)
if lst is None:
    st.error("List not found.")
    st.session_state["active_list_id"] = None
    st.stop()

# ── Breadcrumb ────────────────────────────────────────────────────────────────
if st.button("← My Lists", key="breadcrumb_back"):
    st.session_state["active_list_id"] = None
    st.switch_page("app/pages/home.py")

st.divider()

# ── List header ───────────────────────────────────────────────────────────────
col_title, col_edit = st.columns([8, 1])
with col_title:
    st.title(f"📝 {lst['name']}")
    if lst["description"]:
        st.caption(lst["description"])

with col_edit:
    st.write("")
    if st.button("✏️ Edit List", key="edit_list_btn"):
        edit_list_dialog(conn, list_id)

# Tag chips
tags = get_tags_for_list(conn, list_id)
if tags:
    chips_html = " ".join(tag_chip(t["name"], t["color"]) for t in tags)
    st.markdown(chips_html, unsafe_allow_html=True)

# Task summary bar
counts = get_task_counts(conn, list_id)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total", counts["total"])
m2.metric("Completed", counts["completed"])
m3.metric("Remaining", counts["total"] - counts["completed"])
m4.metric("Overdue", counts["overdue"], delta_color="inverse")

st.divider()

# ── Add task button ───────────────────────────────────────────────────────────
if st.button("＋ Add Task", type="primary"):
    create_task_dialog(conn, list_id)

# ── Task list ─────────────────────────────────────────────────────────────────
tasks = get_tasks_for_list(conn, list_id)

if not tasks:
    st.markdown(
        """
        <div style="text-align:center;padding:2rem;color:#64748b">
            <div style="font-size:2rem">📭</div>
            <div style="font-weight:600;margin-top:0.5rem">No tasks yet</div>
            <div style="font-size:0.85rem">Add your first task above.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Status section headers
    pending = [t for t in tasks if t["status"] in ("pending", "in_progress")]
    done = [t for t in tasks if t["status"] == "completed"]
    cancelled = [t for t in tasks if t["status"] == "cancelled"]

    def _render_tasks(task_list):
        for task in task_list:
            if st.session_state.pop(f"edit_task_{task['id']}", False):
                edit_task_dialog(conn, task["id"])
            if st.session_state.pop(f"del_task_{task['id']}", False):
                delete_task_dialog(conn, task["id"])
            render_task_card(conn, task)

    if pending:
        st.markdown('<div class="section-header">Active</div>', unsafe_allow_html=True)
        _render_tasks(pending)

    if done:
        with st.expander(f"✅ Completed ({len(done)})", expanded=False):
            _render_tasks(done)

    if cancelled:
        with st.expander(f"🚫 Cancelled ({len(cancelled)})", expanded=False):
            _render_tasks(cancelled)
