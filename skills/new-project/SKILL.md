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
Supports both interactive input and pre-filled templates (pasted or from file).

## Workflow

### 0. Check for Template

Ask the user if they have a pre-filled template:

Use `AskUserQuestion`:
- **Vorlage einpasten** — Ich habe eine ausgefüllte Vorlage zum Einpastenn
- **Datei-Pfad angeben** — Vorlage als .md-Datei gespeichert
- **Interaktiv anlegen** — Felder jetzt eingeben

#### Branch A: Vorlage einpasten
Ask the user to paste the template content.
Then: `tool_create_project_from_template(template_content=<pasted_content>)`.
Skip to step 5 on success.

#### Branch B: Datei-Pfad
Ask for the absolute file path.
Then: `tool_create_project_from_template(file_path=<path>)`.
Skip to step 5 on success.

For both template branches: if result contains `"error"` → show error, offer to fix or fall back to interactive.

#### Branch C: Interaktiv → continue with steps 1–4 below.

---

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
Do NOT ask for all fields at once — ask ONE field per message, wait for the user's reply, then
ask the next. Never list several remaining fields together in a single message.

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

If `project_type` is `consulting` and a client name was collected in step 3: after the project is
created, call `tool_add_contact(project_id=<new project's id>, name=<client name>,
contact_type="external")` to actually store the client as an external contact (this is what step 3's
"store as external contact after creation" means — the field must be persisted via `tool_add_contact`,
not just collected).

### 5. Set Active Session

Use MCP `tool_set_session(identifier, last_skill="new-project")`.

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

- Name already exists → Show existing project, ask if user wants to use it or create a new one with
  different name. Note: `tool_create_project` signals this as a raised tool-execution error mentioning
  a `UNIQUE constraint` on the slug, not a returned `{"error": ...}` dict. This also applies when
  creating via `tool_create_project_from_template` with a duplicate name — that tool delegates to
  `tool_create_project` internally, so a duplicate slug raises the same error there too (the template
  tool only returns a `{"error": ...}` dict for its own validation failures, e.g. a bad file path or a
  missing `name` field). Recognize this raised-error failure shape in both branches and follow this
  flow; never show the raw technical error text to the user.
- Invalid project type → Show list again
