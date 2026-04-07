"""Tests for style utility functions."""

from app.utils.styles import _contrast_color, priority_badge, status_badge, tag_chip


def test_priority_badge_high():
    html = priority_badge("high")
    assert "badge-high" in html
    assert "High" in html


def test_priority_badge_medium():
    html = priority_badge("medium")
    assert "badge-medium" in html
    assert "Medium" in html


def test_priority_badge_low():
    html = priority_badge("low")
    assert "badge-low" in html
    assert "Low" in html


def test_status_badge_pending():
    html = status_badge("pending")
    assert "badge-pending" in html
    assert "Pending" in html


def test_status_badge_completed():
    html = status_badge("completed")
    assert "badge-completed" in html
    assert "Done" in html


def test_status_badge_in_progress():
    html = status_badge("in_progress")
    assert "badge-in_progress" in html


def test_tag_chip_contains_name():
    html = tag_chip("Work", "#6366f1")
    assert "Work" in html
    assert "#6366f1" in html


def test_tag_chip_active_class():
    html = tag_chip("Work", "#6366f1", active=True)
    assert "tag-chip-active" in html


def test_tag_chip_inactive_no_active_class():
    html = tag_chip("Work", "#6366f1", active=False)
    assert "tag-chip-active" not in html


def test_contrast_color_dark_background_returns_white():
    assert _contrast_color("#000000") == "#ffffff"
    assert _contrast_color("#0f172a") == "#ffffff"


def test_contrast_color_light_background_returns_black():
    assert _contrast_color("#ffffff") == "#000000"
    assert _contrast_color("#f1f5f9") == "#000000"


def test_contrast_color_invalid_returns_white():
    assert _contrast_color("invalid") == "#ffffff"
