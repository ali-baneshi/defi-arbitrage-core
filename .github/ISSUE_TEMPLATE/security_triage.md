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
- [ ] `python -m pytest -q`
- [ ] `ruff check .`

## Follow-up

- [ ] Security.md/process update needed
- [ ] Changelog entry added
