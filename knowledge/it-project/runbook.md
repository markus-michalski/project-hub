# Deployment Runbook — IT Project

> **Template file.** Copy to `~/.project-hub/knowledge/it-project/runbook.md`
> and replace placeholders with your project's actual deployment procedure.

## Purpose

Step-by-step guide for deploying [Service / Application Name] to production.
This document is the authoritative reference during a deployment window.
Keep it updated after every deployment.

## Deployment Overview

| Field | Value |
|-------|-------|
| Service / Application | |
| Version being deployed | |
| Deployment window | YYYY-MM-DD HH:MM – HH:MM (TZ) |
| Deploying engineer | |
| Deployment type | Blue/Green / Rolling / In-place / Canary |
| Estimated downtime | None / < X min |
| Rollback possible? | Yes / No |

## Pre-Deployment Checklist

Complete all items before starting. Do not proceed with unchecked blockers.

**Code & Build**
- [ ] PR merged, all CI checks green
- [ ] Artifact / container image tagged and pushed to registry
- [ ] Release notes / changelog reviewed

**Dependencies & Config**
- [ ] All dependent services are at required versions
- [ ] Environment variables / secrets updated in target environment
- [ ] Database migrations reviewed (destructive changes flagged)
- [ ] Feature flags configured for this release

**Communication**
- [ ] Deployment window communicated to stakeholders
- [ ] On-call engineer confirmed available
- [ ] Rollback decision threshold agreed (e.g. > X errors in 5 min → roll back)

**Access & Tools**
- [ ] Access to production environment confirmed
- [ ] Monitoring dashboards open
- [ ] Runbook printed or accessible offline

---

## Deployment Steps

> Mark each step with ✓ when complete. ⬅ ROLLBACK POINT marks the last safe point to abort.

| Step | Action | Command / Detail | Done |
|------|--------|-----------------|------|
| 1 | Notify team: deployment starting | Post in #deployments channel | ☐ |
| 2 | Create database backup | `[backup command]` | ☐ |
| 3 | ⬅ **ROLLBACK POINT** — verify backup completed | Check backup file size / hash | ☐ |
| 4 | Enable maintenance mode (if applicable) | `[command or flag]` | ☐ |
| 5 | Run database migrations | `[migration command]` | ☐ |
| 6 | Verify migration output — no errors | Check logs / migration table | ☐ |
| 7 | Deploy new application version | `[deploy command / pipeline trigger]` | ☐ |
| 8 | Wait for deployment to complete | Monitor deploy pipeline | ☐ |
| 9 | Disable maintenance mode | `[command or flag]` | ☐ |
| 10 | Run smoke tests (see Post-Deployment section) | `[smoke test command]` | ☐ |
| 11 | Monitor error rates for 15 min | Dashboard: [link] | ☐ |
| 12 | Notify team: deployment complete | Post in #deployments channel | ☐ |

---

## Rollback Procedure

Trigger rollback immediately if:
- Error rate exceeds [X]% in [Y] minutes after go-live
- P0 / P1 bug confirmed in production
- Core functionality unavailable

**Rollback Steps:**

| Step | Action | Command / Detail | Done |
|------|--------|-----------------|------|
| R1 | Notify team: initiating rollback | Post in #deployments channel | ☐ |
| R2 | Enable maintenance mode | `[command]` | ☐ |
| R3 | Revert application to previous version | `[rollback command / previous artifact tag]` | ☐ |
| R4 | Revert database migrations (if applicable) | `[down migration command]` — only if schema changed | ☐ |
| R5 | Restore database backup (last resort) | `[restore command]` — caution: data loss risk | ☐ |
| R6 | Disable maintenance mode | `[command]` | ☐ |
| R7 | Verify rollback successful (smoke tests) | See Post-Deployment Verification | ☐ |
| R8 | Notify stakeholders | Email / Slack to Contact Tree | ☐ |
| R9 | Create incident ticket | Include timeline and root cause hypothesis | ☐ |

**Rollback decision owner:** [Name / Role]
**Rollback authorisation required from:** [Name / Role]

---

## Post-Deployment Verification

Run after every deployment (and after rollback).

**Smoke Tests**

| Test | Expected Result | Pass / Fail |
|------|-----------------|-------------|
| Health check endpoint | HTTP 200, `{"status":"ok"}` | |
| Login / authentication | Successful | |
| Core user flow: [describe] | Completes without error | |
| Core user flow: [describe] | Completes without error | |
| Background job / queue | Processing, no error spike | |

**Monitoring Gates (15 min post-deployment)**

| Metric | Baseline | Alert Threshold | Current |
|--------|----------|-----------------|---------|
| Error rate (5xx) | <0.1% | >1% | |
| P95 response time | <500 ms | >1,000 ms | |
| Queue depth | <100 | >1,000 | |
| CPU utilisation | <60% | >85% | |

---

## Contact Tree

Call in order. Only escalate if previous contact is unavailable.

| Priority | Role | Name | Phone | Slack / Teams |
|----------|------|------|-------|---------------|
| 1 | On-call Engineer | | | |
| 2 | Tech Lead | | | |
| 3 | Product Owner | | | |
| 4 | Project Sponsor / Stakeholder | | | |
| 5 | External Vendor On-call | | | |

---

## Known Issues & Workarounds

| Issue | Symptom | Workaround | Ticket |
|-------|---------|------------|--------|
| [Known issue 1] | [What it looks like] | [Short-term fix] | #000 |
| [Known issue 2] | [What it looks like] | [Short-term fix] | #000 |

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| YYYY-MM-DD | 1.0 | Initial version | — |
