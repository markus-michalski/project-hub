## Description

<!-- Brief description of the change and the problem it solves. -->

## Type of Change

- [ ] `feat`: New feature (minor version bump)
- [ ] `fix`: Bug fix (patch version bump)
- [ ] `docs`: Documentation only (no version bump)
- [ ] `chore`: Maintenance (no version bump)
- [ ] `refactor`: Code refactoring without behavior change
- [ ] Breaking change (major version bump — add `!` suffix: `feat!`)

## Checklist

### Before Submitting

- [ ] My commits follow [Conventional Commits](https://conventionalcommits.org/)
- [ ] All tests pass locally (`pytest`)
- [ ] `ruff check servers/` passes
- [ ] `mypy servers/project-hub-server/` passes (no new errors)

### Documentation

- [ ] I have updated `CLAUDE.md` if routing or workflow rules changed
- [ ] I have updated `README.md` if user-facing behavior changed
- [ ] I have added/updated `SKILL.md` if a skill was added or changed

### Testing

- [ ] I have added tests for new MCP tools or Python functions
- [ ] Smoke tests pass (`pytest tests/smoke/ -q`)

**Manual testing performed:**
<!-- Describe what you tested manually, if applicable. -->

## Related Issues

Closes #<!-- issue number -->
