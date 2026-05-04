"""File attachment operations for notes."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Optional

from .db import db_connection
from .notes import get_note
from .projects import get_project_by_id

_SIZE_WARN_BYTES = 10 * 1024 * 1024  # 10 MB


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

    home = home_override or Path.home()
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
    """Remove an attachment by file name. Deletes the file and updates the DB."""
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

    updated = [a for a in current if a["name"] != file_name]

    with db_connection() as conn:
        with conn:
            conn.execute(
                "UPDATE notes SET attachments = ? WHERE id = ?",
                (json.dumps(updated), note_id),
            )
