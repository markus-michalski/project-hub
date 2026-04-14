---
name: knowledge
description: |
  Manage project-type knowledge base: governance docs, process SOPs, role matrices.
  Use when: (1) User types /knowledge, (2) "Governance aktualisieren", "Prozess zeigen",
  (3) User pastes a new document and wants it merged into knowledge,
  (4) User wants Confluence-ready export of a knowledge topic.
  Reads/writes Markdown files from ~/.project-hub/knowledge/<project-type>/.
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "[list|show <topic>|update <topic>|export <topic>|delete <topic>]"
---

# Knowledge Management Skill

Maintains a local knowledge base of governance structures, process SOPs, and role
definitions per project type. Files live at `~/.project-hub/knowledge/<project-type>/`
and are auto-loaded when you resume a project.

## Commands

### `/knowledge` — Show overview

No argument: list all available topics for the current project type.

### `/knowledge list [project-type]`

List knowledge topics. Uses active project's type from session if no argument given.

### `/knowledge show <topic>`

Display full content of a knowledge topic.

### `/knowledge update <topic>`

Update a knowledge file with new content. Claude merges intelligently.

### `/knowledge export <topic>`

Export a knowledge topic in Confluence-ready Markdown format.

### `/knowledge delete <topic>`

Delete a knowledge topic after confirmation.

---

## Workflow

### Step 1: Resolve project type

- Get active session: `tool_get_session()`
- If session has active project: use its `project_type`
- If command includes a project-type override (e.g. `/knowledge list it-project`): use that
- If no project active and no override: ask user which project type

### Step 2: Execute command

---

#### LIST

Call `tool_list_knowledge(project_type)`.

Output:

```
## Knowledge Base — [project-type]

Verfügbare Themen:

1. governance — Governance Structure (governance.md)
2. process    — Onboarding Process SOP (process.md)
3. roles      — Standard Roles & RACI (roles.md)

Befehle:
- /knowledge show governance
- /knowledge update governance
- /knowledge export governance
```

If list is empty:

```
Noch keine Knowledge-Dokumente für [project-type].

Initiale Templates installieren?
Kopiere sie von ${CLAUDE_PLUGIN_ROOT}/knowledge/[project-type]/ nach ~/.project-hub/knowledge/[project-type]/
```

---

#### SHOW `<topic>`

Call `tool_get_knowledge(project_type, topic)`.

If not found: list available topics and ask user to choose.

If found: display the full Markdown content with a header:

```
## Knowledge: [title]
Datei: ~/.project-hub/knowledge/[project-type]/[topic].md

---
[full content]
---

Befehle: /knowledge update [topic] | /knowledge export [topic]
```

---

#### UPDATE `<topic>`

**Two sub-scenarios:**

**A) User pastes new document content** (e.g. "hier ist das neue Growth-Dokument: [...]")

1. Call `tool_get_knowledge(project_type, topic)` to load existing file
2. Analyze: what does the new doc add, change, or contradict?
3. Merge strategy:
   - Preserve existing structure (headings, RACI tables, etc.)
   - Add new sections for newly introduced teams/functions
   - Update rows in tables where the new doc has newer/conflicting information
   - Add a "Change Log" entry at the bottom
4. Call `tool_save_knowledge(project_type, topic, merged_content)`
5. Show diff summary:

```
## Knowledge aktualisiert: [title]

Änderungen:
+ Neuer Abschnitt "Product Growth" hinzugefügt (Rollen, Verantwortlichkeiten)
+ RACI-Tabelle: 2 neue Zeilen für Growth-Aktivitäten
~ Escalation Matrix: Growth-Lead als zusätzlicher Approver bei Deviations
+ Change Log Eintrag: [Datum] — Integration Product Growth

Datei gespeichert: ~/.project-hub/knowledge/[project-type]/[topic].md
```

**B) User wants to edit directly** (no new doc pasted)

1. Show current content
2. Ask: "Was soll ich ändern?"
3. Apply changes, save, show diff summary

---

#### EXPORT `<topic>`

1. Call `tool_get_knowledge(project_type, topic)`
2. Clean up the Markdown for Confluence compatibility:
   - Keep H1 as page title
   - Keep H2/H3 as section headings
   - Keep tables (Confluence renders standard Markdown tables)
   - Remove any internal template notes (lines starting with `> **Template`)
   - Ensure all cells are clean (no raw variable placeholders like `YYYY-MM-DD` unless intentional)
3. Output:

```
## Confluence Export: [title]

Kopiere den folgenden Markdown-Block direkt in Confluence
(Insert > Markup > Markdown oder im neuen Editor direkt einfügen):

---
[cleaned Markdown content]
---

Hinweis: Confluence rendert Markdown-Tabellen nativ.
Prüfe nach dem Einfügen, ob die Tabellen korrekt formatiert sind.
```

---

#### DELETE `<topic>`

1. Confirm: "Möchtest du `[topic].md` wirklich löschen? Das kann nicht rückgängig gemacht werden. (ja/nein)"
2. On confirmation: call `tool_delete_knowledge(project_type, topic)`
3. Confirm deletion.

---

## Template Installation Helper

If a user has no knowledge files yet, offer to copy templates from the plugin repo:

```bash
# Copy templates to local knowledge directory
mkdir -p ~/.project-hub/knowledge/merchant-onboarding
cp ${CLAUDE_PLUGIN_ROOT}/knowledge/merchant-onboarding/*.md ~/.project-hub/knowledge/merchant-onboarding/
```

Tell user: "Templates kopiert. Öffne die Dateien und ersetze die Platzhalter mit euren echten Inhalten.
Die Dateien liegen in `~/.project-hub/knowledge/merchant-onboarding/`."
