---
name: setup
description: "First-time setup for project-hub. Creates venv, installs dependencies, copies config, initializes database. Use when: (1) Plugin just installed, (2) MCP server not responding, (3) User says 'setup' or 'einrichten'."
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

# Check config
test -f ~/.project-hub/config.yaml && echo "config: OK" || echo "config: MISSING"

# Check dependencies
~/.project-hub/venv/bin/python3 -c "import mcp; import fastmcp; import yaml" 2>/dev/null && echo "deps: OK" || echo "deps: MISSING"

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

### Step 5: Copy Config (if missing)

```bash
cp ${CLAUDE_PLUGIN_ROOT}/config/config.example.yaml ~/.project-hub/config.yaml
```

Then tell the user: "Die Config wurde nach `~/.project-hub/config.yaml` kopiert.
Du kannst folgende Einstellungen anpassen:
- `docs_root` — Wo Projekt-Dokumente gespeichert werden (Standard: `~/.project-hub/projects`)
- `user.name` / `user.email` — Deine Daten für Kommunikations-Drafts
- `default_language` — Sprache für generierte Texte (`en` oder `de`)"

### Step 5b: Install Knowledge Templates (if missing)

Note: `${CLAUDE_PLUGIN_ROOT}` is NOT available as a shell variable. Use Python to derive
the plugin root from the MCP server script location:

```bash
~/.project-hub/venv/bin/python3 -c "
import shutil, sys
from pathlib import Path

# Derive plugin root: run.py is at <plugin_root>/servers/project-hub-server/run.py
run_py = Path('$HOME/.project-hub/venv').parent.parent
# Find the actual plugin root via the MCP server path in sys path or via known relative location
# The server is installed at <plugin_root>/servers/project-hub-server/
# We need to find it — check common locations
candidates = [
    Path.home() / '.claude' / 'plugins' / 'project-hub',
    Path.home() / 'projekte' / 'project-hub',
]
plugin_root = None
for c in candidates:
    if (c / 'knowledge' / 'merchant-onboarding').exists():
        plugin_root = c
        break

if plugin_root is None:
    print('knowledge: PLUGIN_ROOT_NOT_FOUND')
    sys.exit(0)

src = plugin_root / 'knowledge' / 'merchant-onboarding'
dst = Path.home() / '.project-hub' / 'knowledge' / 'merchant-onboarding'
dst.mkdir(parents=True, exist_ok=True)
copied = 0
for f in src.glob('*.md'):
    target = dst / f.name
    if not target.exists():
        shutil.copy2(f, target)
        copied += 1
if copied:
    print(f'knowledge: COPIED {copied} templates')
else:
    print('knowledge: OK (already exists)')
"
```

Tell user: "Knowledge-Templates für `merchant-onboarding` nach `~/.project-hub/knowledge/merchant-onboarding/` kopiert.
Ersetze die Platzhalter mit euren echten Inhalten oder nutze `/knowledge update governance` um sie mit deinen Dokumenten zu befüllen."

### Step 6: Verify MCP Server + Init DB

```bash
~/.project-hub/venv/bin/python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/servers/project-hub-server')
from tools.db import init_db
init_db()
print('DB: OK')
"
```

### Step 7: Report

```
## Project Hub Setup

- Daten-Verzeichnis: OK / ERSTELLT  (~/.project-hub)
- Venv:             OK / ERSTELLT  (~/.project-hub/venv)
- Dependencies:     OK / INSTALLIERT
- Config:           OK / ERSTELLT  (~/.project-hub/config.yaml)
- Knowledge:        OK / ERSTELLT  (~/.project-hub/knowledge/merchant-onboarding/)
- Datenbank:        OK / INITIALISIERT

Starte Claude Code neu, damit der MCP Server geladen wird.
Danach kannst du loslegen:
- `/new-project`  — Erstes Projekt anlegen
- `/knowledge`    — Knowledge-Templates mit echten Inhalten befüllen
- `/help`         — Alle Skills anzeigen
```

## Error Handling

- `python3` not found → Tell user to install Python 3.11+
- `pip install` fails → Show the exact error and suggest running manually
- DB init fails → Show error, check if `~/.project-hub/` is writable
