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
argument-hint: "[list [project-type]|show <topic>|update <topic>|export <topic>|delete <topic>|sync [--force]]"
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

### `/knowledge sync [--force]`

Compare bundled plugin templates with your installed knowledge files.
Shows what's new or changed. Use `--force` to apply updates after confirmation.
**Even when `--force` is already in the command, a dry-run report and an explicit user
confirmation are still required before anything is written (unless the report finds nothing to
sync, in which case nothing is written and no confirmation is needed) — see SYNC steps 3–4
below.**

---

## Workflow

### Step 1: Resolve project type

- Get active session: `tool_get_session()`
- Resolve `project_type` using this priority order (not a set of independent conditions —
  check them in order and stop at the first match):
  1. **Command-level override — `list` only** (e.g. `/knowledge list it-project`). `list` is the
     only subcommand whose second token is a project-type; if given, it always wins, even when a
     session has an active project of a *different* type. An explicit argument in the command is
     a deliberate, specific instruction and must never be silently replaced by the session's
     default. **Do not apply this rule to `show <topic>`, `update <topic>`, `export <topic>`, or
     `delete <topic>`** — their second token is always a topic name, never a project-type
     override, even if it happens to match a project-type name (e.g. `/knowledge delete
     governance` must resolve `project_type` from the session, not from the word "governance").
  2. **Active session's `project_type`** — used for every subcommand other than `list` with an
     explicit override, and for `list` when no override was given.
  3. **Ask the user** which project type to use — only if neither of the above applies (no
     override, no active project).

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

Initiale Templates installieren? Nutze /knowledge sync, um alle Templates zu installieren.
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

1. Call `tool_get_knowledge(project_type, topic)` to load existing file.
   - **If it returns `None`** (no file exists yet for this topic): do not assume this is a
     new topic — it may be a typo of an existing one (e.g. `update governnace` instead of
     `governance`). Call `tool_list_knowledge(project_type)`, show the available topics, and ask
     the user to confirm: either pick an existing topic, or explicitly confirm that `[topic]`
     should be created as a **new** file. Only proceed once the user has confirmed.
   - **Once confirmed as a new topic**: there is nothing to merge against, so skip steps 2, 3
     and 5 below. Ensure the saved content starts with a level-1 `# Title` heading (add one from
     the topic name if the pasted content doesn't have one — `list_knowledge`/`get_knowledge`
     derive the display title from this H1). Save it directly as the new file's content (step 4),
     then confirm to the user that a **new** file was created (not "aktualisiert"/"updated" — no
     diff summary, since there was nothing to diff against).
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

1. Call `tool_get_knowledge(project_type, topic)`.
   If not found: same handling as SHOW — list available topics (`tool_list_knowledge`) and ask
   the user to choose. Never fabricate an export block for a topic that doesn't exist.
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
2. Branch on the answer:
   - **If the user does not confirm** ("nein" or similar): do **not** call
     `tool_delete_knowledge` at all; acknowledge that nothing was deleted. Stop here.
   - **If the user confirms**: call `tool_delete_knowledge(project_type, topic)` — this returns
     `True`/`False`.
     - `True`: confirm the deletion to the user.
     - `False` (topic didn't actually exist): tell the user the topic wasn't found — never
       present this as a successful deletion.

---

#### SYNC `[--force]`

1. Call `tool_sync_knowledge_templates(force=False)` to get the report (always dry-run first)
2. Display the results:

```
## Knowledge Template Sync

Checking templates...
  it-project/charter.md      — UP TO DATE
  it-project/runbook.md      — NEW (not installed yet)
  consulting/engagement.md   — NEWER VERSION AVAILABLE (plugin: 3.2KB, local: 1.8KB)
  ...

[N] Dateien können aktualisiert werden.
```

(`[N]` is the actual count of NEW/NEWER-VERSION entries from the report — never a hardcoded
number.)

3. If everything is up-to-date (`N` = 0): report "Alle Templates sind aktuell." and stop — this
   applies even if `--force` was given, since there is nothing to sync. Do not proceed to step 4.

4. Otherwise (`N` > 0, regardless of whether `--force` was given): ask for confirmation, with
   `[N]` interpolated from the actual count:
   "Soll ich die [N] Dateien jetzt synchronisieren? Bestehende Dateien werden überschrieben. (ja/nein)"

5. On confirmation: call `tool_sync_knowledge_templates(force=True)`
6. Report what was synced:

```
Synchronisiert:
  ✓ it-project/runbook.md
  ✓ consulting/engagement.md

Dateien liegen jetzt in ~/.project-hub/knowledge/.
Öffne sie und ersetze Platzhalter mit euren echten Inhalten.
```

**Important:** Never call with `force=True` without explicit user confirmation.

---

## Template Installation Helper

If a user has no knowledge files yet, suggest using `/knowledge sync` to install all templates at once.
This replaces the manual `cp` approach and ensures future updates can be detected.
