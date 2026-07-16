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

Detect platform and resolve a working interpreter first (same fallback chain
as `skills/setup/SKILL.md` Step 0 — see there for the full rationale,
especially the exit-code-49 Microsoft Store alias trap on managed Windows
devices):

```bash
python3 -c "import sys; print(sys.platform)"
python -c "import sys; print(sys.platform)"
py -3 -c "import sys; print(sys.platform)"
```

Use the first one that actually runs — don't stop at the first failure, a
`python`/`python3` exit code 49 with no output means the Store-alias stub, not
"Python missing". `win32` → Windows (venv Python at `venv\Scripts\python.exe`),
anything else → POSIX (`venv/bin/python3`).

The check below is multi-line — never pass multi-line content via `-c
"<script>"` (breaks under PowerShell). Save it to a file (e.g.
`~/.project-hub/_session_scratch.py`) using your own file-write capability,
then run it as a plain file argument via the venv's Python — POSIX:
`~/.project-hub/venv/bin/python3 <path>`, Windows:
`& "$env:USERPROFILE\.project-hub\venv\Scripts\python.exe" <path>`. Unlike
setup's Step 1, this doesn't need the OS-temp-dir fallback for a
not-yet-existing `~/.project-hub`: if that directory is missing, the venv
interpreter this step invokes is missing too, so the step fails and routes
to "Setup unvollständig" either way — the file-write location doesn't matter:

```python
from pathlib import Path
base = Path.home() / '.project-hub'
print('venv:', 'OK' if (base / 'venv').is_dir() else 'MISSING')
print('config:', 'OK' if (base / 'config.yaml').is_file() else 'MISSING')
try:
    import mcp, fastmcp, yaml
    print('deps: OK')
except ImportError:
    print('deps: MISSING')
```

If anything is MISSING → tell user:
```
Setup unvollständig. Bitte `/project-hub:setup` ausführen und danach Claude Code neu starten.
```
**STOP** — do not continue.

### 2. Load Active Projects

Use MCP `tool_list_projects(status="active")` → iterate `result["items"]`.

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
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]` — all contacts
- MCP `tool_list_notes(project_id, limit=5)` → iterate `result["items"]` — most recent 5 notes
- If `project_type` is NOT `generic`: MCP `tool_get_all_knowledge(project_type)` — domain knowledge

### 5. Set Session

Use MCP `tool_set_session(identifier, last_skill="session-start")`.

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
