"""Tests for custom project type management."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.project_types import (
    create_project_type,
    delete_project_type,
    get_project_type,
    list_project_types,
)


@pytest.fixture()
def type_dirs(tmp_path, monkeypatch):
    """Provide isolated built-in and user project-type directories."""
    builtin = tmp_path / "builtin-types"
    user = tmp_path / "user-types"
    builtin.mkdir()
    user.mkdir()

    monkeypatch.setattr("tools.project_types._BUILTIN_TYPES_ROOT", builtin)
    monkeypatch.setattr("tools.project_types._get_user_types_root", lambda: user)

    return builtin, user


def _make_type(parent: Path, name: str, label: str = "", description: str = "") -> Path:
    d = parent / name
    d.mkdir(parents=True)
    readme = f"""---
name: {name}
label: {label or name}
description: {description}
---

# {label or name}
"""
    (d / "README.md").write_text(readme, encoding="utf-8")
    return d


# ---------------------------------------------------------------------------
# list_project_types
# ---------------------------------------------------------------------------

def test_list_returns_builtins(type_dirs):
    builtin, _ = type_dirs
    _make_type(builtin, "it-project", "IT Project", "Internal IT project")

    result = list_project_types()

    assert len(result) == 1
    assert result[0]["name"] == "it-project"
    assert result[0]["source"] == "built-in"


def test_list_returns_custom(type_dirs):
    _, user = type_dirs
    _make_type(user, "hr-onboarding", "HR Onboarding", "Human resources onboarding")

    result = list_project_types()

    assert len(result) == 1
    assert result[0]["name"] == "hr-onboarding"
    assert result[0]["source"] == "custom"


def test_list_returns_both_with_source_indicator(type_dirs):
    builtin, user = type_dirs
    _make_type(builtin, "it-project", "IT Project")
    _make_type(user, "hr-onboarding", "HR Onboarding")

    result = list_project_types()
    sources = {r["name"]: r["source"] for r in result}

    assert sources["it-project"] == "built-in"
    assert sources["hr-onboarding"] == "custom"


def test_list_custom_overrides_builtin(type_dirs):
    builtin, user = type_dirs
    _make_type(builtin, "generic", "Generic (built-in)")
    _make_type(user, "generic", "Generic (custom)")

    result = list_project_types()
    generic = next(r for r in result if r["name"] == "generic")

    assert generic["source"] == "custom"
    assert len(result) == 1


def test_list_empty_when_no_types(type_dirs):
    result = list_project_types()
    assert result == []


# ---------------------------------------------------------------------------
# get_project_type
# ---------------------------------------------------------------------------

def test_get_builtin_type(type_dirs):
    builtin, _ = type_dirs
    _make_type(builtin, "consulting", "Consulting", "Client consulting project")

    result = get_project_type("consulting")

    assert result is not None
    assert result["name"] == "consulting"
    assert result["source"] == "built-in"
    assert "readme" in result
    assert result["readme"] != ""


def test_get_custom_type(type_dirs):
    _, user = type_dirs
    _make_type(user, "real-estate", "Real Estate", "Property management")

    result = get_project_type("real-estate")

    assert result is not None
    assert result["source"] == "custom"


def test_get_custom_takes_precedence_over_builtin(type_dirs):
    builtin, user = type_dirs
    _make_type(builtin, "generic", "Generic built-in")
    _make_type(user, "generic", "Generic custom")

    result = get_project_type("generic")

    assert result is not None
    assert result["source"] == "custom"


def test_get_nonexistent_returns_none(type_dirs):
    result = get_project_type("does-not-exist")
    assert result is None


# ---------------------------------------------------------------------------
# create_project_type
# ---------------------------------------------------------------------------

def test_create_project_type_basic(type_dirs):
    _, user = type_dirs

    result = create_project_type("Legal", description="Legal case management")

    assert result["name"] == "legal"
    assert result["label"] == "Legal"
    assert result["source"] == "custom"
    assert result["created"] is True
    assert (user / "legal" / "README.md").exists()
    assert (user / "legal" / "knowledge").is_dir()


def test_create_project_type_with_phases(type_dirs):
    _, user = type_dirs

    create_project_type("HR", phases=["Intake", "Onboarding", "Integration"])

    readme = (user / "hr" / "README.md").read_text()
    assert "Intake" in readme
    assert "Onboarding" in readme
    assert "Integration" in readme


def test_create_project_type_with_contacts(type_dirs):
    _, user = type_dirs

    create_project_type("Event", contacts=["Event Manager", "Venue Contact", "Catering"])

    readme = (user / "event" / "README.md").read_text()
    assert "Event Manager" in readme
    assert "Venue Contact" in readme


def test_create_project_type_slugifies_name(type_dirs):
    _, user = type_dirs

    result = create_project_type("Real Estate & Property")

    assert result["name"] == "real-estate-property"
    assert (user / "real-estate-property").exists()


def test_create_project_type_duplicate_returns_error(type_dirs):
    _, user = type_dirs
    create_project_type("Legal")

    result = create_project_type("Legal")

    assert "error" in result


def test_create_project_type_flags_builtin_override(type_dirs):
    builtin, _ = type_dirs
    _make_type(builtin, "generic", "Generic built-in")

    result = create_project_type("generic")

    assert result["overrides_builtin"] is True


# ---------------------------------------------------------------------------
# delete_project_type
# ---------------------------------------------------------------------------

def test_delete_custom_type(type_dirs):
    _, user = type_dirs
    _make_type(user, "my-type", "My Type")

    result = delete_project_type("my-type")

    assert result["deleted"] is True
    assert not (user / "my-type").exists()


def test_delete_builtin_returns_error(type_dirs):
    builtin, _ = type_dirs
    _make_type(builtin, "it-project", "IT Project")

    result = delete_project_type("it-project")

    assert "error" in result
    assert (builtin / "it-project").exists()


def test_delete_nonexistent_returns_error(type_dirs):
    result = delete_project_type("does-not-exist")
    assert "error" in result
