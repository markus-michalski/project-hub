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

Call MCP `tool_list_project_types()` and show the returned types (built-in + any custom ones) for
the user to choose from — do NOT hardcode a static list, custom types created via
`/project-hub:type-creator` must show up here too. Typical built-in types:
- `merchant-onboarding` — Merchant Onboarding (BNPL, Direct Debit, ...)
- `it-project` — IT / Software Project
- `marketing` — Marketing Campaign
- `consulting` — Consulting Engagement
- `event` — Event Planning
- `generic` — General Purpose

Any additional `custom` rows returned by `tool_list_project_types()` are user-defined types — list
them alongside the built-ins.

Exception: if this step's answer was already pre-supplied by the caller (e.g. type-creator's Step 8
handoff names the type just created) — use that type directly and skip the question.

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

Use MCP `tool_create_project()` with collected data. If the result contains an `error` key, follow
the "Name already exists" flow under Error Handling instead of continuing below.

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

- Name already exists → `tool_create_project` (and `tool_create_project_from_template`, which
  delegates to it) returns `{"error": "A project with slug '<slug>' already exists (existing
  project: '<name>')"}` — check the result for an `error` key before proceeding. Show the named
  existing project and ask if the user wants to use it or create a new one with a different name.
- Invalid project type → Show list again
