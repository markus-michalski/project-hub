---
name: compose
description: |
  Draft an email, Slack message, or Teams message based on project context or pasted input, or
  export/import a project as a JSON file to hand off to a colleague.
  Use when: user needs to write a communication, says "schreib eine E-Mail", "draft email",
  "Slack-Nachricht", "Teams-Nachricht", "Antwort auf diese E-Mail", "Projekt exportieren",
  "Projekt importieren", "Projekt für Kollegen exportieren", "Projekt aus Datei laden".
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<email|slack|teams|export|import>"
---

# Compose

Draft professional communications — emails, Slack messages, or Teams messages — using active project context.

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()`.

If there IS an active project, load context:
- MCP `tool_get_project_by_id(project_id)`
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]`

Project context ensures the right tone, correct names/roles, and relevant phase info.

If there is NO active project: do not call `tool_get_project_by_id` or `tool_list_contacts` (there
is no project_id to pass). Tell the user project context isn't available and continue anyway —
compose can draft a generic communication without a project, unlike skills that hard-require one
(`/resume` first). Exception: **Projekt exportieren** (Step 8) genuinely needs an active project —
if the user picks it with none loaded, tell them to `/resume` first instead. (**Projekt
importieren**, Step 9, needs no active project either — it creates one — so it's unaffected either
way.) **Step 7 (Offer to Save Reference)** also needs an active project — it is skipped, not offered,
when there is none; see its own handling there.

### 2. Determine Channel

If argument provided: use it (email / slack / teams / export / import).
If not: ask — "Für welchen Kanal? E-Mail, Slack, Teams — oder Projekt für Kollegen exportieren/importieren?"

Options: email | slack | teams | **Projekt exportieren (für Kollegen)** | **Projekt importieren (aus Datei)**

If user picks **Projekt exportieren**: jump to [Step 8 — Export Project](#8-export-project).
If user picks **Projekt importieren**: jump to [Step 9 — Import Project](#9-import-project).

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

One question is **not** conditional on "only if necessary" — always ask it regardless of how clear
the wording seems:
- **For `merchant-onboarding` projects: always explicitly ask/confirm whether this is for the
  external merchant or the internal team**, even if the wording sounds unambiguous ("an den
  Merchant" still gets confirmed) — external vs. internal need different styles (Step 5), and
  getting this wrong on a merchant-facing message is the costliest mistake this skill can make. If
  there is no active project (no `merchant-onboarding` type to check against — see Step 1), apply
  the same rule whenever the recipient's audience isn't obviously internal or external: ask
  explicitly rather than guessing.

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

**Any other project type** (e.g. a custom type created via `/project-hub:type-creator` that doesn't
match one of the buckets above): fall back to the `it-project / marketing / generic` guidance above
— never leave tone undefined or refuse to draft just because the exact type string isn't listed here.

### 6. Offer Refinement

After drafting, ask:
- "Soll ich den Ton anpassen?"
- "Willst du etwas hinzufügen oder weglassen?"
- "Soll ich eine Version auf Englisch erstellen?"

### 7. Offer to Save Reference

Only if a project is active (Step 1): "Möchtest du diese Kommunikation als Notiz im Projekt
speichern?" If yes → MCP `tool_add_note(project_id, title, content, note_type="email")`.

If there is no active project: skip this step silently — there is no `project_id` to save against,
and `tool_add_note` requires one. Do not guess a project or invent an ID. Composing without a
project (Step 1) is a legitimate path on its own; don't push the user to load or create one just to
save this draft. If the user explicitly asks to save it anyway, tell them to `/resume` (load an
existing project) or `/project-hub:new-project` (start a new one) first, then re-run compose.

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
**Verknüpfungen:** [n]

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

### 9. Import Project

Import a project from a JSON file created by `tool_export_project` (Step 8). No active project is
required for this — importing always inserts a project record: either a brand-new one (no slug
collision), a renamed duplicate (`rename`), or a from-scratch re-insert after deleting the existing
one (`overwrite`). There is no merge path — nothing about an existing project's own data is ever
combined with the imported data.

**Workflow:**

1. Ask for the path to the export file: "Pfad zur Export-Datei:"
2. Ask for the merge strategy, explaining the options — default to **skip** (the tool's own safe
   default) if the user doesn't state a preference:
   - `skip` — abort if a project with the same slug already exists (safe default)
   - `rename` — insert with a unique slug suffix, existing project untouched
   - `overwrite` — deletes the existing project **and all of its contacts and notes**, then
     re-inserts from the export (**destructive** — only use on explicit user confirmation, never
     as a silent retry after `skip` reports a conflict)
3. Call MCP `tool_import_project(json_path, merge_strategy)`. This raises instead of returning a
   result dict for these cases — handle each before showing anything:
   - File doesn't exist at the given path → tell the user, ask them to re-check/re-enter it (back to
     step 1).
   - Unsupported/mismatched `export_version` → tell the user this export file isn't compatible with
     this installation (it was likely produced by a different, incompatible plugin version) and
     cannot be imported here; don't retry.
   - Invalid `merge_strategy` → shouldn't occur if step 2's three options are passed through
     verbatim; if it does, re-ask step 2.
4. Show the result:
   - If `imported` is true: confirm the imported project's name, slug, and counts (contacts, notes,
     links). Note any entries listed under `links_not_restored` (linked projects that don't exist in
     this DB yet). Also note: attachments/docs are not part of the export (Phase 1 scope, same as
     Step 8) — the imported project starts with no docs folder and no files, even if the source
     project had some.
   - If `imported` is false (e.g. `skip` hit an existing slug): tell the user plainly that the import
     was skipped/aborted and why, and ask whether they want to retry with `rename` or `overwrite`
     instead — never retry automatically.

## Context Usage

- Use contact names from the project when addressing people
- Reference current phase in status communications
- For replies: analyze the original email's tone and match appropriately
- For merchant-onboarding: always clarify internal vs. external communication — they require different styles
