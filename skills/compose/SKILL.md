---
name: compose
description: |
  Draft an email, Slack message, or Teams message based on project context or pasted input.
  Use when: user needs to write a communication, says "schreib eine E-Mail", "draft email",
  "Slack-Nachricht", "Teams-Nachricht", "Antwort auf diese E-Mail".
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<email|slack|teams>"
---

# Compose

Draft professional communications — emails, Slack messages, or Teams messages — using active project context.

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()` and load project context:
- MCP `tool_get_project_by_id(project_id)`
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]`

Project context ensures the right tone, correct names/roles, and relevant phase info.

### 2. Determine Channel

If argument provided: use it (email / slack / teams / export).
If not: ask — "Für welchen Kanal? E-Mail, Slack, Teams — oder Projekt für Kollegen exportieren?"

Options: email | slack | teams | **Projekt exportieren (für Kollegen)**

If user picks **Projekt exportieren**: jump to [Step 8 — Export Project](#8-export-project).

### 3. Collect Input

Ask for the communication goal. Accept multiple input formats:

- **Free description**: "Schreib eine Kickoff-E-Mail an den Merchant"
- **Pasted email to reply to**: "Antworte auf diese E-Mail: [paste]"
- **Pasted notes/info to communicate**: "Fasse das für ein Slack-Update zusammen: [paste]"
- **Specific request**: "Statusupdate für das Management über die UAT-Phase"

Ask clarifying questions only if necessary:
- Recipient (if not clear from context — use contact list)
- Tone adjustment needed? (default: professional but friendly)
- Any specific points to include / avoid?

### 4. Generate Communication

#### Email Format

```
**Betreff:** [Subject line]

---

[Salutation]

[Body — clear, concise, professional]

[Closing]

[Signature placeholder]
```

#### Slack / Teams Format

```
[Emoji if appropriate] **[Short topic headline]**

[Body — shorter than email, use bullet points, direct]

[Call to action or question if needed]
```

### 5. Tone Guidelines by Project Type

**merchant-onboarding:**
- External (merchant): professional, welcoming, clear — they are a partner, not a subordinate
- Internal: direct, concise, action-oriented
- Escalations: factual, non-emotional, solution-focused

**consulting:**
- Client-facing: formal to semi-formal, value-oriented
- Internal: direct and efficient

**event:**
- Vendor: clear, specific, confirm details
- Attendees: friendly, informative, clear call to action

**it-project / marketing / generic:**
- Internal: direct and to the point
- External: professional and clear

### 6. Offer Refinement

After drafting, ask:
- "Soll ich den Ton anpassen?"
- "Willst du etwas hinzufügen oder weglassen?"
- "Soll ich eine Version auf Englisch erstellen?"

### 7. Offer to Save Reference

"Möchtest du diese Kommunikation als Notiz im Projekt speichern?"
If yes → MCP `tool_add_note(project_id, title, content, note_type="email")`.

### 8. Export Project

Export the active project as a JSON file to share with a colleague.

**Workflow:**

1. Confirm the active project: show name + ID
2. Ask for optional destination path:
   "Ziel-Pfad (optional, Enter für Standard `~/.project-hub/exports/{slug}-{date}.json`):"
3. Call MCP `tool_export_project(project_id, output_path)` (output_path = "" for default)
4. Show result:

```
## Projekt exportiert

**Projekt:** [project name]
**Datei:** [path]
**Kontakte:** [n]
**Notizen:** [n]

Anhänge sind in Phase 1 NICHT enthalten.

Schicke die Datei an den Kollegen — er kann sie mit `/project-hub:compose` → "Projekt importieren"
oder direkt via `tool_import_project` einlesen.
```

5. Offer to also export the import instructions:
   "Soll ich auch eine kurze Anleitung zum Import mitschicken?"
   If yes, show:
   ```
   ## Import-Anleitung für [project name]

   1. Datei [filename] auf deinen Rechner kopieren
   2. Claude Code öffnen
   3. Skill starten: `/project-hub:compose`
   4. Option wählen: "Projekt importieren"
   5. Pfad zur Datei angeben
   6. Merge-Strategie wählen (skip / rename / overwrite)
   ```

## Context Usage

- Use contact names from the project when addressing people
- Reference current phase in status communications
- For replies: analyze the original email's tone and match appropriately
- For merchant-onboarding: always clarify internal vs. external communication — they require different styles
