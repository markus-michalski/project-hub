---
name: configure
description: |
  Interactively view and change PROJECT-HUB settings in ~/.project-hub/config.yaml.
  Use ONLY for project-hub configuration — NOT for mm-dev-toolkit, storyforge, or other
  plugin settings.
  Use when: (1) User says "Hub konfigurieren", "Hub-Einstellungen ändern", "project-hub config",
  "meinen Namen im Hub ändern", "Sprache im Hub ändern", "docs-Pfad ändern",
  (2) User explicitly invokes `/project-hub:configure`,
  (3) Context is clearly about changing project-hub settings.
  Do NOT trigger on bare "konfigurieren" / "configure" / "Einstellungen" — defer to
  the specific plugin the user is talking about.
model: claude-haiku-4-5
user-invocable: true
---

# Configure

View and update project-hub settings interactively.

## Workflow

### 1. Read Current Config

```bash
cat ~/.project-hub/config.yaml
```

If file not found:
```
Config-Datei nicht gefunden unter ~/.project-hub/config.yaml
Bitte zuerst `/project-hub:setup` ausführen.
```
**STOP**.

### 2. Parse and Display Current Values

Show the user their current settings before asking what to change:

```
## Project Hub — Aktuelle Einstellungen

| Setting | Aktueller Wert |
|---------|---------------|
| Name | [user.name] |
| E-Mail | [user.email] |
| Organisation | [user.organization] |
| Docs-Pfad | [docs_root] |
| Sprache | [default_language] (de = Deutsch, en = Englisch) |
| E-Mail-Ton | [communication.default_tone] |
| E-Mail-Signatur | [erste Zeile der Signatur oder "nicht gesetzt"] |
```

### 3. Ask What to Change

Use `AskUserQuestion` to pick which setting to update. Offer these options:

- **Name** — Dein Name für Kommunikations-Drafts
- **E-Mail** — Deine E-Mail-Adresse
- **Organisation** — Deine Firma / Organisation
- **Docs-Pfad** — Wo Projekt-Dokumente gespeichert werden (`docs_root`)
- **Sprache** — Standard-Sprache für generierte Texte (de / en)
- **E-Mail-Signatur** — Signatur für E-Mail-Drafts
- **E-Mail-Ton** — Ton für E-Mail-Drafts (professional / friendly / formal)
- **Projekttypen verwalten** — Eigene Projekttypen ansehen, erstellen oder löschen

### 4. Collect New Value

Ask the user for the new value. Show the current value for reference:

```
Aktuell: "[current value]"
Neuer Wert:
```

**Validation:**
- `user.email`: must contain `@`
- `docs_root`: accept `~`-paths, do NOT expand them (keep as-is in YAML)
- `default_language`: only `de` or `en` are valid
- `communication.default_tone`: only `professional`, `friendly`, or `formal`

If validation fails → show error and ask again.

### 5. Write Updated Config

Read the full config file, apply the change, write it back.

Use Python to preserve YAML structure and comments:

```bash
~/.project-hub/venv/bin/python3 -c "
import yaml, re
from pathlib import Path

config_path = Path.home() / '.project-hub' / 'config.yaml'
content = config_path.read_text()

# Parse to verify structure
config = yaml.safe_load(content)

# Apply change (example for user.name — adjust per setting)
config['user']['name'] = '$NEW_VALUE'

# Write back — use yaml.dump only for the value line, preserve comments via regex
# Simple approach: use sed-like replacement to keep comments intact
config_path.write_text(yaml.dump(config, default_flow_style=False, allow_unicode=True))
print('OK')
"
```

**Note:** When writing, use `yaml.dump(config, default_flow_style=False, allow_unicode=True)` to preserve Unicode characters (Umlaute). Comments in the original file will be lost — that is acceptable.

### 6. Confirm Change

```
✅ [Setting-Name] aktualisiert:
   [alter Wert] → [neuer Wert]

Weitere Einstellung ändern? `/project-hub:configure`
```

### 7. Handle "Projekttypen verwalten"

If the user selected **Projekttypen verwalten**:

**7a. Load and display types**

Call `tool_list_project_types()` and show a table:

```
## Projekttypen

| Typ | Quelle | Beschreibung |
|-----|--------|-------------|
| consulting | built-in | Client consulting project |
| hr-onboarding | custom | Employee HR processes |
```

**7b. Ask what to do**

Use `AskUserQuestion`:
- **Neuen Typ erstellen** → invoke `/project-hub:type-creator`
- **Typ löschen** → proceed to 7c
- **Zurück** → back to step 3

**7c. Delete a custom type**

- Ask user: "Welchen Typ möchtest du löschen?" (free text)
- Check: call `tool_get_project_type(name)` — if `source == "built-in"`, show error "Built-in Typen können nicht gelöscht werden" and offer to pick again
- Confirm deletion: "Typ '{name}' wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden."
  - Use `AskUserQuestion`: **Ja, löschen** / **Abbrechen**
- Call `tool_delete_project_type(name)` and confirm result

### 8. Offer Another Change

After confirming, offer to change another setting:

Use `AskUserQuestion`:
- **Ja, weitere Einstellung ändern** → back to step 3
- **Nein, fertig** → end skill

## Settings Reference

| YAML-Key | Display-Name | Type | Valid Values |
|----------|-------------|------|-------------|
| `user.name` | Name | string | any |
| `user.email` | E-Mail | string | must contain `@` |
| `user.organization` | Organisation | string | any |
| `docs_root` | Docs-Pfad | path | any (keep `~` as-is) |
| `default_language` | Sprache | enum | `de`, `en` |
| `communication.default_tone` | E-Mail-Ton | enum | `professional`, `friendly`, `formal` |
| `communication.email_signature` | E-Mail-Signatur | multiline string | any |
