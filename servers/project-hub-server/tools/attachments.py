"""File attachment operations for notes.

Every file copy also generates a best-effort `<name>.md` sibling (via MarkItDown)
so the text content of PDFs/DOCX/XLSX etc. is available without re-parsing the
binary on every read. Images are skipped (no real OCR). See _convert_to_markdown_sibling().
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any, Optional

from .db import db_connection
from .notes import get_note
from .projects import get_project_by_id

_SIZE_WARN_BYTES = 10 * 1024 * 1024  # 10 MB

# MarkItDown only extracts EXIF metadata for images (no llm_client wired in),
# not real OCR text — a sibling .md would just be metadata noise. Claude reads
# images natively, so skipping them is strictly better.
_MARKDOWN_SKIP_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp",
    ".tiff", ".tif", ".svg", ".heic", ".md", ".markdown",
}

# Lazily instantiated on first real use — importing markitdown pulls in a heavy
# transitive chain (pandas, numpy, onnxruntime, ~215 MB) that would otherwise
# slow down every MCP server cold start, even sessions that never touch attachments.
# Typed as Any (not markitdown.MarkItDown) so mypy never has to resolve markitdown's
# own type stubs, which transitively pull in a numpy stub requiring Python 3.12+
# syntax — incompatible with this project's `python_version = "3.11"` mypy target.
_markitdown: Optional[Any] = None
_markitdown_load_attempted = False


def _get_markitdown() -> Optional[Any]:
    global _markitdown, _markitdown_load_attempted
    if _markitdown is not None or _markitdown_load_attempted:
        return _markitdown
    _markitdown_load_attempted = True
    try:
        from markitdown import MarkItDown

        _markitdown = MarkItDown()
    except Exception as exc:
        # Markdown-sibling generation is best-effort — a missing markitdown
        # install, or a broken native dependency (e.g. onnxruntime failing to
        # load its platform binary), must not disable attach_file/remove_attachment.
        print(f"[project-hub] WARNING: markitdown unavailable: {exc}", file=sys.stderr)
        _markitdown = None
    return _markitdown


def _convert_to_markdown_sibling(dest: Path) -> None:
    """Best-effort: write `dest.name + '.md'` next to a copied attachment.

    Never raises — conversion failures only warn to stderr and must never abort
    the attachment copy itself.
    """
    if dest.suffix.lower() in _MARKDOWN_SKIP_EXTENSIONS:
        return
    markitdown = _get_markitdown()
    if markitdown is None:
        return
    try:
        result = markitdown.convert(str(dest))
        markdown = result.markdown.strip()
        if markdown:
            dest.with_name(dest.name + ".md").write_text(markdown, encoding="utf-8")
    except Exception as exc:
        print(
            f"[project-hub] WARNING: Markdown conversion failed for {dest.name}: {exc}",
            file=sys.stderr,
        )


def _get_attachments_dir(note: dict) -> Path:
    project = get_project_by_id(note["project_id"])
    if not project or not project.get("docs_path"):
        raise ValueError(f"Project for note {note['id']} has no docs_path")
    return Path(project["docs_path"]) / "attachments"


def attach_file(
    note_id: int,
    file_path: str,
    *,
    home_override: Optional[Path] = None,
) -> dict:
    """Copy a local file to the note's attachments folder and store the reference.

    home_override: used in tests to simulate a different home directory for
    path-traversal checking.
    """
    note = get_note(note_id)
    if note is None:
        raise ValueError(f"Note not found: {note_id}")

    source = Path(file_path).resolve()
    if not source.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # .resolve() matters on Windows: home_override/Path.home() can be an 8.3
    # short path (e.g. RUNNER~1) that won't compare equal to the resolved
    # long-form `source` below even for genuinely identical directories.
    home = (home_override or Path.home()).resolve()
    try:
        source.relative_to(home)
    except ValueError:
        raise ValueError(f"Path traversal blocked: {file_path} is not under {home}")

    size = source.stat().st_size
    if size > _SIZE_WARN_BYTES:
        print(
            f"[project-hub] WARNING: Attachment {source.name} is {size / 1024 / 1024:.1f} MB (> 10 MB)",
            file=sys.stderr,
        )

    dest_dir = _get_attachments_dir(note)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / source.name
    shutil.copy2(source, dest)
    _convert_to_markdown_sibling(dest)

    attachment = {"name": source.name, "path": str(dest), "size": size}

    current = json.loads(note["attachments"])
    current.append(attachment)

    with db_connection() as conn:
        with conn:
            conn.execute(
                "UPDATE notes SET attachments = ? WHERE id = ?",
                (json.dumps(current), note_id),
            )

    return attachment


def list_attachments(note_id: int) -> list[dict]:
    """Return all attachments for a note."""
    note = get_note(note_id)
    if note is None:
        raise ValueError(f"Note not found: {note_id}")
    return json.loads(note["attachments"])


def remove_attachment(note_id: int, file_name: str) -> None:
    """Remove an attachment by file name. Deletes the file (and its markdown
    sibling, if one was generated) and updates the DB.
    """
    note = get_note(note_id)
    if note is None:
        raise ValueError(f"Note not found: {note_id}")

    current: list[dict] = json.loads(note["attachments"])
    match = next((a for a in current if a["name"] == file_name), None)
    if match is None:
        raise ValueError(f"Attachment not found: {file_name}")

    file_path = Path(match["path"])
    if file_path.exists():
        file_path.unlink()

    sibling = file_path.with_name(file_path.name + ".md")
    if sibling.exists():
        sibling.unlink()

    updated = [a for a in current if a["name"] != file_name]

    with db_connection() as conn:
        with conn:
            conn.execute(
                "UPDATE notes SET attachments = ? WHERE id = ?",
                (json.dumps(updated), note_id),
            )
