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

Use MCP `tool_list_projects()` → iterate `result["items"]` to get all projects.
`tool_list_projects()` defaults to `limit=50`. If `result["total"]` is greater
than the number of items actually returned, fetch the remaining pages with
`offset` until all projects are loaded — never present a partial first page
as if it were the complete registry. The server sorts by `updated_at` with no
tiebreaker, so pages can overlap or gap when projects share the same
timestamp; after fetching, de-duplicate the merged list by `id` before
grouping. Once loaded (and de-duplicated), the footer's total count must
equal `result["total"]`.

### 2. Load Session

Use MCP `tool_get_session()` to identify the currently *active session*
project — i.e. `session["project_id"]`, which may be missing or `null`
(treat that the same as "no active project", don't error).

### 3. Output

Group projects by their own `status` field (active/paused/completed/
cancelled) — independently of session. `status` is a free-text DB column
with no fixed set of allowed values, so a project can carry a status
outside these four (e.g. `archiviert` set via `/project-hub:status`'s
German labels, or any other value written by `tool_update_project`). Put
any project whose `status` is not exactly `active`, `paused`, `completed`,
or `cancelled` into a fifth **Sonstige** section — never drop it silently,
and never fold it into one of the four known sections. Every loaded
project must land in exactly one of the five sections, so the five section
counts always sum to `[N] Projekte gesamt`.

Then mark whichever project's `id` equals `session["project_id"]` with
`← aktiv`, regardless of which status section it landed in. These are two
unrelated things that happen to share the word "aktiv": a project can be
the current session's active project while its own `status` is `paused` or
`completed` (e.g. you loaded it, then paused it) — it still gets `← aktiv`
in the Pausierte/Abgeschlossene/Abgebrochene/Sonstige section, it does not
move to the Aktive Projekte section.

Each project item from `tool_list_projects` includes a `links` list (see
`tool_link_project`), shaped as
`[{"relation": "successor" | "predecessor" | "related", "project": {"id", "slug", "name"}}, ...]`
— one entry per linked project, from THIS project's own point of view. Map
`relation` to a label using the linked project's `name`:
- `"successor"` → `Nachfolger von: [project.name]` (this project is the
  successor — it came *after* the linked one)
- `"predecessor"` → `Vorgänger von: [project.name]` (this project is the
  predecessor — it came *before* the linked one)
- `"related"` → `Verknüpft mit: [project.name]` (symmetric, no direction)

If `links` is non-empty, append one `↳ Relationen: [label]` line per entry
under the project's table row (one line per link, so a project with two
links gets two stacked lines). Omit the line entirely when `links` is
empty.

```
## Project Hub Dashboard

### Aktive Projekte
| Projekt | Typ | Phase | Go-Live | Letzte Aktivität |
|---------|-----|-------|---------|-----------------|
| [Name] ← aktiv | [Typ] | [Phase] | [Datum] | [updated_at] |
| [Name] | [Typ] | [Phase] | [Datum] | [updated_at] |
  ↳ Relationen: Nachfolger von: [verlinktes Projekt]
  ↳ Relationen: Verknüpft mit: [anderes verlinktes Projekt]

### Pausierte Projekte
[same table format or "Keine"]

### Abgeschlossene Projekte
[same table format or "Keine"]

### Abgebrochene Projekte
[same table format or "Keine"]

### Sonstige
[same table format or "Keine" — projects whose `status` is none of
active/paused/completed/cancelled]

---
**[N] Projekte gesamt** — Aktiv: [N] | Pausiert: [N] | Abgeschlossen: [N] | Abgebrochen: [N] | Sonstige: [N]

Tipp: `/resume [Projektname]` um ein Projekt zu laden
```

## Edge Cases

- No projects at all → "Noch keine Projekte. Starte mit `/new-project`."
- Single project → Show that project's details directly instead of the
  grouped table. Use the already-loaded `result["items"][0]` from step 1 —
  do not call `tool_get_project`/`tool_get_project_by_id`, no extra fetch is
  needed. Show: Name, Typ, Phase, Go-Live, Status, letzte Aktivität
  (`updated_at`), and Relationen (via `links`, same label mapping as above).
  Keep it to these fields — do not pull in contacts, notes, or docs; that is
  `/project-hub:resume`'s and `/project-hub:status`'s job, not this skill's.
  Suggest `/resume` so the user can formally load it into the session. Do
  NOT call `tool_set_session` here — this skill only reads session state
  (step 2), it never sets it; "load it automatically" means presenting its
  info without asking the user to pick from a list, not silently changing
  the active session.
