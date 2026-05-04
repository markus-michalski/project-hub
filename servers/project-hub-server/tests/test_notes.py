"""Tests for notes CRUD operations."""
import pytest
from tools.notes import add_note, delete_note, get_note, list_notes, update_note
from tools.projects import create_project


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
    return create_project("Test Project")


def test_add_note(project):
    note = add_note(project["id"], "My Note", "Some content")

    assert note["title"] == "My Note"
    assert note["content"] == "Some content"
    assert note["type"] == "note"
    assert note["project_id"] == project["id"]


def test_add_note_with_type(project):
    note = add_note(project["id"], "Kickoff", "Notes here", note_type="meeting-notes", agenda="1. Intro")

    assert note["type"] == "meeting-notes"
    assert note["agenda"] == "1. Intro"


def test_get_note(project):
    note = add_note(project["id"], "Fetch Me", "Content")

    found = get_note(note["id"])
    assert found is not None
    assert found["title"] == "Fetch Me"


def test_get_note_not_found():
    assert get_note(99999) is None


def test_list_notes_empty(project):
    result = list_notes(project["id"])
    assert result["items"] == []
    assert result["total"] == 0


def test_list_notes(project):
    add_note(project["id"], "Note 1", "A")
    add_note(project["id"], "Note 2", "B")

    result = list_notes(project["id"])
    assert len(result["items"]) == 2
    assert result["total"] == 2


def test_list_notes_filter_by_type(project):
    add_note(project["id"], "Meeting", "...", note_type="meeting-notes")
    add_note(project["id"], "Decision", "...", note_type="decision")

    meetings = list_notes(project["id"], note_type="meeting-notes")
    assert len(meetings["items"]) == 1
    assert meetings["total"] == 1
    assert meetings["items"][0]["type"] == "meeting-notes"


def test_list_notes_limit(project):
    for i in range(5):
        add_note(project["id"], f"Note {i}", "content")

    result = list_notes(project["id"], limit=3)
    assert len(result["items"]) == 3
    assert result["total"] == 5


def test_list_notes_pagination(project):
    for i in range(5):
        add_note(project["id"], f"Note {i}", "content")

    page1 = list_notes(project["id"], limit=3, offset=0)
    page2 = list_notes(project["id"], limit=3, offset=3)

    assert len(page1["items"]) == 3
    assert len(page2["items"]) == 2
    assert page1["total"] == 5


def test_list_notes_ordered_newest_first(project):
    add_note(project["id"], "First", "a")
    add_note(project["id"], "Second", "b")

    result = list_notes(project["id"])
    assert result["items"][0]["title"] == "Second"


def test_update_note_title(project):
    note = add_note(project["id"], "Old Title", "Content")

    updated = update_note(note["id"], title="New Title")

    assert updated["title"] == "New Title"
    assert updated["content"] == "Content"  # Unchanged


def test_update_note_content(project):
    note = add_note(project["id"], "Title", "Old content")

    updated = update_note(note["id"], content="New content")

    assert updated["content"] == "New content"
    assert updated["title"] == "Title"  # Unchanged


def test_update_note_type(project):
    note = add_note(project["id"], "Title", "Content", note_type="note")

    updated = update_note(note["id"], note_type="decision")

    assert updated["type"] == "decision"


def test_update_note_no_fields_returns_unchanged(project):
    note = add_note(project["id"], "Unchanged", "Content")

    result = update_note(note["id"])

    assert result["title"] == "Unchanged"


def test_update_note_not_found():
    result = update_note(99999, title="Ghost")
    assert result is None


def test_delete_note(project):
    note = add_note(project["id"], "Delete Me", "content")

    assert delete_note(note["id"]) is True
    assert get_note(note["id"]) is None


def test_delete_note_not_found():
    assert delete_note(99999) is False


def test_note_has_updated_at(project):
    note = add_note(project["id"], "Timestamped", "Content")
    assert "updated_at" in note
    assert note["updated_at"] is not None


def test_update_note_sets_updated_at(project):
    note = add_note(project["id"], "Track Me", "Initial")
    original_updated_at = note["updated_at"]

    import time
    time.sleep(0.01)

    updated = update_note(note["id"], content="Changed")
    assert updated["updated_at"] >= original_updated_at


def test_list_notes_includes_updated_at(project):
    add_note(project["id"], "Note A", "Content A")
    result = list_notes(project["id"])
    assert "updated_at" in result["items"][0]
