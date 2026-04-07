"""Calendar/timeline view for tasks with due dates."""

from datetime import date, timedelta

import streamlit as st
from streamlit_calendar import calendar

from app.models.task_model import complete_task, get_task, get_tasks_with_due_date
from app.utils.styles import inject_css

inject_css()

conn = st.session_state.get("conn")
if conn is None:
    st.error("Database not initialised.")
    st.stop()

st.title("📅 Calendar")

# ── Sidebar date range filter ─────────────────────────────────────────────────
with st.sidebar:
    st.divider()
    st.markdown("### Calendar Filter")
    today = date.today()
    filter_start = st.date_input("From", value=today - timedelta(days=7))
    filter_end = st.date_input("To", value=today + timedelta(days=30))

# ── Build FullCalendar events ─────────────────────────────────────────────────
_STATUS_COLORS = {
    "pending": "#6366f1",
    "in_progress": "#a855f7",
    "completed": "#22c55e",
    "cancelled": "#475569",
}

all_tasks = get_tasks_with_due_date(conn)

events = []
for task in all_tasks:
    task_date = task["due_date"][:10]
    # Apply date range filter
    if filter_start and filter_end:
        if not (filter_start.isoformat() <= task_date <= filter_end.isoformat()):
            continue

    color = _STATUS_COLORS.get(task["status"], "#6366f1")
    # Overdue pending tasks: highlight red
    if task["status"] in ("pending", "in_progress") and task_date < today.isoformat():
        color = "#ef4444"

    events.append(
        {
            "id": str(task["id"]),
            "title": task["title"],
            "start": task_date,
            "end": task_date,
            "color": color,
            "extendedProps": {
                "status": task["status"],
                "priority": task["priority"],
                "list_name": task["list_name"],
                "description": task["description"] or "",
            },
        }
    )

# ── View selector ─────────────────────────────────────────────────────────────
view_options = {
    "Month": "dayGridMonth",
    "Week": "timeGridWeek",
    "Agenda": "listWeek",
}
selected_view = st.radio(
    "View", list(view_options.keys()), horizontal=True, label_visibility="collapsed"
)
initial_view = view_options[selected_view]

# ── Calendar widget ───────────────────────────────────────────────────────────
calendar_options = {
    "initialView": initial_view,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "",
    },
    "height": 620,
    "selectable": False,
    "editable": False,
    "eventDisplay": "block",
    "dayMaxEvents": 3,
}

custom_css = """
.fc-event {
    border-radius: 4px !important;
    padding: 2px 6px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}
.fc-daygrid-day { background: #0f172a !important; }
.fc-col-header-cell { background: #1e293b !important; color: #94a3b8 !important; }
.fc-toolbar-title { color: #e2e8f0 !important; }
.fc-button { background: #6366f1 !important; border-color: #6366f1 !important; }
.fc-button:hover { background: #4f46e5 !important; }
"""

result = calendar(
    events=events,
    options=calendar_options,
    custom_css=custom_css,
    key=f"calendar_{initial_view}",
)

# ── Event click detail panel ──────────────────────────────────────────────────
if result and result.get("eventClick"):
    event_id = result["eventClick"]["event"]["id"]
    task = get_task(conn, int(event_id))
    if task:
        with st.expander(f"📌 {task['title']}", expanded=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f"**List:** {result['eventClick']['event']['extendedProps']['list_name']}"
                )
                st.markdown(f"**Due:** {task['due_date']}")
                st.markdown(f"**Priority:** {task['priority'].capitalize()}")
                st.markdown(
                    f"**Status:** {task['status'].replace('_', ' ').capitalize()}"
                )
                if task["description"]:
                    st.markdown(f"**Description:** {task['description']}")
            with col2:
                if task["status"] != "completed":
                    if st.button(
                        "✅ Mark Complete", use_container_width=True, type="primary"
                    ):
                        complete_task(conn, task["id"])
                        st.rerun()
                else:
                    st.success("Completed!")

# ── Legend ────────────────────────────────────────────────────────────────────
st.divider()
st.html("""
<div style="display:flex;gap:1rem;flex-wrap:wrap;font-size:0.8rem;color:#94a3b8">
  <span><span style="background:#6366f1;padding:2px 8px;border-radius:4px">&nbsp;</span> Pending</span>
  <span><span style="background:#a855f7;padding:2px 8px;border-radius:4px">&nbsp;</span> In Progress</span>
  <span><span style="background:#22c55e;padding:2px 8px;border-radius:4px">&nbsp;</span> Completed</span>
  <span><span style="background:#ef4444;padding:2px 8px;border-radius:4px">&nbsp;</span> Overdue</span>
  <span><span style="background:#475569;padding:2px 8px;border-radius:4px">&nbsp;</span> Cancelled</span>
</div>
""")
