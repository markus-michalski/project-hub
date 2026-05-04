"""Tests for project CRUD operations."""
from tools.projects import create_project, get_project, list_projects, update_project


def test_create_project_basic(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    project = create_project("My Test Project")

    assert project["name"] == "My Test Project"
    assert project["slug"] == "my-test-project"
    assert project["type"] == "generic"
    assert project["status"] == "active"
    assert project["id"] is not None


def test_create_project_with_type(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    project = create_project("Acme Onboarding", project_type="merchant-onboarding", market="DE")

    assert project["type"] == "merchant-onboarding"
    assert project["market"] == "DE"


def test_slugify_special_chars(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    project = create_project("Müller & Partner GmbH")

    # Special chars stripped, spaces become dashes
    assert "-" in project["slug"]
    assert "&" not in project["slug"]


def test_get_project_by_slug(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    create_project("Search Me")

    found = get_project("search-me")
    assert found is not None
    assert found["name"] == "Search Me"


def test_get_project_by_name_case_insensitive(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    create_project("Case Test")

    found = get_project("case test")
    assert found is not None
    assert found["name"] == "Case Test"


def test_get_project_not_found():
    result = get_project("does-not-exist")
    assert result is None


def test_list_projects_empty():
    result = list_projects()
    assert result["items"] == []
    assert result["total"] == 0


def test_list_projects(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    create_project("Alpha")
    create_project("Beta")

    result = list_projects()
    assert len(result["items"]) == 2
    assert result["total"] == 2


def test_list_projects_filter_by_status(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    p = create_project("Active One")
    create_project("Another Active")
    update_project(p["slug"], status="paused")

    active = list_projects(status="active")
    paused = list_projects(status="paused")

    assert len(active["items"]) == 1
    assert active["total"] == 1
    assert len(paused["items"]) == 1


def test_list_projects_pagination(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    for i in range(5):
        create_project(f"Project {i}")

    page1 = list_projects(limit=3, offset=0)
    page2 = list_projects(limit=3, offset=3)

    assert len(page1["items"]) == 3
    assert page1["total"] == 5
    assert len(page2["items"]) == 2
    assert page2["offset"] == 3


def test_update_project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    project = create_project("Update Me")
    updated = update_project(project["slug"], phase="UAT", status="paused")

    assert updated["phase"] == "UAT"
    assert updated["status"] == "paused"


def test_update_project_updated_at_changes(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    project = create_project("Timestamp Test")
    original_ts = project["updated_at"]

    import time
    time.sleep(1.1)  # SQLite datetime() has 1s resolution

    update_project(project["slug"], phase="Done")
    refreshed = get_project(project["slug"])

    assert refreshed["updated_at"] != original_ts


def test_update_project_no_fields_returns_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)

    project = create_project("No Change")
    result = update_project(project["slug"])

    assert result["name"] == "No Change"
