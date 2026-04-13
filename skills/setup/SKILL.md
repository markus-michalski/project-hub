---
name: setup
description: "First-time setup for project-hub. Creates venv, installs dependencies, initializes database. Use when: (1) Plugin just installed, (2) MCP server not responding, (3) User says 'setup' or 'einrichten'."
model: claude-sonnet-4-6
user-invocable: true
---

# Project Hub Setup

First-time setup and repair for the project-hub plugin.

## Workflow

### Step 1: Check Current State

```bash
# Check venv
test -d ~/.project-hub/venv && echo "venv: OK" || echo "venv: MISSING"

# Check dependencies
~/.project-hub/venv/bin/python3 -c "import mcp; import fastmcp" 2>/dev/null && echo "deps: OK" || echo "deps: MISSING"

# Check data directory
test -d ~/.project-hub && echo "data-dir: OK" || echo "data-dir: MISSING"
```

### Step 2: Create Data Directory (if missing)

```bash
mkdir -p ~/.project-hub
```

### Step 3: Create Venv (if missing)

```bash
python3 -m venv ~/.project-hub/venv
```

### Step 4: Install Dependencies (if missing)

```bash
~/.project-hub/venv/bin/pip install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt
```

### Step 5: Verify MCP Server

```bash
~/.project-hub/venv/bin/python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/servers/project-hub-server')
from tools.db import init_db
init_db()
print('DB: OK')
"
```

### Step 6: Report

```
## Project Hub Setup

- Daten-Verzeichnis: OK / ERSTELLT (~/.project-hub)
- Venv:             OK / ERSTELLT (~/.project-hub/venv)
- Dependencies:     OK / INSTALLIERT
- Datenbank:        OK / INITIALISIERT

Starte Claude Code neu, damit der MCP Server geladen wird.
Danach kannst du loslegen:
- `/new-project` — Erstes Projekt anlegen
- `/help` — Alle Skills anzeigen
```

## Error Handling

- `python3` not found → Tell user to install Python 3.11+
- `pip install` fails → Show the exact error and suggest running manually
- DB init fails → Show error, check if `~/.project-hub/` is writable
