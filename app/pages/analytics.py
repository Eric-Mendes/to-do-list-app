"""Analytics page — task stats and charts."""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from app.components.charts import (
    completion_rate_chart,
    status_distribution_chart,
    tasks_over_time_chart,
)
from app.models.task_model import (
    get_completion_rate_by_list,
    get_completion_stats,
    get_completion_streak,
    get_tasks_by_status,
    get_tasks_in_period,
)
from app.utils.styles import inject_css

inject_css()

conn = st.session_state.get("conn")
if conn is None:
    st.error("Database not initialised.")
    st.stop()

st.title("📊 Analytics")

# ── Date range selector ───────────────────────────────────────────────────────
today = date.today()
preset_col, custom_col = st.columns([2, 3])
with preset_col:
    preset = st.selectbox(
        "Period",
        ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"],
        index=1,
    )

if preset == "Last 7 days":
    start_date = today - timedelta(days=7)
    end_date = today
elif preset == "Last 30 days":
    start_date = today - timedelta(days=30)
    end_date = today
elif preset == "Last 90 days":
    start_date = today - timedelta(days=90)
    end_date = today
else:
    with custom_col:
        date_range = st.date_input(
            "Custom range",
            value=(today - timedelta(days=30), today),
        )
        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
            start_date, end_date = date_range[0], date_range[1]
        else:
            start_date = end_date = today

start_str = start_date.isoformat()
end_str = end_date.isoformat()

# ── KPI Metrics ───────────────────────────────────────────────────────────────
stats = get_completion_stats(conn, start_str, end_str)
streak = get_completion_streak(conn)

st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Created", stats["created"], help="Tasks created in the selected period")
k2.metric(
    "Completed", stats["completed"], help="Tasks completed in the selected period"
)
k3.metric(
    "Completion Rate",
    f"{round(stats['completed'] / stats['created'] * 100, 1) if stats['created'] else 0}%",
)
k4.metric("Planned", stats["planned"], help="Future pending tasks with a due date")
k5.metric(
    "🔥 Streak", f"{streak}d", help="Consecutive days with at least 1 task completed"
)

if stats["missed"] > 0:
    st.warning(
        f"⚠️ You have **{stats['missed']} overdue task(s)** past their due date."
    )

st.divider()

# ── Tasks over time chart ─────────────────────────────────────────────────────
st.subheader("Tasks Over Time")

tasks = get_tasks_in_period(conn, start_str, end_str)
all_completed = conn.execute(
    "SELECT * FROM tasks WHERE status='completed' AND date(completed_at) BETWEEN ? AND ?",
    (start_str, end_str),
).fetchall()

# Build daily aggregation
day_range = pd.date_range(start=start_str, end=end_str, freq="D")
created_counts = (
    pd.Series([t["created_at"][:10] for t in tasks])
    .value_counts()
    .reindex(day_range.strftime("%Y-%m-%d"), fill_value=0)
    .reset_index(name="created")
    .rename(columns={"index": "date"})
)
completed_counts = (
    pd.Series([t["completed_at"][:10] for t in all_completed])
    .value_counts()
    .reindex(day_range.strftime("%Y-%m-%d"), fill_value=0)
    .reset_index(name="completed")
    .rename(columns={"index": "date"})
)

if not created_counts.empty and not completed_counts.empty:
    merged = created_counts.merge(completed_counts, on="date", how="outer").fillna(0)
    st.plotly_chart(tasks_over_time_chart(merged), use_container_width=True)
else:
    st.info("No task data for the selected period.")

# ── Status distribution + completion rate ─────────────────────────────────────
col_pie, col_bar = st.columns(2)

with col_pie:
    st.subheader("Task Status Distribution")
    status_counts = get_tasks_by_status(conn)
    if status_counts:
        st.plotly_chart(
            status_distribution_chart(status_counts), use_container_width=True
        )
    else:
        st.info("No tasks yet.")

with col_bar:
    st.subheader("Completion Rate by List")
    rate_data = get_completion_rate_by_list(conn)
    if rate_data:
        st.plotly_chart(completion_rate_chart(rate_data), use_container_width=True)
    else:
        st.info("No lists with tasks yet.")
