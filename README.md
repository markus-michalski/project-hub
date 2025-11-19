# Claude Code Project Management Agents

**Status:** 🚧 In Planung / Noch keine Agents

Spezialisierte Claude Code Agents für Project Management, Agile Workflows und Team-Koordination.

## 📋 Übersicht

Dieses Repository wird **professionelle** Claude Code Agents für Project Management enthalten. Die Struktur ist vorbereitet, die Agents müssen noch erstellt werden.

## 🎯 Geplante Agents

### Agile/Scrum Management
- **Plugin:** `agile-scrum`
- **Agents:** (noch zu erstellen)
- **Fokus:** Sprint Planning, Backlog Refinement, Retrospektiven

### Kanban Workflow
- **Plugin:** `kanban-workflow`
- **Agents:** (noch zu erstellen)
- **Fokus:** WIP Limits, Flow Metrics, Continuous Delivery

### Product Management
- **Plugin:** `product-management`
- **Agents:** (noch zu erstellen)
- **Fokus:** Roadmap Planning, Feature Prioritization, Stakeholder Management

### Project Planning
- **Plugin:** `project-planning`
- **Agents:** (noch zu erstellen)
- **Fokus:** Gantt Charts, Resource Allocation, Risk Management

### Team Coordination
- **Plugin:** `team-coordination`
- **Agents:** (noch zu erstellen)
- **Fokus:** Meeting Facilitation, Decision Tracking, Communication Patterns

## 📁 Repository-Struktur

```
claude-agents-project-management/
├── .claude-plugin/
│   └── marketplace.json    # Plugin-Konfiguration (fertig)
├── agents/
│   └── (Agents werden hier erstellt)
└── README.md
```

## 🚀 Installation (Future)

Sobald die Agents erstellt sind:

### Variante 1: Als Claude Code Marketplace Plugin

```bash
# In Claude Code
/add marketplace https://github.com/<username>/claude-agents-project-management
```

### Variante 2: Manuelle Installation

```bash
# 1. Plugin-Verzeichnis erstellen
mkdir -p ~/.claude/plugins/marketplaces/project-management-pro/.claude-plugin
mkdir -p ~/.claude/plugins/marketplaces/project-management-pro/agents

# 2. Plugin-Dateien kopieren
cp /home/markus/projekte/claude/claude-agents-project-management/.claude-plugin/marketplace.json \
   ~/.claude/plugins/marketplaces/project-management-pro/.claude-plugin/
cp /home/markus/projekte/claude/claude-agents-project-management/agents/*.md \
   ~/.claude/plugins/marketplaces/project-management-pro/agents/

# 3. Plugin in settings.json aktivieren
```

Füge folgendes in `~/.claude/settings.json` ein:

```json
{
  "enabledPlugins": {
    "agile-scrum@project-management-pro": true,
    "kanban-workflow@project-management-pro": true,
    "product-management@project-management-pro": true,
    "project-planning@project-management-pro": true,
    "team-coordination@project-management-pro": true
  }
}
```

## 📖 Agent-Entwicklung

### Nächste Schritte

1. **Research Phase**
   - Best Practices für Agile/Scrum sammeln
   - Kanban-Prinzipien recherchieren
   - Product Management Frameworks analysieren
   - Project Planning Methodologien studieren

2. **Agent-Erstellung**
   - Agents in `agents/` Verzeichnis erstellen (`.md` Format)
   - Jeder Agent sollte 500-1000 Zeilen Best Practices enthalten
   - marketplace.json mit Agent-Pfaden aktualisieren

3. **Testing & Iteration**
   - Agents in realen Projekten testen
   - Feedback sammeln
   - Agents basierend auf Erfahrungen verbessern

### Agent-Template

Jeder Agent sollte folgende Bereiche abdecken:

```markdown
# Agent Name

## Role & Expertise
[Was kann der Agent?]

## Core Principles
[Grundprinzipien des Frameworks/Methodologie]

## Best Practices
[Konkrete Best Practices mit Code-Beispielen wenn relevant]

## Common Patterns
[Häufige Muster und Lösungen]

## Anti-Patterns
[Was sollte vermieden werden?]

## Tools & Integration
[Relevante Tools und Integrationen]

## Examples
[Real-World Beispiele]
```

## 🎯 Mögliche Agent-Inhalte

### Agile/Scrum Agent
- Sprint Planning Best Practices
- User Story Writing (INVEST-Prinzipien)
- Backlog Refinement Techniken
- Estimation (Planning Poker, T-Shirt Sizing)
- Retrospektive Formate
- Daily Standup Patterns
- Definition of Done/Ready
- Velocity Tracking

### Kanban Agent
- WIP Limit Strategien
- Flow Metrics (Lead Time, Cycle Time, Throughput)
- Cumulative Flow Diagrams
- Pull-System Implementation
- Swim Lanes Design
- Blocker Management
- Continuous Improvement Patterns

### Product Management Agent
- Product Vision & Strategy
- Roadmap Planning (Now/Next/Later)
- Feature Prioritization (RICE, WSJF, Kano Model)
- User Research Methods
- Stakeholder Communication
- OKRs & Metrics
- Product Discovery Techniques

### Project Planning Agent
- Work Breakdown Structure (WBS)
- Critical Path Method
- Resource Allocation Strategies
- Risk Register Management
- Milestone Planning
- Gantt Chart Best Practices
- Budget Tracking

### Team Coordination Agent
- Meeting Facilitation (Agenda, Timeboxing)
- Decision Documentation (RACI, DACI)
- Async Communication Patterns
- Documentation Standards
- Onboarding Workflows
- Knowledge Sharing Practices
- Conflict Resolution

## 🔧 marketplace.json Struktur

Die `marketplace.json` ist bereits vorbereitet mit 5 Plugins:

1. **`agile-scrum`** - Agile/Scrum Workflows
2. **`kanban-workflow`** - Kanban Management
3. **`product-management`** - Product Strategy
4. **`project-planning`** - Classical Project Management
5. **`team-coordination`** - Team Collaboration

**Vorteil:** Du kannst wählen, welche Plugins du aktivieren möchtest!

## 📝 TODO

- [ ] Agile/Scrum Agent erstellen (`agents/agile-scrum-pro.md`)
- [ ] Kanban Workflow Agent erstellen (`agents/kanban-workflow-pro.md`)
- [ ] Product Management Agent erstellen (`agents/product-management-pro.md`)
- [ ] Project Planning Agent erstellen (`agents/project-planning-pro.md`)
- [ ] Team Coordination Agent erstellen (`agents/team-coordination-pro.md`)
- [ ] marketplace.json mit Agent-Pfaden aktualisieren
- [ ] Agents testen
- [ ] README mit konkreten Beispielen erweitern
- [ ] GitHub Repository erstellen (public)

## 📚 Ressourcen für Agent-Entwicklung

### Agile/Scrum
- [Scrum Guide](https://scrumguides.org/)
- [Agile Manifesto](https://agilemanifesto.org/)
- [Mountain Goat Software](https://www.mountaingoatsoftware.com/)

### Kanban
- [Kanban University](https://kanban.university/)
- [Lean Kanban Guide](https://www.leankanban.com/)

### Product Management
- [Product School](https://productschool.com/)
- [Mind the Product](https://www.mindtheproduct.com/)
- [Silicon Valley Product Group](https://www.svpg.com/)

### Project Management
- [PMI - Project Management Institute](https://www.pmi.org/)
- [PRINCE2](https://www.axelos.com/certifications/prince2)

### Team Coordination
- [Team Topologies](https://teamtopologies.com/)
- [Atlassian Team Playbook](https://www.atlassian.com/team-playbook)

## 📄 Lizenz

**Noch nicht öffentlich!** Aktuell nur für private Entwicklungszwecke.

Geplante Lizenz: MIT License

## 🤝 Beitragen

Da dies ein privates Entwicklungs-Repository ist, sind externe Beiträge noch nicht möglich.

Nach Fertigstellung und Testing wird das Repository öffentlich gemacht.

---

**Erstellt:** November 2025
**Status:** 🚧 Repository-Struktur vorbereitet, Agents noch zu erstellen
**Nächster Schritt:** Research & Agent-Entwicklung
