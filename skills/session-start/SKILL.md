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
    import mcp, jinja2, yaml
    from mcp.server.mcpserver import MCPServer  # noqa: F401 — detects a stale mcp 1.x venv (project-hub#123): `mcp` itself imports under both 1.x and 2.x, this submodule only exists from 2.x on
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

If the user already passed a non-empty project name as an argument (ignoring surrounding
whitespace) when invoking this skill: skip the active-project listing below and the picker in
Step 3 — there is nothing to list or pick from when the target project is already known. Go
straight to `tool_get_project(<argument>)`:
- If it resolves → continue at Step 4 with that project.
- If it returns nothing (no match) → tell the user the given project name wasn't found. The
  argument only matches an exact slug or exact case-insensitive name, so a near-miss (e.g.
  "Acme" for "Acme GmbH") also lands here even though a matching project exists — don't assume
  not-found means "doesn't exist". Fall through to MCP `tool_list_projects()` (no status filter,
  so paused/completed/archived projects the user may have meant are included too) → iterate
  `result["items"]` and let them pick from that instead of the flow silently continuing with no
  project.

Otherwise (no argument given, or it was only whitespace): use MCP
`tool_list_projects(status="active")` → iterate `result["items"]`.

If no active projects exist (and this is the no-argument path, not the not-found fallback
above) → suggest:
```
Noch keine Projekte vorhanden. Starte mit `/project-hub:new-project` um dein erstes Projekt anzulegen.
```
**STOP**.

### 3. Pick Project

Use `AskUserQuestion` with the list of project names from whichever call populated it in Step 2
(the active-only list on the no-argument path, or the unfiltered not-found-fallback list) plus
"Neues Projekt anlegen".

On "Neues Projekt anlegen" → hand off to `/project-hub:new-project` and STOP.

### 4. Load Full Context

If the project was resolved via Step 2's argument branch, reuse that `tool_get_project` result
— no need to call it a second time. If it was resolved via Step 3's picker instead, call MCP
`tool_get_project(identifier)` here to get the full project object (`id`, `type`, description,
...).

Load the rest in parallel:
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]` — all contacts
- MCP `tool_list_notes(project_id, limit=5)` → iterate `result["items"]` — most recent 5 notes
- If the project object's `type` field (from the project object resolved above, either reused
  from Step 2 or freshly fetched here) is NOT `generic`: MCP
  `tool_get_all_knowledge(project_type=<that type value>)` — domain knowledge (note: there is no
  `project_type` key on the project object itself; `project_type` is only the tool's parameter
  name). For a `generic`-type project, this call is skipped entirely — see Step 6's output
  template for what to show in that case.

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
[List: topic — title — oder "Keine Knowledge-Dokumente für diesen Projekttyp" (non-generic type,
`tool_get_all_knowledge` ran and returned nothing) — oder "Knowledge-Laden für `generic`-Projekte
wird standardmäßig übersprungen — `/knowledge` zeigt installierte Dokumente" (generic type, see
below)]

---
Was soll ich tun?
```

For a `generic`-type project, Step 4 never calls `tool_get_all_knowledge` at all — this is a
pre-existing convention shared with `/resume` and CLAUDE.md's Session Pattern, not something this
skill decides. It does **not** mean `generic` projects have no knowledge base: the plugin ships
`knowledge/generic/charter.md` as a template, `sync_knowledge_templates()` installs it into
`~/.project-hub/knowledge/generic/` like any other type, and `tool_get_all_knowledge("generic")`
works normally server-side — there is no special-casing there. The skip is purely a session-start
convention. Since the call never runs, this skill has no data on whether generic knowledge files
exist, so the "Knowledge geladen" line must NOT claim "Keine Knowledge-Dokumente" (that asserts a
fact this skill never checked) — use the skipped-load wording above instead, and point to
`/knowledge` so the user can see what's actually installed.

#### Kontextuelle Hinweise

After the session header, add relevant suggestions based on the loaded data:

- No contacts → "Noch keine Kontakte. `/add-contact` zum Hinzufügen."
- No notes → "Noch keine Notizen. `/add-note` zum Starten."
- Open action items in recent notes → "Offene Action-Items vorhanden — `/next-step` für priorisierte Übersicht."
- Go-live within 14 days → "Go-Live in [N] Tagen — check ob alle Aufgaben erledigt sind."
- No activity in last 7 days → "Letztes Update vor [N] Tagen — alles aktuell?"
- No knowledge files for non-generic type (i.e. `tool_get_all_knowledge` ran and returned
  nothing) → "Noch keine Knowledge-Dokumente. `/knowledge` zum Einrichten."
- `generic`-type project (knowledge loading was skipped in Step 4, so this skill has no data on
  whether files exist — see the note above the Kontextuelle-Hinweise heading) →
  "Nutze `/knowledge`, um zu sehen, welche Knowledge-Dokumente für dieses Projekt bereits
  installiert sind."
