---
name: Security triage
about: Track a security hardening or vulnerability remediation task
---

## Summary

## Source

- [ ] Internal review
- [ ] Dependency scanner
- [ ] Secret scanner
- [ ] External report

## Severity

- [ ] Low
- [ ] Medium
- [ ] High
- [ ] Critical

## Affected Area

- [ ] Build/install
- [ ] Input validation
- [ ] Runtime boundaries
- [ ] CI/CD
- [ ] Documentation/process

## Mitigation Plan

## Validation

- [ ] `PYTHONPATH=src python scripts/validate_all.py`
- [ ] `PYTHONPATH=src python scripts/validate_repository.py`
- [ ] `PYTHONPATH=src python scripts/release_readiness.py --json`

## Follow-up

- [ ] Backport needed
- [ ] Security.md/process update needed
- [ ] Changelog/release note entry added
