"""Contact CRUD operations."""
from __future__ import annotations

from typing import Optional

from .db import db_connection


def list_contacts(project_id: int, contact_type: str = "", limit: int = 0) -> list[dict]:
    """List contacts for a project, optionally filtered by type (internal/external).

    limit: max number of contacts to return (0 = all).
    """
    with db_connection() as conn:
        base = "SELECT * FROM contacts WHERE project_id = ?"
        params: list = [project_id]
        if contact_type:
            base += " AND type = ?"
            params.append(contact_type)
        base += " ORDER BY type, name"
        if limit > 0:
            base += " LIMIT ?"
            params.append(limit)
        rows = conn.execute(base, params).fetchall()
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
