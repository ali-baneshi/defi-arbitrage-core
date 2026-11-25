# Contributing

The goal is a small, dependency-light offline analyzer that one maintainer can
audit in an afternoon. Prefer deletion and repair over new layers.

## Before changing behavior

1. Read `docs/en/PRODUCT.md` and `docs/en/ARCHITECTURE.md`.
2. Check whether the change expands the input/output contract. If it does,
   update the schema, runtime validation, tests, and docs together.
3. Add a test only for a contract or a real failure mode, not for an
   implementation detail.

## Validation

```bash
PYTHONPATH=src python scripts/validate_all.py
python -m pytest -q
ruff check .
```

## Rules

- Keep live trading, wallets, signing, RPC, and deployment out of this package.
- Do not add a runtime dependency without a demonstrated need and an install
  check.
- Keep one import package (`arbcore`) and one console script
  (`defi-arbitrage-core`).
- Keep documentation in English under `docs/en/`.
- Do not commit generated files, caches, logs, databases, secrets, or local
  paths.
- Every behavior change updates the docs that describe it in the same commit.
- A judgment call that removes surface goes in `docs/en/DECISIONS.md`.

## Commit checks

Every commit must leave the tree green:

```bash
PYTHONPATH=src python scripts/validate_all.py
python -m pytest -q
ruff check .
```
