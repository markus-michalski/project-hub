---
name: delete-testdata
description: |
  Fully tears down the zz-sandbox- test fixtures (project, contact, note — cascades automatically),
  for a clean decommission or full reset. Idempotent: a call against an already-empty sandbox is a
  clean no-op, never an error. Enforces a zz-sandbox- prefix gate — refuses and stops before any
  lookup if the target does not carry the prefix, the highest-blast-radius of the three testdata
  skills. Use when: (1) skill-rollout's rollout pipeline or onboarding live-verification needs to
  tear down or verify this guard, (2) explicit "/project-hub:delete-testdata". Never triggers from
  ordinary conversation.
model: claude-sonnet-4-6
user-invocable: true
disable-model-invocation: true
---

# Delete Test Data

Fully removes the `zz-sandbox-` fixture set. This is the **highest blast radius** of the three testdata
skills — it is the one skill-rollout's onboarding calls with a synthetic, provably-nonexistent,
non-prefixed slug to live-verify the prefix guard actually works before trusting any of the three
skills for automated use. Companion skills: `create-testdata`, `reset-testdata`. Full convention:
skill-rollout's `reference/self-improving-skills.md`, section "create-testdata / reset-testdata /
delete-testdata Convention" (issue #35).

## Argument

`target` (optional, defaults to `zz-sandbox-project`) — the project slug/name to tear down.

## Workflow

### 1. Prefix gate — mandatory, first, unconditional, before ANY tool call

Confirm `target` starts with the literal `zz-sandbox-` prefix. **If it does not, refuse and stop
immediately — do not call `tool_get_project`, do not call anything else.** This is the exact check
skill-rollout's onboarding live-verifies: it calls this skill once with a synthetic,
provably-nonexistent, non-`zz-sandbox-` slug and expects this refusal to fire before any lookup
happens. Never weaken this to "check after looking it up" — the whole safety property depends on
refusing before any tool call can touch real data, not on the lookup itself happening to fail.

### 2. Look up the target — idempotent no-op if absent

Call `tool_get_project(target)`. **If not found: this is a clean, expected outcome, not an error.**
Report "nothing to delete" and stop here. `delete-testdata` must never error on an empty sandbox — a
freshly-cleaned sandbox calling this skill again is the normal case skill-rollout's fixed test sequence
(check → delete unconditionally → create → reset) relies on.

### 3. Delete — full teardown, one call

`tool_delete_project(target)`. Deleting the project cascades to its contacts, notes, and any
project-links automatically (`ON DELETE CASCADE` in project-hub's schema) — do not delete contacts/
notes individually first, the cascade already covers them in this one call.

### 4. Confirm via independent read

Call `tool_get_project(target)` again and confirm it now returns nothing. Never trust step 3's own
return value as the only evidence of deletion.

```
## Test-Fixtures entfernt

**Projekt:** <target> — vollständig gelöscht (inkl. Kontakte/Notizen via Cascade)
```

If step 2 found nothing, report instead:

```
## Keine Test-Fixtures vorhanden

Nichts zu löschen — <target> existiert nicht.
```
