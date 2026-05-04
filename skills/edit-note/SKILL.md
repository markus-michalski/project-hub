---
name: edit-note
description: |
  Edit an existing note in the active project.
  Use when: user wants to correct, update, or extend a saved note,
  says "Notiz bearbeiten", "edit note", "korrigiere Notiz", "update note".
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<note-id>"
---

# Edit Note

Edit the title, content, or type of an existing note.

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()`.
If no active project → "Kein aktives Projekt. Bitte zuerst `/resume`."

### 2. Find Note

**If note ID provided as argument:**
Use MCP `tool_get_note(note_id)` to load the note directly.

**If no argument:**
Use MCP `tool_list_notes(project_id)` → iterate `result["items"]` and show a numbered list so the user can pick:

```
Welche Notiz möchtest du bearbeiten?

1. [Datum] — Kickoff Meeting (meeting-notes)
2. [Datum] — Go-Live Entscheidung (decision)
3. [Datum] — E-Mail von Max Müller (email)
```

If no notes exist → "Keine Notizen vorhanden. Nutze `/add-note` um eine zu erstellen."

### 3. Show Current Content

Use MCP `tool_list_attachments(note_id)` to load current attachments.

Display the note clearly:

```
## Notiz bearbeiten

**ID:** [id]
**Titel:** [title]
**Typ:** [type]
**Erstellt:** [created_at]

### Inhalt
[content]

### Anhänge
[Keine] oder:
- report.pdf (102 KB)
- contract.docx (45 KB)
```

### 4. Collect Changes

Ask: "Was möchtest du ändern?"

Options:
- Titel ändern
- Inhalt bearbeiten / ergänzen
- Typ ändern (note | meeting-notes | email | decision | action-item)
- Agenda aktualisieren (nur bei meeting-notes)
- Datei anhängen
- Anhang entfernen

Accept free-form responses — infer what the user wants to change.
If the user pastes new content, use it as the updated `content`.
If the user describes what to add/change, apply the edit intelligently.

### 5. Save Changes

**Text changes:** Use MCP `tool_update_note(note_id, title, content, note_type, agenda)`. Only pass fields that actually changed.

**Add attachment:** Use MCP `tool_attach_file(note_id, file_path)`. Ask for absolute file path.

**Remove attachment:** Use MCP `tool_remove_attachment(note_id, file_name)`.

### 6. Confirm

```
Notiz aktualisiert.

**Titel:** [new title]
**Typ:** [type]
**Anhänge:** [names] oder "Keine"

[updated content preview — first 3 lines]

Tipp: `/summarize [note-id]` erstellt ein strukturiertes Summary.
```
