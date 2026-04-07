"""Custom CSS injection for Streamlit."""

import streamlit as st

_BASE_CSS = """
<style>
/* ── Global resets ─────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
}
[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}

/* ── Cards ─────────────────────────────────────────────────── */
.todo-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.todo-card:hover {
    border-color: #6366f1;
    box-shadow: 0 0 0 1px #6366f1, 0 4px 16px rgba(99,102,241,0.15);
}

/* ── Badges ────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-high   { background: #7f1d1d; color: #fca5a5; }
.badge-medium { background: #78350f; color: #fcd34d; }
.badge-low    { background: #14532d; color: #86efac; }
.badge-pending     { background: #1e3a5f; color: #93c5fd; }
.badge-in_progress { background: #3b1f6e; color: #c4b5fd; }
.badge-completed   { background: #14532d; color: #86efac; }
.badge-cancelled   { background: #1f2937; color: #9ca3af; }
.badge-overdue     { background: #7f1d1d; color: #fca5a5; }

/* ── Tags / chips ──────────────────────────────────────────── */
.tag-chip {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    margin: 2px 3px;
    cursor: pointer;
}
.tag-chip-active {
    box-shadow: 0 0 0 2px #f1f5f9;
}

/* ── Buttons ───────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: background 0.2s;
}

/* ── Section headers ───────────────────────────────────────── */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 1rem 0 0.5rem;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid #334155;
}

/* ── Metric cards ───────────────────────────────────────────── */
[data-testid="stMetric"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem;
}

/* ── Scrollbar ─────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>
"""


def inject_css() -> None:
    """Inject the base CSS styles into the Streamlit app."""
    st.markdown(_BASE_CSS, unsafe_allow_html=True)


def priority_badge(priority: str) -> str:
    """Return an HTML badge for a priority level."""
    labels = {"high": "High", "medium": "Medium", "low": "Low"}
    return f'<span class="badge badge-{priority}">{labels.get(priority, priority)}</span>'


def status_badge(status: str) -> str:
    """Return an HTML badge for a task status."""
    labels = {
        "pending": "Pending",
        "in_progress": "In Progress",
        "completed": "Done",
        "cancelled": "Cancelled",
    }
    return f'<span class="badge badge-{status}">{labels.get(status, status)}</span>'


def tag_chip(name: str, color: str, active: bool = False) -> str:
    """Return an HTML chip for a tag."""
    extra = " tag-chip-active" if active else ""
    text_color = _contrast_color(color)
    return (
        f'<span class="tag-chip{extra}" '
        f'style="background:{color};color:{text_color}">{name}</span>'
    )


def _contrast_color(hex_color: str) -> str:
    """Return black or white depending on background luminance."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return "#ffffff"
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#ffffff"
