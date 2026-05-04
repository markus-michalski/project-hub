# Project Charter — IT Project

> **Template file.** Copy to `~/.project-hub/knowledge/it-project/charter.md`
> and replace placeholders with your project's actual content.

## Project Overview

| Field | Value |
|-------|-------|
| Project Name | |
| Project Sponsor | |
| Project Manager | |
| Tech Lead | |
| Start Date | YYYY-MM-DD |
| Target End Date | YYYY-MM-DD |
| Budget | |
| Priority | High / Medium / Low |
| Project Phase | Discovery / Planning / Execution / UAT / Go-Live |

## Objectives

Define 2–4 SMART goals. Each must be Specific, Measurable, Achievable, Relevant, Time-bound.

| # | Objective | Metric | Target | Deadline |
|---|-----------|--------|--------|----------|
| 1 | [Specific outcome the project delivers] | [How success is measured] | [Quantified target] | YYYY-MM-DD |
| 2 | [Specific outcome the project delivers] | [How success is measured] | [Quantified target] | YYYY-MM-DD |
| 3 | [Specific outcome the project delivers] | [How success is measured] | [Quantified target] | YYYY-MM-DD |

## Scope

### In Scope

| Item | Description |
|------|-------------|
| | Feature / system / component |
| | Feature / system / component |
| | Feature / system / component |

### Out of Scope

| Item | Reason / Future Phase |
|------|-----------------------|
| | Explicitly excluded — reason |
| | Deferred to Phase 2 |
| | Requires separate budget approval |

## Stakeholders

RACI: **R** = Responsible, **A** = Accountable, **C** = Consulted, **I** = Informed

| Name | Role | Requirements | Architecture | Testing | Deployment | Sign-off |
|------|------|:---:|:---:|:---:|:---:|:---:|
| | Project Sponsor | I | C | I | I | A |
| | Product Owner | A | C | C | I | R |
| | Tech Lead | C | A | C | R | C |
| | QA Lead | C | I | A | C | C |
| | Operations | I | C | I | A | C |

**Contact details:**

| Name | Role | Email | Phone | Availability |
|------|------|-------|-------|-------------|
| | Project Sponsor | | | |
| | Product Owner | | | |
| | Tech Lead | | | |
| | QA Lead | | | |

## Risks

| # | Risk | Likelihood | Impact | Score | Mitigation | Owner |
|---|------|:---:|:---:|:---:|-----------|-------|
| R1 | Scope creep | Medium | High | High | Strict change control process, CR required for all additions | PM |
| R2 | Key person dependency | Medium | High | High | Knowledge sharing sessions, documentation of critical paths | Tech Lead |
| R3 | Third-party / vendor delay | Low | High | Medium | Early vendor engagement, contractual SLAs | PM |
| R4 | Data migration failure | Low | Critical | High | Dry-run migrations, rollback scripts, data validation gates | Tech Lead |
| R5 | [Custom risk] | | | | | |

**Risk Score = Likelihood × Impact:** Low–Low = Low, Medium–High = High, High–Critical = Critical

## Timeline

| Phase | Description | Target Date | Owner | Status |
|-------|-------------|-------------|-------|--------|
| M0 | Project kick-off & charter signed | YYYY-MM-DD | PM | |
| M1 | Requirements finalised | YYYY-MM-DD | Product Owner | |
| M2 | Architecture approved | YYYY-MM-DD | Tech Lead | |
| M3 | Development complete | YYYY-MM-DD | Tech Lead | |
| M4 | QA / UAT sign-off | YYYY-MM-DD | QA Lead | |
| M5 | Go-Live | YYYY-MM-DD | PM | |
| M6 | Hypercare period ends | YYYY-MM-DD | Operations | |

## Budget Overview

| Category | Estimated | Actual | Variance | Notes |
|----------|-----------|--------|----------|-------|
| Internal development (FTE) | | | | |
| External / contractor | | | | |
| Infrastructure / cloud | | | | |
| Licenses & tooling | | | | |
| Training | | | | |
| Contingency (10%) | | | | |
| **Total** | | | | |

## Success Criteria

- [ ] All objectives in the Objectives table met by target date
- [ ] Go-live with zero P0 / P1 bugs open
- [ ] Performance benchmarks met (define targets: e.g. p95 response < 500 ms)
- [ ] All stakeholders have signed off
- [ ] Documentation updated (runbook, ADRs, API docs)
- [ ] Monitoring and alerting configured and verified

## Definition of Done

- All acceptance criteria reviewed and passed
- Code reviewed and merged to main
- Unit, integration, and E2E tests passing in CI
- Security scan completed, no critical findings
- Runbook written and reviewed by Operations
- Deployed to production and smoke-tested
- Rollback procedure documented and tested
- Stakeholder sign-off obtained in writing

## Change Log

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial version | — |
