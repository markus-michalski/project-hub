---
name: session-start
description: |
  Start a guided PROJECT-HUB session: checks setup, lets user pick an active client/hub
  project, then loads full context (contacts, notes, knowledge). Use ONLY for project-hub
  session initialization — NOT for code sessions (mm-dev-toolkit), book sessions (storyforge),
  or video sessions (vidcraft).
  Use when: (1) User says "Hub-Session starten", "Hub-Projekt laden", "starte Hub-Session",
  "welches Hub-Projekt soll ich laden", (2) User explicitly invokes `/project-hub:session-start`,
  (3) Context is clearly about starting a client/contact-tracking work session in project-hub.
  Do NOT trigger on bare "start" / "Session starten" — multiple plugins have session-start
  skills; defer if target plugin is unclear.
model: claude-sonnet-4-6
user-invocable: true
---

# Session Start

Guided session initialization: verify setup, pick a project, load full context.

## Workflow

### 1. Check Setup

```bash
test -d ~/.project-hub/venv && echo "venv: OK" || echo "venv: MISSING"
test -f ~/.project-hub/config.yaml && echo "config: OK" || echo "config: MISSING"
~/.project-hub/venv/bin/python3 -c "import mcp, fastmcp, yaml" 2>/dev/null && echo "deps: OK" || echo "deps: MISSING"
```

If anything is MISSING → tell user:
```
Setup unvollständig. Bitte `/project-hub:setup` ausführen und danach Claude Code neu starten.
```
**STOP** — do not continue.

### 2. Load Active Projects

Use MCP `tool_list_projects(status="active")`.

If no active projects exist → suggest:
```
Noch keine Projekte vorhanden. Starte mit `/project-hub:new-project` um dein erstes Projekt anzulegen.
```
**STOP**.

### 3. Pick Project

Use `AskUserQuestion` with the list of active project names plus "Neues Projekt anlegen".

If the user already passed a project name as an argument → skip this step and use it directly.

On "Neues Projekt anlegen" → hand off to `/project-hub:new-project` and STOP.

### 4. Load Full Context

Load all context in parallel:
- MCP `tool_get_project(identifier)` — full project details
- MCP `tool_list_contacts(project_id)` — all contacts
- MCP `tool_list_notes(project_id, limit=5)` — most recent 5 notes
- If `project_type` is NOT `generic`: MCP `tool_get_all_knowledge(project_type)` — domain knowledge

### 5. Set Session

Use MCP `tool_set_session(project_id, last_skill="session-start")`.

### 6. Output Session Header

```
## Hub-Session gestartet

**Projekt:** [Name]
**Typ:** [Typ Label]  |  **Status:** [Status]  |  **Phase:** [Phase]
**Go-Live:** [Datum oder "nicht gesetzt"]

### Beschreibung
[description]

### Kontakte ([N] intern / [M] extern)
[Intern: Name — Rolle]
[Extern: Name — Firma — Rolle]

### Letzte Aktivität (5 Notizen)
| Datum | Titel | Typ |
|-------|-------|-----|
| [Datum] | [Titel] | [Typ] |

### Knowledge geladen
[List: topic — title — oder "Keine Knowledge-Dokumente für diesen Projekttyp"]

---
Was soll ich tun?
```

#### Kontextuelle Hinweise

After the session header, add relevant suggestions based on the loaded data:

- No contacts → "Noch keine Kontakte. `/add-contact` zum Hinzufügen."
- No notes → "Noch keine Notizen. `/add-note` zum Starten."
- Open action items in recent notes → "Offene Action-Items vorhanden — `/next-step` für priorisierte Übersicht."
- Go-live within 14 days → "Go-Live in [N] Tagen — check ob alle Aufgaben erledigt sind."
- No activity in last 7 days → "Letztes Update vor [N] Tagen — alles aktuell?"
- No knowledge files for non-generic type → "Noch keine Knowledge-Dokumente. `/knowledge` zum Einrichten."
