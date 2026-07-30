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
- MCP `tool_list_notes(project_id, note_type="action-item", limit=100)` → iterate `result["items"]`
  — ALL open action items for Analysis A. Check `result["total"]`; if `total > 100`, page with
  `offset=100`, `offset=200`, ... until every action item is loaded. Analysis A promises
  oldest-first ("most overdue at top"), so this list must never be silently truncated.
- MCP `tool_list_notes(project_id, limit=20)` → iterate `result["items"]` — recent notes (all
  types) for Analyses B/C/D (phase progress, stale notes, communication gaps)
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]` — contacts for communication
  suggestions. This is a paginated display snapshot, not a complete lookup source
  ([project-hub#122](https://github.com/markus-michalski/project-hub/issues/122)) — if a name
  surfaces that isn't in this list, call `tool_search_contacts(query=<most distinctive part of
  the name>, project_id=0)` (returns a bare list, not an `{"items": ...}` dict) before
  concluding the contact doesn't exist or offering to create one

### 3. Analyze

From the loaded data, identify:

**A) Overdue / Open Action Items**
- Notes with `type = "action-item"` that have no completion marker
  - A completion marker requires an explicit, unambiguous signal — not just the keyword's presence:
    - **Keyword marker:** one of "erledigt", "abgeschlossen", "done", "fertig" appears as a
      **whole word** (case-insensitive — not as a substring, e.g. "fertig" must not match inside
      "fertigstellen"/"unfertig") in the note's **content only** — never the title. Titles are
      phrased as the goal ("Doku fertig machen", "Angebot fertigstellen", "Migration abgeschlossen
      melden") and routinely contain these words while the item is still open, so title matches are
      ignored entirely.
    - **Negation cancels it:** if the keyword is preceded (within ~3 words) by a negation — "nicht",
      "noch nicht", "kein(e)", "not", "never" — it does NOT count as completion. "noch nicht
      erledigt", "not done yet", "Status: offen, nicht abgeschlossen" are still open.
    - **Checklist marker:** the content contains at least one `- [x]` / `[x]` checked box **and** no
      remaining `- [ ]` unchecked box. A note with any unchecked box left is still open even if it
      also has checked ones (e.g. "- [x] Vertrag geprüft\n- [ ] Freigabe einholen" is OPEN, not
      done). This checks the note's own `content` field only — it's independent of the separate
      on-disk `docs/misc/todo.md` action-item list.
  - Scan only the content for markers (title is never scanned) before treating a note as still open.
- Sort by date: oldest first (most overdue at top) — use `created_at`, not `updated_at`; editing an
  old note doesn't make the underlying item newer.
- For the recommendation logic in step 4, an item only counts as "overdue" once it's 3+ days old
  (Priority MITTEL or HOCH, see table below). Items <3 days old (NIEDRIG) still appear in the
  Section A output table but never drive the "overdue" recommendation branch.

**B) Upcoming Milestones**
- Go-live date: if within 30 days, flag it
- Current phase: flag if it seems stale (no notes in last 14 days with phase progress)
  - Basis: use `created_at` for the "last 14 days" window — a note only counts if it was newly
    created in that window; editing an older note (bumping `updated_at`) does not reset the
    staleness clock.
  - A note only counts as "phase progress" if its title or content references the current phase
    name or an explicit status/progress update (e.g. the phase name itself, or words like
    "Fortschritt", "Status-Update", "Phase abgeschlossen"). A recent note about an unrelated topic
    does not reset the staleness clock.
  - If `project["phase"]` is empty (no phase set), the phase-name match is unsatisfiable — skip it
    and fall back to the status/progress keyword list alone. Show "Phase: nicht gesetzt" in the
    output header instead of silently degrading.

**C) Stale Notes**
- Notes with no update in >7 days that contain open questions or decisions pending

**D) Communication Gaps**
- External contacts with no recent note mentioning them (>14 days)
  - "Mentioning them" means, within the last 14 days (by `created_at`), a note's title or content
    contains any of: a token of the contact's `name` (first name OR last name alone match — not
    the full string), the local-part of the contact's `email` (before the `@`), or the contact's
    `company` value — case-insensitive. Real notes reference people by surname only ("Rücksprache
    mit Schmidt"), by first name, by email, or by company, so requiring the literal full `name`
    string produces false gaps.
  - A recent note matching none of these doesn't count as recent contact with them.
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

Pick ONE concrete suggestion, following this priority order strictly. "Overdue" here always means
3+ days old (Priority MITTEL or HOCH) — a NIEDRIG item (<3 days old) still shows in the Section A
table but never drives this recommendation:
1. If a HOCH-priority overdue action item exists (>7 days old) → "Action-Item [Titel] ist
   überfällig. Erledige es oder dokumentiere den Status via `/add-note action-item`." This wins over
   every milestone below, including a KRITISCH go-live — an item open more than a week has already
   outlasted the entire runway of even a 7-day go-live.
2. Elif go-live within 7 days (KRITISCH) → "Go-Live in [N] Tagen — KRITISCH. Prüfe den Fortschritt via `/status`."
3. Elif a MITTEL-priority overdue action item exists (3-7 days old) → "Action-Item [Titel] ist überfällig. Erledige es oder dokumentiere den Status via `/add-note action-item`."
4. Elif go-live within 14 days → "Go-Live in [N] Tagen. Prüfe den Fortschritt via `/status`."
5. Elif communication gap with key contact → "Follow-up mit [Kontakt] ausstehend. Verfasse eine Nachricht via `/compose email`."
6. Elif no recent notes → "Letztes Update vor [N] Tagen. Halte das Projekt aktuell via `/add-note`."
7. Else → "Alles im grünen Bereich. Nächste Aktion: Phase-Update via `/status`."
