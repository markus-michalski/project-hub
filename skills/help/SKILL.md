---
name: help
description: |
  Show all available PROJECT-HUB skills and how to use them. Use ONLY for project-hub-specific
  help — multiple plugins have help skills.
  Use when: (1) User says "Hub-Hilfe", "project-hub help", "welche Hub-Skills gibt es",
  (2) User explicitly invokes `/project-hub:help`,
  (3) Context is clearly about the project-hub plugin.
  Do NOT trigger on bare "Hilfe" / "Help" — defer.
model: claude-haiku-4-5
user-invocable: true
---

# Help

Show all available skills and current project context.

## Workflow

### 1. Load Session

Use MCP `tool_get_session()` to show active project (if any).

### 2. Output

```
## Project Hub — Hilfe

[If active project:]
**Aktives Projekt:** [Name] ([Typ] | [Phase])

---

### Projekte verwalten
| Skill | Beschreibung |
|-------|-------------|
| `/new-project [name]` | Neues Projekt anlegen |
| `/resume [name]` | Projekt laden / wechseln |
| `/dashboard` | Alle Projekte in der Übersicht |
| `/status` | Aktuelles Projekt anzeigen & aktualisieren |

### Daten erfassen
| Skill | Beschreibung |
|-------|-------------|
| `/add-contact` | Kontakt hinzufügen (intern oder extern) |
| `/add-note [type]` | Notiz, Meeting-Protokoll, E-Mail oder Entscheidung speichern |

### Kommunikation
| Skill | Beschreibung |
|-------|-------------|
| `/summarize [note-id]` | Summary aus E-Mail oder Meeting-Notizen erstellen |
| `/compose [email\|slack\|teams]` | E-Mail, Slack- oder Teams-Nachricht verfassen |

### Knowledge Base
| Skill | Beschreibung |
|-------|-------------|
| `/knowledge` | Alle Knowledge-Dokumente anzeigen |
| `/knowledge show <topic>` | Governance / Prozess / Rollen anzeigen |
| `/knowledge update <topic>` | Dokument mit neuen Inhalten aktualisieren |
| `/knowledge export <topic>` | Confluence-fertigen Export erstellen |

---

### Note-Typen für `/add-note`
- `note` — allgemeine Notiz
- `meeting-notes` — Meeting-Protokoll (kann Agenda enthalten)
- `email` — E-Mail-Korrespondenz ablegen
- `decision` — Entscheidung dokumentieren
- `action-item` — Aufgabe mit Verantwortlichem

### Projekttypen
- `merchant-onboarding` — Merchant Onboarding (BNPL, Direct Debit, ...)
- `it-project` — IT / Software Projekt
- `marketing` — Marketing Kampagne
- `consulting` — Consulting Engagement
- `event` — Veranstaltungsplanung
- `generic` — Allgemeines Projekt

---

Alle Skills arbeiten im Kontext des aktiven Projekts.
Starte mit `/new-project` oder `/resume` um ein Projekt zu laden.
```
