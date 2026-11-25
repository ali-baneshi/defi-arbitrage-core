---
name: Release hardening
about: Track concrete tasks required for a maintainer release
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
- [ ] Schema drift
- [ ] Scope-boundary regressions

## Validation Plan

- [ ] `PYTHONPATH=src python scripts/validate_all.py`
- [ ] `python -m pytest -q`
- [ ] `ruff check .`
- [ ] `python scripts/benchmark.py`

## Exit Criteria

- [ ] All checks pass in CI
- [ ] README/docs updated for user-facing changes
- [ ] `docs/en/RELEASE_CHECKLIST.md` is complete
