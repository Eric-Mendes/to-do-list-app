"""Plotly chart wrappers with app color palette."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

_PALETTE = ["#6366f1", "#22c55e", "#ef4444", "#f59e0b", "#a855f7", "#06b6d4"]
_LAYOUT = dict(
    paper_bgcolor="#0f172a",
    plot_bgcolor="#0f172a",
    font=dict(color="#94a3b8", size=12),
    margin=dict(l=16, r=16, t=32, b=16),
)


def tasks_over_time_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of tasks created vs completed over time.

    df must have columns: date, created, completed.
    """
    fig = go.Figure()
    fig.add_bar(
        x=df["date"],
        y=df["created"],
        name="Created",
        marker_color=_PALETTE[0],
    )
    fig.add_bar(
        x=df["date"],
        y=df["completed"],
        name="Completed",
        marker_color=_PALETTE[1],
    )
    fig.update_layout(
        **_LAYOUT,
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="#1e293b"),
        yaxis=dict(gridcolor="#1e293b"),
    )
    return fig


def status_distribution_chart(status_counts: dict[str, int]) -> go.Figure:
    """Pie chart of task status distribution."""
    status_colors = {
        "pending": "#6366f1",
        "in_progress": "#a855f7",
        "completed": "#22c55e",
        "cancelled": "#475569",
    }
    labels = list(status_counts.keys())
    values = list(status_counts.values())
    colors = [status_colors.get(lbl, "#94a3b8") for lbl in labels]

    fig = go.Figure(
        go.Pie(
            labels=[lbl.replace("_", " ").title() for lbl in labels],
            values=values,
            marker_colors=colors,
            hole=0.45,
            textinfo="label+percent",
            textfont_color="#f1f5f9",
        )
    )
    fig.update_layout(**_LAYOUT)
    return fig


def completion_rate_chart(rate_data: list[dict]) -> go.Figure:
    """Horizontal bar chart of completion rate per list."""
    if not rate_data:
        return go.Figure().update_layout(**_LAYOUT)

    df = pd.DataFrame(rate_data)
    fig = px.bar(
        df,
        x="rate",
        y="list",
        orientation="h",
        text="rate",
        color="rate",
        color_continuous_scale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#22c55e"]],
        range_color=[0, 100],
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
    fig.update_layout(
        **_LAYOUT,
        coloraxis_showscale=False,
        xaxis=dict(range=[0, 100], title="Completion %", gridcolor="#1e293b"),
        yaxis=dict(title="", gridcolor="#1e293b"),
    )
    return fig
