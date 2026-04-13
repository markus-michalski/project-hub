"""Notes CRUD operations."""
from __future__ import annotations

from typing import Optional

from .db import get_connection


def list_notes(project_id: int, note_type: str = "") -> list[dict]:
    """List notes for a project, optionally filtered by type."""
    conn = get_connection()
    if note_type:
        rows = conn.execute(
            "SELECT * FROM notes WHERE project_id = ? AND type = ? ORDER BY created_at DESC",
            (project_id, note_type),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM notes WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_note(note_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_note(
    project_id: int,
    title: str,
    content: str,
    note_type: str = "note",
    agenda: str = "",
) -> dict:
    """Add a note to a project.

    note_type options: note, meeting-notes, email, decision, action-item
    agenda: optional agenda text to compare against during meeting-notes summarization
    """
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            "INSERT INTO notes (project_id, title, type, content, agenda) VALUES (?, ?, ?, ?, ?)",
            (project_id, title, note_type, content, agenda),
        )
        note_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    return dict(row)


def delete_note(note_id: int) -> bool:
    conn = get_connection()
    with conn:
        result = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.close()
    return result.rowcount > 0
