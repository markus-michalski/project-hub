---
name: summarize
description: |
  Create a structured summary of an email, meeting notes, or any pasted content.
  Optionally compare meeting notes against an agenda.
  Use when: user pastes an email or meeting notes and wants a summary,
  says "fasse zusammen", "summarize", "Summary erstellen".
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<note-id|paste content directly>"
---

# Summarize

Create a structured summary of emails, meeting notes, or any content — in the context of the active project.

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()` to load project context. `tool_get_session()` **always returns a
dict**, even with no active project — the underlying session row always exists — so never treat
the dict's truthiness as "a project is active". Check the `project_id` field instead: `project_id`
being `null`/absent means no active project.

If `project_id` is set, also call `tool_list_contacts(project_id)` (and
`tool_list_shared_contacts()` for cross-project shared contacts) to actually load who the
stakeholders are, needed for the Context Usage section below — `tool_get_session()` does **not**
return contacts. Both tools return a paginated `{"items": [...], "total": N, "limit": L, "offset":
O}` shape (default `limit=50`), not a bare list — read `result["items"]` and, if `total` exceeds
`limit`, page through with `offset` so contacts past the first page aren't silently dropped.
Project context makes the summary smarter — it knows who the stakeholders are, what phase we're
in, etc.

**Before saying a contact is unknown**
([project-hub#122](https://github.com/markus-michalski/project-hub/issues/122))**:** even with
full pagination above, a name in the summarized content might genuinely not be in this
project's/shared contact set yet. Before concluding a mentioned name is unknown or offering to
add it as a new contact, call `tool_search_contacts(query=<most distinctive part of the name>,
project_id=0)` — it searches across all projects and shared contacts in one call, catching a
contact that exists but was created elsewhere. Unlike `tool_list_contacts`/
`tool_list_shared_contacts` above, this tool returns a **bare list**, not an `{"items": ...}`
dict — iterate the result directly.

If `project_id` is `null` (no active project) → still proceed, but explicitly tell the user in
your response that no project is loaded and context is limited (e.g. "Hinweis: Kein aktives
Projekt geladen, Kontext eingeschränkt."). Do not silently proceed as if nothing were missing.

### 2. Get Content to Summarize

**Option A — Note ID provided as argument:**
Use MCP `tool_get_note(note_id)` to load the saved note (content + agenda). If it returns `None`
(invalid or stale `note_id`), tell the user the note wasn't found and ask for a valid id, or for
the content to be pasted directly instead — do not summarize nothing or invent content.

**Option B — Direct input:**
The user pastes the content directly in the message.
Ask: "Gibt es eine Agenda zum Vergleich?" (only if content looks like meeting notes)

### 3. Determine Summary Type

Detect from content or note type:
- **Email** → Email summary format
- **Meeting notes** (with or without agenda) → Meeting summary format
- **Mixed / unknown** → General summary format

### 4. Generate Summary

#### Email Summary Format

```
## Email Summary

**Von:** [Sender if identifiable]
**Betreff/Thema:** [Subject/Topic]
**Datum:** [Date if available]

### Kernaussage (BLUF)
[1–2 sentences: the bottom line]

### Wichtige Punkte
- [Point 1]
- [Point 2]
- [...]

### Action Items
- [ ] [Action] — [Owner if mentioned] — [Deadline if mentioned]

### Entscheidungen
- [Decision if any]

### Nächste Schritte
[What needs to happen next]
```

#### Meeting Notes Summary Format

```
## Meeting Summary: [Title/Topic]

**Datum:** [Date if available]
**Teilnehmer:** [Participants if mentioned]
**Projekt:** [Active project name, if any]

### Kernaussagen
[2–3 bullet points: the most important outcomes]

### Besprochene Punkte
- [Topic 1]: [Summary]
- [Topic 2]: [Summary]

### Entscheidungen
- [Decision 1]
- [Decision 2]

### Action Items
| Aufgabe | Verantwortlich | Deadline |
|---------|----------------|----------|
| [Task] | [Owner] | [Date] |

### Agenda-Abgleich (only if agenda provided)
| Agendapunkt | Besprochen? | Ergebnis |
|-------------|-------------|---------|
| [Point 1] | ✅ Ja | [Result] |
| [Point 2] | ⚠️ Teilweise | [Notes] |
| [Point 3] | ❌ Nein | [Reason/carry forward] |

### Offene Punkte / Carry Forward
- [Item not addressed or requiring follow-up]
```

**If no agenda was provided or loaded:** omit the entire Agenda-Abgleich section, heading
included — do not leave it in with an empty or placeholder table. The section only belongs in the
output when an agenda actually exists to compare against.

#### General Summary Format

Use this when content doesn't clearly match Email or Meeting Notes (Step 3's "Mixed / unknown"
case) — e.g. a freeform note, status update, or fragment with no sender/subject header and no
participant list or decisions.

```
## Summary: [Short descriptive title]

**Datum:** [Date if available]
**Projekt:** [Active project name, if any]

### Kernpunkte
- [Point 1]
- [Point 2]

### Action Items (if any)
- [ ] [Action] — [Owner if mentioned] — [Deadline if mentioned]

### Sonstiges
[Anything else worth noting]
```

### 5. Offer to Save

**If `project_id` is `null`** (no active project, per Step 1): do not ask the save question at
all — saving is impossible without a real `project_id` for `tool_add_note`, and asking first only
to walk it back afterward is confusing. Tell the user directly instead, e.g. "Kein aktives Projekt
geladen, daher kann ich das nicht als Notiz speichern — lade zuerst ein Projekt mit
`/project-hub:resume`."

**If a project is active:** after generating the summary, ask:
"Möchtest du dieses Summary als Notiz im Projekt speichern?"

If yes:
- Derive `title` from the summary's own subject/topic line (the Betreff/Thema value for an Email
  Summary, the Title/Topic value for a Meeting Summary, the title for a General Summary) — do not
  ask the user a separate title question. Only ask the user directly for a title if the summary
  genuinely has nothing to draw from.
- Call MCP `tool_add_note(project_id, title, content=summary, note_type="note")`. Always pass the
  literal `note_type="note"` for this save — regardless of the summarized content's own type
  (Email/Meeting/General), this saved note records the *summary itself*, not a re-classification
  of the original content. Do not substitute a more specific type like `"meeting-notes"` or
  `"email"`: `note_type` also decides which docs subfolder the note file lands in (`misc/` for
  `"note"` vs. `meeting-notes/` / `emails/` for the others), what report label it gets ("Notiz" vs.
  "Meeting"/"E-Mail"), and whether `tool_list_notes(project_id, note_type=...)` filtering will find
  it — `"note"` here is a deliberate choice, not an oversight to "fix" later.

## Context Usage

Always incorporate project context into the summary where helpful:
- Reference contact names/roles when matching participants
- Note if action items align with current project phase
- Flag anything that seems like a risk or blocker given the current phase
