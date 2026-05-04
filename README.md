# Project Hub — Claude Code Plugin

![GitHub Tag](https://img.shields.io/github/v/tag/markus-michalski/project-hub?sort=semver&style=for-the-badge)
![License: PolyForm NC 1.0.0](https://img.shields.io/badge/license-PolyForm%20NC%201.0.0-red.svg?style=for-the-badge)

A personal project management hub for Claude Code. Create projects, store contacts, log meeting notes and emails, generate summaries, and draft communications — all within persistent project context.

**Full documentation:** [faq.markus-michalski.net/en/plugins/project-hub](https://faq.markus-michalski.net/en/plugins/project-hub)

## Installation

**Prerequisites:** Python 3.11+, Claude Code with plugin support

```bash
# 1. Clone the plugin
git clone https://github.com/markus-michalski/project-hub \
  ~/.claude/plugins/project-hub
```

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "project-hub@project-hub": true
  }
}
```

```bash
# 2. Initial setup
/project-hub:setup
```

## License

[PolyForm Noncommercial License 1.0.0](LICENSE.md) — source-available, personal and non-commercial use only. Commercial use requires explicit permission; contact the maintainer.
