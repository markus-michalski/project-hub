"""Session management — track the currently active project."""
from __future__ import annotations

from .db import get_connection


def get_session() -> dict:
    """Return current session state including active project details."""
    conn = get_connection()
    row = conn.execute("""
        SELECT s.id, s.project_id, s.last_skill, s.updated_at,
               p.name as project_name, p.type as project_type,
               p.status as project_status, p.phase as project_phase,
               p.description as project_description
        FROM session s
        LEFT JOIN projects p ON p.id = s.project_id
        WHERE s.id = 1
    """).fetchone()
    conn.close()
    return dict(row) if row else {}


def set_session(project_id: int, last_skill: str = "") -> dict:
    """Set the active project in the session."""
    conn = get_connection()
    with conn:
        conn.execute(
            """UPDATE session
               SET project_id = ?, last_skill = ?, updated_at = datetime('now')
               WHERE id = 1""",
            (project_id, last_skill),
        )
    return get_session()


def clear_session() -> dict:
    """Clear the active project from the session."""
    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE session SET project_id = NULL, last_skill = '', updated_at = datetime('now') WHERE id = 1"
        )
    return get_session()
