"""Tests for file attachment operations on notes."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest
from tools import attachments as attachments_module
from tools.attachments import _convert_to_markdown_sibling, attach_file, list_attachments, remove_attachment
from tools.notes import add_note, get_note
from tools.projects import create_project


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.projects.get_docs_root", lambda: tmp_path)
    return create_project("Attach Project")


@pytest.fixture
def note(project):
    return add_note(project["id"], "Test Note", "Content here")


# pytest's tmp_path fixture always lives under the OS temp dir (/tmp on POSIX,
# %TEMP% on Windows) — use the same OS-correct root here instead of hardcoding
# the POSIX path, or sample_file (built on tmp_path) fails relative_to() on Windows.
# .resolve() matters on Windows: tempfile.gettempdir() can return an 8.3 short
# path (e.g. RUNNER~1) while attach_file() resolves the source file to its long
# canonical form — relative_to() needs both sides in the same form to match.
_HOME = Path(tempfile.gettempdir()).resolve()


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


def test_remove_attachment_deletes_markdown_sibling(project, note, tmp_path):
    f = tmp_path / "report.txt"
    f.write_text("important content")
    info = attach_file(note["id"], str(f), home_override=_HOME)
    sibling = Path(info["path"]).with_name("report.txt.md")
    assert sibling.exists()

    remove_attachment(note["id"], "report.txt")

    assert not sibling.exists()


def test_remove_attachment_no_sibling_present_does_not_raise(project, note, sample_file):
    # sample_file's fake "PDF" content produces no markdown sibling (not real PDF
    # bytes) — removal must still succeed without erroring on a missing sibling.
    attach_file(note["id"], str(sample_file), home_override=_HOME)

    remove_attachment(note["id"], "report.pdf")  # must not raise


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


# --- _get_markitdown ---

def test_get_markitdown_swallows_non_import_error(monkeypatch):
    # Regression: a broken native dependency (e.g. onnxruntime failing to load
    # its platform binary) raises OSError/RuntimeError from MarkItDown(), not
    # ImportError — _get_markitdown() must swallow that too, not just ImportError,
    # or attach_file() crashes after the file is already copied but before the
    # DB write, leaving an orphaned attachment with no DB reference.
    monkeypatch.setattr(attachments_module, "_markitdown", None)
    monkeypatch.setattr(attachments_module, "_markitdown_load_attempted", False)

    class _BrokenMarkItDown:
        def __init__(self):
            raise OSError("simulated broken onnxruntime native lib")

    fake_module = type(sys)("markitdown")
    fake_module.MarkItDown = _BrokenMarkItDown
    monkeypatch.setitem(sys.modules, "markitdown", fake_module)

    result = attachments_module._get_markitdown()

    assert result is None


def test_attach_file_survives_broken_markitdown_constructor(project, note, tmp_path, monkeypatch):
    # End-to-end version of the above: attach_file must still succeed (file copied,
    # DB updated) even if the markitdown backend is broken at instantiation time.
    monkeypatch.setattr(attachments_module, "_markitdown", None)
    monkeypatch.setattr(attachments_module, "_markitdown_load_attempted", False)

    class _BrokenMarkItDown:
        def __init__(self):
            raise OSError("simulated broken onnxruntime native lib")

    fake_module = type(sys)("markitdown")
    fake_module.MarkItDown = _BrokenMarkItDown
    monkeypatch.setitem(sys.modules, "markitdown", fake_module)

    f = tmp_path / "report.txt"
    f.write_text("important content")

    result = attach_file(note["id"], str(f), home_override=_HOME)

    assert Path(result["path"]).exists()
    assert list_attachments(note["id"]) == [result]


# --- _convert_to_markdown_sibling ---

def test_markdown_sibling_created_for_convertible_file(tmp_path):
    source = tmp_path / "notiz.txt"
    source.write_text("Hallo Welt")
    dest = tmp_path / "attachments" / "notiz.txt"
    dest.parent.mkdir()
    import shutil
    shutil.copy2(source, dest)

    _convert_to_markdown_sibling(dest)

    sibling = dest.with_name("notiz.txt.md")
    assert sibling.exists()
    assert sibling.read_text().strip() == "Hallo Welt"


def test_markdown_sibling_skipped_for_images(tmp_path):
    dest = tmp_path / "foto.png"
    dest.write_bytes(b"\x89PNG\r\n\x1a\nnot a real png")

    _convert_to_markdown_sibling(dest)

    assert not dest.with_name("foto.png.md").exists()


def test_markdown_sibling_skipped_for_already_markdown_file(tmp_path):
    dest = tmp_path / "bereits.md"
    dest.write_text("# Schon Markdown")

    _convert_to_markdown_sibling(dest)

    assert not dest.with_name("bereits.md.md").exists()


def test_markdown_conversion_failure_does_not_abort_copy(tmp_path, monkeypatch):
    # Regression: _convert_to_markdown_sibling promises "never raises" — a broken
    # markitdown install or a conversion error must not abort the attachment copy.
    def _boom(_path):
        raise RuntimeError("simulated conversion failure")

    monkeypatch.setattr(attachments_module, "_markitdown", type("M", (), {"convert": staticmethod(_boom)})())

    dest = tmp_path / "doc.pdf"
    dest.write_text("not really a pdf")

    _convert_to_markdown_sibling(dest)

    assert dest.exists()
    assert not dest.with_name("doc.pdf.md").exists()


def test_markdown_sibling_skipped_for_empty_conversion_result(tmp_path, monkeypatch):
    class _EmptyResult:
        markdown = "   \n  "

    monkeypatch.setattr(
        attachments_module, "_markitdown",
        type("M", (), {"convert": staticmethod(lambda _p: _EmptyResult())})(),
    )

    dest = tmp_path / "leer.pdf"
    dest.write_text("irrelevant")

    _convert_to_markdown_sibling(dest)

    assert not dest.with_name("leer.pdf.md").exists()


def test_attach_file_creates_markdown_sibling(project, note, tmp_path):
    f = tmp_path / "report.txt"
    f.write_text("important content")

    attach_file(note["id"], str(f), home_override=_HOME)

    attachments = list_attachments(note["id"])
    copied_path = Path(attachments[0]["path"])
    sibling = copied_path.with_name("report.txt.md")
    assert sibling.exists()
    assert sibling.read_text().strip() == "important content"
