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

Use MCP `tool_get_session()` to load project context (name, type, phase, contacts).
Project context makes the summary smarter — it knows who the stakeholders are, what phase we're in, etc.

If no active project → still proceed, but note that context is limited.

### 2. Get Content to Summarize

**Option A — Note ID provided as argument:**
Use MCP `tool_get_note(note_id)` to load the saved note (content + agenda).

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
**Projekt:** [Active project name]

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

### 5. Offer to Save

After generating the summary, ask:
"Möchtest du dieses Summary als Notiz im Projekt speichern?"
If yes → use MCP `tool_add_note(project_id, title, content=summary, note_type="note")`.

## Context Usage

Always incorporate project context into the summary where helpful:
- Reference contact names/roles when matching participants
- Note if action items align with current project phase
- Flag anything that seems like a risk or blocker given the current phase
