# Validation Guide

This repository has a dependency-free validation baseline for constrained environments and optional checks for prepared CI/dev environments.

## Validation Layers

- Schema validation: public JSON shapes documented under `schemas/`
- Runtime/domain validation: fail-closed checks in Python and Rust adapters
- Workflow validation: scripts that prove examples, outputs, and release reports behave deterministically
- Negative validation: intentionally bad inputs that must fail

## Baseline Command

```bash
PYTHONPATH=src python scripts/validate_all.py
```

This runs:

1. Python compile checks for `src`, `tests`, `scripts`, and `examples`.
2. Dependency-free unit checks in `scripts/run_unit_checks.py`.
3. Example snapshot validation and JSON analysis workflow.
4. Custom provider example.
5. Solidity/Vyper contract manifest and template validation.
6. Repository metadata checks for required docs, schemas, README commands, and tracked generated files.
7. Negative validation scenarios for bad snapshots and unsafe contract manifest changes.
8. Deterministic demo workflow with machine-readable output inspection.
9. Release readiness report that separates local validation from public release gates.
10. Active-tree secret scan.

Use this when `pytest`, `ruff`, or other optional tools are unavailable.

## Machine-Readable Workflows

```bash
PYTHONPATH=src python scripts/demo_workflow.py
PYTHONPATH=src python scripts/validate_negative_cases.py
PYTHONPATH=src python scripts/validate_contracts.py --json
PYTHONPATH=src python scripts/release_readiness.py --json
```

`demo_workflow.py` verifies that the profitable example produces a positive opportunity, the no-opportunity example returns an empty list, and contract validation succeeds.

## Optional Rust Validation

```bash
PYTHONPATH=src python scripts/validate_all.py --include-rust
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
```

Rust remains optional. Python must remain usable without Cargo.

## Optional Dev Tool Validation

```bash
python -m pytest -q
python -m ruff check .
```

Run these only where the tools are already installed or in CI. Do not install new packages in constrained environments.

## Interpreting Failure

- Compile failure: fix syntax/import errors first.
- Example workflow failure: inspect snapshot schema and CLI output.
- Contract validation failure: inspect finding code and path; do not bypass errors.
- Repository validation failure: restore missing docs/schemas or remove tracked generated files.
- Secret scan failure: remove the value and rotate if it may be real.

## Release Readiness Report

`PYTHONPATH=src python scripts/release_readiness.py --json` intentionally reports `public_release_ready: false` until manual gates are completed: historical credential rotation, exclusion of old `.git` backups, independent history scanning, and localization scope/refresh. A `true` local validation result is not permission to publish.

## Fail-Closed Behavior Covered

Dependency-free checks cover invalid snapshots, invalid metadata, unbounded risk policy values, contract entrypoint drift, contract source-hash drift, and non-local contract network metadata. These checks are intentionally negative: they prove unsafe or ambiguous inputs fail with non-zero exits.

## Schema Validation vs Domain Validation

Schemas document stable machine-readable shapes. Runtime validation goes further and enforces domain rules such as:

- positive rates
- bounded hop and result limits
- object-only metadata
- explicit non-empty network labels
- Rust opportunity parity and fail-closed parsing

When the two differ, runtime validation is authoritative for safety.

## CI Coverage Expectations

`PYTHONPATH=src python scripts/validate_repository.py` checks that CI runs optional `ruff`/`pytest` in prepared environments, the dependency-free baseline with Rust included, the release readiness report, and Rust unit tests. This makes CI drift visible without requiring those tools locally.

## Structured CLI Checks

The validation suite exercises `--diagnostics`, JSON validation-only output, and `--error-json` failure output so wrappers can consume deterministic success and failure states.


## Drift Checks Added For Reviewers

Repository validation now checks that `docs/en/PROJECT_BOUNDARIES.md` exists and carries the canonical boundary markers, and that `scripts/release_readiness.py` exposes separate local, reviewer, open-source, public-release, and production readiness fields. This keeps status claims machine-checkable instead of relying only on prose.


## Python/Rust Parity

`PYTHONPATH=src python scripts/validate_rust_service.py` now checks more than process startup: it compares Python and Rust JSON opportunities on canonical fixtures and verifies fail-closed Rust behavior for invalid timestamps, invalid metadata, and excessive policy bounds. This protects the optional analyzer from silently drifting away from the Python contracts.
