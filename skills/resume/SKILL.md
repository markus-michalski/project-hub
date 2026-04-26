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
If no argument: Use MCP `tool_list_projects()` and show numbered list, ask user to choose.

If no projects exist → suggest `/new-project`.

### 2. Load Context

Load all relevant context in parallel:
- MCP `tool_get_project_by_id(project_id)` — full project details
- MCP `tool_list_contacts(project_id)` — all contacts
- MCP `tool_list_notes(project_id)` — recent notes (latest 5)
- If `project_type` is NOT `generic`: MCP `tool_list_knowledge(project_type)` — check for knowledge files

### 3. Set Session

Use MCP `tool_set_session(project_id, last_skill="resume")`.

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

### Interne Kontakte
[List: Name — Rolle — Email]

### Externe Kontakte
[List: Name — Firma — Rolle — Email]

### Letzte Notizen
[List: Datum — Titel — Typ]

### Docs-Ordner
[docs_path]

### Knowledge Base  ← only if project_type != generic AND knowledge files exist
[List: topic — title]

---
Was soll ich tun?
```

## Knowledge Auto-Load

If knowledge files are found for the project type:

1. Load them silently (do NOT dump full content into the output)
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
