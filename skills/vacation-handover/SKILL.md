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

`tool_list_projects()` defaults to `limit=50`. If `result["total"]` is greater than the number
of items actually returned, fetch the remaining pages with `offset=<items loaded so far>` until
all projects are loaded — never filter and build the handover from a partial first page. The
server sorts by `updated_at` with no tiebreaker, so pages can overlap or gap when projects share
the same timestamp; after fetching, de-duplicate the merged list by `id` before filtering.

Filter for:
- `type == project_type`
- `status` is NOT one of: `"closed"`, `"archived"`, `"completed"`, `"done"`, `"cancelled"` — the
  real system's only supported status values are `active`/`paused`/`completed`/`cancelled` (per
  `tool_list_projects`'s own docstring); `"closed"`/`"archived"`/`"done"` don't currently occur
  but stay excluded defensively in case of legacy data.

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

Both calls are paginated server-side (`tool_list_contacts` defaults to `limit=50`). If either
call's `result["total"]` exceeds the number of items already loaded, page with
`offset=<items loaded so far>` etc. until every contact and every note for that project has
been loaded — never derive Step 6's contact tables or note-based fields from a partial first
page.

Additionally — **once** for the whole handover run, not inside the per-project loop above — call
`tool_list_shared_contacts()`. If `result["total"] > result["limit"]`, page with
`offset=<items loaded so far>` until the number loaded equals `result["total"]`, same as Step 4.
A shared contact can be homed on any single project (including one outside `OPEN_PROJECTS`, or
none of them specifically) but still be relevant to several — e.g. an Implementation Manager who
covers multiple merchants. `tool_list_contacts(project_id)` only returns contacts homed on that
exact project, so a shared contact homed elsewhere is invisible to it and needs this separate
call to be found. (A shared contact that happens to be homed on the *current* project IS returned
by both calls — see the de-duplication rule in Step 6, "Internal contact derivation".)

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
| **Internal contacts** | Combine project-scoped and relevant shared contacts into the template's fixed bucket table — see "Internal contact derivation" below. |
| **External contacts (Partner)** | Filter `type == "external"` whose `role` contains "partner" (e.g. "Partner Manager") OR whose `company` is a payment partner ("Adyen", "Mollie", "Stripe", "Tink"). Format: Name, Role, Email. |
| **External contacts (Merchant)** | All remaining `type == "external"` contacts (i.e. not classified as Partner above). Format: Name, Role, Email, Phone. |

**Internal contact derivation:**

1. Start from `type == "internal"` contacts loaded via `tool_list_contacts(project_id)` (Step 5).
2. Add every contact from the `tool_list_shared_contacts()` list (Step 5 addendum) whose surname
   — case-insensitive, also accepting `Lastname, Firstname` order and hyphen/umlaut spelling
   variants — is mentioned in this project's note titles, note content, or `project.description`.
   Do not add a shared contact just because they exist; do not dump the whole shared-contact
   directory into every project block. If two different shared contacts both match a mention,
   include both rather than guessing which one is meant.
3. De-duplicate by contact `id` — a shared contact homed on *this* project is returned by both
   calls in step 1 and 2 above.
4. Never print a shared contact's `project_name`/`project_slug` fields (they show which project
   the contact was originally created under) anywhere in the rendered document — this is another
   client's project name and must not leak into a different client's handover.
5. If `tool_list_shared_contacts()` itself fails, say so explicitly in the generated document
   (e.g. under Internal contacts: "shared contacts could not be loaded") instead of silently
   proceeding as if the project-scoped list were complete.

For each contact from steps 1–4, match role keywords against the template's five fixed bucket
rows: "commercial", "kaz", "account" → Commercial; "technical", "tech", "integration",
"engineer" → Technical Integration; "partner" → Partner Manager; "support" → Technical Support;
"growth" → Growth. Put the contact's Name (and Slack handle if known) into that bucket row's
cell — if several contacts match the same bucket, list them all in that cell. Keep all five rows
in the table in order; if a bucket has no matching contact, its cell reads `none` — never leave
the template's own placeholder text (`[name / @slack-handle]`) in the delivered document.

For a contact whose role matches none of the five buckets but is non-empty, append one extra row
below the five, using their real role text as-is as the Role cell (e.g. "Sales Manager",
"Operations Lead", "Implementation Manager") — do NOT replace it with `[?]`; a known role is not
unknown just because it doesn't fit one of the five bucket names, and hiding it behind `[?]`
defeats the point of a contact table. Reserve `[?]` for a contact whose role field is genuinely
empty. Never silently drop a real contact just because their role doesn't match a bucket.

If a contacts section has no entries at all: output `none` for that row.

**Formatting rules:**
- Use `none` (not `–`, `N/A`, or empty) when a field has no data — consistent with the
  original Riverty handover format.
- Keep bullet lists concise (1 line each).
- Dates stay in the format found in the notes (do not convert formats).
- Before filling placeholders, strip the template's own internal scaffolding from the output:
  HTML comments (`<!-- ... -->`) and any line starting with `> **Template` (these are authoring
  notes for whoever maintains the template in the knowledge base — they must never reach the
  delivered document, not only the Confluence export copy produced on request in Step 8).
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
