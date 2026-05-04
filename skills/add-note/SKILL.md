---
name: add-note
description: |
  Add a note, meeting minutes, email, or decision to the active project.
  Use when: user wants to log something, paste an email, add meeting notes,
  document a decision, or track an action item.
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<type: note|meeting-notes|email|decision|action-item>"
---

# Add Note

Log a note, meeting minutes, email, decision, or action item to the active project.

## Note Types

| Type | When to use |
|------|-------------|
| `note` | General notes, observations, reminders |
| `meeting-notes` | Meeting transcript or raw notes (pair with agenda for `/summarize`) |
| `email` | Paste an email or email thread for reference |
| `decision` | Document a decision made in the project |
| `action-item` | Track a specific action item with owner/deadline |

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()`.
If no active project → "Kein aktives Projekt. Bitte zuerst `/resume`."

### 2. Determine Type

If argument provided: use it as note type.
If not: ask the user which type fits, or infer from context.

### 3. Collect Content

Ask for:
- **Title** (short descriptor, e.g. "Kickoff Meeting 2026-04-13" or "Go-Live Decision")
- **Content** (the actual text — user can paste raw email, meeting notes, etc.)
- **Agenda** (optional, only for `meeting-notes`) — paste the original agenda if available, used by `/summarize` for comparison

### 4. Save Note

Use MCP `tool_add_note(project_id, title, content, note_type, agenda)`.

### 5. Optional: Attach Files

After saving, ask: "Möchtest du eine Datei anhängen?" (skip if user is clearly in a hurry)

If yes: ask for the absolute file path.
Use MCP `tool_attach_file(note_id, file_path)`.
Repeat until the user is done.

### 6. Output

```
## Notiz gespeichert

**Titel:** [Titel]
**Typ:** [Typ]
**Projekt:** [Projektname]

Notiz-ID: [id] (für späteres Abrufen)
[Anhänge: [name1], [name2]] (nur wenn Dateien angehängt wurden)

Tipp: `/summarize [note-id]` erstellt ein strukturiertes Summary dieser Notiz.
```

## Notes

- For `meeting-notes` with an agenda: remind the user they can run `/summarize` to get a structured summary with agenda comparison
- For `email`: the raw email can be used later with `/summarize` or `/compose` as reference
- Attachment paths must be absolute and within `~/` (path traversal protection)
