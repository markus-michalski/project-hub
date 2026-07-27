# Vacation Handover Template — Client Onboarding

> **Template file** — used by `/project-hub:vacation-handover` to auto-generate handover documents.
> Fields marked `{{LIKE_THIS}}` are filled automatically from project-hub data.
> Fields marked `[like this]` are derived from notes or require manual input.
>
> To produce a filled handover: `/project-hub:vacation-handover [start-date] [end-date]`
> To export to Confluence after generation: say "Export to Confluence"

---

## Vacation Handover – {{AUTHOR_NAME}}

**Role:** Enterprise Client Onboarding Project Manager
**Vacation Dates:** {{VACATION_START}} – {{VACATION_END}}

---

<!-- REPEAT per open project — the skill generates one block per active project -->

### Customer: {{PROJECT_NAME}}

#### Current Status

- **Onboarding Type:** [Direct / Partner Adyen / Partner Mollie / Partner Stripe / other]
- **Onboarding Phase:** {{PROJECT_PHASE}}
- **Summary:**
  - [Key facts from project description and recent notes]
  - [Current blockers or open topics]
  - [Expected next milestone]

#### ToDo

- [Open action items from project-hub notes — or: none]

#### Upcoming Meetings / Workshops

- [Meeting name, recurrence, time — or: none]

#### Pending Deliverables

- [Deliverable description with planned date — or: none]

#### Risks & Issues

- [Risk or issue description — or: none]

#### 👥 Key Contacts

**Internal:**

| Role | Name / Slack |
|---|---|
| Commercial | [name / @slack-handle] |
| Technical Integration | [name / @slack-handle] |
| Partner Manager | [name / @slack-handle] |
| Technical Support | [name / @slack-handle] |
| Growth | [name / @slack-handle] |

**External — Merchant:**

| Name | Role | Email | Phone |
|---|---|---|---|
| [Name] | [Role] | [email@domain.com] | [+49 xxx] |

**External — Partner (if applicable):**

| Name | Role | Email |
|---|---|---|
| [Name] | Partner Manager | [email@partner.com] |

#### 🔗 Tools & Links

- **Teams Channel:** [link from contacts or notes]
- **JIRA:** [COEOPM-XXXX: Ticket Title — STATUS]

---
<!-- END REPEAT -->

## Change Log

| Date | Change | Author |
|---|---|---|
| {{TODAY}} | Template created | Markus Michalski |
