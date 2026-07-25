---
name: get-template
description: |
  Get a fillable project template for any project type. The template can be copied,
  filled in outside the chat, and later imported via /project-hub:new-project.
  Use when: (1) User says "Vorlage holen", "Projektvorlage", "Template für neues Projekt",
  "gib mir die Vorlage", "welche Felder brauche ich", (2) User explicitly invokes
  `/project-hub:get-template`, (3) User wants to prepare a project outside the chat.
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "[project-type]"
---

# Get Project Template

Output a fillable template for a project type so it can be prepared outside the chat.

## Workflow

### 1. Determine Project Type

Call `tool_list_project_types()` first — returns every available type (built-in and custom, e.g.
one created via `/project-hub:type-creator`), each with `name`, `label`, `description`, `source`.
Keep this list around; Step 3 needs it too.

If argument provided: use it directly as the project type.

If not: use `AskUserQuestion` with options built from the list above (value = `name`, display =
`label`, hint = `description`) — this makes custom types selectable too, not just the built-ins.

### 2. Load Template

Use MCP `tool_get_project_template(project_type)`.

If result contains `"error"` → show error message and STOP.

If result contains `"fallback": true` → note: "Kein spezifisches Template für diesen Typ — generisches Template verwendet."
The effective type for Step 3's heading is now this response's own `"project_type"` field
(`"generic"`), not the type originally requested — the delivered body is the generic template, so
the heading must say so too.

### 3. Output Template

Resolve the heading label: look up the effective type (the requested type, or `"generic"` on the
fallback case above) in the list fetched in Step 1 and use its `"label"` field. If it isn't in the
list for some reason, use the raw type string itself as the label.

Show the template as a fenced markdown code block so it can be copied cleanly:

````
## Projektvorlage: [project_type_label]

Fülle alle Felder aus und importiere die Vorlage danach mit einer der folgenden Methoden:

**Option A — Im Chat einpasten:**
Rufe `/project-hub:new-project` auf und paste die ausgefüllte Vorlage.

**Option B — Als Datei speichern:**
Speichere die Vorlage als `.md`-Datei (z.B. `~/Desktop/neues-projekt.md`),
dann: `/project-hub:new-project` → Dateipfad angeben.

```markdown
[template_content]
```
````

## Error Handling

- Unknown type → show fallback note, deliver generic template
- MCP unavailable → tell user to restart Claude Code and try again
