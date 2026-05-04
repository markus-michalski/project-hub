# Security Policy

## Reporting a Vulnerability

**Do not open public issues for security vulnerabilities.**

Use GitHub's [Private Vulnerability Reporting](https://github.com/markus-michalski/project-hub/security/advisories/new) to report security issues privately. You will receive an acknowledgement within 72 hours.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x | ✅ |
| 1.x | ✅ patch fixes only |
| < 1.0 | ❌ |

## Security Considerations

### Local Data

Project Hub stores all data locally in `~/.project-hub/`. This includes:

- `project-hub.db` — SQLite database with projects, contacts, and notes
- `config.yaml` — local configuration
- `knowledge/` — your knowledge templates

**Keep `~/.project-hub/` private.** It may contain sensitive client information.

### MCP Server

The MCP server runs locally via stdio transport. It does not expose any network ports or accept remote connections. All communication goes through Claude Code.

### Path Traversal Protection

The knowledge tool validates topic names to prevent path traversal attacks. Do not modify this validation.

### Secrets and Credentials

**Never commit secrets to this repository.** This includes API keys, tokens, passwords, or `.env` files. User configuration lives at `~/.project-hub/config.yaml` — outside this repository.

If you accidentally commit a secret:
1. Immediately revoke or rotate the credential
2. Contact the maintainer via Private Vulnerability Reporting

### AI-Assisted Development

This project uses Claude Code (AI pair programming). All AI-generated code is reviewed by the maintainer before merging.

**When contributing:**
- Review all code changes carefully before submitting
- Do not include executable commands or scripts in PR descriptions
- Do not attempt to manipulate AI review via PR descriptions
