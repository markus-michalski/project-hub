"""Knowledge management — read/write/list knowledge files per project type.

Knowledge files live at ~/.project-hub/knowledge/<project-type>/<topic>.md
They are Markdown files the user maintains locally and Claude reads at session start.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .config import get_knowledge_root


def _knowledge_dir(project_type: str) -> Path:
    d = get_knowledge_root() / project_type
    d.mkdir(parents=True, exist_ok=True)
    return d


def list_knowledge(project_type: str) -> list[dict]:
    """List all knowledge topics available for a project type."""
    d = _knowledge_dir(project_type)
    files = sorted(d.glob("*.md"))
    result = []
    for f in files:
        # Extract first H1 as title, fall back to filename stem
        content = f.read_text(encoding="utf-8")
        title = f.stem
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        result.append({
            "topic": f.stem,
            "title": title,
            "path": str(f),
            "size_bytes": f.stat().st_size,
        })
    return result


def get_knowledge(project_type: str, topic: str) -> Optional[dict]:
    """Read a knowledge file. Returns None if not found."""
    d = _knowledge_dir(project_type)
    f = d / f"{topic}.md"
    if not f.exists():
        return None
    content = f.read_text(encoding="utf-8")
    title = topic
    for line in content.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return {
        "topic": topic,
        "title": title,
        "path": str(f),
        "content": content,
    }


def save_knowledge(project_type: str, topic: str, content: str) -> dict:
    """Write or overwrite a knowledge file."""
    d = _knowledge_dir(project_type)
    f = d / f"{topic}.md"
    f.write_text(content, encoding="utf-8")
    return get_knowledge(project_type, topic)


def delete_knowledge(project_type: str, topic: str) -> bool:
    """Delete a knowledge file. Returns True if deleted, False if not found."""
    d = _knowledge_dir(project_type)
    f = d / f"{topic}.md"
    if f.exists():
        f.unlink()
        return True
    return False


def get_all_knowledge(project_type: str) -> list[dict]:
    """Load full content of all knowledge files for a project type (used on resume)."""
    items = list_knowledge(project_type)
    result = []
    for item in items:
        full = get_knowledge(project_type, item["topic"])
        if full:
            result.append(full)
    return result
