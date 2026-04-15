---
name: search
description: |
  Search across notes and contacts in the project hub.
  Use when: user wants to find something, says "suche", "finde", "search",
  "wo steht", "wer ist zuständig für", "gibt es eine Notiz über".
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<search query>"
---

# Search

Search notes and contacts across the active project (or all projects).

## Workflow

### 1. Get Search Query

If argument provided: use it as the search query.
If not: ask "Wonach suchst du?"

### 2. Determine Scope

Use MCP `tool_get_session()` to check for an active project.

- If active project → search within that project by default
- If no active project → search across all projects

If active project, ask briefly: "Nur in [Projektname] suchen oder in allen Projekten?"
Skip this question if the user's query already implies a scope (e.g. "in allen Projekten").

### 3. Run Search in Parallel

Run both searches simultaneously:
- MCP `tool_search_notes(query, project_id)`
- MCP `tool_search_contacts(query, project_id)`

### 4. Present Results

```
## Suchergebnisse für "[query]"

### Notizen ([N] Treffer)
| Projekt | Datum | Titel | Typ |
|---------|-------|-------|-----|
| [project_name] | [created_at] | [title] | [type] |

### Kontakte ([N] Treffer)
| Projekt | Name | Rolle | Firma | E-Mail |
|---------|------|-------|-------|--------|
| [project_name] | [name] | [role] | [company] | [email] |
```

If no results in a category → "Keine Notizen gefunden." / "Keine Kontakte gefunden."

If both categories empty:
```
Keine Ergebnisse für "[query]".
Tipp: Probiere einen kürzeren Begriff oder prüfe die Schreibweise.
```

### 5. Offer Follow-Up

After results, offer:
- "Note öffnen: `/summarize [id]`"
- "Projekt laden: `/resume [project-name]`"
- "Neue Suche mit anderem Begriff"
