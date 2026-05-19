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

If argument provided: use it directly.

If not: use `AskUserQuestion` with available types:
- `merchant-onboarding` — Merchant Onboarding
- `it-project` — IT / Software Project
- `marketing` — Marketing Campaign
- `consulting` — Consulting Engagement
- `event` — Event Planning
- `generic` — General Purpose

### 2. Load Template

Use MCP `tool_get_project_template(project_type)`.

If result contains `"error"` → show error message and STOP.

If result contains `"fallback": true` → note: "Kein spezifisches Template für diesen Typ — generisches Template verwendet."

### 3. Output Template

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
