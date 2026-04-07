"""Sidebar navigation and tag folder tree."""

import sqlite3

import streamlit as st

from app.database.seed import seed_demo_data
from app.models.tag_model import create_tag, get_all_tags


def render_sidebar(conn: sqlite3.Connection) -> None:
    """Render the sidebar with tag-based folder navigation.

    Sets st.session_state["active_tag"] to the selected tag id or None.
    """
    with st.sidebar:
        st.markdown("## My To-Do App")
        st.divider()

        # Navigation hint (handled by st.navigation in main.py)
        st.markdown("### Folders")

        tags = get_all_tags(conn)
        active = st.session_state.get("active_tag")

        # "All Lists" button
        all_active = active is None
        if st.button(
            "📋 All Lists",
            use_container_width=True,
            type="primary" if all_active else "secondary",
            key="nav_all",
        ):
            st.session_state["active_tag"] = None
            st.session_state["active_list_id"] = None
            st.rerun()

        # Tag buttons
        for tag in tags:
            is_active = active == tag["id"]
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(
                    f"🏷️ {tag['name']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    key=f"nav_tag_{tag['id']}",
                ):
                    st.session_state["active_tag"] = tag["id"]
                    st.session_state["active_list_id"] = None
                    st.rerun()

        st.divider()

        # New tag form
        with st.expander("➕ New Folder (Tag)"):
            with st.form("new_tag_form", clear_on_submit=True):
                tag_name = st.text_input("Folder name", placeholder="e.g. Work")
                tag_color = st.color_picker("Color", value="#6366f1")
                submitted = st.form_submit_button("Create", use_container_width=True)
                if submitted and tag_name.strip():
                    try:
                        create_tag(conn, tag_name.strip(), tag_color)
                        st.success(f'Folder "{tag_name}" created!')
                        st.rerun()
                    except Exception:
                        st.error("A folder with that name already exists.")

        st.divider()

        # Demo data
        with st.expander("🎲 Demo Data"):
            st.caption("Load realistic sample data to explore the app.")
            if st.button("Load Demo Data", use_container_width=True):
                seed_demo_data(conn)
                st.session_state["active_tag"] = None
                st.session_state["active_list_id"] = None
                st.success("Demo data loaded!")
                st.rerun()
