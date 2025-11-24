# Claude Code Project Assistant Agents

**Status:** ✅ Ready to Use

Specialized Claude Code agents that support you as a **personal project assistant**.

## 📋 Overview

This repository contains **professional** Claude Code agents that assist you with daily project management tasks - as if you had a personal assistant by your side.

## 🎯 Available Agents

### 1. Document Analyst
**Plugin:** `document-analyst`

**What does this agent do?**
- Analyzes project documents (requirements, specifications, meeting notes)
- Extracts key information and key points
- Identifies action items and responsibilities
- Creates structured summaries
- Compares document versions and shows changes

**Use Cases:**
- "Analyze this requirements document and summarize the key points"
- "Extract all action items from these meeting notes"
- "Compare version 1 and version 2 of the specification"

### 2. Timeline Planner
**Plugin:** `timeline-planner`

**What does this agent do?**
- Creates project timelines from task lists
- Calculates resource capacity
- Identifies bottlenecks and critical paths
- Manages dependencies between tasks
- Creates Gantt charts and roadmaps

**Use Cases:**
- "Create a timeline plan for these 20 tasks with 3 developers"
- "Calculate capacity for Q1 2025 based on these tasks"
- "Identify bottlenecks in this project plan"

### 3. Meeting Facilitator
**Plugin:** `meeting-facilitator`

**What does this agent do?**
- Prepares meeting agendas
- Creates meeting briefs with context and objectives
- Generates discussion points based on input
- Produces structured meeting notes
- Tracks follow-up actions from meetings

**Use Cases:**
- "Prepare an agenda for the sprint planning meeting"
- "Create a meeting brief for the stakeholder update"
- "Convert these meeting notes into a structured protocol"

### 4. Report Generator
**Plugin:** `report-generator`

**What does this agent do?**
- Generates status reports (weekly/monthly)
- Creates executive summaries
- Produces stakeholder updates
- Creates project dashboards
- Visualizes data (Markdown tables, charts)

**Use Cases:**
- "Create a weekly status report based on this data"
- "Generate an executive summary for management"
- "Create a stakeholder update with key achievements"

### 5. Task Coordinator
**Plugin:** `task-coordinator`

**What does this agent do?**
- Tracks action items across multiple projects
- Manages follow-ups and deadlines
- Coordinates cross-team dependencies
- Ensures accountability
- Prioritizes tasks by urgency

**Use Cases:**
- "Show me all open action items from the last 3 meetings"
- "Create a follow-up list for this week"
- "Prioritize these 15 tasks by importance and dependencies"

### 6. Decision Tracker
**Plugin:** `decision-tracker`

**What does this agent do?**
- Documents decisions in structured format
- Tracks decision history over time
- Manages decision logs (ADR - Architecture Decision Records)
- Ensures follow-through
- Identifies open decisions

**Use Cases:**
- "Document this decision as an ADR"
- "Show all decisions related to 'API design'"
- "Which decisions are still open?"

### 7. Stakeholder Communicator
**Plugin:** `stakeholder-communicator`

**What does this agent do?**
- Crafts targeted communication for different stakeholder groups
- Creates stakeholder communication plans
- Manages executive, technical, and customer communication
- Handles crisis and change communication
- Develops stakeholder matrices and engagement strategies

**Use Cases:**
- "Create an executive brief for the CEO about project status"
- "Draft a technical update email for the development team"
- "Prepare a customer communication about upcoming changes"

### 8. Risk Manager
**Plugin:** `risk-manager`

**What does this agent do?**
- Identifies and assesses project risks
- Creates risk registers and response plans
- Develops mitigation and contingency strategies
- Tracks risk indicators and triggers
- Manages risk monitoring and reporting

**Use Cases:**
- "Create initial risk assessment for cloud migration project"
- "Analyze these risks and prioritize by severity"
- "Develop mitigation plan for integration failure risk"

### 9. Budget Tracker
**Plugin:** `budget-tracker`

**What does this agent do?**
- Plans and tracks project budgets
- Forecasts costs and identifies variances
- Analyzes spending trends and burn rates
- Creates budget reports and dashboards
- Manages contingency reserves

**Use Cases:**
- "Create budget plan for 6-month project with 5 developers"
- "Analyze current spending and forecast completion cost"
- "Generate monthly budget status report"

### 10. Quality Assurance
**Plugin:** `quality-assurance`

**What does this agent do?**
- Defines quality standards and acceptance criteria
- Creates testing strategies and QA checklists
- Develops code review processes
- Tracks quality metrics and defect rates
- Builds pre-release and deployment checklists

**Use Cases:**
- "Create Definition of Done for our project"
- "Design testing strategy for new feature"
- "Generate pre-release quality checklist"

### 11. Knowledge Manager
**Plugin:** `knowledge-manager`

**What does this agent do?**
- Captures and organizes organizational knowledge
- Creates onboarding guides and documentation
- Builds knowledge bases and FAQs
- Develops runbooks and playbooks
- Manages documentation maintenance

**Use Cases:**
- "Create 30-day onboarding guide for new developers"
- "Document our deployment process as a runbook"
- "Build FAQ for common development issues"

### 12. Project Assistant (All-in-One)
**Plugin:** `project-assistant-full`

Loads all 11 agents above for complete project assistance.

## 📁 Repository Structure

```
claude-agents-project-management/
├── .claude-plugin/
│   └── marketplace.json    # Plugin configuration
├── agents/
│   ├── document-analyst.md
│   ├── timeline-planner.md
│   ├── meeting-facilitator.md
│   ├── report-generator.md
│   ├── task-coordinator.md
│   └── decision-tracker.md
└── README.md
```

## 🚀 Installation

### Option 1: Via Claude Code Marketplace Plugin

```bash
# In Claude Code
/add marketplace https://github.com/markus-michalski/claude-agents-project-management
```

### Option 2: Manual Installation

```bash
# 1. Create plugin directory
mkdir -p ~/.claude/plugins/marketplaces/project-assistant-pro/.claude-plugin
mkdir -p ~/.claude/plugins/marketplaces/project-assistant-pro/agents

# 2. Copy plugin files
cp /path/to/claude-agents-project-management/.claude-plugin/marketplace.json \
   ~/.claude/plugins/marketplaces/project-assistant-pro/.claude-plugin/
cp /path/to/claude-agents-project-management/agents/*.md \
   ~/.claude/plugins/marketplaces/project-assistant-pro/agents/

# 3. Enable plugin in settings.json
```

Add this to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "document-analyst@project-assistant-pro": true,
    "timeline-planner@project-assistant-pro": true,
    "meeting-facilitator@project-assistant-pro": true,
    "report-generator@project-assistant-pro": true,
    "task-coordinator@project-assistant-pro": true,
    "decision-tracker@project-assistant-pro": true,
    "stakeholder-communicator@project-assistant-pro": true,
    "risk-manager@project-assistant-pro": true,
    "budget-tracker@project-assistant-pro": true,
    "quality-assurance@project-assistant-pro": true,
    "knowledge-manager@project-assistant-pro": true,
    "project-assistant-full@project-assistant-pro": true
  }
}
```

## 📖 Usage

### With Task Tool

```typescript
// Document Analyst
Task({
  subagent_type: "document-analyst:document-analyst",
  prompt: "Analyze these requirements and extract all action items",
  description: "Analyze requirements document"
})

// Timeline Planner
Task({
  subagent_type: "timeline-planner:timeline-planner",
  prompt: "Create a timeline plan for these 15 tasks",
  description: "Create timeline plan"
})

// Meeting Facilitator
Task({
  subagent_type: "meeting-facilitator:meeting-facilitator",
  prompt: "Prepare an agenda for sprint planning",
  description: "Prepare meeting agenda"
})

// Report Generator
Task({
  subagent_type: "report-generator:report-generator",
  prompt: "Generate a weekly status report",
  description: "Generate status report"
})

// Task Coordinator
Task({
  subagent_type: "task-coordinator:task-coordinator",
  prompt: "Show all open action items from last week",
  description: "Track action items"
})

// Decision Tracker
Task({
  subagent_type: "decision-tracker:decision-tracker",
  prompt: "Document this architecture decision as ADR",
  description: "Create decision record"
})

// Stakeholder Communicator
Task({
  subagent_type: "stakeholder-communicator:stakeholder-communicator",
  prompt: "Create executive brief for CEO about cloud migration project status",
  description: "Create executive communication"
})

// Risk Manager
Task({
  subagent_type: "risk-manager:risk-manager",
  prompt: "Create risk assessment for 6-month cloud migration with 5-person team",
  description: "Assess project risks"
})

// Budget Tracker
Task({
  subagent_type: "budget-tracker:budget-tracker",
  prompt: "Analyze current spending and forecast total project cost",
  description: "Track budget status"
})

// Quality Assurance
Task({
  subagent_type: "quality-assurance:quality-assurance",
  prompt: "Create Definition of Done and testing strategy for new feature",
  description: "Define quality standards"
})

// Knowledge Manager
Task({
  subagent_type: "knowledge-manager:knowledge-manager",
  prompt: "Create 30-day onboarding guide for new backend developers",
  description: "Build onboarding guide"
})

// All-in-One Assistant
Task({
  subagent_type: "project-assistant-full:project-assistant",
  prompt: "Analyze this meeting transcript and create action items, decisions, and a summary",
  description: "Full project assistance"
})
```

## 🔧 marketplace.json Structure

The `marketplace.json` contains 12 plugins:

1. **`document-analyst`** - Document analysis
2. **`timeline-planner`** - Timeline & capacity planning
3. **`meeting-facilitator`** - Meeting preparation
4. **`report-generator`** - Report creation
5. **`task-coordinator`** - Task coordination
6. **`decision-tracker`** - Decision documentation
7. **`stakeholder-communicator`** - Stakeholder communication
8. **`risk-manager`** - Risk management
9. **`budget-tracker`** - Budget tracking
10. **`quality-assurance`** - Quality assurance
11. **`knowledge-manager`** - Knowledge management
12. **`project-assistant-full`** - All agents combined

**Advantage:** You can activate individual agents or use all of them together!

## 🎯 Agent Capabilities

### Document Analyst
- BLUF (Bottom Line Up Front) summaries
- Executive summaries
- Action item extraction
- Stakeholder identification
- Risk and dependency analysis
- Version comparison

### Timeline Planner
- Critical Path Method (CPM)
- Resource capacity planning
- Dependency management
- Mermaid Gantt charts
- Milestone tracking
- Bottleneck identification

### Meeting Facilitator
- Meeting agenda templates (Sprint Planning, Retrospective, Stakeholder Updates, etc.)
- Meeting briefs with context and objectives
- Structured meeting notes
- Action item tracking
- Decision documentation
- Follow-up management

### Report Generator
- Weekly/monthly status reports
- Executive summaries
- Stakeholder updates
- KPI dashboards
- Risk reports
- Progress visualization

### Task Coordinator
- GTD (Getting Things Done) framework
- Eisenhower Matrix prioritization
- RACI matrix accountability
- Dependency coordination
- Follow-up tracking
- Multi-project overview

### Decision Tracker
- Architecture Decision Records (ADR)
- Decision logs
- Decision matrices
- Historical context
- Follow-through tracking
- Open decision management

### Stakeholder Communicator
- Executive communication templates
- Technical team communication
- Customer communication
- Crisis and change communication
- Stakeholder analysis and matrices
- Multi-channel communication plans

### Risk Manager
- Risk identification and assessment
- Risk registers and matrices
- Mitigation and contingency planning
- Risk monitoring and tracking
- Monte Carlo simulation
- Risk burndown charts

### Budget Tracker
- Budget planning and baseline
- Cost tracking and forecasting
- Earned Value Management (EVM)
- Burn rate analysis
- Variance reporting
- Contingency management

### Quality Assurance
- Definition of Done (DoD)
- Code quality standards
- Testing strategy (pyramid model)
- QA checklists (code review, pre-release, accessibility)
- Quality metrics and dashboards
- Bug triage and severity classification

### Knowledge Manager
- Knowledge base structure
- Architecture Decision Records (ADR)
- Onboarding guides
- Runbooks and playbooks
- FAQ creation
- Documentation maintenance

## 📚 Inspiration & Resources

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


## 🤖 Real-World Use Cases

### Use Case 1: Sprint Planning
```typescript
// 1. Analyze last sprint's retrospective notes
Task({
  subagent_type: "document-analyst:document-analyst",
  prompt: "Analyze these retrospective notes and extract learnings",
  description: "Analyze retrospective"
})

// 2. Create meeting agenda for sprint planning
Task({
  subagent_type: "meeting-facilitator:meeting-facilitator",
  prompt: "Prepare sprint planning agenda based on backlog",
  description: "Prepare sprint planning"
})

// 3. Create timeline for sprint
Task({
  subagent_type: "timeline-planner:timeline-planner",
  prompt: "Create 2-week sprint timeline for these 20 tasks",
  description: "Create sprint timeline"
})
```

### Use Case 2: Stakeholder Update
```typescript
// 1. Generate status report
Task({
  subagent_type: "report-generator:report-generator",
  prompt: "Create weekly status report from these updates",
  description: "Generate status report"
})

// 2. Extract decisions made this week
Task({
  subagent_type: "decision-tracker:decision-tracker",
  prompt: "Document all decisions from this week's meetings",
  description: "Track decisions"
})

// 3. Identify open action items
Task({
  subagent_type: "task-coordinator:task-coordinator",
  prompt: "Show all open action items and their status",
  description: "Track action items"
})
```

### Use Case 3: Project Kickoff
```typescript
// All-in-One approach
Task({
  subagent_type: "project-assistant-full:project-assistant",
  prompt: "Analyze requirements doc, create timeline, prepare kickoff meeting agenda",
  description: "Complete project kickoff"
})
```

## 📄 License

MIT License

## 🤝 Contributing

This repository is open for contributions. Feel free to:
- Report issues
- Suggest improvements
- Add new agent capabilities
- Share real-world use cases

## 🔄 Version History

- **v1.0.0** (November 2025) - Initial release with 11 specialized agents + all-in-one assistant
  - Core agents: Document Analyst, Timeline Planner, Meeting Facilitator, Report Generator, Task Coordinator, Decision Tracker
  - Extended agents: Stakeholder Communicator, Risk Manager, Budget Tracker, Quality Assurance, Knowledge Manager

---

**Created:** November 2025
**Status:** ✅ Production Ready
**Author:** Markus Michalski
**Repository:** https://github.com/markus-michalski/claude-agents-project-management
