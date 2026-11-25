## Summary

## Why This Change Matters

## Validation

- [ ] `PYTHONPATH=src python scripts/validate_all.py`
- [ ] `python -m pytest -q`
- [ ] `ruff check .`
- [ ] Schema and docs updated if the input or output contract changed

## Public Contract Checklist

- [ ] No secrets, credentials, logs, generated metadata, or bulky artifacts are included.
- [ ] No production-readiness, trading-profit, deployment, or audit claims were added.
- [ ] User-facing changes updated README, `docs/en/`, examples, and schemas as needed.
- [ ] The change preserves deterministic offline analysis boundaries.
- [ ] A removed or changed surface is recorded in `docs/en/DECISIONS.md`.
