---
name: setup
description: "First-time setup for the PROJECT-HUB plugin specifically. Creates venv, installs dependencies, copies config, initializes database. Use ONLY when: (1) project-hub plugin just installed, (2) project-hub MCP server not responding, (3) User says 'setup project-hub' / 'project-hub einrichten' or explicitly invokes `/project-hub:setup`. Do NOT trigger on bare 'setup' / 'einrichten' — multiple plugins have setup skills; defer if the target plugin is unclear."
model: claude-haiku-4-5
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

### Step 5b: Install Knowledge Templates

Note: `${CLAUDE_PLUGIN_ROOT}` is NOT available as a shell variable. Use Python to derive
the plugin root by checking known installation locations:

```bash
~/.project-hub/venv/bin/python3 -c "
import shutil, sys
from pathlib import Path

# Find plugin root — check known locations
candidates = [
    Path.home() / '.claude' / 'plugins' / 'marketplaces' / 'project-hub',
    Path.home() / '.claude' / 'plugins' / 'project-hub',
    Path.home() / 'projekte' / 'project-hub',
]
plugin_root = None
for c in candidates:
    if (c / 'knowledge').exists():
        plugin_root = c
        break

if plugin_root is None:
    print('knowledge: PLUGIN_ROOT_NOT_FOUND — skipping template install')
    sys.exit(0)

knowledge_src = plugin_root / 'knowledge'
knowledge_dst = Path.home() / '.project-hub' / 'knowledge'
total_copied = 0

for type_dir in sorted(knowledge_src.iterdir()):
    if not type_dir.is_dir():
        continue
    dst = knowledge_dst / type_dir.name
    dst.mkdir(parents=True, exist_ok=True)
    copied = 0
    for f in type_dir.glob('*.md'):
        target = dst / f.name
        if not target.exists():
            shutil.copy2(f, target)
            copied += 1
    total_copied += copied
    status = f'COPIED {copied}' if copied else 'OK (exists)'
    print(f'  {type_dir.name}: {status}')

print(f'knowledge: {total_copied} templates installed total')
"
```

**Ask the user which project types they want to install templates for.**
Present the available types and let them choose (all / specific ones / skip).

Available types: `merchant-onboarding`, `it-project`, `consulting`, `marketing`, `event`, `generic`

If user selects specific types: run the Python script above but filter `type_dir.name` to only
the selected types.

If user selects all: run as-is.

If user skips: skip this step entirely.

After install, tell user:
"Knowledge-Templates installiert nach `~/.project-hub/knowledge/`.
Öffne die Dateien und ersetze die Platzhalter mit deinen echten Inhalten,
oder nutze `/knowledge update <topic>` um sie interaktiv zu befüllen."

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
- Knowledge:        OK / INSTALLIERT (~/.project-hub/knowledge/[gewählte Types])
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
