---
name: add-contact
description: |
  Add a contact (internal or external) to the active project.
  Use when: user wants to add a person, stakeholder, or contact to the current project.
model: claude-sonnet-4-6
user-invocable: true
---

# Add Contact

Add an internal or external contact to the active project.

## Workflow

### 1. Check Active Project

Use MCP `tool_get_session()`.
If no active project → "Kein aktives Projekt. Bitte zuerst `/resume` oder `/new-project`."

### 2. Ask for the Name — Then Check for Duplicates, ALWAYS

Ask for the contact's name first, before collecting anything else.

Then call `tool_search_contacts(name, project_id=0)` unconditionally — not only when the
user explicitly asks to see existing contacts first. `project_id=0` searches name, role,
email, and company across **every** project (including shared contacts), case-insensitive,
with no pagination limit — unlike `tool_list_contacts`/`tool_list_shared_contacts`, which
default to 50 results per page and can silently miss a match once a project or the shared
directory grows past that. Skipping this search is exactly how duplicate contacts get
created ([project-hub#56](https://github.com/markus-michalski/project-hub/issues/56)).

If a match is found, say so and ask whether the user meant to update that existing entry
instead (→ step 3 pre-filled with its current values, saved via `tool_update_contact`
instead of `tool_add_contact`). Only continue to step 3 as a genuinely new contact once
it's clear there's no match.

### 3. Collect Remaining Details

Ask in a natural, conversational way:

**Required:**
- Type: internal (own organization) or external (merchant, client, vendor, partner)
- Role (e.g. Onboarding PM, Tech Lead, Account Manager, Merchant PM, Legal)

**Optional:**
- Email address — if provided and it wasn't already covered by the step 2 search, run
  `tool_search_contacts(email, project_id=0)` too before saving. An email match can surface
  a contact registered under a completely different name.
- Phone number
- Company (relevant for external contacts)
- Notes (anything worth remembering)

For `merchant-onboarding` projects, suggest standard roles based on type:
- Internal: Onboarding PM, Technical Implementation Manager, Account Manager, Legal/Compliance, Risk
- External: Merchant PM, Merchant Technical Contact, Merchant Legal/Commercial

**For internal contacts:** Ask if this person works on multiple projects (e.g. a colleague who is involved in all client projects):
- If yes → set `is_shared=True` so they appear in all projects automatically
- If no → leave default (`is_shared=False`)

External contacts are always project-specific and should never be shared.

### 4. Save Contact

Use MCP `tool_add_contact(project_id, name, role, contact_type, email, phone, company, notes, is_shared)`.

**Before adding a shared contact, search first:** `tool_search_contacts(query=<lastname>, project_id=0)`.
Search by surname, not by the exact spelling in front of you — the same person often
appears as "Jan Kalle Wulf" in one source and "Jan-Kalle Wulf" in another. If they
already exist as a shared contact, update that contact instead of creating a new one.

#### Duplicate warnings

`tool_add_contact` refuses a contact whose name matches an existing shared contact:

- **"A shared contact with this name or email already exists"** — the names are the same
  once spelling variants are folded away. Use the existing contact; there is nothing to
  add. This cannot be forced.
- **"A shared contact with a very similar name already exists"** — a heuristic match
  (e.g. `Mathias` / `Matthias`, or a dropped middle name). Usually the same person.

**Important:** Never call with `force=True` without explicit user confirmation. Show the
user the existing contact the error names and ask whether it is the same person. If they
confirm it is someone else, retry with `force=True`. Never set `force=True` merely to
make the error go away.

### 5. Output

```
## Kontakt hinzugefügt

**Name:** [Name]
**Rolle:** [Rolle]
**Typ:** [Intern / Extern]
**Geteilt:** [Ja — in allen Projekten verfügbar / Nein]
**E-Mail:** [Email oder "—"]
**Telefon:** [Phone oder "—"]
**Firma:** [Company oder "—"]

Möchtest du noch einen Kontakt hinzufügen?
```

### 6. Allow Adding More

Ask if user wants to add another contact. If yes, repeat from step 2 — the duplicate check
must run again for each new contact, not just the first one in the session.
