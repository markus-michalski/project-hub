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


def _find_duplicate_shared_contact(
    name: str, email: str = "", exclude_id: Optional[int] = None
) -> Optional[dict]:
    """Return the first shared contact that matches name or email (case-insensitive).

    Used to prevent duplicate shared contacts before insert or promote operations.
    exclude_id: ignore this contact id (needed when re-saving an already-shared contact).
    """
    with db_connection() as conn:
        base = """
            SELECT c.*, p.name as project_name
            FROM contacts c
            JOIN projects p ON p.id = c.project_id
            WHERE c.is_shared = 1
        """
        conditions: list[str] = []
        params: list = []

        if exclude_id is not None:
            conditions.append("c.id != ?")
            params.append(exclude_id)

        name_cond = "LOWER(c.name) = LOWER(?)"
        if email:
            match_cond = f"({name_cond} OR LOWER(c.email) = LOWER(?))"
            match_params = [name, email]
        else:
            match_cond = name_cond
            match_params = [name]

        conditions.append(match_cond)
        params.extend(match_params)

        where = " AND ".join(conditions)
        row = conn.execute(f"{base} AND {where} LIMIT 1", params).fetchone()
        return dict(row) if row else None


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
    Raises ValueError if a shared contact with the same name or email already exists.
    """
    if is_shared and contact_type == "external":
        raise ValueError("External contacts cannot be shared across projects.")
    existing = _find_duplicate_shared_contact(name, email)
    if existing:
        raise ValueError(
            f"A shared contact with this name or email already exists: "
            f"'{existing['name']}' (id={existing['id']}, project='{existing['project_name']}'). "
            f"This contact is available in all projects — no need to add it again."
        )
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

    # Fetch current state once if needed for validation
    needs_current = updates.get("is_shared") or "name" in updates or "email" in updates
    current_dict: dict = {}
    if needs_current:
        with db_connection() as conn:
            row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        current_dict = dict(row) if row else {}

    if updates.get("is_shared"):
        effective_type = updates.get("type") or current_dict.get("type", "internal")
        if effective_type == "external":
            raise ValueError("External contacts cannot be shared across projects.")

    # Block if effective name/email would collide with any existing shared contact
    if "name" in updates or "email" in updates or updates.get("is_shared"):
        effective_name = updates.get("name") or current_dict.get("name", "")
        effective_email = updates.get("email") or current_dict.get("email", "")
        existing = _find_duplicate_shared_contact(effective_name, effective_email, exclude_id=contact_id)
        if existing:
            raise ValueError(
                f"A shared contact with this name or email already exists: "
                f"'{existing['name']}' (id={existing['id']}, project='{existing['project_name']}'). "
                f"This contact is available in all projects."
            )

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
