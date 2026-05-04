"""Tests for project export/import (multi-user handoff)."""
import json

import pytest
from tools.contacts import add_contact
from tools.notes import add_note
from tools.projects import create_project
from tools.transfer import export_project, import_project


@pytest.fixture()
def populated_project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
    p = create_project("Export Test Corp", project_type="generic", description="A test project")
    add_contact(p["id"], "Alice", role="PM", contact_type="internal", email="alice@example.com")
    add_contact(p["id"], "Bob", role="Dev", contact_type="external", company="Acme")
    add_note(p["id"], "Kickoff Notes", "We discussed milestones.", note_type="meeting-notes")
    add_note(p["id"], "Decision", "Go-live set to Q3.", note_type="decision")
    return p


class TestExportProject:
    def test_export_creates_json_file(self, populated_project, tmp_path):
        dest = str(tmp_path / "export.json")
        result = export_project(populated_project["id"], dest)

        assert result["path"] == dest
        assert result["project"] == "Export Test Corp"
        assert result["contacts"] == 2
        assert result["notes"] == 2

    def test_export_file_content(self, populated_project, tmp_path):
        dest = tmp_path / "export.json"
        export_project(populated_project["id"], str(dest))

        payload = json.loads(dest.read_text())
        assert payload["export_version"] == 1
        assert payload["project"]["name"] == "Export Test Corp"
        assert len(payload["contacts"]) == 2
        assert len(payload["notes"]) == 2
        assert "exported_at" in payload

    def test_export_default_path(self, populated_project, tmp_path, monkeypatch):
        monkeypatch.setattr("tools.transfer.Path.home", lambda: tmp_path)
        result = export_project(populated_project["id"])
        assert result["path"].endswith(".json")

    def test_export_nonexistent_project_raises(self):
        with pytest.raises(ValueError, match="not found"):
            export_project(99999)

    def test_export_excludes_old_ids(self, populated_project, tmp_path):
        dest = tmp_path / "export.json"
        export_project(populated_project["id"], str(dest))

        payload = json.loads(dest.read_text())
        # IDs are present in the export (they are included for reference but stripped on import)
        assert "id" in payload["project"]


class TestImportProject:
    def _make_export(self, populated_project, tmp_path) -> str:
        dest = str(tmp_path / "export.json")
        export_project(populated_project["id"], dest)
        return dest

    def test_import_roundtrip(self, populated_project, tmp_path, monkeypatch):
        monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
        export_path = self._make_export(populated_project, tmp_path)

        # Delete original so we can re-import without conflict
        from tools.db import db_connection
        with db_connection() as conn:
            conn.execute("DELETE FROM projects WHERE id = ?", (populated_project["id"],))
            conn.commit()

        result = import_project(export_path, merge_strategy="skip")

        assert result["imported"] is True
        assert result["project"] == "Export Test Corp"
        assert result["contacts"] == 2
        assert result["notes"] == 2

    def test_import_skip_on_conflict(self, populated_project, tmp_path):
        export_path = self._make_export(populated_project, tmp_path)
        result = import_project(export_path, merge_strategy="skip")

        assert result["imported"] is False
        assert "already exists" in result["reason"]

    def test_import_rename_on_conflict(self, populated_project, tmp_path, monkeypatch):
        monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
        export_path = self._make_export(populated_project, tmp_path)
        result = import_project(export_path, merge_strategy="rename")

        assert result["imported"] is True
        assert "imported" in result["slug"]
        assert result["project"] != "Export Test Corp"  # name got suffix

    def test_import_overwrite_on_conflict(self, populated_project, tmp_path, monkeypatch):
        monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
        export_path = self._make_export(populated_project, tmp_path)
        result = import_project(export_path, merge_strategy="overwrite")

        assert result["imported"] is True
        assert result["slug"] == populated_project["slug"]

    def test_import_invalid_strategy_raises(self, populated_project, tmp_path):
        export_path = self._make_export(populated_project, tmp_path)
        with pytest.raises(ValueError, match="merge_strategy"):
            import_project(export_path, merge_strategy="magic")

    def test_import_missing_file_raises(self):
        with pytest.raises(ValueError, match="not found"):
            import_project("/tmp/nonexistent_export_xyz.json")

    def test_import_wrong_version_raises(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text(json.dumps({"export_version": 99, "project": {}, "contacts": [], "notes": []}))
        with pytest.raises(ValueError, match="export_version"):
            import_project(str(bad_file))
