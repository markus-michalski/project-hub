---
name: next-step
description: |
  Show what's next for the active CLIENT/HUB project: overdue action items, upcoming
  milestones, stale notes, and suggested next communication. Use ONLY for hub-tracked
  client projects — NOT for code projects (mm-dev-toolkit), book chapters (storyforge),
  or video production (vidcraft).
  Use when: (1) User says "Was steht an", "Was kommt als nächstes", "nächster Schritt im Hub",
  "What's next", "next step", "offene Aufgaben Hub", (2) User explicitly invokes
  `/project-hub:next-step`, (3) An active hub project is loaded and user asks about priorities.
  Do NOT trigger on bare "Was muss ich tun" / "What should I do" without hub context — defer.
model: claude-sonnet-4-6
user-invocable: true
---

# Next Step

Analyze the active hub project and output a prioritized action list.

## Workflow

### 1. Check Active Session

Use MCP `tool_get_session()`.

If no active project → output:
```
Kein aktives Hub-Projekt geladen.

Bitte zuerst ein Projekt laden:
- `/project-hub:resume [Name]` — bestehendes Projekt laden
- `/project-hub:session-start` — geführte Projektauswahl
```
**STOP**.

### 2. Load Project Context

Load in parallel:
- MCP `tool_get_project_by_id(project_id)` — full project details (phase, go-live, status)
- MCP `tool_list_notes(project_id, limit=20)` → iterate `result["items"]` — recent notes to scan for action items
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]` — contacts for communication suggestions

### 3. Analyze

From the loaded data, identify:

**A) Overdue / Open Action Items**
- Notes with `type = "action-item"` that have no completion marker
- Sort by date: oldest first (most overdue at top)

**B) Upcoming Milestones**
- Go-live date: if within 30 days, flag it
- Current phase: flag if it seems stale (no notes in last 14 days with phase progress)

**C) Stale Notes**
- Notes with no update in >7 days that contain open questions or decisions pending

**D) Communication Gaps**
- External contacts with no recent note mentioning them (>14 days)
- Suggest a follow-up if appropriate

**E) Missing Data**
- No contacts → suggest `/add-contact`
- No recent notes → suggest `/add-note meeting-notes`
- No go-live date set → suggest setting it via `/status`

### 4. Output

```
## Was steht an? — [Projektname]

**Phase:** [Phase]  |  **Go-Live:** [Datum oder "nicht gesetzt"]  |  **Status:** [Status]

---

### Offene Action-Items ([N])
| Priorität | Aufgabe | Seit |
|-----------|---------|------|
| HOCH      | [Titel] | [N Tage] |
| MITTEL    | [Titel] | [N Tage] |

_[Falls keine: "Keine offenen Action-Items — gut gemacht!"]_

### Anstehende Meilensteine
- [Go-Live in N Tagen — Phase: X]
- [oder: "Kein Go-Live-Datum gesetzt"]

### Kommunikations-Vorschläge
- [Kontakt Name] — letzter Kontakt vor [N] Tagen → Follow-up empfohlen
  → `/compose email` um eine E-Mail zu verfassen

### Sonstiges
- [Stale notes / fehlende Daten / offene Fragen]

---

**Empfohlener nächster Schritt:** [Ein konkreter Schritt mit passendem Skill-Befehl]
```

#### Priority Rules

- Action items older than 7 days → **HOCH**
- Action items 3-7 days old → **MITTEL**
- Action items < 3 days old → **NIEDRIG**
- Go-live within 7 days → prepend **KRITISCH** to milestone
- Go-live within 14 days → **HOCH**
- Go-live within 30 days → **MITTEL**

#### Empfohlener nächster Schritt Logic

Pick ONE concrete suggestion:
1. If overdue action items exist → "Action-Item [Titel] ist überfällig. Erledige es oder dokumentiere den Status via `/add-note action-item`."
2. Elif go-live within 14 days → "Go-Live in [N] Tagen. Prüfe den Fortschritt via `/status`."
3. Elif communication gap with key contact → "Follow-up mit [Kontakt] ausstehend. Verfasse eine Nachricht via `/compose email`."
4. Elif no recent notes → "Letztes Update vor [N] Tagen. Halte das Projekt aktuell via `/add-note`."
5. Else → "Alles im grünen Bereich. Nächste Aktion: Phase-Update via `/status`."
