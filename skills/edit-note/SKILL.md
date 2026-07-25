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
If it returns nothing (no note with that ID) → "Notiz [id] nicht gefunden." and stop — do not proceed to Step 3 with missing/undefined values.
`tool_get_note` is not scoped to a project — it will happily return a note that belongs to a different project than the one active in Step 1. Compare the loaded note's `project_id` against the active project's ID from `tool_get_session()`; on mismatch, stop with "Notiz [id] gehört nicht zum aktiven Projekt." rather than continuing to edit it.

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

### Agenda
[agenda]

### Anhänge
[Keine] oder:
- report.pdf (102 KB)
- contract.docx (45 KB)
```

Attachment sizes come back from `tool_list_attachments` in raw bytes — convert to a human-readable KB/MB figure for display, don't print the raw byte count.

If the note's type is `meeting-notes`, always show the Agenda section — with the agenda text if present, or `[Keine]` if it's empty — the user needs to see whether an agenda already exists before being asked about it in Step 4. Omit the section entirely for other types (they never have a meaningful agenda value).

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

**Type changes:** only accept an exact match to one of the five documented types (note | meeting-notes | email | decision | action-item). If the user names something else, don't forward it as-is — tell them it isn't a supported type and offer the real list to pick from.

**Agenda changes:** only apply if the note's type is (or is being changed to, in the same turn) `meeting-notes`. If the user asks to update the agenda on a note of a different type, point out the mismatch and ask whether they also want to change the type, rather than silently writing an agenda value onto a non-meeting-notes note.

`tool_update_note` only ever *sets* fields — it never clears one, even if you pass an empty string (the server drops falsy values before writing). Two consequences to handle explicitly:
- If the user asks to remove/clear the agenda (or title, or content), tell them that's not possible through this tool — the field can only be overwritten with different non-empty text, not blanked out.
- If the user changes the type *away from* `meeting-notes`, the old agenda text stays attached to the note (it is not cleared automatically). Mention this to the user; if they want it gone, they need to overwrite it with placeholder text (e.g. "-") since it can't be cleared outright.

### 5. Save Changes

**Text changes:** Use MCP `tool_update_note(note_id, title, content, note_type, agenda)`. Only pass fields that actually changed.

`tool_update_note` only writes to the database — unlike creating a note, it does **not** touch the Markdown file under `docs_path` that was written when the note was first added. After an edit, that file still has the old title/content, and if the type changed, it also sits in the wrong subfolder. Tell the user the update is DB-only and the on-disk copy (if one exists) is now stale — do not imply the doc file was refreshed.

**Add attachment:** Use MCP `tool_attach_file(note_id, file_path)`. Ask for absolute file path — must be under the user's home directory (path-traversal protection); if the call fails with a path-traversal error, explain that the file has to live under the home directory rather than surfacing the raw error.

**Remove attachment:** Use MCP `tool_remove_attachment(note_id, file_name)`. If the name doesn't match an existing attachment, the call fails — tell the user it wasn't found and show the real current attachment names so they can retry with the correct one.

### 6. Confirm

Before showing the confirmation, re-read the note with `tool_get_note(note_id)` rather than assuming the values you sent were applied as-is — this also catches the empty-value no-op case above (e.g. a requested agenda removal that silently didn't happen) so the confirmation reflects what's actually stored, not what was requested.

```
Notiz aktualisiert.

**Titel:** [new title]
**Typ:** [type]
**Anhänge:** [names] oder "Keine"

[updated content preview — first 3 lines]

Tipp: `/summarize [note-id]` erstellt ein strukturiertes Summary.
```
