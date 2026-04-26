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
- Nothing yet

### Security
- Nothing yet

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

[Unreleased]: https://github.com/markus-michalski/project-hub/compare/v1.5.1...HEAD
[1.0.0]: https://github.com/markus-michalski/claude-agents-project-management/releases/tag/v1.0.0
[1.1.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.1.0
[1.3.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.3.0
[1.3.1]: https://github.com/markus-michalski/project-hub/releases/tag/v1.3.1
[1.3.2]: https://github.com/markus-michalski/project-hub/releases/tag/v1.3.2
[1.4.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.4.0
[1.5.0]: https://github.com/markus-michalski/project-hub/releases/tag/v1.5.0
[1.5.1]: https://github.com/markus-michalski/project-hub/releases/tag/v1.5.1
