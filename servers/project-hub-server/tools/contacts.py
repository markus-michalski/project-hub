"""Contact CRUD operations."""
from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Optional

from .db import db_connection

# Names that differ by less than this are treated as the same person unless force=True.
_NEAR_MATCH_THRESHOLD = 0.88

_UMLAUT_MAP = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
    "Ä": "ae", "Ö": "oe", "Ü": "ue",
})


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


def _normalize_name(name: str) -> str:
    """Fold a person name to a comparable form.

    Handles the variants that occur when the same person is entered from different
    sources: casing, "Lastname, Firstname" order (Teams profile format), hyphens vs.
    spaces, umlaut transliteration and accents.
    """
    n = name.strip()
    if n.count(",") == 1:
        last, first = (part.strip() for part in n.split(","))
        if last and first:
            n = f"{first} {last}"
    n = n.translate(_UMLAUT_MAP)
    # Umlauts are transliterated above, so NFKD here only strips remaining accents.
    n = unicodedata.normalize("NFKD", n)
    n = "".join(ch for ch in n if not unicodedata.combining(ch))
    n = re.sub(r"[^a-z0-9]+", " ", n.lower())
    return " ".join(n.split())


def _name_key(name: str) -> str:
    """Order-independent comparison key, so "Wulf Jan" matches "Jan Wulf"."""
    return " ".join(sorted(_normalize_name(name).split()))


def _find_duplicate_shared_contact(
    name: str, email: str = "", exclude_id: Optional[int] = None
) -> tuple[Optional[dict], str]:
    """Find a shared contact that is likely the same person as (name, email).

    Returns (contact, kind) where kind is:
      "exact" — same email, or same name once normalized (never a legitimate duplicate)
      "near"  — name similarity above threshold, e.g. "Mathias" vs. "Matthias"
      ""      — no match, contact is None

    Comparison happens in Python rather than SQL because normalization (name order,
    punctuation, umlauts) cannot be expressed in SQLite's LOWER(). The shared-contact
    set is small enough that fetching it is cheaper than the alternative.
    exclude_id: ignore this contact id (needed when re-saving an already-shared contact).
    """
    sql = """
        SELECT c.*, p.name as project_name
        FROM contacts c
        JOIN projects p ON p.id = c.project_id
        WHERE c.is_shared = 1
    """
    params: list = []
    if exclude_id is not None:
        sql += " AND c.id != ?"
        params.append(exclude_id)

    with db_connection() as conn:
        rows = [dict(r) for r in conn.execute(sql, params).fetchall()]

    key = _name_key(name)
    email_lower = email.strip().lower()
    near: Optional[dict] = None

    for row in rows:
        if email_lower and (row["email"] or "").strip().lower() == email_lower:
            return row, "exact"
        row_key = _name_key(row["name"])
        if not key or not row_key:
            continue
        if row_key == key:
            return row, "exact"
        if near is None and SequenceMatcher(None, key, row_key).ratio() >= _NEAR_MATCH_THRESHOLD:
            near = row  # keep scanning — an exact match anywhere still wins

    return (near, "near") if near else (None, "")


def _duplicate_message(existing: dict, kind: str) -> str:
    where = f"(id={existing['id']}, project='{existing['project_name']}')"
    if kind == "exact":
        return (
            f"A shared contact with this name or email already exists: "
            f"'{existing['name']}' {where}. "
            f"This contact is available in all projects — no need to add it again."
        )
    return (
        f"A shared contact with a very similar name already exists: "
        f"'{existing['name']}' {where}. "
        f"If this is the same person, update that contact instead of creating a new one. "
        f"If it is genuinely a different person, pass force=True."
    )


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
    force: bool = False,
) -> dict:
    """Add a contact to a project.

    is_shared: if True, the contact is available across all projects.
    Only internal contacts can be shared; external contacts are always project-specific.
    Raises ValueError if a shared contact with the same or a very similar name exists.
    force: allow creation despite a similar-name match. Exact matches are never forceable.
    """
    if is_shared and contact_type == "external":
        raise ValueError("External contacts cannot be shared across projects.")
    existing, kind = _find_duplicate_shared_contact(name, email)
    if existing and not (force and kind == "near"):
        raise ValueError(_duplicate_message(existing, kind))
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


def update_contact(contact_id: int, force: bool = False, **fields) -> Optional[dict]:
    """Update fields on an existing contact.

    Raises ValueError if trying to share an external contact.
    force: allow the update despite a similar-name match against an existing shared
    contact. Exact matches are never forceable.
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
        existing, kind = _find_duplicate_shared_contact(
            effective_name, effective_email, exclude_id=contact_id
        )
        if existing and not (force and kind == "near"):
            raise ValueError(_duplicate_message(existing, kind))

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
