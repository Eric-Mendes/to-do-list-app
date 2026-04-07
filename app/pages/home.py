"""Home page — lists overview."""

import os

import streamlit as st

from app.components.list_card import render_list_card
from app.components.modals import (
    create_list_dialog,
    delete_list_dialog,
    edit_list_dialog,
)
from app.models.list_model import get_all_lists, get_lists_by_tag
from app.utils.styles import inject_css

inject_css()

conn = st.session_state.get("conn")
if conn is None:
    st.error("Database not initialised. Please restart the app.")
    st.stop()

active_tag = st.session_state.get("active_tag")

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_btn = st.columns([6, 1])
with col_title:
    st.title("📋 My Lists")
with col_btn:
    st.write("")
    if st.button("＋ New List", use_container_width=True, type="primary"):
        create_list_dialog(conn)

st.divider()

# ── Fetch lists ───────────────────────────────────────────────────────────────
if active_tag is not None:
    lists = get_lists_by_tag(conn, active_tag)
else:
    lists = get_all_lists(conn)

# ── Empty state ───────────────────────────────────────────────────────────────
if not lists:
    st.markdown(
        """
        <div style="text-align:center;padding:3rem 1rem;color:#64748b">
            <div style="font-size:3rem">📭</div>
            <div style="font-size:1.1rem;font-weight:600;margin-top:0.5rem">
                No lists yet
            </div>
            <div style="font-size:0.9rem;margin-top:0.25rem">
                Click <b>＋ New List</b> to create your first list.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # Grid: 2 columns
    cols = st.columns(2, gap="medium")
    for idx, lst in enumerate(lists):
        with cols[idx % 2]:
            # Handle edit/delete dialog triggers set by list_card buttons
            if st.session_state.pop(f"edit_list_{lst['id']}", False):
                edit_list_dialog(conn, lst["id"])
            if st.session_state.pop(f"confirm_del_list_{lst['id']}", False):
                delete_list_dialog(conn, lst["id"])
            render_list_card(conn, lst)

# ── Navigate to list detail if a list was opened ─────────────────────────────
if st.session_state.get("current_page") == "list_detail":
    st.session_state.pop("current_page", None)
    st.switch_page(os.path.join(os.path.dirname(__file__), "list_detail.py"))
