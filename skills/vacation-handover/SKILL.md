---
name: vacation-handover
description: |
  Generate a vacation handover document for all open projects of the active project type.
  Checks if a vacation-handover template exists in the knowledge base for the current type.
  If a template exists: fetches all open projects and fills the template with current data;
  offers Confluence export. If no template is configured: reports that clearly.
  Use when: (1) User says "ich bin im Urlaub", "Urlaub Übergabe", "vacation handover",
  "Übergabe erstellen", "handover document", "ich gehe in Urlaub",
  (2) User explicitly invokes `/project-hub:vacation-handover`.
  Do NOT trigger on bare "Urlaub" mentions without handover context — defer.
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "[start-date] [end-date]  — e.g. 28.07.2026 08.08.2026"
---

# Vacation Handover

Generate a complete vacation handover document for all open projects of the active type.

## Workflow

### Step 1: Resolve Project Type

Call `tool_get_session()`.

Extract `project_type` from the session result.

If no active session or no `project_type`:
- Call `tool_list_project_types()` → show numbered list → ask user to choose.

### Step 2: Check Template Availability

Call `tool_get_knowledge(project_type, "vacation-handover")`.

**If the result is `None` (not found):**

Output:
```
❌ Kein Vacation-Handover-Template für Projekttyp „[project_type]" konfiguriert.

Um ein Template anzulegen:
  /knowledge update vacation-handover

Das Template beschreibt die Struktur des Übergabe-Dokuments.
Orientiere dich am merchant-onboarding-Template als Beispiel:
  /knowledge show vacation-handover  (nach Typwechsel auf merchant-onboarding)

Danach kann dieser Skill das Template befüllen.
```
**STOP.**

### Step 3: Collect Vacation Dates

Parse vacation dates from skill arguments if provided (e.g. `28.07.2026 08.08.2026` or `28.07. 08.08.`).

If not provided or not parseable, ask:

```
📅 Wann gehst du in Urlaub?

Startdatum (z.B. 28.07.2026):
Enddatum   (z.B. 08.08.2026):
```

Store as `VACATION_START` and `VACATION_END` strings as entered by the user (keep the format they provided).

### Step 4: Load All Open Projects

Call `tool_list_projects()` → iterate `result["items"]`.

Filter for:
- `type == project_type`
- `status` is NOT one of: `"closed"`, `"archived"`, `"completed"`, `"done"`

If no open projects match:

```
✅ Keine offenen [project_type]-Projekte gefunden.

Alle Projekte sind abgeschlossen oder archiviert — kein Handover nötig.
```
**STOP.**

Log internally: `OPEN_PROJECTS = [list of filtered projects]`

### Step 5: Load Project Details (parallel per project)

For each project in `OPEN_PROJECTS`, load in parallel:
- `tool_list_contacts(project_id=project.id)` → `result["items"]`
- `tool_list_notes(project_id=project.id, limit=100)` → `result["items"]`

If any project has `result["total"] > 100` for notes, page with `offset=100` etc. until all
notes are loaded.

### Step 6: Generate the Handover Document

Use the template from Step 2 as the structural blueprint. Replace all `{{PLACEHOLDER}}`
fields and generate the `[derived fields]`.

**Document header** (once):

- `{{AUTHOR_NAME}}` → `"Markus Michalski"` (active user — hardcoded for this template type)
- `{{VACATION_START}}` → value from Step 3
- `{{VACATION_END}}` → value from Step 3

**Per-project block** (one per project in `OPEN_PROJECTS`):

Pull from **project record**:
- `{{PROJECT_NAME}}` → `project.name`
- `{{PROJECT_PHASE}}` → `project.phase` (or `"[not set]"` if empty)
- **Summary bullets** → Condense `project.description` into 2–4 bullet points highlighting
  current status, blockers, and next milestone.

Pull from **notes** (scan all notes for each project):

| Field | How to derive |
|---|---|
| **Onboarding Type** | Search for a note whose title or content contains `"Onboarding Type:"` or `"type: Direct"` / `"type: Partner"` → extract the value after the colon. If not found: `[not specified]`. |
| **Additional summary bullets** | Notes of `note_type == "decision"` or with titles suggesting key facts — add as extra bullet points in the Summary section. |
| **ToDo** | Notes with `note_type == "action-item"` that lack an explicit completion marker (see below). List each as a bullet. If none: `none`. |
| **Upcoming Meetings** | Notes with `note_type == "meeting-notes"` OR title/content containing "meeting", "Termin", "workshop", "call". List name, recurrence, time. If none: `none`. |
| **Pending Deliverables** | Notes (any type) whose title/content contains "pending", "ausstehend", "deliverable", "geplant", "planned", "roll-out". (There is no dedicated `deliverable` note type — derive by keyword.) If none: `none`. |
| **Risks & Issues** | Notes (any type) whose title/content contains "risk", "Risiko", "issue", "blocker", "problem". (There is no dedicated `risk`/`issue` note type — derive by keyword.) If none: `none`. |
| **Teams Channel** | Scan ALL note content for URLs matching `teams.microsoft.com` → extract the full URL. If multiple found, take the most recent. If none: `[not found in notes]`. |
| **JIRA Ticket** | Scan ALL note content for patterns matching `COEOPM-\d+` (or any `[A-Z]+-\d+` pattern) → extract ticket ID + surrounding context (title, status badge). If none: `[not found in notes]`. |

**Completion marker for action items** — an item is considered closed only when its note
*content* (not title) contains one of the following as a whole word (case-insensitive):
`erledigt`, `abgeschlossen`, `done`, `fertig`, `completed`. Substring matches are ignored
(e.g. "fertigstellen" does not count). Items whose title contains these words are NOT
considered closed — titles describe the goal, not the outcome.

Pull from **contacts**:

| Field | How to derive |
|---|---|
| **Internal contacts** | Filter `type == "internal"`. Map each contact's `role` field to the table row: look for role keywords — "commercial", "kaz", "account" → Commercial; "technical", "tech", "integration", "engineer" → Technical Integration; "partner" → Partner Manager; "support" → Technical Support; "growth" → Growth. If role is empty: add to the table with a `[?]` role label. |
| **External contacts (Partner)** | Filter `type == "external"` whose `role` contains "partner" (e.g. "Partner Manager") OR whose `company` is a payment partner ("Adyen", "Mollie", "Stripe", "Tink"). Format: Name, Role, Email. |
| **External contacts (Merchant)** | All remaining `type == "external"` contacts (i.e. not classified as Partner above). Format: Name, Role, Email, Phone. |

If a contacts section has no entries at all: output `none` for that row.

**Formatting rules:**
- Use `none` (not `–`, `N/A`, or empty) when a field has no data — consistent with the
  original Riverty handover format.
- Keep bullet lists concise (1 line each).
- Dates stay in the format found in the notes (do not convert formats).
- Output clean Markdown — no HTML, no `{{}}` placeholders remaining.

### Step 7: Output the Document

Output the complete filled document in Markdown.

Then add the following footer:

```
---
📋 **Nächste Schritte:**
- **Anpassen:** Sage "Ändere [Kundenname] ToDo: ..." und ich aktualisiere den Block.
- **Confluence-Export:** Sage "Export to Confluence" für einen kopier-fertigen Markdown-Block.
- **Als Notiz speichern:** Sage "Speichere das Handover als Notiz" → ich lege eine Note im aktiven Projekt an.
```

### Step 8: Confluence Export (on request)

If the user asks to export to Confluence (e.g. "export to Confluence", "Confluence", "kopieren"):

Output:

```
## Confluence Export: Vacation Handover – Markus Michalski – [START]–[END]

Kopiere den folgenden Block direkt in Confluence
(Insert → Markup → Markdown, oder im neuen Editor direkt einfügen):

---
[cleaned content]
---

💡 Hinweis: Confluence rendert Markdown-Tabellen nativ im neuen Editor.
   Prüfe nach dem Einfügen die Tabellenformatierung.
```

**Cleaning rules for Confluence export:**
- Remove all HTML comments (`<!-- ... -->`)
- Remove all lines starting with `> **Template` (internal notes)
- Remove all remaining `{{PLACEHOLDER}}` patterns (should be none left if Step 6 ran correctly)
- Ensure no empty table cells remain — replace with a space or `—`
- Keep all headings, bullet lists, tables, and bold/italic exactly as-is

### Step 9: Save as Note (on request)

If the user asks to save the handover as a note:

Call `tool_add_note(project_id=session.project_id, title="Vacation Handover [START]–[END]", content=[full document content], note_type="note")`.

Confirm: "Handover als Notiz gespeichert in Projekt [name]."
