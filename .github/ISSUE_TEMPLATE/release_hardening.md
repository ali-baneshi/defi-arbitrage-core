---
name: Release hardening
about: Track concrete tasks required for safe public release
---

## Objective

## Scope

- [ ] CI hardening
- [ ] Security checks
- [ ] Deterministic output checks
- [ ] Schema compatibility checks
- [ ] Documentation alignment

## Risk Addressed

- [ ] Installation reliability
- [ ] Supply-chain risk
- [ ] Secret exposure risk
- [ ] Contract/schema drift
- [ ] Scope-boundary regressions

## Validation Plan

- [ ] `PYTHONPATH=src python scripts/validate_all.py`
- [ ] `PYTHONPATH=src python scripts/validate_golden_fixtures.py`
- [ ] `PYTHONPATH=src python scripts/validate_schema_consistency.py`
- [ ] `PYTHONPATH=src python scripts/release_readiness.py --json`

## Exit Criteria

- [ ] All checks pass in CI
- [ ] README/docs updated for user-facing changes
- [ ] Release notes include risk and rollback notes
