"""Tests for date helper utilities."""

from datetime import date, timedelta

import pytest

from app.utils.date_helpers import days_until_due, format_due_date_label, is_overdue


def _date(delta: int) -> str:
    return (date.today() + timedelta(days=delta)).isoformat()


# --- is_overdue ---


def test_is_overdue_past_date():
    assert is_overdue(_date(-1)) is True


def test_is_overdue_today():
    assert is_overdue(_date(0)) is False


def test_is_overdue_future():
    assert is_overdue(_date(5)) is False


def test_is_overdue_none():
    assert is_overdue(None) is False


# --- days_until_due ---


def test_days_until_due_today():
    assert days_until_due(_date(0)) == 0


def test_days_until_due_tomorrow():
    assert days_until_due(_date(1)) == 1


def test_days_until_due_overdue():
    assert days_until_due(_date(-3)) == -3


def test_days_until_due_none():
    assert days_until_due(None) is None


# --- format_due_date_label ---


def test_format_no_due_date():
    assert format_due_date_label(None) == "No due date"


def test_format_today():
    assert format_due_date_label(_date(0)) == "Today"


def test_format_tomorrow():
    assert format_due_date_label(_date(1)) == "Tomorrow"


def test_format_in_n_days():
    assert format_due_date_label(_date(5)) == "In 5 days"


def test_format_overdue_one_day():
    assert format_due_date_label(_date(-1)) == "Overdue (1 day ago)"


def test_format_overdue_multiple_days():
    assert format_due_date_label(_date(-7)) == "Overdue (7 days ago)"
