# Contributing to Project Hub

Thank you for your interest. This document explains how to contribute.

## Governance Model

Project Hub follows a **Benevolent Dictator For Life (BDFL)** model.
[Markus Michalski](https://github.com/markus-michalski) is the sole maintainer with final say on all changes, direction, and releases. Contributions are welcome within that structure.

## License

This project is licensed under the **[PolyForm Noncommercial License 1.0.0](LICENSE.md)** — source-available, personal and non-commercial use only. Not OSI Open Source.

## Contributor License Agreement (CLA)

Before your first PR can be merged, you must sign the [Contributor License Agreement](CLA.md). Signing is automated via [cla-assistant.io](https://cla-assistant.io/) — a bot will comment on your PR with a one-click signing link. You only need to sign once.

## Branch Model

- **`master`** — the only long-lived branch, always in a releasable state
- **Feature branches** — short-lived, branched from `master`, merged via PR

Branch naming:

| Prefix | When |
|--------|------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `chore/` | Maintenance |
| `refactor/` | Code refactoring without behavior change |

## Development Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/project-hub.git
cd project-hub
git remote add upstream https://github.com/markus-michalski/project-hub.git
```

### 2. Create a Feature Branch

```bash
git checkout master
git pull upstream master
git checkout -b feat/your-feature-name
```

### 3. Set Up Local Development

```bash
python3 -m venv ~/.project-hub/venv
~/.project-hub/venv/bin/pip install -r requirements.txt
~/.project-hub/venv/bin/pip install pytest ruff mypy
```

### 4. Make Your Changes

Follow existing patterns. For each change type:

- **New skill**: Create `skills/your-skill/SKILL.md` with frontmatter (`name`, `description`, `model`, `user-invocable`). Add routing entry to `CLAUDE.md`. Add entry to `skills/help/SKILL.md`.
- **New MCP tool**: Add to `servers/project-hub-server/tools/`. Export via `server.py`. Document in `CLAUDE.md`.
- **New project type**: Add `project-types/{name}/README.md` and `project-types/{name}/research.md`. Add knowledge templates to `knowledge/{name}/`.

### 5. Test Locally

```bash
# Run all tests
~/.project-hub/venv/bin/pytest

# Lint
~/.project-hub/venv/bin/ruff check servers/

# Type checking
~/.project-hub/venv/bin/mypy servers/project-hub-server/
```

All checks must pass before opening a PR.

### 6. Commit Convention

This project uses **[Conventional Commits](https://www.conventionalcommits.org/)**:

```
feat: add pagination to list_projects
fix: resolve updated_at missing from notes response
docs: update CONTRIBUTING with project-type guide
chore: bump version to 2.0.0
```

| Type | When | Version impact |
|------|------|----------------|
| `feat` | New feature | Minor |
| `fix` | Bug fix | Patch |
| `docs` | Documentation | None |
| `chore` | Maintenance | None |
| `refactor` | Refactoring | None |
| `feat!` | Breaking change | Major |

### 7. Open a Pull Request

Use the PR template. Fill in every checklist item.

## Code Style

- Python: formatted and linted by `ruff`
- Type hints required on all public functions
- Tests required for new MCP tools and Python functions
- No comments explaining what code does — only *why* when non-obvious

## What Gets Accepted

- Bug fixes with tests
- Performance improvements with benchmarks
- New project types (README + research + knowledge templates)
- Documentation improvements

**Out of scope (maintainer-only):**
- Architectural changes to the MCP server
- New core skills without prior issue discussion
- Breaking API changes without version bump

When in doubt: open an issue first before investing time in a PR.
