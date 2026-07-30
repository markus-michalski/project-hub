# Project Hub — Claude Plugin

## Overview

Project Hub is a Claude Code plugin for tracking client projects, contacts, notes, meetings,
and decisions. It replaces scattered notes and email threads with a structured, searchable
project registry — not a code repo manager, not a book/video project manager.

## Configuration

- Config: `~/.project-hub/config.yaml`
- Database: `~/.project-hub/project-hub.db`
- Knowledge (user): `~/.project-hub/knowledge/<project-type>/`
- Venv: `~/.project-hub/venv/`
- Project docs: `{docs_root}/<project-slug>/docs/`, `docs_root` defaults to
  `~/Documents/project-hub` and is configurable via `config.yaml` — distinct
  from the fixed `~/.project-hub/` infra directory above
- `{plugin_root}` = directory containing this CLAUDE.md

## MCP Server

Server name: `project-hub-mcp`

Use MCP tools for ALL state operations (projects, contacts, notes, session).
Never read the SQLite file directly — always go through MCP tools.

## Skill Routing

| User Intent | Skill |
|------------|-------|
| "Neues Hub-Projekt" / "Hub-Projekt anlegen" / "Kunden-Projekt anlegen" / "neuer Client" / `/project-hub:new-project` | `/project-hub:new-project` |
| "Hub-Projekt {name}" / "Lade Hub-Projekt {name}" / "Wechsle zu {name}" / `/project-hub:resume` | `/project-hub:resume [name]` |
| "Hub-Dashboard" / "Kunden-Dashboard" / "alle Hub-Projekte" / "Hub-Übersicht" / `/project-hub:dashboard` | `/project-hub:dashboard` |
| "Hub-Status" / "Status des Hub-Projekts" / "Phase ändern" / `/project-hub:status` | `/project-hub:status` |
| "Kontakt hinzufügen" / "Person anlegen" / "Stakeholder eintragen" / "add contact" / `/project-hub:add-contact` | `/project-hub:add-contact` |
| "Notiz hinzufügen" / "Meeting-Protokoll" / "E-Mail einfügen" / "Entscheidung dokumentieren" / "add note" / `/project-hub:add-note` | `/project-hub:add-note` |
| "Notiz bearbeiten" / "edit note" / "korrigiere Notiz" / "update note" / `/project-hub:edit-note` | `/project-hub:edit-note` |
| "E-Mail schreiben" / "Slack-Nachricht" / "Teams-Nachricht" / "Draft email" / "compose" / "Projekt exportieren" / "Projekt importieren" / `/project-hub:compose` | `/project-hub:compose` |
| "fasse zusammen" / "Summary erstellen" / "summarize" / "Meeting zusammenfassen" / `/project-hub:summarize` | `/project-hub:summarize` |
| "suche" / "finde" / "search" / "wo steht" / "wer ist zuständig für" / "gibt es eine Notiz" / `/project-hub:search` | `/project-hub:search` |
| "Governance aktualisieren" / "Prozess zeigen" / "Wissen laden" / "knowledge" / `/project-hub:knowledge` | `/project-hub:knowledge` |
| "Hub-Session starten" / "Hub-Projekt laden" / "welches Hub-Projekt soll ich laden" / "starte Hub-Session" / `/project-hub:session-start` | `/project-hub:session-start` |
| "Was steht an" / "What's next" / "nächster Schritt Hub" / "offene Aufgaben Hub" / "next step" / `/project-hub:next-step` | `/project-hub:next-step` |
| "Hub konfigurieren" / "Hub-Einstellungen" / "project-hub config" / "meinen Namen im Hub" / "Sprache im Hub" / `/project-hub:configure` | `/project-hub:configure` |
| "neuen Projekttyp anlegen" / "eigenen Typ erstellen" / "custom project type" / `/project-hub:type-creator` | `/project-hub:type-creator` |
| "Hub-Hilfe" / "project-hub help" / "welche Hub-Skills gibt es" / `/project-hub:help` | `/project-hub:help` |
| "project-hub einrichten" / "setup project-hub" / `/project-hub:setup` | `/project-hub:setup` |
| "Report erstellen" / "HTML-Report" / "Bericht exportieren" / "Projektbericht" / "all-projects report" / `/project-hub:report` | `/project-hub:report [full\|summary\|all-projects]` |
| "Vorlage holen" / "Projektvorlage" / "Template für neues Projekt" / "gib mir die Vorlage" / "welche Felder brauche ich" / `/project-hub:get-template` | `/project-hub:get-template [type]` |

`create-testdata` / `reset-testdata` / `delete-testdata` are intentionally **not** in this table —
they are machine-invoked sandbox infrastructure for skill-rollout's live-tier testing
(project-hub#82), never triggered from conversation (`disable-model-invocation: true`). See the
Anti-Patterns section below.

## Anti-Patterns

- **NEVER** activate `/project-hub:dashboard` on bare "Dashboard" / "Übersicht" — mm-dev-toolkit,
  storyforge, and vidcraft have their own dashboard skills. Only trigger with explicit hub/client
  context or `/project-hub:dashboard`.
- **NEVER** activate `/project-hub:new-project` on bare "Projekt anlegen" when the user is
  talking about a code repo, book, or video project — defer to the appropriate plugin.
- **NEVER** activate `/project-hub:resume` on bare "weitermachen" / "resume" without a confirmed
  hub project context. Verify via `tool_list_projects` if uncertain.
- **NEVER** activate `/project-hub:session-start` on bare "start" / "starten" — multiple plugins
  have session-start skills; only trigger with explicit hub context or direct invocation.
- **NEVER** activate `/project-hub:next-step` on bare "Was soll ich tun" / "next" without hub/
  client context — mm-dev-toolkit and other plugins have their own next-step skills.
- **NEVER** activate `/project-hub:configure` on bare "konfigurieren" / "Einstellungen" without
  explicit project-hub context — defer to the appropriate plugin.
- **NEVER** activate `/project-hub:help` on bare "Hilfe" / "Help" — only on explicit hub context
  or direct invocation.
- **NEVER** activate `/project-hub:setup` on bare "setup" / "einrichten" — only when target is
  explicitly project-hub.
- **NEVER** modify the database directly — all state changes go through MCP tools.
- **NEVER** confuse hub projects (client/contact tracking) with dev projects (mm-dev-toolkit),
  books (storyforge), or videos (vidcraft).
- **NEVER** treat `/project-hub:create-testdata`, `/project-hub:reset-testdata`, or
  `/project-hub:delete-testdata` as conversational skills — they exist solely for
  skill-rollout's live-tier sandbox testing (project-hub#82), gated by
  `disable-model-invocation: true`, and operate only on the fixed `zz-sandbox-`-prefixed
  fixture set. Never invoke them on a bare "Testdaten anlegen"/"reset" without that explicit
  automation context, and never let them touch anything outside the `zz-sandbox-` prefix.

## Session Pattern (`/resume`)

```
1. Find project
   - With argument: tool_get_project(identifier) — response is wrapped, `None` means not
     found; unwrap with `project = response["result"]` (see "Response wrapping" under
     "MCP Tool API Notes" below)
   - Without argument: tool_list_projects()  ← no status filter; returns all statuses;
     NOT wrapped (see "Response wrapping" below) — read `response["items"]` directly
     Show numbered list, ask user to pick.
     The returned rows already have full project data — no second fetch needed.

2. Load context in parallel (use the unwrapped project object from step 1 directly, do NOT re-fetch):
   - tool_list_contacts(project_id)       → project-specific contacts
   - tool_list_shared_contacts()          → shared contacts (cross-project); page to completion
     via offset if total > limit — see skills/resume/SKILL.md Step 2 for the full loading rules
     and the project-hub#122 "search before declaring a contact unknown" safety net
   - tool_list_notes(project_id)          → all notes (default limit=50; check total for overflow)
   - tool_get_all_knowledge(project_type=<type>) → only when project["type"] != "generic"

3. Set session: tool_set_session(identifier, last_skill="resume")

4. Present project summary to user
```

On explicit project name (e.g. `/project-hub:resume Acme`):
- Go directly to `tool_get_project("Acme")`, skip the list step.

## MCP Tool API Notes

**Response wrapping — unwrap before indexing:**

MCPServer wraps a tool's return value in `{"result": ...}` whenever its Python return annotation is
anything other than a plain `dict` — that covers `list[dict]`, `dict | None`, and `bool` alike. A
bare `dict` return type is passed through as-is (it's already a valid top-level JSON object, so
MCPServer doesn't add another envelope). The rule tracks the *annotation*, not the runtime shape, so
it can silently change if a signature changes — when in doubt, check the `-> ...` annotation on
the tool's `def` in `server.py` rather than assume from a past call.

Examples: `tool_get_project(identifier)` is declared `-> dict | None`, so its result is
`response["result"]` (itself `{...}` or `None`) — **not** the top-level `response`. By contrast
`tool_list_projects(...)` is declared `-> dict` (`{"items": [...], "total": N, ...}`), so it is
**not** wrapped — read `response["items"]` directly, never `response["result"]["items"]`.

**`type` vs `project_type`/`contact_type`/`note_type` asymmetry:**

Read-back (GET/LIST responses) uses the bare field name `type`:
```json
{"id": 1, "type": "generic", ...}           ← project
{"id": 1, "type": "internal", ...}          ← contact
{"id": 1, "type": "note", ...}              ← note
```

Create/filter parameters use the verbose form:
```
tool_create_project(project_type=...)
tool_list_projects(project_type=...)
tool_list_contacts(contact_type=...)
tool_list_notes(note_type=...)
tool_get_all_knowledge(project_type=...)
```

When reading a project object and branching on its type (e.g. for knowledge loading), first
unwrap the tool response per "Response wrapping" above, then use `project["type"]` — **not**
`project["project_type"]` (that key does not exist) and **not** the raw, still-wrapped
`tool_get_project(...)` return value.
Pass the value to tools as their `project_type` parameter.
