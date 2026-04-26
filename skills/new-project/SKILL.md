---
name: new-project
description: |
  Create a new CLIENT/HUB project in the project-hub registry (for tracking contacts, notes,
  meetings, decisions, deliverables). Use ONLY for client-facing or hub-tracked projects —
  NOT for code/dev projects (use mm-dev-toolkit), book projects (use storyforge), or video
  projects (use vidcraft).
  Use when: (1) User says "Hub-Projekt anlegen", "Kunden-Projekt anlegen", "Projekt im Hub anlegen",
  "neuer Client im Hub", (2) User explicitly invokes `/project-hub:new-project`,
  (3) Context is clearly a client/contact-tracking project (CRM-like, not a code repo or creative work).
  Do NOT trigger on bare "neues Projekt" / "Projekt anlegen" without hub/client context — defer.
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
