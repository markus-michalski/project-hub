"""Project Hub MCP Server.

Provides persistent project management: projects, contacts, notes, and session tracking.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from tools.contacts import add_contact, delete_contact, list_contacts, update_contact
from tools.db import init_db
from tools.knowledge import (
    delete_knowledge,
    get_all_knowledge,
    get_knowledge,
    list_knowledge,
    save_knowledge,
    sync_knowledge_templates,
)
from tools.notes import add_note, delete_note, get_note, list_notes, update_note
from tools.projects import (
    create_project,
    get_project,
    get_project_by_id,
    list_docs,
    list_projects,
    update_project,
)
from tools.project_types import (
    create_project_type,
    delete_project_type,
    get_project_type,
    list_project_types,
)
from tools.search import search_contacts, search_notes
from tools.session import clear_session, get_session, set_session

# Initialize DB on startup
init_db()

mcp = FastMCP("project-hub-mcp")


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_get_session() -> dict:
    """Get current session — which project is active, last used skill."""
    return get_session()


@mcp.tool()
def tool_set_session(identifier: str, last_skill: str = "") -> dict:
    """Set the active project for this session by slug or name."""
    return set_session(identifier, last_skill)


@mcp.tool()
def tool_clear_session() -> dict:
    """Clear the active project (no project selected)."""
    return clear_session()


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_list_projects(status: str = "", limit: int = 50, offset: int = 0) -> dict:
    """List projects with pagination.

    status: active | paused | completed (empty = all)
    Returns {"items": [...], "total": N, "limit": L, "offset": O}.
    """
    return list_projects(status, limit, offset)


@mcp.tool()
def tool_get_project(identifier: str) -> dict | None:
    """Get a project by slug or name."""
    return get_project(identifier)


@mcp.tool()
def tool_get_project_by_id(project_id: int) -> dict | None:
    """Get a project by its numeric ID."""
    return get_project_by_id(project_id)


@mcp.tool()
def tool_create_project(
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
    """Create a new project and its docs folder structure.

    project_type: any built-in or custom type name (use tool_list_project_types to discover available types)
    market: relevant market/country (e.g. DE, NL, SE — mainly for merchant-onboarding)
    products: integrated products (e.g. BNPL 30d, Pay in 3 — mainly for merchant-onboarding)
    phase: current project phase
    go_live: target go-live date
    budget: budget information
    """
    return create_project(name, project_type, description, market, products, phase, go_live, budget, notes)


@mcp.tool()
def tool_update_project(
    identifier: str,
    name: str = "",
    project_type: str = "",
    status: str = "",
    description: str = "",
    market: str = "",
    products: str = "",
    phase: str = "",
    go_live: str = "",
    budget: str = "",
    notes: str = "",
) -> dict | None:
    """Update project fields. Only non-empty values are updated.

    status options: active | paused | completed | cancelled
    """
    fields = {
        k: v for k, v in {
            "name": name, "type": project_type, "status": status,
            "description": description, "market": market, "products": products,
            "phase": phase, "go_live": go_live, "budget": budget, "notes": notes,
        }.items() if v
    }
    return update_project(identifier, **fields)


@mcp.tool()
def tool_list_docs(project_id: int) -> dict:
    """List all documents in a project's docs folder."""
    return list_docs(project_id)


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_list_contacts(
    project_id: int, contact_type: str = "", limit: int = 50, offset: int = 0
) -> dict:
    """List contacts for a project with pagination.

    contact_type: internal | external (empty = all)
    Returns {"items": [...], "total": N, "limit": L, "offset": O}.
    """
    return list_contacts(project_id, contact_type, limit, offset)


@mcp.tool()
def tool_add_contact(
    project_id: int,
    name: str,
    role: str = "",
    contact_type: str = "internal",
    email: str = "",
    phone: str = "",
    company: str = "",
    notes: str = "",
) -> dict:
    """Add a contact to a project.

    contact_type: internal (own company) | external (merchant, client, partner, vendor)
    role examples: Onboarding PM, Tech Lead, Account Manager, Legal, Merchant PM, etc.
    """
    return add_contact(project_id, name, role, contact_type, email, phone, company, notes)


@mcp.tool()
def tool_update_contact(
    contact_id: int,
    name: str = "",
    role: str = "",
    contact_type: str = "",
    email: str = "",
    phone: str = "",
    company: str = "",
    notes: str = "",
) -> dict | None:
    """Update an existing contact."""
    fields = {k: v for k, v in {
        "name": name, "role": role, "type": contact_type,
        "email": email, "phone": phone, "company": company, "notes": notes,
    }.items() if v}
    return update_contact(contact_id, **fields)


@mcp.tool()
def tool_delete_contact(contact_id: int) -> bool:
    """Delete a contact by ID."""
    return delete_contact(contact_id)


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_list_notes(
    project_id: int, note_type: str = "", limit: int = 50, offset: int = 0
) -> dict:
    """List notes for a project with pagination.

    note_type: note | meeting-notes | email | decision | action-item (empty = all)
    Returns {"items": [...], "total": N, "limit": L, "offset": O}, newest first.
    """
    return list_notes(project_id, note_type, limit, offset)


@mcp.tool()
def tool_get_note(note_id: int) -> dict | None:
    """Get a specific note by ID."""
    return get_note(note_id)


@mcp.tool()
def tool_add_note(
    project_id: int,
    title: str,
    content: str,
    note_type: str = "note",
    agenda: str = "",
) -> dict:
    """Add a note to a project.

    note_type: note | meeting-notes | email | decision | action-item
    agenda: optional agenda to compare against (used by /summarize for meeting-notes)
    content: the raw text (email body, meeting transcript, free-form notes, etc.)
    """
    return add_note(project_id, title, content, note_type, agenda)


@mcp.tool()
def tool_update_note(
    note_id: int,
    title: str = "",
    content: str = "",
    note_type: str = "",
    agenda: str = "",
) -> dict | None:
    """Update an existing note. Only non-empty values are changed.

    note_type: note | meeting-notes | email | decision | action-item
    """
    return update_note(note_id, title, content, note_type, agenda)


@mcp.tool()
def tool_delete_note(note_id: int) -> bool:
    """Delete a note by ID."""
    return delete_note(note_id)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_search_notes(query: str, project_id: int = 0) -> list[dict]:
    """Search notes by title or content (case-insensitive).

    project_id: limit to a specific project (0 = search all projects).
    Returns matches ordered newest first, including project_name for cross-project results.
    """
    return search_notes(query, project_id)


@mcp.tool()
def tool_search_contacts(query: str, project_id: int = 0) -> list[dict]:
    """Search contacts by name, role, email, or company (case-insensitive).

    project_id: limit to a specific project (0 = search all projects).
    Returns matches ordered by name, including project_name for cross-project results.
    """
    return search_contacts(query, project_id)


# ---------------------------------------------------------------------------
# Knowledge
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_list_knowledge(project_type: str) -> list[dict]:
    """List all knowledge topics available for a given project type.

    Returns topic name, title (from H1), file path, and size.
    project_type examples: merchant-onboarding, it-project, generic
    """
    return list_knowledge(project_type)


@mcp.tool()
def tool_get_knowledge(project_type: str, topic: str) -> dict | None:
    """Read a knowledge file by project type and topic name.

    Returns full content as Markdown string plus metadata.
    Returns None if not found.
    """
    return get_knowledge(project_type, topic)


@mcp.tool()
def tool_get_all_knowledge(project_type: str) -> list[dict]:
    """Load ALL knowledge files for a project type in one call.

    Used by /resume to auto-load governance, process, and role knowledge
    when switching to a merchant-onboarding project.
    """
    return get_all_knowledge(project_type)


@mcp.tool()
def tool_save_knowledge(project_type: str, topic: str, content: str) -> dict:
    """Write or overwrite a knowledge file.

    content: full Markdown content (start with # Title)
    topic: filename without extension (e.g. 'governance', 'process', 'roles')
    Returns the saved knowledge entry with metadata.
    """
    return save_knowledge(project_type, topic, content)


@mcp.tool()
def tool_delete_knowledge(project_type: str, topic: str) -> bool:
    """Delete a knowledge file. Returns True if deleted, False if not found."""
    return delete_knowledge(project_type, topic)


# ---------------------------------------------------------------------------
# Project Types
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_list_project_types() -> list[dict]:
    """List all available project types: built-in and user-defined custom types.

    Each entry includes: name, label, description, source (built-in | custom), path.
    Custom types override built-ins when names collide.
    """
    return list_project_types()


@mcp.tool()
def tool_get_project_type(type_name: str) -> dict | None:
    """Get project type details by name.

    Checks user-defined types in ~/.project-hub/project-types/ first,
    then falls back to built-in types shipped with the plugin.
    Returns readme content plus metadata, or None if not found.
    """
    return get_project_type(type_name)


@mcp.tool()
def tool_create_project_type(
    name: str,
    description: str = "",
    phases: list[str] | None = None,
    contacts: list[str] | None = None,
) -> dict:
    """Create a custom project type scaffold in ~/.project-hub/project-types/{name}/.

    name: display name (will be slugified, e.g. "HR Onboarding" → "hr-onboarding")
    description: one-line description of this project type
    phases: optional list of standard phase names
    contacts: optional list of typical contact roles
    Returns error dict if the type already exists.
    """
    return create_project_type(name, description, phases, contacts)


@mcp.tool()
def tool_delete_project_type(type_name: str) -> dict:
    """Delete a custom project type.

    Built-in types shipped with the plugin cannot be deleted.
    Returns {"deleted": True, "name": ...} on success or {"error": ...} on failure.
    """
    return delete_project_type(type_name)


@mcp.tool()
def tool_sync_knowledge_templates(force: bool = False) -> dict:
    """Compare bundled plugin templates with the user's installed knowledge files.

    Reports new files and files where the plugin ships a different version.
    Set force=True to copy all new/changed templates to ~/.project-hub/knowledge/.
    User confirmation should be obtained before calling with force=True.

    Returns: {items: [{path, status, plugin_bytes, local_bytes?}], synced: [path, ...]}
    status values: "up-to-date" | "newer-version-available" | "new"
    """
    return sync_knowledge_templates(force=force)
