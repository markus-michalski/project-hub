---
name: dashboard
description: |
  Show an overview of all projects with their status and key info.
  Use when: user wants a project overview, says "dashboard", "alle Projekte", "Übersicht".
model: claude-sonnet-4-6
user-invocable: true
---

# Dashboard

Show an overview of all projects.

## Workflow

### 1. Load Projects

Use MCP `tool_list_projects()` to get all projects.

### 2. Load Session

Use MCP `tool_get_session()` to identify the currently active project.

### 3. Output

Group projects by status. Mark the active project with `← aktiv`.

```
## Project Hub Dashboard

### Aktive Projekte
| Projekt | Typ | Phase | Go-Live | Letzte Aktivität |
|---------|-----|-------|---------|-----------------|
| [Name] ← aktiv | [Typ] | [Phase] | [Datum] | [updated_at] |
| [Name] | [Typ] | [Phase] | [Datum] | [updated_at] |

### Pausierte Projekte
[same table format or "Keine"]

### Abgeschlossene Projekte
[same table format or "Keine"]

---
**[N] Projekte gesamt** — Aktiv: [N] | Pausiert: [N] | Abgeschlossen: [N]

Tipp: `/resume [Projektname]` um ein Projekt zu laden
```

## Edge Cases

- No projects at all → "Noch keine Projekte. Starte mit `/new-project`."
- Single project → Load it automatically and suggest `/resume`
