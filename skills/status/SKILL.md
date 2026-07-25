---
name: status
description: |
  Show or update the status of the active CLIENT/HUB project. Use ONLY for hub-tracked
  client projects — NOT for code projects (mm-dev-toolkit), book status (storyforge), or
  video status (vidcraft).
  Use when: (1) User says "Hub-Status", "Status des Hub-Projekts", "Phase im Hub-Projekt
  ändern", (2) User explicitly invokes `/project-hub:status`,
  (3) An active hub project is loaded and the user wants its status/phase.
  Do NOT trigger on bare "Status" / "Stand" without hub/client context — defer.
model: claude-haiku-4-5
user-invocable: true
---

# Status

Show the full status of the active project, or update it.

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()`. It always returns a dict (a `LEFT JOIN` over a singleton session
row), so check `result["project_id"]` for truthiness — not whether the result itself is
empty/absent.
If no active project (`project_id` falsy) → "Kein aktives Projekt. Bitte zuerst `/resume`."

### 2. Load Full Context

In parallel:
- MCP `tool_get_project_by_id(project_id)` — project details (the `slug` field here is the
  `identifier` Step 4's update call needs — keep it around, do not re-derive it from `project_id`)
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]` — project-specific contacts.
  `type` is the field name on each returned row (`contact_type` is only the tool PARAMETER name,
  used on add/update/list — never a field on the row itself). If `result["total"] >
  result["limit"]` (default `limit=50`), note that older contacts exist and mention `/search`.
- MCP `tool_list_shared_contacts()` → iterate `result["items"]` — contacts shared across all
  projects (`is_shared=1`), owned by other projects but explicitly cross-project-visible, same as
  `/resume` (skills/resume/SKILL.md) — without this call, shared contacts silently disappear here.
- MCP `tool_list_notes(project_id)` → iterate `result["items"]` — recent notes (latest 3, newest
  first). If `result["total"] > result["limit"]` (default `limit=50`), older notes exist — mention
  `/search` for deep history.
- MCP `tool_list_docs(project_id)` — documents

### 3. Display Status

Bucket each project-specific contact (from Step 2's `tool_list_contacts`) by its `type` field:
`type == "external"` → Externe Kontakte, everything else (including `internal` and any
unexpected/empty value) → Interne Kontakte — so no project contact is dropped by the bucketing
itself. This is separate from Step 2's `tool_list_shared_contacts()` call, which supplies its own
"Geteilte Kontakte" section below.

```
## Projektstatus: [Name]

**Typ:** [Typ]  |  **Status:** [Aktiv/Pausiert/Abgeschlossen/Abgebrochen]
**Phase:** [Phase]  |  **Go-Live:** [Datum oder "nicht gesetzt"]
[**Markt:** [Markt]  |  **Produkte:** [Produkte]]  ← only for merchant-onboarding

### Beschreibung
[description]

### Interne Kontakte ([N])
| Name | Rolle | E-Mail |
|------|-------|--------|
| [Name] | [Rolle] | [Email] |
[...]  ← "Keine internen Kontakte." wenn keine vorhanden

### Externe Kontakte ([N])
| Name | Firma | Rolle | E-Mail |
|------|-------|-------|--------|
| [Name] | [Firma] | [Rolle] | [Email] |
[...]  ← "Keine externen Kontakte." wenn keine vorhanden

### Geteilte Kontakte (alle Projekte)
| Name | Rolle | E-Mail |
|------|-------|--------|
| [Name] | [Rolle] | [Email] |
[...]  ← only if tool_list_shared_contacts() returned any items; omit section otherwise

### Letzte Notizen
- [Datum] — [Titel] ([Typ])
- [...]  ← "Noch keine Notizen." wenn keine vorhanden

### Dokumente
[Folder: N files each]
[...]  ← "Keine Dokumente." wenn keine vorhanden

### Docs-Pfad
[docs_path]
```

`**Status:**` maps the raw field to German the same way `report.py` does:
active → Aktiv, paused → Pausiert, completed → Abgeschlossen, cancelled → Abgebrochen.

### 4. Offer Updates

After displaying, ask:
"Möchtest du etwas aktualisieren?"

Options:
- Phase ändern
- Go-Live Datum setzen/ändern
- Status ändern (aktiv / pausiert / abgeschlossen / abgebrochen)
- Beschreibung aktualisieren
- Produkte / Markt ergänzen (merchant-onboarding)

If user wants to update → collect new value → MCP `tool_update_project(identifier, **fields)`.
`identifier` is the project's **slug** (or name) from Step 2's loaded project object — e.g.
`"acme-onboarding"` — never the numeric `project_id`; `tool_update_project` matches by slug/name,
so passing the numeric ID matches nothing and returns `None`/empty (see the confirmation guard
below). "abgebrochen" maps to `status="cancelled"` (the tool's fourth valid status value,
alongside active/paused/completed — also shown as its own bucket on `/dashboard`).

If `tool_update_project` returned the updated project, confirm:
```
✅ [Field] aktualisiert: [old] → [new]
```
If it returned `None`/empty instead (e.g. a wrong or numeric `identifier` matched no project), do
NOT print the ✅ line — report the failure instead: "Update fehlgeschlagen — Projekt nicht
gefunden."
