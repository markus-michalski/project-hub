"""Export and import projects for offline sharing / multi-user handoff.

Phase 1 scope: project record + contacts + notes (no attachment binaries).
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .db import db_connection

_EXPORT_VERSION = 1


def export_project(project_id: int, output_path: str = "") -> dict:
    """Export a project with all contacts and notes as a JSON file.

    project_id: numeric project ID (use tool_get_project to find it)
    output_path: destination file path; defaults to
                 ~/.project-hub/exports/{slug}-{date}.json

    Returns {"path": str, "project": str, "contacts": int, "notes": int}.
    Raises ValueError if project not found.
    """
    with db_connection() as conn:
        project_row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if not project_row:
            raise ValueError(f"Project {project_id} not found")

        project = dict(project_row)
        slug = project["slug"]

        contact_rows = conn.execute(
            "SELECT * FROM contacts WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()
        contacts = [dict(r) for r in contact_rows]

        note_rows = conn.execute(
            "SELECT * FROM notes WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()
        notes = [dict(r) for r in note_rows]

    payload = {
        "export_version": _EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "contacts": contacts,
        "notes": notes,
    }

    if not output_path:
        date_str = datetime.now().strftime("%Y%m%d")
        export_dir = Path.home() / ".project-hub" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        dest = export_dir / f"{slug}-{date_str}.json"
    else:
        dest = Path(output_path).expanduser()
        dest.parent.mkdir(parents=True, exist_ok=True)

    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"[project-hub] Exported project '{project['name']}' → {dest}",
        file=sys.stderr,
    )

    return {
        "path": str(dest),
        "project": project["name"],
        "contacts": len(contacts),
        "notes": len(notes),
    }


def import_project(json_path: str, merge_strategy: str = "skip") -> dict:
    """Import a project from a JSON export file.

    json_path: path to the .json file produced by export_project
    merge_strategy: what to do when a project with the same slug already exists
        - "skip"      — abort import, return {"imported": False, "reason": "exists"}
        - "rename"    — append _imported_{timestamp} suffix to slug/name and insert
        - "overwrite" — delete existing project (cascade) and re-insert

    Returns summary dict.
    Raises ValueError on invalid file format or unsupported version.
    """
    if merge_strategy not in ("skip", "rename", "overwrite"):
        raise ValueError(f"merge_strategy must be skip|rename|overwrite, got '{merge_strategy}'")

    src = Path(json_path).expanduser()
    if not src.exists():
        raise ValueError(f"File not found: {src}")

    raw = json.loads(src.read_text(encoding="utf-8"))

    if raw.get("export_version") != _EXPORT_VERSION:
        raise ValueError(
            f"Unsupported export_version {raw.get('export_version')!r} (expected {_EXPORT_VERSION})"
        )

    project = raw["project"]
    contacts: list[dict] = raw.get("contacts", [])
    notes: list[dict] = raw.get("notes", [])

    with db_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM projects WHERE slug = ?", (project["slug"],)
        ).fetchone()

        if existing:
            if merge_strategy == "skip":
                return {
                    "imported": False,
                    "reason": f"project with slug '{project['slug']}' already exists",
                    "project": project["name"],
                }
            elif merge_strategy == "overwrite":
                conn.execute("DELETE FROM projects WHERE slug = ?", (project["slug"],))
                conn.commit()
            elif merge_strategy == "rename":
                suffix = datetime.now().strftime("%Y%m%d%H%M%S")
                project["slug"] = f"{project['slug']}_imported_{suffix}"
                project["name"] = f"{project['name']} (imported {suffix})"

        # Strip the old primary key and docs_path — both will be reassigned
        project.pop("id", None)
        project.pop("docs_path", None)
        project["docs_path"] = ""

        cols = ", ".join(project.keys())
        placeholders = ", ".join("?" for _ in project)
        conn.execute(
            f"INSERT INTO projects ({cols}) VALUES ({placeholders})",
            list(project.values()),
        )
        conn.commit()

        new_project_id: int = conn.execute(
            "SELECT id FROM projects WHERE slug = ?", (project["slug"],)
        ).fetchone()[0]

        imported_contacts = 0
        for c in contacts:
            c.pop("id", None)
            c["project_id"] = new_project_id
            cols_c = ", ".join(c.keys())
            ph_c = ", ".join("?" for _ in c)
            conn.execute(f"INSERT INTO contacts ({cols_c}) VALUES ({ph_c})", list(c.values()))
            imported_contacts += 1

        imported_notes = 0
        for n in notes:
            n.pop("id", None)
            n["project_id"] = new_project_id
            cols_n = ", ".join(n.keys())
            ph_n = ", ".join("?" for _ in n)
            conn.execute(f"INSERT INTO notes ({cols_n}) VALUES ({ph_n})", list(n.values()))
            imported_notes += 1

        conn.commit()

    print(
        f"[project-hub] Imported project '{project['name']}' "
        f"({imported_contacts} contacts, {imported_notes} notes)",
        file=sys.stderr,
    )

    return {
        "imported": True,
        "project": project["name"],
        "slug": project["slug"],
        "project_id": new_project_id,
        "contacts": imported_contacts,
        "notes": imported_notes,
        "merge_strategy": merge_strategy,
    }
