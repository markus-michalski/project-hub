---
name: setup
description: "First-time setup for the PROJECT-HUB plugin specifically. Creates venv, installs dependencies, copies config, initializes database. Use ONLY when: (1) project-hub plugin just installed, (2) project-hub MCP server not responding, (3) User says 'setup project-hub' / 'project-hub einrichten' or explicitly invokes `/project-hub:setup`. Do NOT trigger on bare 'setup' / 'einrichten' — multiple plugins have setup skills; defer if the target plugin is unclear."
model: claude-haiku-4-5
user-invocable: true
---

# Project Hub Setup

First-time setup and repair for the project-hub plugin.

## Workflow

### Step 0: Detect Platform and Resolve a Working Python Interpreter

Try each of the following in order and use the **first one that actually runs**
(prints a platform string, doesn't error):

```bash
python3 -c "import sys; print(sys.platform)"
python -c "import sys; print(sys.platform)"
py -3 -c "import sys; print(sys.platform)"
```

**Do not stop at the first failure.** On Windows, `python3`/`python` frequently
fail with **exit code 49 and no output** even when Python is genuinely
installed — this is the Microsoft Store app-execution-alias stub, not a
missing-Python error. It's common on Intune/SCCM-managed devices where Python
was pushed via MSI/EXE without adding it to `PATH`. `py` (the Python Launcher
for Windows) is a separate executable that always lives in `C:\Windows\` — on
`PATH` regardless of how Python itself was installed — so try it before
concluding Python is missing.

If all three fail, check known install locations as a last resort (Windows,
PowerShell syntax): `$env:ProgramFiles\Python3*\python.exe`,
`${env:ProgramFiles(x86)}\Python3*\python.exe`,
`$env:LocalAppData\Programs\Python\Python3*\python.exe` — use the first one
that exists.

Only if *every* option above fails is Python genuinely not installed or not
locatable — see Error Handling.

Call whichever command succeeded `<PY>` — use it verbatim (not the literal
text `<PY>`) for every subsequent system-level Python invocation in this skill
(Steps 1, 2, 3, 5), until the venv exists in Step 3. From Step 4 onward the
venv's *own* interpreter is used instead, which is already resolved separately
via the OS branch below and unaffected by this detection.

**Windows quoting note:** `python3`/`python`/`py -3` need no special handling.
But if `<PY>` came from the known-install-path fallback, it's a full path that
may contain spaces (e.g. `C:\Program Files\Python313\python.exe` — exactly the
Intune-managed-device case this fallback exists for). On Windows, invoke it
via the call operator with quotes: `& "<PY>" -c "..."`, not bare `<PY> -c
"..."` — PowerShell doesn't split unquoted paths on spaces the way you'd want.

Output `win32` means Windows (venv layout: `venv\Scripts\python.exe`,
`venv\Scripts\pip.exe`); any other output means POSIX (Linux/macOS/WSL, venv
layout: `venv/bin/python3`, `venv/bin/pip`). Use this result for every
POSIX/Windows choice below.

### Step 1: Check Current State

Use `<PY>` (the interpreter resolved in Step 0 — remember Step 0's Windows
quoting note: `& "<PY>" -c "..."`, not bare `<PY>`, if `<PY>` is a
space-containing full path from the known-install fallback):

```bash
<PY> -c "
from pathlib import Path
base = Path.home() / '.project-hub'
print('venv:', 'OK' if (base / 'venv').is_dir() else 'MISSING')
print('config:', 'OK' if (base / 'config.yaml').is_file() else 'MISSING')
print('data-dir:', 'OK' if base.is_dir() else 'MISSING')
"
```

### Step 2: Create Data Directory (if missing)

```bash
<PY> -c "from pathlib import Path; Path.home().joinpath('.project-hub').mkdir(parents=True, exist_ok=True)"
```

### Step 3: Create Venv (if missing)

Use `<PY>` — the same interpreter resolved in Step 0, not a hardcoded
`python`/`python3`. On a managed device where only `py -3` worked in Step 0,
hardcoding `python` here would immediately hit the same Store-alias failure
Step 0 just worked around.

- POSIX: `<PY> -m venv ~/.project-hub/venv`
- Windows: `<PY> -m venv "$env:USERPROFILE\.project-hub\venv"`

### Step 4: Sync Dependencies (always)

Always run this, even if venv already existed. `pip` is idempotent and fast on a warm
cache (~1s). This ensures new deps added in later releases are never silently skipped.

- POSIX: `~/.project-hub/venv/bin/pip install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt -q`
- Windows: `& "$env:USERPROFILE\.project-hub\venv\Scripts\pip.exe" install -r ${CLAUDE_PLUGIN_ROOT}/requirements.txt -q`

### Step 5: Copy Config (if missing)

Use `<PY>` (still the Step 0 interpreter — this step doesn't need the venv):

```bash
<PY> -c "
import shutil
from pathlib import Path
shutil.copy2('${CLAUDE_PLUGIN_ROOT}/config/config.example.yaml', Path.home() / '.project-hub' / 'config.yaml')
"
```

Then tell the user: "Die Config wurde nach `~/.project-hub/config.yaml` kopiert.
Du kannst folgende Einstellungen anpassen:
- `docs_root` — Wo Projekt-Dokumente gespeichert werden (Standard: `~/.project-hub/projects`)
- `db_path` — SQLite-Datenbankpfad (Standard: lokal; für Team-Nutzung: Netzwerk-Share eintragen)
- `user.name` / `user.email` — Deine Daten für Kommunikations-Drafts
- `default_language` — Sprache für generierte Texte (`en` oder `de`)"

After copying the config, check whether the user's existing config already has a `db_path`
set to a network path:

Run the following script via the venv's Python (see Step 0 for platform detection —
POSIX: `~/.project-hub/venv/bin/python3 -c "<script>"`, Windows:
`& "$env:USERPROFILE\.project-hub\venv\Scripts\python.exe" -c "<script>"`):

```python
import yaml
from pathlib import Path
cfg_path = Path.home() / '.project-hub' / 'config.yaml'
if not cfg_path.exists():
    exit(0)
cfg = yaml.safe_load(cfg_path.read_text()) or {}
db_path = cfg.get('db_path', '')
network_hints = ['/mnt/', '/media/', 'Dropbox', 'OneDrive', 'Google Drive', '/Volumes/', '/net/']
if any(h in str(db_path) for h in network_hints):
    print('NETWORK_SHARE:' + str(db_path))
else:
    print('LOCAL')
```

If the output starts with `NETWORK_SHARE:`, show:
```
⚠️  Netzwerk-Pfad erkannt: {db_path}
Hinweise für Team-Nutzung:
- WAL-Modus ist aktiv (mehrere gleichzeitige Leser möglich).
- Schreib-Konflikte werden automatisch mit Retry behandelt.
- Alle Team-Mitglieder müssen denselben Pfad in ihrer config.yaml eintragen.
- Echtzeit-Synchronisation / Konflikt-Erkennung: NICHT in Phase 1.
- Hohe Latenz auf dem Share? Schreib-Timeouts können vorkommen.
```

### Step 5b: Install Knowledge Templates

Note: `${CLAUDE_PLUGIN_ROOT}` is NOT available as a shell variable. Use Python to derive
the plugin root by checking known installation locations. Run via the venv's Python
(see Step 0 — POSIX: `~/.project-hub/venv/bin/python3 -c "<script>"`, Windows:
`& "$env:USERPROFILE\.project-hub\venv\Scripts\python.exe" -c "<script>"`):

```python
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

Run via the venv's Python (see Step 0 — POSIX: `~/.project-hub/venv/bin/python3 -c "<script>"`,
Windows: `& "$env:USERPROFILE\.project-hub\venv\Scripts\python.exe" -c "<script>"`):

```python
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/servers/project-hub-server')
from tools.db import init_db
init_db()
print('DB: OK')
```

### Step 7: Report

```
## Project Hub Setup

- Daten-Verzeichnis: OK / ERSTELLT  (~/.project-hub)
- Venv:             OK / ERSTELLT  (~/.project-hub/venv)
- Dependencies:     SYNCHRONISIERT
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

- `python3` not found (POSIX), and no other interpreter in Step 0's chain
  works either → Python is genuinely not installed. Tell user to install
  Python 3.11+.
- On Windows, `python`/`python3` exiting with code 49 and no output is
  **not** "Python not found" — it's the Microsoft Store app-execution-alias
  stub. Do not tell the user to install Python; instead fall through Step 0's
  chain (`py -3`, then known install paths).
- Only if **every** entry in Step 0's fallback chain fails is Python actually
  missing on Windows → tell the user to install Python 3.11+ from python.org
  and check "Add python.exe to PATH" during install. On a managed device
  where the user can't install software themselves, suggest contacting IT to
  confirm the Python install location or add it to `PATH`.
- `pip install` fails → Show the exact error and suggest running manually
- DB init fails → Show error, check if `~/.project-hub/` is writable
