---
name: reset-testdata
description: |
  Resets the zz-sandbox- test fixtures back to their documented baseline state, without deleting
  them, undoing whatever mutations a live-tier rollout run left behind. Enforces a zz-sandbox- prefix
  gate before touching anything. Use when: (1) skill-rollout's rollout pipeline needs a clean fixture
  state between runs, (2) explicit "/project-hub:reset-testdata". Never triggers from ordinary
  conversation — this is machine-invoked test infrastructure, not a user-facing feature.
model: claude-sonnet-4-6
user-invocable: true
disable-model-invocation: true
---

# Reset Test Data

Resets the `zz-sandbox-` fixtures (project, contact, note — created by `create-testdata`) back to
their documented baseline field values, **without deleting any of them** — they remain as reusable
fixtures across many rollout runs. Companion skills: `create-testdata`, `delete-testdata`. Full
convention: skill-rollout's `reference/self-improving-skills.md`, section "create-testdata /
reset-testdata / delete-testdata Convention" (issue #35).

## Baseline values

**No field is ever reset to an empty string.** `tool_update_project`/`tool_update_contact`/
`tool_update_note` treat an empty-string argument as "leave this field unchanged" (they filter out
falsy values before writing) — passing `""` to clear a field is silently a no-op, not a reset. Every
optional field's baseline is instead the literal marker `zz-sandbox-baseline`, which `create-testdata`
also uses at creation time, so both skills produce identical, verifiable state.

| Entity | Field | Baseline |
|--------|-------|----------|
| Project (`zz-sandbox-project`) | `status` | `active` |
| | `phase` | `zz-sandbox-baseline` |
| | `description` | `Disposable test fixture for skill-rollout live-tier testing (project-hub#82). Managed exclusively by create-testdata/reset-testdata/delete-testdata — do not edit manually.` |
| | `market` / `products` / `budget` / `notes` | `zz-sandbox-baseline` |
| Contact (`zz-sandbox-contact`) | `role` | `QA Bot` |
| | `contact_type` | `internal` |
| | `email` / `phone` / `company` / `notes` | `zz-sandbox-baseline` |
| Note (`zz-sandbox-note`) | `content` | `Baseline fixture note — reset by reset-testdata to this exact text.` |
| | `note_type` | `note` |
| | `agenda` | `zz-sandbox-baseline` |

## Workflow

### 1. Prefix gate — mandatory, first, unconditional

Before calling any MCP tool: confirm the target is exactly `zz-sandbox-project` (and, for its contact/
note, that their name/title carries the `zz-sandbox-` prefix and they belong to that project). If ever
asked to reset anything else, refuse and stop.

### 2. Confirm the fixture exists

Call `tool_get_project("zz-sandbox-project")`. If not found, refuse and stop: report there is nothing
to reset and instruct the caller to run `create-testdata` first.

### 3. Reset the project fields

```
tool_update_project(
  identifier="zz-sandbox-project",
  status="active", phase="zz-sandbox-baseline",
  description="Disposable test fixture for skill-rollout live-tier testing (project-hub#82). Managed exclusively by create-testdata/reset-testdata/delete-testdata — do not edit manually.",
  market="zz-sandbox-baseline", products="zz-sandbox-baseline", budget="zz-sandbox-baseline", notes="zz-sandbox-baseline",
)
```

### 4. Reset the contact

Find it via `tool_list_contacts(project_id)`, filtering for `name == "zz-sandbox-contact"`. **Before
touching it, confirm its name literally carries the `zz-sandbox-` prefix** — if a differently-named
contact is ever found instead (should never happen given `create-testdata`'s fixed names, but never
assume), refuse and stop, do not update it. Then:

```
tool_update_contact(
  contact_id=<id>, role="QA Bot", contact_type="internal",
  email="zz-sandbox-baseline", phone="zz-sandbox-baseline", company="zz-sandbox-baseline", notes="zz-sandbox-baseline",
)
```

### 5. Reset the note

Find it via `tool_list_notes(project_id)`, filtering for `title == "zz-sandbox-note"`. Same prefix
check as step 4 before touching it. Then:

```
tool_update_note(
  note_id=<id>, content="Baseline fixture note — reset by reset-testdata to this exact text.",
  note_type="note", agenda="zz-sandbox-baseline",
)
```

### 6. Confirm and report

Independently re-read (`tool_get_project`, `tool_list_contacts`, `tool_list_notes`) and confirm all
three entities **still exist** — reset must never delete, that is `delete-testdata`'s job, and the two
skills must stay behaviorally distinct — and their fields now match the baseline table above.

```
## Test-Fixtures zurückgesetzt

**Projekt:** zz-sandbox-project — zurückgesetzt auf Baseline
**Kontakt:** zz-sandbox-contact — zurückgesetzt auf Baseline
**Notiz:** zz-sandbox-note — zurückgesetzt auf Baseline
```
