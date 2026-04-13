---
name: status
description: |
  Show or update the status of the active project.
  Use when: user wants to see project details, update phase, change status,
  says "Status", "was ist der Stand", "update Phase".
model: claude-sonnet-4-6
user-invocable: true
---

# Status

Show the full status of the active project, or update it.

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()`.
If no active project → "Kein aktives Projekt. Bitte zuerst `/resume`."

### 2. Load Full Context

In parallel:
- MCP `tool_get_project_by_id(project_id)` — project details
- MCP `tool_list_contacts(project_id)` — contacts
- MCP `tool_list_notes(project_id)` — recent notes (latest 3)
- MCP `tool_list_docs(project_id)` — documents

### 3. Display Status

```
## Projektstatus: [Name]

**Typ:** [Typ]  |  **Status:** [active/paused/completed]
**Phase:** [Phase]  |  **Go-Live:** [Datum oder "nicht gesetzt"]
[**Markt:** [Markt]  |  **Produkte:** [Produkte]]  ← only for merchant-onboarding

### Beschreibung
[description]

### Interne Kontakte ([N])
| Name | Rolle | E-Mail |
|------|-------|--------|
| [Name] | [Rolle] | [Email] |

### Externe Kontakte ([N])
| Name | Firma | Rolle | E-Mail |
|------|-------|-------|--------|
| [Name] | [Firma] | [Rolle] | [Email] |

### Letzte Notizen
- [Datum] — [Titel] ([Typ])
- [...]

### Dokumente
[Folder: N files each]

### Docs-Pfad
[docs_path]
```

### 4. Offer Updates

After displaying, ask:
"Möchtest du etwas aktualisieren?"

Options:
- Phase ändern
- Go-Live Datum setzen/ändern
- Status ändern (aktiv / pausiert / abgeschlossen)
- Beschreibung aktualisieren
- Produkte / Markt ergänzen (merchant-onboarding)

If user wants to update → collect new value → MCP `tool_update_project(identifier, **fields)`.

Confirm update:
```
✅ [Field] aktualisiert: [old] → [new]
```
