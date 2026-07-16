# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- `setup`/`session-start` now fall back to the `py -3` launcher when `python`/
  `python3` resolve to the Microsoft Store app-execution-alias stub (exit code
  49) instead of a real interpreter — common on Intune/SCCM-managed Windows
  devices where Python is installed but not on `PATH`. Venv creation (Step 3)
  now reuses the interpreter resolved during platform detection instead of
  hardcoding `python`/`python3` again (#69)
- `setup` Step 5b (knowledge template install) now uses the interpolated
  `${CLAUDE_PLUGIN_ROOT}` — already proven to work in Steps 4/5/6 — instead of
  guessing the plugin root via a hardcoded candidate-path search that could
  silently install templates from the wrong version, or skip them entirely,
  once the plugin cache and a dev checkout diverge. Note: since template
  files are never overwritten once present, re-running setup fixes future/
  never-installed cases but won't retroactively replace templates a previous
  run already installed from the wrong source — delete the affected files
  under `~/.project-hub/knowledge/` manually and re-run setup if needed (#70)

### Security
- Nothing yet

## [2.4.0] - 2026-07-16

### Added
- include project links in export/import (#64) (#67)
- show project relations in dashboard/report output (#63) (#66)
- add project-to-project relations (#59) (#65)

### Changed
- add marketplace install method, fix stale resume session pattern (#58)
- bump the actions-all group across 1 directory with 2 updates (#54)
- bump the pip-all group across 1 directory with 3 updates (#53)

### Fixed
- launch MCP server on native Windows without WSL (#68)
- check for existing contacts before creating a new one (#62)
- correct type annotation for fields dict in tool_update_contact

## [2.3.1] - 2026-06-17

### Fixed
- prevent duplicate entries when shared contact already exists (#51)

## [2.3.0] - 2026-06-17

### Added
- add shared/global contact directory across projects (#50)

### Changed
- bump actions/checkout (#45)
- bump the pip-all group across 1 directory with 3 updates (#48)

## [2.2.2] - 2026-06-12

### Changed
- bump the pip-all group with 2 updates (#44)

### Fixed
- load all notes instead of hardcoded limit=5 (#47)

## [2.2.1] - 2026-05-27

### Changed
- bump the pip-all group with 2 updates (#41)

### Fixed
- repair updated_at migration for legacy notes databases (#43)

## [2.2.0] - 2026-05-19

### Added
- add fillable project-type templates with import support (#40)

### Changed
- bump the pip-all group with 3 updates (#39)
- bump the pip-all group with 3 updates (#38)
- simplify README, link to wiki documentation
- bump the pip-all group with 8 updates (#37)
- bump the actions-all group with 2 updates (#36)
- switch to PolyForm NC 1.0.0 license + full governance setup

## [2.1.0] - 2026-05-04

### Added
- static HTML report export (issue #26) (#33)
- multi-user support — shared DB path + export/import (Phase 1) (#32)
- file attachments for notes (#31)
- add custom user-defined project types (#30)
- auto-export notes as markdown files to docs_path subfolders (#29)
- Phase 3 — DB + Knowledge (closes #11, #12, #13, #14) (#27)
- Phase 2 — Skills Gap (session-start, next-step, configure, haiku-migration) (#22)
- add CLAUDE.md and smoke test suite (phase 1, closes #2, closes #4)

### Changed
- feat!: Phase 4 — Governance + Scalability (closes #15, #16, #17) (#28)
- add .claude/settings.local.json to .gitignore
- fix import sorting in new test files (ruff I001)
- unit tests contacts/knowledge/search + mypy clean (closes #5, closes #6)
- fix import sorting violations flagged by ruff I rule
- migrate to pyproject.toml, close #3

### Fixed
- always sync deps via pip install, remove partial dep-check (#35)

## [1.5.1] - 2026-04-26

### Changed
- require explicit hub/client context in skill triggers

## [1.5.0] - 2026-04-15

### Added
- audit improvements — reliability, new features, tests

### Changed
- pin actions to versions with Node.js 24 support
- add GitHub Actions workflow with ruff + pytest matrix

## [1.4.0] - 2026-04-14

### Added
- install knowledge templates for all project types with user selection
- add knowledge templates for all project types

## [1.3.2] - 2026-04-14

### Fixed
- add env fallback for CLAUDE_PLUGIN_ROOT to suppress doctor warning

## [1.3.1] - 2026-04-14

### Fixed
- use Python to copy knowledge templates instead of ${CLAUDE_PLUGIN_ROOT} in bash

## [1.3.0] - 2026-04-14

### Added
- add knowledge management system

## [1.1.0] - 2026-04-13

### Added
- add config.yaml support for docs_root, db_path, user and language
- add /setup skill for first-time installation

### Changed
- add marketplace.json for /add marketplace installer
- feat!: rebuild as project-hub plugin with MCP server and skills
- Revise CHANGELOG for version 1.0.0 release

## [1.0.0] - 2025-11-24

### Changed
- Reset CHANGELOG to unreleased state
- Remove release script (belongs in script_collection)
- Prepare for public release
- Restructure plugins for project assistant use cases
- Initialize project management agents repository

### Fixed
- Correct Unreleased link in CHANGELOG

### Added
- Initial release with 11 specialized project management agents
- Core agents:
  - Document Analyst: Analyze and summarize project documents
  - Timeline Planner: Create timelines and manage dependencies
  - Meeting Facilitator: Prepare agendas and meeting documentation
  - Report Generator: Generate status reports and dashboards
  - Task Coordinator: Track action items and coordinate tasks
  - Decision Tracker: Document decisions using ADR format
- Extended agents:
  - Stakeholder Communicator: Craft targeted stakeholder communication
  - Risk Manager: Identify, assess, and mitigate project risks
  - Budget Tracker: Plan and track project budgets
  - Quality Assurance: Define quality standards and testing strategies
  - Knowledge Manager: Capture and organize organizational knowledge
- All-in-One assistant combining all 11 specialized agents
- Complete documentation with usage examples
- MIT License
- Comprehensive README with installation instructions

[Unreleased]: https://github.com/markus-michalski/project-hub/compare/v2.4.0...HEAD
[1.0.0]: https://github.com/markus-michalski/claude-agents-project-management/releases/tag/v1.0.0
[1.1.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.1.0
[1.3.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.3.0
[1.3.1]: https://github.com/markus-michalski/project-hub/releases/tag/v1.3.1
[1.3.2]: https://github.com/markus-michalski/project-hub/releases/tag/v1.3.2
[1.4.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.4.0
[1.5.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.5.0
[1.5.1]: https://github.com/markus-michalski/project-hub/releases/tag/v1.5.1
[2.1.0]: https://github.com/markus-michalski/project-hub/releases/tag/v2.1.0
[2.2.0]: https://github.com/markus-michalski/project-hub/releases/tag/v2.2.0
[2.2.1]: https://github.com/markus-michalski/project-hub/releases/tag/v2.2.1
[2.2.2]: https://github.com/markus-michalski/project-hub/releases/tag/v2.2.2
[2.3.0]: https://github.com/markus-michalski/project-hub/releases/tag/v2.3.0
[2.3.1]: https://github.com/markus-michalski/project-hub/releases/tag/v2.3.1
[2.4.0]: https://github.com/markus-michalski/project-hub/releases/tag/v2.4.0
