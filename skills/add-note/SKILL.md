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
If not, and the user's invoking message already contains the content to log (e.g. they pasted
an email or meeting notes along with the command): infer the type directly from that content
when it is unambiguous, instead of asking:
- Clear email headers/quoting (`Von:`/`From:`/`Betreff:`/`Subject:`, or a forwarded-message
  marker) → infer `email`.
- An explicit attendee/Teilnehmer list **and** explicit meeting/agenda framing together → infer
  `meeting-notes`. A bare date or timestamp alone is not sufficient — most emails and decisions
  carry one too — so require both signals before inferring.
- Otherwise: ask which type fits.
If not, and no content has been pasted yet: ask the user which type fits now, then proceed to
Step 3 to collect the content.

### 3. Collect Content

Ask for:
- **Title** (short descriptor, e.g. "Kickoff Meeting 2026-04-13" or "Go-Live Decision")
- **Content** (the actual text — user can paste raw email, meeting notes, etc.)
- **Agenda** (optional, only for `meeting-notes`) — paste the original agenda if available, used by `/summarize` for comparison

**Mandatory: identify real source files.** If `content` came from, or references, one or more
real local files — the user gave a file path, named a folder ("hier liegen die Dokumente der
letzten Woche"), or handed over documents to read and summarize — collect every relevant absolute
file path now (list the folder first via `ls`/Glob if a directory was given). This is not an
optional follow-up question: skipping it has already caused real, unrecoverable data loss
(project-hub#134 — a referenced folder was deleted before its documents were ever preserved).
Content that is genuinely freeform/dictated text with no backing file has nothing to collect here.

### 4. Save Note (+ Preserve Originals)

Use MCP `tool_add_note(project_id, title, content, note_type, agenda, source_paths)` — pass every
absolute path collected in Step 3 as `source_paths` so the originals are copied into the project's
attachments folder in the same call, not as a separate step someone might forget. Omit
`source_paths` only when Step 3 found no real backing file.

If the result contains `attachment_failures`, surface each one to the user (e.g. "Diese Datei(en)
konnten nicht gesichert werden: [path] — [error]") instead of silently dropping it — note creation
still succeeded, but the original for that specific path was not preserved and the user needs to
know.

### 5. Optional: Attach Additional Files

After saving, ask: "Möchtest du eine weitere Datei anhängen?" (skip if user is clearly in a hurry)
— for files not already covered by Step 3/4.

If yes: ask for the file path(s). Each must be a fully expanded absolute path under the user's home
directory (e.g. `/home/<user>/Documents/spec.pdf`), not a relative path — neither `tool_attach_file`
nor `tool_attach_files` expand `~`, so a literal `~/Documents/spec.pdf` will fail with a misleading
"File not found" error instead of a path-traversal error. If the user gives a relative or
`~`-prefixed path, expand it yourself (or ask them for the full path) before calling the tool.
Use MCP `tool_attach_file(note_id, file_path)` for a single file, or
`tool_attach_files(note_id, file_paths)` for several at once — same partial-failure surfacing as
Step 4 applies (check `failed` in the result).
Repeat until the user is done.

### 6. Output

```
## Notiz gespeichert

**Titel:** [Titel]
**Typ:** [Typ]
**Projekt:** [Projektname]

Notiz-ID: [id] (für späteres Abrufen)
[Anhänge: [name1], [name2]] (nur wenn Dateien angehängt wurden)
[Nicht gesichert: [path1] ([error1]), ...] (nur wenn attachment_failures/failed vorhanden)

Tipp: `/summarize [note-id]` erstellt ein strukturiertes Summary dieser Notiz[, bei `meeting-notes`
mit Agenda direkt im Abgleich gegen die Agenda].
```

## Notes

- For `meeting-notes` with an agenda: remind the user they can run `/summarize` to get a structured summary with agenda comparison
- For `email`: the raw email can be used later with `/summarize` or `/compose` as reference
- Attachment paths must be fully expanded absolute paths under the user's home directory (path
  traversal protection) — `~` is not expanded by `tool_attach_file`/`tool_attach_files`, expand it
  before passing the path in. Hidden/dotfile paths (anything under a `.`-prefixed folder, e.g.
  `~/.ssh/`, `~/.config/`) are refused too, as a precaution against sweeping up credentials —
  don't conflate this with the path-traversal error; it's a different, narrower block on a path
  that IS under the home directory.
- Preserving originals (`source_paths` on `tool_add_note`, or `tool_attach_file(s)`) is mandatory
  whenever real files are involved — never treat it as skippable just because the user didn't
  explicitly ask to "attach" something (project-hub#134)
