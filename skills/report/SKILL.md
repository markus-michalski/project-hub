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

Only these values are accepted; anything else is an error (see Error Handling, "Invalid
report_type" — unrecognized arguments are never silently treated as `full`):

- No argument → `full` report for active project
- `full` → explicit full report
- `summary` → executive summary (1 page: header + action items + last 5 notes)
- `all-projects` (or `all`) → cross-project overview table with charts (no active project needed)

## Workflow

### 1. Determine Report Type

Parse argument:
- No argument (empty) → report_type = "full" (default)
- `full` → report_type = "full"
- `summary` → report_type = "summary"
- `all-projects` or `all` → report_type = "all-projects"
- Anything else → invalid. Do NOT silently fall back to "full" — follow the Error Handling
  section's "Invalid report_type" rule: show the valid options (full, summary, all-projects,
  and the `all` alias) and ask again.

### 2. Get Active Project (for full/summary)

Skip this entire step when `report_type == "all-projects"` — go directly to Step 3 with
`project_id=None`.

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

For `report_type="all-projects"`, pass `project_id=None` as a style convention — Step 2 was
skipped, so there's no active-project id to carry over anyway. This is not a correctness
requirement: `_render_all_projects()` never reads `project_id` (see
`servers/project-hub-server/tools/report.py`), so a stray value would be harmless — it just keeps
the call self-consistent.

### 4. Open Report

After successful generation, open the file:
```bash
xdg-open "<path>" 2>/dev/null || open "<path>" 2>/dev/null || true
```

### 5. Show Result

```
Bericht erstellt: /home/user/.project-hub/reports/acme-gmbh-full-20260504.html

Öffne den Bericht im Browser. Für PDF: Drucken → Als PDF speichern.
```

Always show the file path — even if auto-open fails, the user can open manually.

## Error Handling

- Project not found → Ask user to load a project first (`/project-hub:resume`)
- Invalid report_type → Show valid options (full, summary, all-projects — `all` also works as an
  alias for all-projects) and ask again. If the given argument looks like a project name rather
  than a typo (e.g. `/project-hub:report acme-gmbh`), suggest `/project-hub:resume <name>` as the
  likely intended command instead of re-prompting for a report type.
- File write error → Show error and suggest checking disk space
