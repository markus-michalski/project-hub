---
name: report
description: |
  Generate a static HTML report for the active project or all projects.
  Trigger when user says: "Report erstellen", "HTML-Report", "Bericht exportieren",
  "Dashboard exportieren", "Projektbericht", "report", "/project-hub:report",
  "Übersicht exportieren", "all-projects report".
model: claude-sonnet-4-6
user-invocable: true
argument-hint: "[full|summary|all-projects]"
---

# Skill: /project-hub:report

Generates a self-contained HTML report that can be opened in any browser — no server needed.
Ideal for sharing project status with management or clients, or saving as PDF via browser print.

## Argument Handling

- No argument → `full` report for active project
- `summary` → executive summary (1 page: header + action items + last 5 notes)
- `all-projects` → cross-project overview table with charts (no active project needed)
- `full` → explicit full report

## Workflow

### 1. Determine Report Type

Parse argument (default: `full`):
- `full` or empty → report_type = "full"
- `summary` → report_type = "summary"
- `all-projects` or `all` → report_type = "all-projects"

### 2. Get Active Project (for full/summary)

```
tool_get_session() → check active project
```

If no active project and report_type != "all-projects":
- Ask: "Welches Projekt soll ich als Bericht exportieren?"
- Use `tool_list_projects("active")` to show options
- Load with `tool_get_project(identifier)`

### 3. Generate Report

```
tool_generate_report(
  project_id=<project_id or None>,
  report_type=<"full"|"summary"|"all-projects">,
)
```

### 4. Open Report

After successful generation, open the file:
```bash
xdg-open "<path>" 2>/dev/null || open "<path>" 2>/dev/null || true
```

### 5. Show Result

```
Bericht erstellt: /home/user/.project-hub/reports/acme-gmbh-20260504.html

Öffne den Bericht im Browser. Für PDF: Drucken → Als PDF speichern.
```

Always show the file path — even if auto-open fails, the user can open manually.

## Error Handling

- Project not found → Ask user to load a project first (`/project-hub:resume`)
- Invalid report_type → Show valid options and ask again
- File write error → Show error and suggest checking disk space
