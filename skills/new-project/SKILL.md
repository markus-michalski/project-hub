---
name: new-project
description: |
  Create a new project in the project hub.
  Use when: user wants to start a new project, says "neues Projekt", "create project", "Projekt anlegen".
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<project-name>"
---

# New Project

Create a new project with all relevant metadata.

## Workflow

### 1. Determine Project Name

If argument provided: use it as the project name.
If not: ask the user for a project name.

### 2. Select Project Type

Show available types and ask user to choose:
- `merchant-onboarding` — Merchant Onboarding (BNPL, Direct Debit, ...)
- `it-project` — IT / Software Project
- `marketing` — Marketing Campaign
- `consulting` — Consulting Engagement
- `event` — Event Planning
- `generic` — General Purpose

### 3. Collect Project Details

Based on project type, ask for relevant fields interactively.
Do NOT ask for all fields at once — ask in a natural, conversational way.

**Always ask:**
- Description (what is this project about?)
- Target completion / go-live date (optional)

**merchant-onboarding additionally:**
- Market/country (DE, NL, SE, ...)
- Products (BNPL 30d, Pay in 3, Direct Debit, ...)
- Current phase (default: Discovery)

**consulting additionally:**
- Client name (store as external contact after creation)

**event additionally:**
- Event date (= go_live)
- Location (= market field)

### 4. Create Project

Use MCP `tool_create_project()` with collected data.

### 5. Set Active Session

Use MCP `tool_set_session(project_id, last_skill="new-project")`.

### 6. Output

```
## Projekt angelegt

**Name:** [Name]
**Typ:** [Typ]
**Status:** Aktiv
**Phase:** [Phase]
**Go-Live:** [Datum oder "nicht gesetzt"]
**Docs-Ordner:** [docs_path]

Das Projekt ist jetzt aktiv. Was möchtest du als nächstes tun?
- `/add-contact` — Kontakte hinzufügen
- `/add-note` — Erste Notiz anlegen
- `/status` — Projektstatus anzeigen
```

## Error Handling

- Name already exists → Show existing project, ask if user wants to use it or create a new one with different name
- Invalid project type → Show list again
