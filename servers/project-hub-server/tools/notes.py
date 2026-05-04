"""Notes CRUD operations."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .db import db_connection


def list_notes(project_id: int, note_type: str = "", limit: int = 50, offset: int = 0) -> dict:
    """List notes for a project with pagination.

    Returns {"items": [...], "total": N, "limit": L, "offset": O}, newest first.
    """
    with db_connection() as conn:
        where = "WHERE project_id = ?"
        params: list = [project_id]
        if note_type:
            where += " AND type = ?"
            params.append(note_type)

        total: int = conn.execute(
            f"SELECT COUNT(*) FROM notes {where}", params
        ).fetchone()[0]

        rows = conn.execute(
            f"SELECT * FROM notes {where} ORDER BY updated_at DESC, created_at DESC, id DESC"
            f" LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()
        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


def get_note(note_id: int) -> Optional[dict]:
    with db_connection() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
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
    with db_connection() as conn:
        with conn:
            cursor = conn.execute(
                "INSERT INTO notes (project_id, title, type, content, agenda) VALUES (?, ?, ?, ?, ?)",
                (project_id, title, note_type, content, agenda),
            )
            note_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row)


def update_note(
    note_id: int,
    title: str = "",
    content: str = "",
    note_type: str = "",
    agenda: str = "",
) -> Optional[dict]:
    """Update an existing note. Only non-empty values are updated."""
    allowed = {"title": title, "type": note_type, "content": content, "agenda": agenda}
    updates = {k: v for k, v in allowed.items() if v}
    if not updates:
        return get_note(note_id)

    updates["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [note_id]

    with db_connection() as conn:
        with conn:
            conn.execute(f"UPDATE notes SET {set_clause} WHERE id = ?", values)
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row) if row else None


def delete_note(note_id: int) -> bool:
    with db_connection() as conn:
        with conn:
            result = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return result.rowcount > 0
