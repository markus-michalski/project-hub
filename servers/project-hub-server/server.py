"""Project Hub MCP Server.

Provides persistent project management: projects, contacts, notes, and session tracking.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from tools.db import init_db
from tools.projects import (
    list_projects,
    get_project,
    get_project_by_id,
    create_project,
    update_project,
    list_docs,
)
from tools.contacts import list_contacts, add_contact, update_contact, delete_contact
from tools.notes import list_notes, get_note, add_note, delete_note
from tools.session import get_session, set_session, clear_session

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
def tool_set_session(project_id: int, last_skill: str = "") -> dict:
    """Set the active project for this session."""
    return set_session(project_id, last_skill)


@mcp.tool()
def tool_clear_session() -> dict:
    """Clear the active project (no project selected)."""
    return clear_session()


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_list_projects(status: str = "") -> list[dict]:
    """List all projects. Optionally filter by status: active, paused, completed."""
    return list_projects(status)


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

    project_type: merchant-onboarding | it-project | marketing | consulting | event | generic
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
def tool_list_contacts(project_id: int, contact_type: str = "") -> list[dict]:
    """List contacts for a project. contact_type: internal | external (empty = all)."""
    return list_contacts(project_id, contact_type)


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
def tool_list_notes(project_id: int, note_type: str = "") -> list[dict]:
    """List notes for a project.

    note_type: note | meeting-notes | email | decision | action-item (empty = all)
    """
    return list_notes(project_id, note_type)


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
def tool_delete_note(note_id: int) -> bool:
    """Delete a note by ID."""
    return delete_note(note_id)
