"""Tests for session management."""
import pytest

from tools.projects import create_project
from tools.session import clear_session, get_session, set_session


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
    return create_project("Session Test Project")


def test_initial_session_has_no_project():
    session = get_session()
    assert session["project_id"] is None


def test_set_session(project):
    session = set_session(project["id"], last_skill="resume")

    assert session["project_id"] == project["id"]
    assert session["last_skill"] == "resume"
    assert session["project_name"] == "Session Test Project"


def test_clear_session(project):
    set_session(project["id"])
    session = clear_session()

    assert session["project_id"] is None
    assert session["last_skill"] == ""


def test_session_includes_project_details(project):
    session = set_session(project["id"])

    assert session["project_name"] == "Session Test Project"
    assert session["project_type"] == "generic"
    assert session["project_status"] == "active"
