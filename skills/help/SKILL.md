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

### 2. Load Project Types

Use MCP `tool_list_project_types()` to get the full list of project types (built-in and
custom, e.g. created via `/project-hub:type-creator`) for the "Projekttypen" section below.

### 3. Output

```
## Project Hub — Hilfe

[If active project:]
**Aktives Projekt:** [Name] ([Typ] | [Phase])

---

### Projekte verwalten
| Skill | Beschreibung |
|-------|-------------|
| `/project-hub:new-project [name]` | Neues Projekt anlegen |
| `/project-hub:resume [name]` | Projekt laden / wechseln |
| `/project-hub:dashboard` | Alle Projekte in der Übersicht |
| `/project-hub:status` | Aktuelles Projekt anzeigen & aktualisieren |
| `/project-hub:session-start` | Geführte Session-Initialisierung: Setup prüfen, Projekt wählen, Kontext laden |
| `/project-hub:next-step` | Nächsten Schritt für aktives Projekt anzeigen (offene Action-Items, Fristen) |

### Daten erfassen
| Skill | Beschreibung |
|-------|-------------|
| `/project-hub:add-contact` | Kontakt hinzufügen (intern oder extern) |
| `/project-hub:add-note [type]` | Notiz, Meeting-Protokoll, E-Mail oder Entscheidung speichern |
| `/project-hub:edit-note [note-id]` | Bestehende Notiz korrigieren oder aktualisieren |

### Kommunikation
| Skill | Beschreibung |
|-------|-------------|
| `/project-hub:summarize [note-id]` | Summary aus E-Mail oder Meeting-Notizen erstellen |
| `/project-hub:compose [email\|slack\|teams\|export\|import]` | E-Mail/Slack/Teams verfassen, oder Projekt exportieren/importieren |
| `/project-hub:report [full\|summary\|all-projects]` | HTML-Report für aktuelles Projekt oder alle Projekte erstellen |

### Knowledge Base
| Skill | Beschreibung |
|-------|-------------|
| `/project-hub:knowledge` | Übersicht aller Topics für den aktuellen Projekttyp |
| `/project-hub:knowledge list [project-type]` | Knowledge-Topics auflisten |
| `/project-hub:knowledge show <topic>` | Governance / Prozess / Rollen anzeigen |
| `/project-hub:knowledge update <topic>` | Dokument mit neuen Inhalten aktualisieren |
| `/project-hub:knowledge export <topic>` | Confluence-fertigen Export erstellen |
| `/project-hub:knowledge delete <topic>` | Knowledge-Topic löschen (nach Bestätigung) |
| `/project-hub:knowledge sync [--force]` | Installierte Knowledge mit gebündelten Plugin-Templates abgleichen |

### Suche
| Skill | Beschreibung |
|-------|-------------|
| `/project-hub:search <query>` | Notizen und Kontakte projektübergreifend durchsuchen |

### Einrichtung & Sonstiges
| Skill | Beschreibung |
|-------|-------------|
| `/project-hub:configure` | Hub-Einstellungen ändern (Name, Sprache, docs-Pfad, ...) |
| `/project-hub:type-creator` | Neuen eigenen Projekttyp anlegen |
| `/project-hub:get-template [project-type]` | Ausfüllbare Projektvorlage holen (außerhalb des Chats befüllen, später importieren) |
| `/project-hub:setup` | Erstmaliges Setup für project-hub (venv, Dependencies, Config) |
| `/project-hub:help` | Diese Übersicht erneut anzeigen |

---

### Note-Typen für `/project-hub:add-note`
- `note` — allgemeine Notiz
- `meeting-notes` — Meeting-Protokoll (kann Agenda enthalten)
- `email` — E-Mail-Korrespondenz ablegen
- `decision` — Entscheidung dokumentieren
- `action-item` — Aufgabe mit Verantwortlichem

### Projekttypen
[Aus tool_list_project_types() rendern, eine Zeile pro Eintrag: `- \`{name}\` — {description}`,
custom Typen (z. B. via `/project-hub:type-creator` angelegt) zusätzlich mit „(custom)" markieren.]

---

Alle Skills arbeiten im Kontext des aktiven Projekts.
Starte mit `/project-hub:new-project`, `/project-hub:resume` oder `/project-hub:session-start` um ein Projekt zu laden.
```
