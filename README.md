# Project Hub — Claude Code Plugin

![GitHub Tag](https://img.shields.io/github/v/tag/markus-michalski/project-hub?sort=semver&style=for-the-badge)
![License: PolyForm NC 1.0.0](https://img.shields.io/badge/license-PolyForm%20NC%201.0.0-red.svg?style=for-the-badge)

A personal project management hub for Claude Code. Create projects, store contacts, log meeting notes and emails, generate summaries, and draft communications — all within persistent project context.

## Overview

Project Hub gives you a persistent "memory" per project. Load a project once with `/resume` and Claude knows your stakeholders, current phase, history, and documents — without you having to repeat yourself.

**Primary use cases:**
- Merchant onboarding coordination (BNPL, Direct Debit, multi-market)
- Consulting engagements
- IT projects, marketing campaigns, events

## Available Skills

All skills operate within the context of the active project.

| Skill | Description |
|-------|-------------|
| `/new-project [name]` | Create a new project |
| `/resume [name]` | Load / switch to a project |
| `/dashboard` | Overview of all projects |
| `/status` | Show and update current project |
| `/add-contact` | Add an internal or external contact |
| `/add-note [type]` | Log a note, meeting minutes, email, or decision |
| `/summarize [note-id]` | Create structured summary from email or meeting notes |
| `/compose [email\|slack\|teams]` | Draft a communication |
| `/help` | Show all skills |

## Project Types

| Type | Use case |
|------|----------|
| `merchant-onboarding` | Enterprise merchant onboarding (BNPL, Direct Debit, ...) |
| `it-project` | IT / software project |
| `marketing` | Marketing campaign |
| `consulting` | Consulting engagement |
| `event` | Event planning |
| `generic` | General purpose |

## Data Storage

```
~/.project-hub/
├── project-hub.db        # SQLite database
└── projects/
    └── {project-slug}/
        └── docs/
            ├── emails/
            ├── meeting-notes/
            └── misc/
```

## Installation

### Prerequisites

- Python 3.11+
- Claude Code with plugin support

### Setup

```bash
# 1. Create virtual environment
mkdir -p ~/.project-hub
python3 -m venv ~/.project-hub/venv

# 2. Install dependencies
~/.project-hub/venv/bin/pip install -r requirements.txt

# 3. Add plugin to Claude Code settings.json
```

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "project-hub@project-hub": true
  }
}
```

## Repository Structure

```
claude-agents-project-management/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
├── skills/
│   ├── new-project/SKILL.md
│   ├── resume/SKILL.md
│   ├── dashboard/SKILL.md
│   ├── add-contact/SKILL.md
│   ├── add-note/SKILL.md
│   ├── summarize/SKILL.md
│   ├── compose/SKILL.md
│   ├── status/SKILL.md
│   └── help/SKILL.md
├── servers/
│   └── project-hub-server/
│       ├── run.py
│       ├── server.py
│       └── tools/
│           ├── db.py
│           ├── projects.py
│           ├── contacts.py
│           ├── notes.py
│           └── session.py
├── project-types/
│   ├── merchant-onboarding.md
│   ├── it-project.md
│   ├── marketing.md
│   ├── consulting.md
│   ├── event.md
│   └── generic.md
└── requirements.txt
```

## License

[PolyForm Noncommercial License 1.0.0](LICENSE.md) — source-available, personal and non-commercial use only. Not OSI Open Source. Commercial use requires explicit permission; contact the maintainer.
