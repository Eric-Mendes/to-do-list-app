"""Integration tests for tag-based folder grouping."""

from app.models.list_model import create_list, get_lists_by_tag
from app.models.tag_model import (
    assign_tag_to_list,
    create_tag,
    delete_tag,
    get_tags_for_list,
    remove_tag_from_list,
)


def test_filter_lists_by_tag(db):
    """Only lists with the target tag are returned."""
    work_tag = create_tag(db, "work")
    personal_tag = create_tag(db, "personal")

    l1 = create_list(db, "Work Tasks")
    l2 = create_list(db, "Home Tasks")
    l3 = create_list(db, "Finance")
    create_list(db, "Untagged")

    assign_tag_to_list(db, l1, work_tag)
    assign_tag_to_list(db, l2, personal_tag)
    assign_tag_to_list(db, l3, personal_tag)

    work_lists = get_lists_by_tag(db, work_tag)
    assert len(work_lists) == 1
    assert work_lists[0]["name"] == "Work Tasks"

    personal_lists = get_lists_by_tag(db, personal_tag)
    assert len(personal_lists) == 2
    assert {lst["name"] for lst in personal_lists} == {"Home Tasks", "Finance"}


def test_list_can_have_multiple_tags(db):
    """A list can belong to multiple tag-folders."""
    t1 = create_tag(db, "alpha")
    t2 = create_tag(db, "beta")
    lst = create_list(db, "Multi-Tag List")

    assign_tag_to_list(db, lst, t1)
    assign_tag_to_list(db, lst, t2)

    assert len(get_lists_by_tag(db, t1)) == 1
    assert len(get_lists_by_tag(db, t2)) == 1
    assert len(get_tags_for_list(db, lst)) == 2


def test_remove_tag_removes_from_folder(db):
    """Removing a tag from a list removes it from that folder view."""
    tag_id = create_tag(db, "removable")
    lst = create_list(db, "My List")
    assign_tag_to_list(db, lst, tag_id)

    assert len(get_lists_by_tag(db, tag_id)) == 1
    remove_tag_from_list(db, lst, tag_id)
    assert len(get_lists_by_tag(db, tag_id)) == 0


def test_delete_tag_removes_all_folder_memberships(db):
    """Deleting a tag removes all list associations for it."""
    tag_id = create_tag(db, "gone")
    for name in ("L1", "L2", "L3"):
        lst = create_list(db, name)
        assign_tag_to_list(db, lst, tag_id)

    assert len(get_lists_by_tag(db, tag_id)) == 3
    delete_tag(db, tag_id)
    assert get_lists_by_tag(db, tag_id) == []
