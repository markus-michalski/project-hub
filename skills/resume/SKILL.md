---
name: resume
description: |
  Resume or switch to an existing CLIENT/HUB project in the project-hub registry. Loads full
  project context (contacts, notes, decisions). Use ONLY for hub-tracked client projects —
  NOT for code repos (mm-dev-toolkit), book projects (storyforge), or video projects (vidcraft).
  Use when: (1) User says "Hub-Projekt {name}", "Wechsle zu Hub-Projekt {name}",
  "Lade Hub-Projekt {name}", (2) User explicitly invokes `/project-hub:resume`,
  (3) The mentioned project name is known to be a hub/client project (verify via
  `tool_list_projects` first if uncertain).
  Do NOT trigger on bare project-name mentions without hub context — defer.
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "<project-name>"
---

# Resume Project

Load a project and restore its full context for the current session.

## Workflow

### 1. Find Project

If argument provided: Use MCP `tool_get_project(identifier)`.
If no argument: Use MCP `tool_list_projects()` → iterate `result["items"]` and show numbered list, ask
user to choose, then use their chosen item directly — `tool_list_projects` rows already contain the
full project record (`id`, `type`, description, etc.), same as `tool_get_project`.

If no projects exist → suggest `/new-project`.

### 2. Load Context

The project object from step 1 already has everything needed (`id`, `type`, description, ...) — do
NOT re-fetch it via `tool_get_project_by_id`. Load the rest in parallel:
- MCP `tool_list_contacts(project_id)` → iterate `result["items"]`; if `result["total"] > 50`, note
  that older entries exist and suggest `/search`. Exclude items with `is_shared == 1` (those are shown
  only under "Geteilte Kontakte" below, not here); split the remainder by `type` — `external` →
  "Externe Kontakte", everything else (including the DB default `internal`) → "Interne Kontakte", so
  an unexpected `type` value never silently drops a contact
- MCP `tool_list_shared_contacts()` → iterate `result["items"]` — shared/global contacts available across all projects
- MCP `tool_list_notes(project_id)` → iterate `result["items"]` — all notes (default limit=50); if `result["total"] > 50`, note that older entries exist and suggest `/search` for deep history
- If `type` is NOT `generic`: MCP `tool_get_all_knowledge(project_type=<that type value>)` — loads
  the full content of every knowledge file for that type in one call

Note: the project object's field is called `type` — there is no `project_type` key on it.
`project_type` is only the *parameter name* the knowledge tools expect; pass the `type` value there.

### 3. Set Session

Use MCP `tool_set_session(identifier, last_skill="resume")`.

### 4. Output

Present the full project context clearly:

```
## Projekt geladen: [Name]

**Typ:** [Typ Label]  |  **Status:** [Status]  |  **Phase:** [Phase]
**Go-Live:** [Datum]  |  **Markt:** [Markt, if set]

### Beschreibung
[description]

### Produkte / Scope
[products, if set]

### Interne Kontakte (projektspezifisch)
[List: Name — Rolle — Email]

### Externe Kontakte
[List: Name — Firma — Rolle — Email]

### Geteilte Kontakte (alle Projekte)
[List: Name — Rolle — Email — only if shared contacts exist; omit section otherwise]

### Letzte Notizen
[List: Datum — Titel — Typ]

### Docs-Ordner
[docs_path]

### Knowledge Base  ← only if `type` != generic AND knowledge files exist
[List: topic — title]

---
Was soll ich tun?
```

## Knowledge Auto-Load

If `tool_get_all_knowledge` returned any items for the project type:

1. Each returned item already includes the file's full `content` — it's loaded in the same call, no
   separate Read needed. Keep this silent (do NOT dump the raw content into the visible output).
2. Mention them briefly in the output: `Knowledge geladen: governance, process, roles`
3. Use this knowledge to inform your responses during the session:
   - When answering questions about process steps, reference the process SOP
   - When drafting communications, use correct role names from roles.md
   - When handling deviations, follow the governance escalation paths
4. If user asks about governance/process/roles explicitly → show the relevant knowledge section

If NO knowledge files exist for a project type that would benefit from them
(e.g. merchant-onboarding), suggest: "Noch keine Knowledge-Dokumente.
`/knowledge` zeigt dir, wie du Templates installierst."

## Tips

- If `products` or `market` are empty and type is `merchant-onboarding`, gently suggest adding them via `/status`
- If no contacts exist, suggest `/add-contact`
- If no notes exist, suggest `/add-note`
