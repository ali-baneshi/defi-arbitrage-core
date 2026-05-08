## Summary

## Why This Change Matters

## Validation

- [ ] `PYTHONPATH=src python scripts/validate_all.py`
- [ ] `PYTHONPATH=src python scripts/validate_repository.py`
- [ ] `PYTHONPATH=src python scripts/validate_documented_commands.py`
- [ ] `pytest` and `ruff check .` where available
- [ ] Rust validation if Rust behavior changed
- [ ] Contract validation if `contracts/`, schemas, or validators changed

## Public Contract Checklist

- [ ] No secrets, credentials, logs, generated metadata, or bulky artifacts are included.
- [ ] No production-readiness, trading-profit, deployment, or audit claims were added.
- [ ] User-facing changes updated docs, examples, and schemas as needed.
- [ ] English docs were updated first, and Persian/Chinese docs were refreshed or intentionally scoped.
- [ ] New behavior preserves deterministic offline analysis boundaries.
