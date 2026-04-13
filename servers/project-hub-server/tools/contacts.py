"""Contact CRUD operations."""
from __future__ import annotations

from typing import Optional

from .db import get_connection


def list_contacts(project_id: int, contact_type: str = "") -> list[dict]:
    """List contacts for a project, optionally filtered by type (internal/external)."""
    conn = get_connection()
    if contact_type:
        rows = conn.execute(
            "SELECT * FROM contacts WHERE project_id = ? AND type = ? ORDER BY type, name",
            (project_id, contact_type),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM contacts WHERE project_id = ? ORDER BY type, name",
            (project_id,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


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
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """INSERT INTO contacts (project_id, name, role, type, email, phone, company, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, name, role, contact_type, email, phone, company, notes),
        )
        contact_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    conn.close()
    return dict(row)


def update_contact(contact_id: int, **fields) -> Optional[dict]:
    """Update fields on an existing contact."""
    allowed = {"name", "role", "type", "email", "phone", "company", "notes"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        conn = get_connection()
        row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [contact_id]

    conn = get_connection()
    with conn:
        conn.execute(
            f"UPDATE contacts SET {set_clause} WHERE id = ?", values
        )
    row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_contact(contact_id: int) -> bool:
    conn = get_connection()
    with conn:
        result = conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.close()
    return result.rowcount > 0
