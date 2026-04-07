"""Date utility functions for due date calculations."""

from datetime import date, datetime
from typing import Optional


def _parse(due_date: str) -> date:
    """Parse an ISO-8601 date string to a date object."""
    return datetime.strptime(due_date[:10], "%Y-%m-%d").date()


def is_overdue(due_date: Optional[str]) -> bool:
    """Return True if the due date is in the past."""
    if due_date is None:
        return False
    return _parse(due_date) < date.today()


def days_until_due(due_date: Optional[str]) -> Optional[int]:
    """Return the number of days until the due date (negative if overdue).

    Returns None if due_date is None.
    """
    if due_date is None:
        return None
    return (_parse(due_date) - date.today()).days


def format_due_date_label(due_date: Optional[str]) -> str:
    """Return a human-friendly label for a due date.

    Examples: "Today", "Tomorrow", "In 3 days", "Overdue (2 days ago)", "No due date".
    """
    if due_date is None:
        return "No due date"
    delta = days_until_due(due_date)
    if delta == 0:
        return "Today"
    if delta == 1:
        return "Tomorrow"
    if delta > 1:
        return f"In {delta} days"
    if delta == -1:
        return "Overdue (1 day ago)"
    return f"Overdue ({abs(delta)} days ago)"
