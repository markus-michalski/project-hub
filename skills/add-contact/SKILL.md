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

### 2. Collect Contact Details

Ask in a natural, conversational way:

**Required:**
- Name
- Type: internal (own organization) or external (merchant, client, vendor, partner)
- Role (e.g. Onboarding PM, Tech Lead, Account Manager, Merchant PM, Legal)

**Optional:**
- Email address
- Phone number
- Company (relevant for external contacts)
- Notes (anything worth remembering)

For `merchant-onboarding` projects, suggest standard roles based on type:
- Internal: Onboarding PM, Technical Implementation Manager, Account Manager, Legal/Compliance, Risk
- External: Merchant PM, Merchant Technical Contact, Merchant Legal/Commercial

### 3. Save Contact

Use MCP `tool_add_contact(project_id, name, role, contact_type, email, phone, company, notes)`.

### 4. Output

```
## Kontakt hinzugefügt

**Name:** [Name]
**Rolle:** [Rolle]
**Typ:** [Intern / Extern]
**E-Mail:** [Email oder "—"]
**Telefon:** [Phone oder "—"]
**Firma:** [Company oder "—"]

Möchtest du noch einen Kontakt hinzufügen?
```

### 5. Allow Adding More

Ask if user wants to add another contact. If yes, repeat from step 2.
