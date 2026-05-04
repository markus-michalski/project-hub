"""Project CRUD operations."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .config import get_docs_root
from .db import db_connection


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


def _row_to_dict(row) -> dict:
    return dict(row) if row else {}


def _ensure_docs_path(slug: str) -> str:
    docs_path = get_docs_root() / slug / "docs"
    docs_path.mkdir(parents=True, exist_ok=True)
    # Create standard subdirectories
    for sub in ["emails", "meeting-notes", "misc"]:
        (docs_path / sub).mkdir(exist_ok=True)
    return str(docs_path)


def list_projects(status: str = "") -> list[dict]:
    """List all projects, optionally filtered by status."""
    with db_connection() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC"
            ).fetchall()
        return [_row_to_dict(r) for r in rows]


def get_project(identifier: str) -> Optional[dict]:
    """Get a project by slug or name (case-insensitive)."""
    with db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM projects WHERE slug = ? OR LOWER(name) = LOWER(?)",
            (identifier, identifier),
        ).fetchone()
        return _row_to_dict(row) if row else None


def get_project_by_id(project_id: int) -> Optional[dict]:
    with db_connection() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return _row_to_dict(row) if row else None


def create_project(
    name: str,
    project_type: str = "generic",
    description: str = "",
    market: str = "",
    products: str = "",
    phase: str = "",
    go_live: str = "",
    budget: str = "",
    notes: str = "",
) -> dict:
    """Create a new project and its docs folder."""
    slug = _slugify(name)
    docs_path = _ensure_docs_path(slug)

    with db_connection() as conn:
        with conn:
            conn.execute(
                """INSERT INTO projects
                   (slug, name, type, description, market, products, phase, go_live, budget, notes, docs_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (slug, name, project_type, description, market, products, phase, go_live, budget, notes, docs_path),
            )
        row = conn.execute("SELECT * FROM projects WHERE slug = ?", (slug,)).fetchone()
        return _row_to_dict(row)


def update_project(identifier: str, **fields) -> Optional[dict]:
    """Update arbitrary fields on a project."""
    allowed = {
        "name", "type", "status", "description", "market",
        "products", "phase", "go_live", "budget", "notes",
    }
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return get_project(identifier)

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values())
    values.append(identifier)
    values.append(identifier)

    with db_connection() as conn:
        with conn:
            conn.execute(
                f"UPDATE projects SET {set_clause}, updated_at = datetime('now') "
                f"WHERE slug = ? OR LOWER(name) = LOWER(?)",
                values,
            )
        return get_project(identifier)


def list_docs(project_id: int) -> dict:
    """Return docs path and list of files for a project."""
    project = get_project_by_id(project_id)
    if not project:
        return {"error": "Project not found"}

    docs_path = Path(project["docs_path"])
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)

    result: dict = {"docs_path": str(docs_path), "files": {}}
    for sub in docs_path.iterdir():
        if sub.is_dir():
            result["files"][sub.name] = [f.name for f in sub.iterdir() if f.is_file()]
    return result
