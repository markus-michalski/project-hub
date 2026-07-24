---
name: create-testdata
description: |
  Creates disposable zz-sandbox- prefixed test fixtures (one project, one contact, one note) via
  project-hub's own real MCP tools, for skill-rollout's live-tier sandbox testing. Enforces a
  zz-sandbox- prefix gate before touching anything. Use when: (1) skill-rollout's onboarding or
  rollout pipeline needs sandbox fixtures for this plugin, (2) explicit "/project-hub:create-testdata".
  Never triggers from ordinary conversation — this is machine-invoked test infrastructure, not a
  user-facing feature.
model: claude-sonnet-4-6
user-invocable: true
disable-model-invocation: true
---

# Create Test Data

Creates the `zz-sandbox-` disposable fixture set (one project, one contact, one note) via project-hub's
real creation tools — never hand-written database rows, so there is no schema-drift risk between the
fixture and what the plugin's own tools actually produce. Companion skills: `reset-testdata`,
`delete-testdata`. Full convention: skill-rollout's `reference/self-improving-skills.md`, section
"create-testdata / reset-testdata / delete-testdata Convention" (issue #35).

## Fixed fixture identifiers

- Project: name/slug `zz-sandbox-project`
- Contact: name `zz-sandbox-contact`
- Note: title `zz-sandbox-note`

These exact names are the whole contract — `reset-testdata` and `delete-testdata` look up entities by
these same fixed names. Do not vary them.

## Workflow

### 1. Prefix gate — mandatory, first, unconditional

Before calling any MCP tool: confirm every identifier this skill is about to create starts with the
literal `zz-sandbox-` prefix (all three fixed names above do, by construction). If ever asked to create
a fixture under any other name, refuse and stop — never create test data outside the `zz-sandbox-`
namespace.

### 2. Refuse to duplicate — check existence first

Call `tool_get_project("zz-sandbox-project")`. If it already exists, refuse and stop: report that the
sandbox is already provisioned and instruct the caller to run `delete-testdata` first. Never attempt to
re-create over an existing fixture — project-hub's `slug` column is `UNIQUE`, so a duplicate
`tool_create_project` call would fail anyway, and silently working around that (e.g. reusing the
existing row) would defeat the point of a clean, known fixture.

### 3. Create the project

**Every optional field is set explicitly to the `zz-sandbox-baseline` marker, never left empty.**
`tool_update_project`/`tool_update_contact`/`tool_update_note` silently ignore empty-string values
(they filter out anything falsy before writing — an empty string means "don't touch this field", not
"clear it"). If a field starts out truly empty, `reset-testdata` can never restore it to that state
later, since it can only call those same update tools. Starting every field at a real, non-empty
baseline value keeps `create-testdata` and `reset-testdata` producing identical, verifiable state.

```
tool_create_project(
  name="zz-sandbox-project",
  project_type="generic",
  description="Disposable test fixture for skill-rollout live-tier testing (project-hub#82). Managed exclusively by create-testdata/reset-testdata/delete-testdata — do not edit manually.",
  market="zz-sandbox-baseline",
  products="zz-sandbox-baseline",
  phase="zz-sandbox-baseline",
  budget="zz-sandbox-baseline",
  notes="zz-sandbox-baseline",
)
```

### 4. Create the contact

```
tool_add_contact(
  project_id=<id from step 3>, name="zz-sandbox-contact", role="QA Bot", contact_type="internal",
  email="zz-sandbox-baseline", phone="zz-sandbox-baseline", company="zz-sandbox-baseline", notes="zz-sandbox-baseline",
)
```

### 5. Create the note

```
tool_add_note(
  project_id=<id from step 3>, title="zz-sandbox-note",
  content="Baseline fixture note — reset by reset-testdata to this exact text.",
  note_type="note", agenda="zz-sandbox-baseline",
)
```

### 6. Confirm and report

Independently re-read what was just created — `tool_get_project("zz-sandbox-project")`,
`tool_list_contacts(project_id)`, `tool_list_notes(project_id)` — never trust the create calls' own
return values as the only evidence the entities actually persisted.

```
## Test-Fixtures angelegt

**Projekt:** zz-sandbox-project (id: <id>)
**Kontakt:** zz-sandbox-contact (id: <id>)
**Notiz:** zz-sandbox-note (id: <id>)
```

Return these three slugs/IDs as the skill's result — skill-rollout's onboarding and rollout pipeline
record them.
