---
name: dashboard
description: |
  Show an overview of all CLIENT/HUB projects in the project-hub registry. Use ONLY for hub
  client/contact projects — NOT for code dashboards (mm-dev-toolkit), book dashboards
  (storyforge), or video dashboards (vidcraft).
  Use when: (1) User says "Hub-Dashboard", "Kunden-Dashboard", "alle Hub-Projekte",
  "Hub-Übersicht", (2) User explicitly invokes `/project-hub:dashboard`,
  (3) Context is clearly hub/client tracking.
  Do NOT trigger on bare "Dashboard" / "Übersicht" without hub/client context — defer.
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
