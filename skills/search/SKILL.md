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

If a non-empty argument is provided (ignoring surrounding whitespace): use it as the search query.
If no argument was provided, or it was only whitespace: ask "Wonach suchst du?"

### 2. Determine Scope

Use MCP `tool_get_session()` to check for an active project. Use the `project_id` field from that
response for step 3 — **not** `id`. `id` is the session row's own primary key (the `session` table
is a single-row table, always `id = 1`); `project_id` is the actual active project. Picking `id` by
mistake silently searches whatever project happens to have id `1`.

- **No active project** (`project_id` is null/absent) → search across all projects (`project_id=0`).
  No scope question.
- **Active project** → ask *first*, before running any search: "Nur in [Projektname] suchen oder in
  allen Projekten?"
  - Skip this question only if the user's query already implies a scope (e.g. "in allen Projekten"
    → search all; an explicit "nur in diesem Projekt" already stated → scope to the active project).
  - If the user names a *different*, non-active project instead of answering yes/no (e.g. "nur in
    Acme"), resolve it via `tool_get_project("Acme")` (or `tool_list_projects` if ambiguous) and use
    that project's id — don't fall through to an all-projects search for an unrecognized answer.
  - The user's answer (or the implied scope) is what determines `project_id` for step 3 — the active
    project's `project_id` (from step 2's `tool_get_session()` call) if scoped, `0` if all projects,
    or a resolved third project's id. Do not search the active project by default before this
    question has been asked or answered/implied.
  - Note: even when scoped to one project, `tool_search_contacts` also returns contacts marked
    `is_shared` from other projects by design (the shared cross-project directory) — this is not a
    scoping bug. Note results, by contrast, are always strictly scoped to the given `project_id`.

### 3. Run Search in Parallel

Run both searches simultaneously:
- MCP `tool_search_notes(query, project_id)`
- MCP `tool_search_contacts(query, project_id)`

Both results include an `id` field even though step 4's table doesn't render it — keep track of each
result's `id` internally so a later request ("open the Kickoff note") or step 5's `/summarize`
follow-up can be resolved without re-searching.

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
- If there's at least one **note** result: "Note öffnen — sag mir einfach den Titel oder die
  Position aus der Liste." When the user does, resolve it yourself to that note's `id` from step 3's
  raw tool results and call `/summarize [id]` — never ask the user to type an id, and never print
  one (step 4's table doesn't show an id column either). This only applies to note results: notes
  and contacts come from independent, overlapping id sequences, so a contact's id must never be
  passed to `/summarize` (which loads a note by id and would silently return an unrelated note). If
  the user names a contact result instead, there's no separate "open" step — the results table
  already shows its full details (name, role, company, email).
- "Projekt laden: `/resume [project-name]`"
- "Neue Suche mit anderem Begriff"
