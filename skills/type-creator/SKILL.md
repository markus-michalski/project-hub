---
name: type-creator
description: |
  Guided wizard to create a new custom project type for project-hub.
  Custom types are saved to ~/.project-hub/project-types/ and immediately available
  as a type option in tool_create_project and /project-hub:new-project.
  Use when: (1) User says "neuen Projekttyp anlegen", "custom project type", "eigenen Typ erstellen",
  (2) User explicitly invokes `/project-hub:type-creator`,
  (3) User picks "Manage Project Types → Create" from /project-hub:configure.
model: claude-haiku-4-5
user-invocable: true
---

# Type Creator

Guided wizard for creating a custom project type.

## Workflow

### 1. Show existing types

Use MCP tool `tool_list_project_types()` and display a compact overview:

```
## Vorhandene Projekttypen

| Typ | Quelle | Beschreibung |
|-----|--------|-------------|
| consulting | built-in | Client consulting project |
| it-project | built-in | Internal IT project |
| ... | ... | ... |
| my-type | custom | My custom type |
```

### 2. Ask for the name

Use `AskUserQuestion`:
- Free text: "Wie soll der neue Projekttyp heißen?"
- Note: The name will be slugified (e.g. "HR Onboarding" → "hr-onboarding")

If the slugified name already exists → show error and ask again.

### 3. Ask for description

Use `AskUserQuestion`:
- Free text: "Kurze Beschreibung (ein Satz):"
- This description appears in the type listing.

### 4. Ask for phases (optional)

Use `AskUserQuestion`:
- **Phasen eingeben** — Enter phase names (one per line or comma-separated)
- **Keine Phasen** — Skip phases

If "Phasen eingeben":
- Free text prompt: "Gib die Phasen ein, eine pro Zeile (z.B. 'Intake, Analyse, Umsetzung'):"
- Parse comma-separated or newline-separated input into a list

### 5. Ask for typical contacts (optional)

Use `AskUserQuestion`:
- **Kontaktrollen eingeben** — Enter typical contact roles
- **Keine Rollen** — Skip contacts

If "Kontaktrollen eingeben":
- Free text: "Typische Kontaktrollen (eine pro Zeile oder kommagetrennt):"
- Parse into a list

### 6. Confirm and create

Show a preview before creating:

```
## Vorschau: Neuer Projekttyp

**Name:** hr-onboarding
**Label:** HR Onboarding
**Beschreibung:** Employee onboarding and HR processes

**Phasen:**
1. Intake
2. Onboarding
3. Integration

**Kontaktrollen:**
- HR Manager
- Team Lead
- IT Admin
```

Use `AskUserQuestion`:
- **Erstellen** — Create the type
- **Abbrechen** — Cancel

### 7. Create via MCP

Call `tool_create_project_type(name, description, phases, contacts)`.

On success:
```
Projekttyp "hr-onboarding" erstellt unter:
~/.project-hub/project-types/hr-onboarding/

Du kannst ihn jetzt bei /project-hub:new-project oder tool_create_project verwenden.
```

If `overrides_builtin: true`:
```
Hinweis: Dieser Typ überschreibt den gleichnamigen built-in Typ.
```

On error:
- Show the error message
- Offer to try again with a different name

### 8. Offer next step

Use `AskUserQuestion`:
- **Weiteren Typ erstellen** — Back to step 2
- **Neues Projekt mit diesem Typ anlegen** → invoke `/project-hub:new-project`
- **Fertig** — End skill
