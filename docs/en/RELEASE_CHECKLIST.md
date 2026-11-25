# Release checklist

This replaces the former release-evidence gate. It is a maintainer checklist,
not a claims system.

## Before tagging

- [ ] `pyproject.toml` version and `arbcore.__version__` match.
- [ ] `PYTHONPATH=src python scripts/validate_all.py` passes.
- [ ] `python -m pytest -q` passes.
- [ ] `ruff check .` passes.
- [ ] `python scripts/benchmark.py` shows the budget holds.
- [ ] The three example snapshots produce documented results.
- [ ] A fresh virtual environment installs with `pip install .` and runs
  `defi-arbitrage-core examples/market_snapshot.json --json`.
- [ ] README, `PRODUCT.md`, and `USAGE.md` agree with the CLI.
- [ ] No secrets, keys, tokens, or local paths are tracked.
- [ ] No generated files (`__pycache__`, caches, build outputs) are tracked.

## Tagging

Tagging, pushing, and publishing are separate, explicit actions. This
repository's normal development does not create tags or publish releases.

## If republishing an old copy

Old clones or backups may contain history that is not part of the current
tree. Scan the full history with an independent tool before publishing a copy,
and do not publish old `.git` directories.
