"""Smoke: DB CRUD roundtrips — project, contact, note, session."""
from tools.contacts import add_contact, list_contacts, update_contact, delete_contact
from tools.notes import add_note, get_note, list_notes, update_note, delete_note
from tools.projects import create_project, get_project, update_project
from tools.session import clear_session, get_session, set_session


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def test_project_create_and_read():
    p = create_project("Smoke Test Project", project_type="generic")
    assert p["id"] is not None
    assert p["name"] == "Smoke Test Project"
    assert p["type"] == "generic"
    assert p["status"] == "active"

    found = get_project(p["slug"])
    assert found is not None
    assert found["id"] == p["id"]


def test_project_update():
    p = create_project("Update Target")
    updated = update_project(p["slug"], phase="UAT", status="paused")
    assert updated["phase"] == "UAT"
    assert updated["status"] == "paused"

    reloaded = get_project(p["slug"])
    assert reloaded["phase"] == "UAT"


def test_project_not_found_returns_none():
    assert get_project("definitely-does-not-exist") is None


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

def test_contact_create_list_update_delete():
    p = create_project("Contact Host")
    pid = p["id"]

    contact = add_contact(pid, name="Alice Tester", role="PM", email="alice@example.com")
    assert contact["id"] is not None
    assert contact["name"] == "Alice Tester"

    contacts = list_contacts(pid)
    assert len(contacts) == 1

    updated = update_contact(contact["id"], role="Tech Lead")
    assert updated["role"] == "Tech Lead"

    result = delete_contact(contact["id"])
    assert result is True

    assert list_contacts(pid) == []


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def test_note_create_read_update_delete():
    p = create_project("Note Host")
    pid = p["id"]

    note = add_note(pid, title="First Note", content="Some content", note_type="note")
    assert note["id"] is not None
    assert note["title"] == "First Note"

    fetched = get_note(note["id"])
    assert fetched is not None
    assert fetched["content"] == "Some content"

    updated = update_note(note["id"], title="Updated Note")
    assert updated["title"] == "Updated Note"

    result_notes = list_notes(pid)
    assert len(result_notes) == 1

    from tools.notes import delete_note as _delete
    assert _delete(note["id"]) is True
    assert list_notes(pid) == []


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

def test_session_roundtrip():
    initial = get_session()
    assert isinstance(initial, dict)
    assert initial.get("project_id") is None

    p = create_project("Session Project")
    set_session(p["id"], last_skill="resume")

    session = get_session()
    assert session["project_id"] == p["id"]
    assert session["last_skill"] == "resume"

    clear_session()
    cleared = get_session()
    assert cleared.get("project_id") is None
