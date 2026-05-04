"""Tests for file attachment operations on notes."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.attachments import attach_file, list_attachments, remove_attachment
from tools.notes import add_note, get_note
from tools.projects import create_project


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
    return create_project("Attach Project")


@pytest.fixture
def note(project):
    return add_note(project["id"], "Test Note", "Content here")


_HOME = Path("/tmp")  # all test files live under /tmp


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "report.pdf"
    f.write_bytes(b"PDF content" * 100)
    return f


# --- attach_file ---

def test_attach_file_copies_to_attachments_folder(project, note, sample_file):
    result = attach_file(note["id"], str(sample_file), home_override=_HOME)

    assert result["name"] == "report.pdf"
    assert Path(result["path"]).exists()
    assert Path(result["path"]).name == "report.pdf"
    assert "attachments" in str(result["path"])


def test_attach_file_original_untouched(project, note, sample_file):
    attach_file(note["id"], str(sample_file), home_override=_HOME)

    assert sample_file.exists()


def test_attach_file_stores_reference_in_db(project, note, sample_file):
    attach_file(note["id"], str(sample_file), home_override=_HOME)

    updated = get_note(note["id"])
    attachments = json.loads(updated["attachments"])
    assert len(attachments) == 1
    assert attachments[0]["name"] == "report.pdf"


def test_attach_file_returns_size(project, note, sample_file):
    result = attach_file(note["id"], str(sample_file), home_override=_HOME)

    assert result["size"] == sample_file.stat().st_size


def test_attach_file_multiple_files(project, note, tmp_path):
    f1 = tmp_path / "doc1.txt"
    f2 = tmp_path / "doc2.txt"
    f1.write_text("first")
    f2.write_text("second")

    attach_file(note["id"], str(f1), home_override=_HOME)
    attach_file(note["id"], str(f2), home_override=_HOME)

    updated = get_note(note["id"])
    attachments = json.loads(updated["attachments"])
    assert len(attachments) == 2
    names = {a["name"] for a in attachments}
    assert names == {"doc1.txt", "doc2.txt"}


def test_attach_file_note_not_found(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("x")

    with pytest.raises(ValueError, match="Note not found"):
        attach_file(99999, str(f))


def test_attach_file_source_not_found(project, note):
    with pytest.raises(FileNotFoundError):
        attach_file(note["id"], "/nonexistent/file.pdf")


def test_attach_file_path_traversal_blocked(project, note, tmp_path):
    evil = tmp_path / "evil.sh"
    evil.write_text("rm -rf /")

    with pytest.raises(ValueError, match="[Pp]ath"):
        attach_file(note["id"], str(evil), home_override=Path("/different/root"))


def test_attach_file_warns_large_file(project, note, tmp_path, capsys):
    big = tmp_path / "big.bin"
    big.write_bytes(b"x" * (11 * 1024 * 1024))  # 11 MB

    attach_file(note["id"], str(big), home_override=_HOME)

    captured = capsys.readouterr()
    assert "10" in captured.err or "10" in captured.out or "MB" in captured.err or "MB" in captured.out


# --- list_attachments ---

def test_list_attachments_empty(note):
    result = list_attachments(note["id"])
    assert result == []


def test_list_attachments_returns_file_info(project, note, sample_file):
    attach_file(note["id"], str(sample_file), home_override=_HOME)

    result = list_attachments(note["id"])
    assert len(result) == 1
    assert result[0]["name"] == "report.pdf"
    assert "path" in result[0]
    assert "size" in result[0]


def test_list_attachments_note_not_found():
    with pytest.raises(ValueError, match="Note not found"):
        list_attachments(99999)


# --- remove_attachment ---

def test_remove_attachment_deletes_file(project, note, sample_file):
    info = attach_file(note["id"], str(sample_file), home_override=_HOME)
    copied_path = Path(info["path"])

    remove_attachment(note["id"], "report.pdf")

    assert not copied_path.exists()


def test_remove_attachment_updates_db(project, note, sample_file):
    attach_file(note["id"], str(sample_file), home_override=_HOME)

    remove_attachment(note["id"], "report.pdf")

    updated = get_note(note["id"])
    attachments = json.loads(updated["attachments"])
    assert attachments == []


def test_remove_attachment_not_found_raises(project, note):
    with pytest.raises(ValueError, match="[Nn]ot found"):
        remove_attachment(note["id"], "missing.pdf")


def test_remove_attachment_note_not_found():
    with pytest.raises(ValueError, match="Note not found"):
        remove_attachment(99999, "x.pdf")


# --- get_note includes attachments ---

def test_get_note_includes_attachments_field(note):
    result = get_note(note["id"])
    assert "attachments" in result
    assert result["attachments"] == "[]"
