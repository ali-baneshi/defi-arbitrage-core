# Reviewer Guide

This guide is for maintainers and external reviewers who need a quick, skeptical read of what is normative, what is illustrative, and what must not be inferred from this repository.

## Canonical Sources Of Truth

- Python package behavior: `src/arbcore/` is authoritative for local analysis, validation, CLI, diagnostics, and contract-template validation.
- Public JSON contracts: `schemas/` documents machine-readable inputs, outputs, diagnostics, errors, policies, and contract reports.
- No-install validation: `PYTHONPATH=src python scripts/validate_all.py --include-rust` is the strongest local baseline when Cargo is available.
- Release status: `PYTHONPATH=src python scripts/release_readiness.py --json` is authoritative for local readiness vs public-release blockers.
- Support matrix: `docs/en/SUPPORT_MATRIX.md` is the quick map of supported, optional, and explicitly unsupported areas.
- Release evidence: `docs/en/RELEASE_EVIDENCE.md` maps readiness states to required manual evidence.
- English docs in `docs/en/` are canonical. `docs/TRANSLATION_STATUS.md` scopes localized docs.

## Normative vs Illustrative

Normative:

- `src/arbcore/models.py`, `validation.py`, `engine.py`, `providers.py`, `reporters.py`, `cli.py`, `diagnostics.py`.
- `src/arbcore/contracts/` for manifest and template validation semantics.
- `schemas/*.json` as public contract documentation.
- `scripts/validate_*.py`, `scripts/demo_workflow.py`, and `scripts/release_readiness.py` as local verification workflows.

Illustrative:

- `examples/*.json` and `examples/custom_provider.py` are deterministic examples only.
- `contracts/solidity/*` and `contracts/vyper/*` are inert templates only.
- `rust/arbcore-rs` is optional acceleration and parity validation, not the orchestration source of truth.

## What Not To Infer

- No production trading readiness.
- No smart-contract audit, compilation, deployment, or execution readiness.
- No live chain RPC, mempool, wallet, signing, or key-management behavior.
- No guarantee that an offline candidate opportunity exists on-chain.
- English remains canonical for release-critical interpretation even when localized mirrors are refreshed.

## Fast Review Path

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/release_readiness.py --json
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
```

If `pytest` or `ruff` are unavailable locally, do not treat them as passed. CI is configured to run them in a prepared environment.
