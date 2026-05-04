"""Tests for contact CRUD operations."""
import pytest
from tools.contacts import add_contact, delete_contact, list_contacts, update_contact
from tools.projects import create_project


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
    return create_project("Contact Test Project")


def test_add_contact_basic(project):
    c = add_contact(project["id"], name="Alice Müller", role="PM")
    assert c["id"] is not None
    assert c["name"] == "Alice Müller"
    assert c["role"] == "PM"
    assert c["type"] == "internal"


def test_add_contact_external(project):
    c = add_contact(
        project["id"],
        name="Bob External",
        role="Merchant PM",
        contact_type="external",
        email="bob@merchant.com",
        company="Acme GmbH",
    )
    assert c["type"] == "external"
    assert c["email"] == "bob@merchant.com"
    assert c["company"] == "Acme GmbH"


def test_list_contacts_all(project):
    add_contact(project["id"], name="Internal One", contact_type="internal")
    add_contact(project["id"], name="External One", contact_type="external")

    result = list_contacts(project["id"])
    assert len(result["items"]) == 2
    assert result["total"] == 2


def test_list_contacts_filter_by_type(project):
    add_contact(project["id"], name="Internal A", contact_type="internal")
    add_contact(project["id"], name="Internal B", contact_type="internal")
    add_contact(project["id"], name="External A", contact_type="external")

    internals = list_contacts(project["id"], contact_type="internal")
    externals = list_contacts(project["id"], contact_type="external")

    assert len(internals["items"]) == 2
    assert internals["total"] == 2
    assert len(externals["items"]) == 1


def test_list_contacts_limit(project):
    for i in range(5):
        add_contact(project["id"], name=f"Contact {i}")

    result = list_contacts(project["id"], limit=3)
    assert len(result["items"]) == 3
    assert result["total"] == 5


def test_list_contacts_pagination(project):
    for i in range(5):
        add_contact(project["id"], name=f"Contact {i:02d}")

    page1 = list_contacts(project["id"], limit=3, offset=0)
    page2 = list_contacts(project["id"], limit=3, offset=3)

    assert len(page1["items"]) == 3
    assert len(page2["items"]) == 2
    assert page1["total"] == 5


def test_list_contacts_empty(project):
    result = list_contacts(project["id"])
    assert result["items"] == []
    assert result["total"] == 0


def test_update_contact_patches_only_provided_fields(project):
    c = add_contact(project["id"], name="Original Name", role="PM", email="old@example.com")

    updated = update_contact(c["id"], role="Tech Lead")

    assert updated["role"] == "Tech Lead"
    assert updated["name"] == "Original Name"
    assert updated["email"] == "old@example.com"


def test_update_contact_multiple_fields(project):
    c = add_contact(project["id"], name="Jane", role="PM")

    updated = update_contact(c["id"], name="Jane Doe", email="jane@example.com", company="ACME")

    assert updated["name"] == "Jane Doe"
    assert updated["email"] == "jane@example.com"
    assert updated["company"] == "ACME"


def test_delete_contact_removes_it(project):
    c = add_contact(project["id"], name="To Be Deleted")

    result = delete_contact(c["id"])

    assert result is True
    assert list_contacts(project["id"])["items"] == []


def test_delete_contact_not_found_returns_false(project):
    assert delete_contact(99999) is False


def test_contacts_isolated_per_project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
    p1 = create_project("Project Alpha")
    p2 = create_project("Project Beta")

    add_contact(p1["id"], name="Alpha Contact")

    assert list_contacts(p1["id"])["total"] == 1
    assert list_contacts(p2["id"])["total"] == 0
