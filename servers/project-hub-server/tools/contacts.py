"""Contact CRUD operations."""
from __future__ import annotations

from typing import Optional

from .db import db_connection


def list_contacts(
    project_id: int, contact_type: str = "", limit: int = 50, offset: int = 0
) -> dict:
    """List contacts for a project with pagination.

    Returns {"items": [...], "total": N, "limit": L, "offset": O}.
    """
    with db_connection() as conn:
        where = "WHERE project_id = ?"
        params: list = [project_id]
        if contact_type:
            where += " AND type = ?"
            params.append(contact_type)

        total: int = conn.execute(
            f"SELECT COUNT(*) FROM contacts {where}", params
        ).fetchone()[0]

        rows = conn.execute(
            f"SELECT * FROM contacts {where} ORDER BY type, name LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()
        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


def add_contact(
    project_id: int,
    name: str,
    role: str = "",
    contact_type: str = "internal",
    email: str = "",
    phone: str = "",
    company: str = "",
    notes: str = "",
) -> dict:
    """Add a contact to a project."""
    with db_connection() as conn:
        with conn:
            cursor = conn.execute(
                """INSERT INTO contacts (project_id, name, role, type, email, phone, company, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (project_id, name, role, contact_type, email, phone, company, notes),
            )
            contact_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return dict(row)


def update_contact(contact_id: int, **fields) -> Optional[dict]:
    """Update fields on an existing contact."""
    allowed = {"name", "role", "type", "email", "phone", "company", "notes"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        with db_connection() as conn:
            row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
            return dict(row) if row else None

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [contact_id]

    with db_connection() as conn:
        with conn:
            conn.execute(
                f"UPDATE contacts SET {set_clause} WHERE id = ?", values
            )
        row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return dict(row) if row else None


def delete_contact(contact_id: int) -> bool:
    with db_connection() as conn:
        with conn:
            result = conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        return result.rowcount > 0
