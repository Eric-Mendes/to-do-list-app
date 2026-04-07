"""Create/Edit/Delete dialogs for lists and tasks."""

import sqlite3
from datetime import date

import streamlit as st

from app.models.list_model import create_list, delete_list, update_list
from app.models.tag_model import (
    assign_tag_to_list,
    get_all_tags,
    get_tags_for_list,
    remove_tag_from_list,
)
from app.models.task_model import (
    complete_task,
    create_task,
    delete_task,
    get_task,
    uncomplete_task,
    update_task,
)

# ── List dialogs ─────────────────────────────────────────────────────────────


@st.dialog("Create List")
def create_list_dialog(conn: sqlite3.Connection) -> None:
    name = st.text_input("List name *", placeholder="e.g. Shopping")
    description = st.text_area("Description (optional)", height=80)

    tags = get_all_tags(conn)
    tag_options = {t["name"]: t["id"] for t in tags}
    selected_tag_names = st.multiselect(
        "Add to folder(s)",
        options=list(tag_options.keys()),
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("List name is required.")
            else:
                list_id = create_list(conn, name.strip(), description.strip() or None)
                for tag_name in selected_tag_names:
                    assign_tag_to_list(conn, list_id, tag_options[tag_name])
                st.success(f'"{name}" created!')
                st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Edit List")
def edit_list_dialog(conn: sqlite3.Connection, list_id: int) -> None:
    from app.models.list_model import get_list

    lst = get_list(conn, list_id)
    if lst is None:
        st.error("List not found.")
        return

    name = st.text_input("List name *", value=lst["name"])
    description = st.text_area("Description", value=lst["description"] or "", height=80)

    # Tag management
    all_tags = get_all_tags(conn)
    current_tags = {t["id"] for t in get_tags_for_list(conn, list_id)}
    tag_options = {t["name"]: t["id"] for t in all_tags}
    current_tag_names = [t["name"] for t in all_tags if t["id"] in current_tags]

    selected_tag_names = st.multiselect(
        "Folders",
        options=list(tag_options.keys()),
        default=current_tag_names,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save", use_container_width=True, type="primary"):
            if not name.strip():
                st.error("List name is required.")
            else:
                update_list(
                    conn,
                    list_id,
                    name=name.strip(),
                    description=description.strip() or None,
                )
                # Sync tags
                new_tag_ids = {tag_options[n] for n in selected_tag_names}
                for tag_id in new_tag_ids - current_tags:
                    assign_tag_to_list(conn, list_id, tag_id)
                for tag_id in current_tags - new_tag_ids:
                    remove_tag_from_list(conn, list_id, tag_id)
                st.success("Saved!")
                st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Delete List")
def delete_list_dialog(conn: sqlite3.Connection, list_id: int) -> None:
    from app.models.list_model import get_list

    lst = get_list(conn, list_id)
    if lst is None:
        st.error("List not found.")
        return

    st.warning(
        f'Are you sure you want to delete **"{lst["name"]}"**? '
        "All tasks inside will also be deleted. This cannot be undone."
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete", use_container_width=True, type="primary"):
            delete_list(conn, list_id)
            st.session_state["active_list_id"] = None
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


# ── Task dialogs ─────────────────────────────────────────────────────────────


@st.dialog("Add Task")
def create_task_dialog(conn: sqlite3.Connection, list_id: int) -> None:
    title = st.text_input("Task title *", placeholder="e.g. Buy groceries")
    description = st.text_area("Description (optional)", height=80)
    col1, col2 = st.columns(2)
    with col1:
        priority = st.selectbox("Priority", ["medium", "high", "low"], index=0)
    with col2:
        due_date = st.date_input("Due date (optional)", value=None)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Add Task", use_container_width=True, type="primary"):
            if not title.strip():
                st.error("Task title is required.")
            else:
                create_task(
                    conn,
                    list_id,
                    title.strip(),
                    description=description.strip() or None,
                    priority=priority,
                    due_date=due_date.isoformat() if due_date else None,
                )
                st.rerun()
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Edit Task")
def edit_task_dialog(conn: sqlite3.Connection, task_id: int) -> None:
    task = get_task(conn, task_id)
    if task is None:
        st.error("Task not found.")
        return

    title = st.text_input("Title *", value=task["title"])
    description = st.text_area(
        "Description", value=task["description"] or "", height=80
    )
    col1, col2 = st.columns(2)
    with col1:
        priority_options = ["high", "medium", "low"]
        priority = st.selectbox(
            "Priority",
            priority_options,
            index=priority_options.index(task["priority"]),
        )
    with col2:
        existing_due = (
            date.fromisoformat(task["due_date"]) if task["due_date"] else None
        )
        due_date = st.date_input("Due date", value=existing_due)

    status_options = ["pending", "in_progress", "completed", "cancelled"]
    status = st.selectbox(
        "Status",
        status_options,
        index=status_options.index(task["status"]),
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save", use_container_width=True, type="primary"):
            if not title.strip():
                st.error("Title is required.")
            else:
                update_task(
                    conn,
                    task_id,
                    title=title.strip(),
                    description=description.strip() or None,
                    priority=priority,
                    due_date=due_date.isoformat() if due_date else None,
                    status=status,
                )
                if status == "completed" and task["status"] != "completed":
                    complete_task(conn, task_id)
                elif status != "completed" and task["status"] == "completed":
                    uncomplete_task(conn, task_id)
                st.rerun()
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Delete Task")
def delete_task_dialog(conn: sqlite3.Connection, task_id: int) -> None:
    task = get_task(conn, task_id)
    if task is None:
        st.error("Task not found.")
        return
    st.warning(f'Delete task **"{task["title"]}"**? This cannot be undone.')
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Delete", use_container_width=True, type="primary"):
            delete_task(conn, task_id)
            st.rerun()
    with c2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
