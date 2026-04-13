"""Project CRUD operations."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .db import get_connection, get_data_dir


def _slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


def _row_to_dict(row) -> dict:
    return dict(row) if row else {}


def _ensure_docs_path(slug: str) -> str:
    docs_path = get_data_dir() / "projects" / slug / "docs"
    docs_path.mkdir(parents=True, exist_ok=True)
    # Create standard subdirectories
    for sub in ["emails", "meeting-notes", "misc"]:
        (docs_path / sub).mkdir(exist_ok=True)
    return str(docs_path)


def list_projects(status: str = "") -> list[dict]:
    """List all projects, optionally filtered by status."""
    conn = get_connection()
    if status:
        rows = conn.execute(
            "SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC", (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC"
        ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_project(identifier: str) -> Optional[dict]:
    """Get a project by slug or name (case-insensitive)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM projects WHERE slug = ? OR LOWER(name) = LOWER(?)",
        (identifier, identifier),
    ).fetchone()
    conn.close()
    return _row_to_dict(row) if row else None


def get_project_by_id(project_id: int) -> Optional[dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    conn.close()
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

    conn = get_connection()
    with conn:
        conn.execute(
            """INSERT INTO projects
               (slug, name, type, description, market, products, phase, go_live, budget, notes, docs_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (slug, name, project_type, description, market, products, phase, go_live, budget, notes, docs_path),
        )
    row = conn.execute("SELECT * FROM projects WHERE slug = ?", (slug,)).fetchone()
    conn.close()
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

    updates["updated_at"] = "datetime('now')"
    set_clause = ", ".join(
        f"{k} = datetime('now')" if k == "updated_at" else f"{k} = ?"
        for k in updates
    )
    values = [v for k, v in updates.items() if k != "updated_at"]
    values.append(identifier)
    values.append(identifier)

    conn = get_connection()
    with conn:
        conn.execute(
            f"UPDATE projects SET {set_clause}, updated_at = datetime('now') "
            f"WHERE slug = ? OR LOWER(name) = LOWER(?)",
            values,
        )
    project = get_project(identifier)
    conn.close()
    return project


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
