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
| "E-Mail schreiben" / "Slack-Nachricht" / "Teams-Nachricht" / "Draft email" / "compose" / `/project-hub:compose` | `/project-hub:compose` |
| "fasse zusammen" / "Summary erstellen" / "summarize" / "Meeting zusammenfassen" / `/project-hub:summarize` | `/project-hub:summarize` |
| "suche" / "finde" / "search" / "wo steht" / "wer ist zuständig für" / "gibt es eine Notiz" / `/project-hub:search` | `/project-hub:search` |
| "Governance aktualisieren" / "Prozess zeigen" / "Wissen laden" / "knowledge" / `/project-hub:knowledge` | `/project-hub:knowledge` |
| "Hub-Session starten" / "Hub-Projekt laden" / "welches Hub-Projekt soll ich laden" / "starte Hub-Session" / `/project-hub:session-start` | `/project-hub:session-start` |
| "Was steht an" / "What's next" / "nächster Schritt Hub" / "offene Aufgaben Hub" / "next step" / `/project-hub:next-step` | `/project-hub:next-step` |
| "Hub konfigurieren" / "Hub-Einstellungen" / "project-hub config" / "meinen Namen im Hub" / "Sprache im Hub" / `/project-hub:configure` | `/project-hub:configure` |
| "neuen Projekttyp anlegen" / "eigenen Typ erstellen" / "custom project type" / `/project-hub:type-creator` | `/project-hub:type-creator` |
| "Hub-Hilfe" / "project-hub help" / "welche Hub-Skills gibt es" / `/project-hub:help` | `/project-hub:help` |
| "project-hub einrichten" / "setup project-hub" / `/project-hub:setup` | `/project-hub:setup` |

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

## Session Pattern (`/resume`)

```
1. tool_get_session()                          → check active project
2. if no project: tool_list_projects("active") → ask user which to load
3. tool_get_project(identifier)                → load full project
4. tool_get_all_knowledge(project_type)        → load domain knowledge
5. tool_list_notes(project_id, limit=5)        → recent activity
6. Present project summary to user
```

On explicit project name (e.g. `/project-hub:resume Acme`):
- Skip step 2, go directly to `tool_get_project("Acme")`.
