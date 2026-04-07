"""Tests for tag model CRUD operations."""

import pytest

from app.models.tag_model import (
    assign_tag_to_list,
    create_tag,
    delete_tag,
    get_all_tags,
    get_tag,
    get_tag_by_name,
    get_tags_for_list,
    remove_tag_from_list,
    update_tag,
)


def _make_list(db, name="My List"):
    db.execute("INSERT INTO task_lists (name) VALUES (?)", (name,))
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def test_create_tag_returns_id(db):
    tag_id = create_tag(db, "work")
    assert isinstance(tag_id, int) and tag_id > 0


def test_create_tag_default_color(db):
    tag_id = create_tag(db, "personal")
    tag = get_tag(db, tag_id)
    assert tag["color"] == "#6366f1"


def test_create_tag_custom_color(db):
    tag_id = create_tag(db, "urgent", "#ef4444")
    tag = get_tag(db, tag_id)
    assert tag["color"] == "#ef4444"


def test_get_tag_returns_correct_record(db):
    tag_id = create_tag(db, "home")
    tag = get_tag(db, tag_id)
    assert tag["id"] == tag_id
    assert tag["name"] == "home"


def test_get_tag_returns_none_for_missing(db):
    assert get_tag(db, 9999) is None


def test_get_tag_by_name(db):
    create_tag(db, "finance")
    tag = get_tag_by_name(db, "finance")
    assert tag is not None
    assert tag["name"] == "finance"


def test_get_tag_by_name_returns_none_for_missing(db):
    assert get_tag_by_name(db, "nonexistent") is None


def test_get_all_tags_empty(db):
    assert get_all_tags(db) == []


def test_get_all_tags_returns_all(db):
    create_tag(db, "b_tag")
    create_tag(db, "a_tag")
    tags = get_all_tags(db)
    assert len(tags) == 2
    assert tags[0]["name"] == "a_tag"


def test_update_tag_name(db):
    tag_id = create_tag(db, "old_name")
    update_tag(db, tag_id, name="new_name")
    assert get_tag(db, tag_id)["name"] == "new_name"


def test_update_tag_color(db):
    tag_id = create_tag(db, "myTag")
    update_tag(db, tag_id, color="#ff0000")
    assert get_tag(db, tag_id)["color"] == "#ff0000"


def test_update_tag_raises_for_missing(db):
    with pytest.raises(ValueError):
        update_tag(db, 9999, name="x")


def test_delete_tag(db):
    tag_id = create_tag(db, "temp")
    delete_tag(db, tag_id)
    assert get_tag(db, tag_id) is None


def test_delete_tag_cascades_list_tags(db):
    list_id = _make_list(db)
    tag_id = create_tag(db, "doomed")
    assign_tag_to_list(db, list_id, tag_id)
    delete_tag(db, tag_id)
    assert get_tags_for_list(db, list_id) == []


def test_tag_name_unique_constraint(db):
    create_tag(db, "duplicate")
    with pytest.raises(Exception):
        create_tag(db, "duplicate")


def test_assign_tag_to_list(db):
    list_id = _make_list(db)
    tag_id = create_tag(db, "work")
    assign_tag_to_list(db, list_id, tag_id)
    tags = get_tags_for_list(db, list_id)
    assert len(tags) == 1
    assert tags[0]["name"] == "work"


def test_assign_tag_idempotent(db):
    list_id = _make_list(db)
    tag_id = create_tag(db, "work")
    assign_tag_to_list(db, list_id, tag_id)
    assign_tag_to_list(db, list_id, tag_id)
    assert len(get_tags_for_list(db, list_id)) == 1


def test_remove_tag_from_list(db):
    list_id = _make_list(db)
    tag_id = create_tag(db, "removeme")
    assign_tag_to_list(db, list_id, tag_id)
    remove_tag_from_list(db, list_id, tag_id)
    assert get_tags_for_list(db, list_id) == []


def test_get_tags_for_list_empty(db):
    list_id = _make_list(db)
    assert get_tags_for_list(db, list_id) == []


def test_get_tags_for_list_multiple(db):
    list_id = _make_list(db)
    t1 = create_tag(db, "alpha")
    t2 = create_tag(db, "beta")
    assign_tag_to_list(db, list_id, t1)
    assign_tag_to_list(db, list_id, t2)
    tags = get_tags_for_list(db, list_id)
    assert {t["name"] for t in tags} == {"alpha", "beta"}
