# Claude Code Project Assistant Agents

**Status:** 🚧 In Planung / Noch keine Agents

Spezialisierte Claude Code Agents, die dich als **persönlicher Projekt-Assistent** unterstützen.

## 📋 Übersicht

Dieses Repository wird **professionelle** Claude Code Agents enthalten, die dich bei täglichen Projekt-Management-Aufgaben unterstützen - als wäre ein persönlicher Assistent an deiner Seite.

## 🎯 Geplante Agents

### 1. Document Analyst
**Plugin:** `document-analyst`

**Was macht der Agent?**
- Analysiert Projektdokumente (Requirements, Spezifikationen, Meeting Notes)
- Extrahiert wichtige Informationen und Key Points
- Identifiziert Action Items und Verantwortlichkeiten
- Erstellt strukturierte Zusammenfassungen
- Vergleicht Dokument-Versionen und zeigt Änderungen

**Use Cases:**
- "Analysiere dieses Requirements-Dokument und fasse die wichtigsten Punkte zusammen"
- "Extrahiere alle Action Items aus diesen Meeting Notes"
- "Vergleiche Version 1 und Version 2 der Spezifikation"

### 2. Timeline Planner
**Plugin:** `timeline-planner`

**Was macht der Agent?**
- Erstellt Projekt-Timelines aus Task-Listen
- Berechnet Ressourcen-Kapazitäten
- Identifiziert Bottlenecks und kritische Pfade
- Managed Abhängigkeiten zwischen Tasks
- Erstellt Gantt-Charts und Roadmaps

**Use Cases:**
- "Erstelle einen Timeline-Plan für diese 20 Tasks mit 3 Entwicklern"
- "Berechne die Kapazität für Q1 2025 basierend auf diesen Aufgaben"
- "Identifiziere Bottlenecks in diesem Projektplan"

### 3. Meeting Facilitator
**Plugin:** `meeting-facilitator`

**Was macht der Agent?**
- Bereitet Meeting-Agendas vor
- Erstellt Meeting-Briefs mit Context und Zielen
- Generiert Diskussionspunkte basierend auf Input
- Produziert strukturierte Meeting-Protokolle
- Trackt Follow-up Actions aus Meetings

**Use Cases:**
- "Bereite eine Agenda für das Sprint Planning Meeting vor"
- "Erstelle ein Meeting-Brief für das Stakeholder-Update"
- "Wandle diese Meeting-Notizen in ein strukturiertes Protokoll um"

### 4. Report Generator
**Plugin:** `report-generator`

**Was macht der Agent?**
- Generiert Status-Reports (wöchentlich/monatlich)
- Erstellt Executive Summaries
- Produziert Stakeholder-Updates
- Erstellt Project Dashboards
- Visualisiert Daten (Markdown-Tables, Charts)

**Use Cases:**
- "Erstelle einen Weekly Status Report basierend auf diesen Daten"
- "Generiere ein Executive Summary für das Management"
- "Erstelle ein Stakeholder-Update mit den wichtigsten Achievements"

### 5. Task Coordinator
**Plugin:** `task-coordinator`

**Was macht der Agent?**
- Trackt Action Items über mehrere Projekte
- Managed Follow-ups und Deadlines
- Koordiniert cross-team Dependencies
- Stellt Accountability sicher
- Priorisiert Tasks nach Dringlichkeit

**Use Cases:**
- "Zeige mir alle offenen Action Items aus den letzten 3 Meetings"
- "Erstelle eine Follow-up-Liste für diese Woche"
- "Priorisiere diese 15 Tasks nach Wichtigkeit und Abhängigkeiten"

### 6. Decision Tracker
**Plugin:** `decision-tracker`

**Was macht der Agent?**
- Dokumentiert Entscheidungen strukturiert
- Trackt Decision History über Zeit
- Managed Decision Logs (ADR - Architecture Decision Records)
- Stellt Follow-through sicher
- Identifiziert offene Entscheidungen

**Use Cases:**
- "Dokumentiere diese Entscheidung als ADR"
- "Zeige alle Entscheidungen zum Thema 'API-Design'"
- "Welche Entscheidungen sind noch offen?"

### 7. Project Assistant (All-in-One)
**Plugin:** `project-assistant-full`

Lädt alle oben genannten Agents für vollständige Assistenz.

## 📁 Repository-Struktur

```
claude-agents-project-management/
├── .claude-plugin/
│   └── marketplace.json    # Plugin-Konfiguration (fertig)
├── agents/
│   ├── document-analyst.md           # (noch zu erstellen)
│   ├── timeline-planner.md           # (noch zu erstellen)
│   ├── meeting-facilitator.md        # (noch zu erstellen)
│   ├── report-generator.md           # (noch zu erstellen)
│   ├── task-coordinator.md           # (noch zu erstellen)
│   └── decision-tracker.md           # (noch zu erstellen)
└── README.md
```

## 🚀 Installation (Future)

Sobald die Agents erstellt sind:

### Variante 1: Als Claude Code Marketplace Plugin

```bash
# In Claude Code
/add marketplace https://github.com/markus-michalski/claude-agents-project-management
```

### Variante 2: Manuelle Installation

```bash
# 1. Plugin-Verzeichnis erstellen
mkdir -p ~/.claude/plugins/marketplaces/project-assistant-pro/.claude-plugin
mkdir -p ~/.claude/plugins/marketplaces/project-assistant-pro/agents

# 2. Plugin-Dateien kopieren
cp /home/markus/projekte/claude/claude-agents-project-management/.claude-plugin/marketplace.json \
   ~/.claude/plugins/marketplaces/project-assistant-pro/.claude-plugin/
cp /home/markus/projekte/claude/claude-agents-project-management/agents/*.md \
   ~/.claude/plugins/marketplaces/project-assistant-pro/agents/

# 3. Plugin in settings.json aktivieren
```

Füge folgendes in `~/.claude/settings.json` ein:

```json
{
  "enabledPlugins": {
    "document-analyst@project-assistant-pro": true,
    "timeline-planner@project-assistant-pro": true,
    "meeting-facilitator@project-assistant-pro": true,
    "report-generator@project-assistant-pro": true,
    "task-coordinator@project-assistant-pro": true,
    "decision-tracker@project-assistant-pro": true,
    "project-assistant-full@project-assistant-pro": true
  }
}
```

## 📖 Verwendung (Future)

### Mit Task-Tool

```typescript
// Document Analyst
Task({
  subagent_type: "document-analyst:document-analyst-pro",
  prompt: "Analysiere diese Requirements und extrahiere alle Action Items",
  description: "Analyze requirements document"
})

// Timeline Planner
Task({
  subagent_type: "timeline-planner:timeline-planner-pro",
  prompt: "Erstelle einen Timeline-Plan für diese 15 Tasks",
  description: "Create timeline plan"
})

// Meeting Facilitator
Task({
  subagent_type: "meeting-facilitator:meeting-facilitator-pro",
  prompt: "Bereite eine Agenda für das Sprint Planning vor",
  description: "Prepare meeting agenda"
})
```

## 🎯 Agent-Entwicklung - Nächste Schritte

### Phase 1: Research & Content-Sammlung

Für jeden Agent muss folgendes recherchiert werden:

#### Document Analyst
- Document Analysis Frameworks
- Information Extraction Techniques
- Summarization Best Practices
- Action Item Identification Patterns
- Markdown Formatting Standards

#### Timeline Planner
- Project Scheduling Methodologies (CPM, PERT)
- Resource Capacity Planning Formulas
- Dependency Management Patterns
- Gantt Chart Best Practices
- Markdown Timeline Formats (Mermaid Gantt)

#### Meeting Facilitator
- Agenda Templates (verschiedene Meeting-Typen)
- Meeting Brief Structures
- Protocol Standards
- Action Item Tracking Patterns
- Timeboxing Techniques

#### Report Generator
- Status Report Templates
- Executive Summary Formats
- Stakeholder Communication Patterns
- Data Visualization in Markdown
- KPI Dashboard Designs

#### Task Coordinator
- Task Management Frameworks (GTD, Eisenhower Matrix)
- Follow-up Tracking Systems
- Dependency Coordination Patterns
- Priority Frameworks (MoSCoW, RICE)
- Accountability Patterns (RACI)

#### Decision Tracker
- ADR (Architecture Decision Records) Format
- Decision Log Templates
- Decision Matrix Frameworks
- Follow-through Tracking
- Historical Context Documentation

### Phase 2: Agent-Erstellung

Jeder Agent sollte enthalten:

```markdown
# [Agent Name]

## Role & Expertise
[Was kann der Agent? Welche Rolle nimmt er ein?]

## Core Capabilities
[Hauptfähigkeiten des Agents]

## Document Templates
[Vorlagen für verschiedene Output-Formate]

## Best Practices
[Best Practices für die jeweilige Aufgabe]

## Workflow Patterns
[Typische Workflows und Prozesse]

## Output Formats
[Standard-Formate für Output (Markdown, Tables, etc.)]

## Examples
[Real-World Beispiele mit Input/Output]

## Common Pitfalls
[Was sollte vermieden werden?]

## Integration Points
[Wie arbeitet der Agent mit anderen Agents zusammen?]
```

### Phase 3: Testing & Iteration

1. **Real-World Testing**
   - Teste jeden Agent mit echten Projekt-Daten
   - Sammle Feedback zu Output-Qualität
   - Iteriere basierend auf Erfahrungen

2. **Cross-Agent Integration**
   - Teste Zusammenarbeit zwischen Agents
   - z.B. Meeting Facilitator → Task Coordinator → Timeline Planner

3. **Template Refinement**
   - Verbessere Templates basierend auf Usage
   - Füge neue Templates hinzu

## 🔧 marketplace.json Struktur

Die `marketplace.json` ist vorbereitet mit 7 Plugins:

1. **`document-analyst`** - Dokumentenanalyse
2. **`timeline-planner`** - Timeline & Kapazitätsplanung
3. **`meeting-facilitator`** - Meeting-Vorbereitung
4. **`report-generator`** - Report-Erstellung
5. **`task-coordinator`** - Task-Koordination
6. **`decision-tracker`** - Entscheidungsdokumentation
7. **`project-assistant-full`** - Alle Agents kombiniert

**Vorteil:** Du kannst einzelne Agents aktivieren oder alle zusammen nutzen!

## 📝 TODO

- [ ] Document Analyst Agent erstellen (`agents/document-analyst.md`)
- [ ] Timeline Planner Agent erstellen (`agents/timeline-planner.md`)
- [ ] Meeting Facilitator Agent erstellen (`agents/meeting-facilitator.md`)
- [ ] Report Generator Agent erstellen (`agents/report-generator.md`)
- [ ] Task Coordinator Agent erstellen (`agents/task-coordinator.md`)
- [ ] Decision Tracker Agent erstellen (`agents/decision-tracker.md`)
- [ ] marketplace.json mit Agent-Pfaden aktualisieren
- [ ] Agents mit realen Projekt-Daten testen
- [ ] Templates für verschiedene Use Cases erstellen
- [ ] Integration zwischen Agents testen

## 📚 Inspiration & Ressourcen

### Document Analysis
- [Information Extraction Best Practices](https://en.wikipedia.org/wiki/Information_extraction)
- Summarization Techniques (BLUF, Pyramid Method)
- Action Item Extraction Patterns

### Timeline Planning
- [Critical Path Method](https://en.wikipedia.org/wiki/Critical_path_method)
- [Resource Leveling](https://en.wikipedia.org/wiki/Resource_leveling)
- [Mermaid Gantt Charts](https://mermaid.js.org/syntax/gantt.html)

### Meeting Facilitation
- [Atlassian Meeting Playbook](https://www.atlassian.com/team-playbook/plays)
- Meeting Design Patterns
- Facilitation Techniques

### Report Generation
- [Executive Summary Templates](https://www.projectmanager.com/templates/executive-summary-template)
- Status Report Best Practices
- Data Visualization in Markdown

### Task Management
- [Getting Things Done (GTD)](https://gettingthingsdone.com/)
- [Eisenhower Matrix](https://en.wikipedia.org/wiki/Time_management#The_Eisenhower_Method)
- [RACI Matrix](https://en.wikipedia.org/wiki/Responsibility_assignment_matrix)

### Decision Tracking
- [ADR Template](https://github.com/joelparkerhenderson/architecture-decision-record)
- [Decision Log Examples](https://www.projectmanager.com/templates/decision-log-template)
- Decision Matrix Methods

## 💡 Mögliche Erweiterungen (Future)

- **Stakeholder Communicator** - Stakeholder-spezifische Kommunikation
- **Risk Manager** - Risiko-Identifikation und -Management
- **Budget Tracker** - Budget-Planung und -Tracking
- **Quality Assurance** - QA-Checklisten und Reviews
- **Knowledge Manager** - Wissens-Dokumentation und -Verteilung

## 📄 Lizenz

MIT License (geplant)

## 🤝 Beitragen

Nach Fertigstellung und Testing wird das Repository öffentlich gemacht.

---

**Erstellt:** November 2025
**Status:** 🚧 Plugin-Struktur vorbereitet, Agents noch zu erstellen
**Nächster Schritt:** Agent-Entwicklung basierend auf realen Use Cases
