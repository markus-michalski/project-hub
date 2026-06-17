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


def list_shared_contacts(limit: int = 50, offset: int = 0) -> dict:
    """List all shared contacts across all projects.

    Returns {"items": [...], "total": N, "limit": L, "offset": O}.
    Each item includes project_name and project_slug for context.
    """
    with db_connection() as conn:
        total: int = conn.execute(
            """SELECT COUNT(*) FROM contacts c
               JOIN projects p ON p.id = c.project_id
               WHERE c.is_shared = 1"""
        ).fetchone()[0]

        rows = conn.execute(
            """SELECT c.*, p.name as project_name, p.slug as project_slug
               FROM contacts c
               JOIN projects p ON p.id = c.project_id
               WHERE c.is_shared = 1
               ORDER BY c.type, c.name LIMIT ? OFFSET ?""",
            (limit, offset),
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
    is_shared: bool = False,
) -> dict:
    """Add a contact to a project.

    is_shared: if True, the contact is available across all projects.
    Only internal contacts can be shared; external contacts are always project-specific.
    """
    if is_shared and contact_type == "external":
        raise ValueError("External contacts cannot be shared across projects.")
    with db_connection() as conn:
        with conn:
            cursor = conn.execute(
                """INSERT INTO contacts (project_id, name, role, type, email, phone, company, notes, is_shared)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (project_id, name, role, contact_type, email, phone, company, notes, int(is_shared)),
            )
            contact_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        return dict(row)


def update_contact(contact_id: int, **fields) -> Optional[dict]:
    """Update fields on an existing contact.

    Raises ValueError if trying to share an external contact.
    """
    allowed = {"name", "role", "type", "email", "phone", "company", "notes", "is_shared"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}

    # Enforce: external contacts cannot be shared
    if updates.get("is_shared"):
        with db_connection() as conn:
            row = conn.execute("SELECT type FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        effective_type = updates.get("type") or (dict(row)["type"] if row else "internal")
        if effective_type == "external":
            raise ValueError("External contacts cannot be shared across projects.")

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
