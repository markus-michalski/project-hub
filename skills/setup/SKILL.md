---
name: setup
description: "First-time setup for the PROJECT-HUB plugin specifically. Creates venv, installs dependencies, copies config, initializes database. Use ONLY when: (1) project-hub plugin just installed, (2) project-hub MCP server not responding, (3) User says 'setup project-hub' / 'project-hub einrichten' or explicitly invokes `/project-hub:setup`. Do NOT trigger on bare 'setup' / 'einrichten' — multiple plugins have setup skills; defer if the target plugin is unclear."
model: claude-haiku-4-5
user-invocable: true
---

# Project Hub Setup

First-time setup and repair for the project-hub plugin.

## Workflow

**Multi-line Python scripts — write a file, don't inline them.** Several
steps below need multi-line Python. Never pass multi-line content via
`<PY> -c "<script>"` — a `-c` argument containing literal newlines parses
differently across bash, PowerShell, and cmd, and reliably breaks under
PowerShell. Instead, for any script longer than one line:

1. Write the script content to a file using your own file-write capability
   (you have one — this isn't a shell heredoc trick, just save the file
   directly). Reuse `~/.project-hub/_setup_scratch.py` as the target path
   from Step 2 onward, since `~/.project-hub` is guaranteed to exist by
   then and it's fine to overwrite this file between steps. For Step 1,
   which runs before Step 2 creates that directory, use the OS temp
   directory instead — resolve it with the single-line (newline-free, so
   safe everywhere) command `<PY> -c "import tempfile; print(tempfile.gettempdir())"`.
2. Run it as `<PY> <path-to-that-file>` — a plain file-path argument,
   portable across every shell, no quoting concerns at all. **Exception:**
   this is the system-level interpreter and only has the standard library.
   Any script that imports a venv-only dependency (pyyaml, etc. — see Step 4)
   must instead run under the venv's own interpreter, even where the
   write-then-run mechanics of this pattern still apply. Step 0 spells out
   exactly which scripts that affects.

Single-line `<PY> -c "..."` commands (Step 2, Step 5's config-copy) are
unaffected by this — the newline-parsing problem only applies to multi-line
content — and can stay exactly as shown.

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
that has no dependency beyond the standard library: Steps 1, 2, 3, and Step
5's config-copy command. This is not simply "everything before Step 4" —
Step 5's config-copy command runs *after* Step 4 but still uses `<PY>`,
because it only needs `shutil`/`pathlib`. What actually decides the choice is
whether a script imports a venv-only dependency (installed in Step 4): if it
does — the network-path-check script inside Step 5, and everything in Steps
5b and 6 — it runs under the venv's *own* interpreter instead, which is
already resolved separately via the OS branch below and unaffected by this
detection.

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

This script is multi-line — follow the write-then-run pattern above: get the
OS temp directory, save the script below as `<tmp>/project-hub-setup-step1.py`,
then run `<PY> <tmp>/project-hub-setup-step1.py` (remember Step 0's Windows
quoting note — `& "<PY>" ...`, not bare `<PY>`, if `<PY>` is a space-containing
full path from the known-install fallback):

```python
from pathlib import Path
base = Path.home() / '.project-hub'
print('venv:', 'OK' if (base / 'venv').is_dir() else 'MISSING')
print('config:', 'OK' if (base / 'config.yaml').is_file() else 'MISSING')
print('data-dir:', 'OK' if base.is_dir() else 'MISSING')
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
<PY> -c "import shutil; from pathlib import Path; cfg = Path.home() / '.project-hub' / 'config.yaml'; exists = cfg.exists(); shutil.copy2(r'${CLAUDE_PLUGIN_ROOT}/config/config.example.yaml', cfg) if not exists else None; print('EXISTS' if exists else 'COPIED')"
```

If the output is `EXISTS`: do NOT copy and do NOT show the config explanation below — the user's
config must not be overwritten. However, DO continue with the `db_path` check further below
(it is especially relevant here: the existing config may already contain a dangerous path). Then
continue to Step 5b.

If the output is `COPIED`: tell the user: "Die Config wurde nach `~/.project-hub/config.yaml` kopiert.
Du kannst folgende Einstellungen anpassen:
- `docs_root` — Wo Projekt-Dokumente gespeichert werden (Standard: `~/Documents/project-hub`)
- `db_path` — SQLite-Datenbankpfad (Standard: lokal; für Team-Nutzung: Netzwerk-Share eintragen)
- `user.name` / `user.email` — Deine Daten für Kommunikations-Drafts
- `default_language` — Sprache für generierte Texte (`en` oder `de`)"

After copying the config, check whether the user's existing config already has a `db_path`
set to a cloud-sync folder (Dropbox/OneDrive/Google Drive/iCloud — the more severe case, see
below) or a plain network share. This script is multi-line — follow the write-then-run
pattern from above (save as `~/.project-hub/_setup_scratch.py`, then run it
via the venv's Python — POSIX: `~/.project-hub/venv/bin/python3 <path>`,
Windows: `& "$env:USERPROFILE\.project-hub\venv\Scripts\python.exe" <path>`):

```python
import yaml
from pathlib import Path
cfg_path = Path.home() / '.project-hub' / 'config.yaml'
if not cfg_path.exists():
    exit(0)
cfg = yaml.safe_load(cfg_path.read_text()) or {}
db_path = cfg.get('db_path', '')
cloud_sync_hints = ['Dropbox', 'OneDrive', 'Google Drive', 'My Drive', 'iCloud', 'Mobile Documents']
network_share_hints = ['/mnt/', '/media/', '/Volumes/', '/net/']
if any(h in str(db_path) for h in cloud_sync_hints):
    print('CLOUD_SYNC:' + str(db_path))
elif any(h in str(db_path) for h in network_share_hints):
    print('NETWORK_SHARE:' + str(db_path))
else:
    print('LOCAL')
```

If the output starts with `CLOUD_SYNC:`, show:
```
🛑  Cloud-Sync-Pfad erkannt: {db_path}
Dropbox/OneDrive/Google Drive & Co. synchronisieren per Datei-Kopie, nicht per
Datei-Sperre — im WAL-Modus können .db/-wal/-shm dabei mitten im Schreibvorgang
kopiert werden und unabhängig voneinander divergieren. Das führt zu STILLER
DATENKORRUPTION, nicht zu einem SQLITE_BUSY-Fehler — der automatische Retry
hilft hier nicht, der Schaden ist bereits passiert.
Empfehlung: `db_path` auf einen lokalen Pfad oder einen echten Netzwerk-Share
(NFS/Samba) setzen, nicht auf einen Cloud-Sync-Ordner.
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

Multi-line — follow the write-then-run pattern (save as
`~/.project-hub/_setup_scratch.py`, then run via the venv's Python — POSIX:
`~/.project-hub/venv/bin/python3 <path>`, Windows:
`& "$env:USERPROFILE\.project-hub\venv\Scripts\python.exe" <path>`).
`${CLAUDE_PLUGIN_ROOT}` is interpolated by the harness the same way it already is in
Steps 4, 5, and 6 below — no need to guess the plugin root via a candidate-path search.
**On Windows the interpolated value can contain backslashes** (e.g.
`C:\Users\...\project-hub`) — wrap it in a raw string (`r'${CLAUDE_PLUGIN_ROOT}/...'`)
wherever it's embedded in a Python string literal, or a plain `'...'` literal
turns a stray `\U`/`\u`/`\N` sequence into an invalid Unicode escape and the
script fails with a `SyntaxError` before it even runs. Applies to this step
and Steps 5 and 6 below, all of which embed the same placeholder:

```python
import shutil
from pathlib import Path

knowledge_src = Path(r'${CLAUDE_PLUGIN_ROOT}/knowledge')
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

Multi-line — follow the write-then-run pattern (save as
`~/.project-hub/_setup_scratch.py`, then run via the venv's Python — POSIX:
`~/.project-hub/venv/bin/python3 <path>`, Windows:
`& "$env:USERPROFILE\.project-hub\venv\Scripts\python.exe" <path>`):

```python
import sys
sys.path.insert(0, r'${CLAUDE_PLUGIN_ROOT}/servers/project-hub-server')
from tools.db import init_db
init_db()
print('DB: OK')
```

### Step 7: Report

The block below is a template, not literal output: every line with ` / `-separated
alternatives (`OK / ERSTELLT`, `OK / INSTALLIERT (...) / ÜBERSPRUNGEN (...)`, etc.)
lists every possible state — replace it with the single alternative that actually
happened in this run. Never print more than one alternative on a line.

```
## Project Hub Setup

- Daten-Verzeichnis: OK / ERSTELLT  (~/.project-hub)
- Venv:             OK / ERSTELLT  (~/.project-hub/venv)
- Dependencies:     SYNCHRONISIERT
- Config:           OK / ERSTELLT  (~/.project-hub/config.yaml)
- Knowledge:        OK / INSTALLIERT (~/.project-hub/knowledge/[gewählte Types]) / ÜBERSPRUNGEN (auf Nutzerwunsch)
- Datenbank:        OK / INITIALISIERT

Starte Claude Code neu, damit der MCP Server geladen wird.
Danach kannst du loslegen:
- `/new-project`  — Erstes Projekt anlegen
- `/knowledge`    — Knowledge-Templates mit echten Inhalten befüllen
- `/help`         — Alle Skills anzeigen
```

If the user chose "skip" in Step 5b, report the Knowledge line as ÜBERSPRUNGEN
(auf Nutzerwunsch) — never OK or INSTALLIERT, since neither is true: nothing
was verified present and nothing was installed.

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
