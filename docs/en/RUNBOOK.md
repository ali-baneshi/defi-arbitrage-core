# Operational Runbook

## Environment Assumptions

- Python 3.10 or newer.
- No required network access for baseline validation.
- No required third-party Python packages for baseline validation.
- Optional: `pytest`, `ruff`, and Cargo for extended validation.

## First-Time Verification

From the repository root:

```bash
PYTHONPATH=src python scripts/validate_all.py
```

Success means the command ends with:

```text
all dependency-free validation checks passed
```

This validates Python syntax, dependency-free unit checks, example snapshots, the custom provider example, smart-contract templates, repository metadata, deterministic demo workflows, and active-tree secret patterns.

## Common Commands

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/no_opportunity_snapshot.json --min-profit-bps 1
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --validate-only
PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics
PYTHONPATH=src python scripts/validate_contracts.py
PYTHONPATH=src python scripts/validate_negative_cases.py
PYTHONPATH=src python scripts/release_readiness.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
```

## Expected Outputs

- Snapshot validation: `Snapshot is valid: ...`
- Example validation: `Validated 2 example snapshot(s) and JSON analysis workflow`
- Unit checks: `dependency-free unit checks passed`
- Contract validation: `contract validation passed`
- Repository validation: `repository metadata validation passed`
- Demo workflow: JSON report with `"ok": true`
- Negative checks: `negative validation checks passed`
- Release readiness: `local_validation_ready: True` and `public_release_ready: False` until manual release gates are complete
- Full baseline: `all dependency-free validation checks passed`

## Troubleshooting

- Missing `pytest` or `ruff`: use `PYTHONPATH=src python scripts/validate_all.py`; do not install packages if your environment forbids it.
- Missing Cargo: omit `--include-rust`; Python remains the authoritative engine.
- Invalid snapshot: run `--validate-only` and fix unsupported keys, missing `edges`, invalid rates, invalid fees, or self-loop edges.
- No opportunities: lower `--min-profit-bps` for local experiments, confirm rates form a cycle, and remember results are candidates only.
- Rust disagreement: use `--engine python`, then run `PYTHONPATH=src python scripts/validate_rust_service.py` before trusting the optional binary.
- Contract validation failure: read the finding code, fix the manifest/path/source marker, and rerun `scripts/validate_contracts.py --json` for a machine-readable report.

## Security Review Checklist

- Confirm `.env` and `.env.*` are not tracked.
- Run `./scripts/secret_scan.sh`.
- Review `contracts/` for real addresses, RPC URLs, deployment claims, unsafe primitives, or missing `NOT AUDITED` notices.
- Review `schemas/` after changing public JSON contracts.
- Confirm docs do not claim production readiness.
- Confirm generated files such as `*.egg-info/`, caches, logs, databases, and Rust `target/` outputs are not tracked.

## Public Release Preparation

1. Rotate every credential that may have existed in previous local history.
2. Ensure old `.git` backups are not inside any publication path.
3. Run `PYTHONPATH=src python scripts/validate_all.py`.
4. Run `pytest` and `ruff check .` only where already available or in CI.
5. Run `cargo test --manifest-path rust/arbcore-rs/Cargo.toml` if claiming Rust support.
6. Run an independent history scanner outside this dependency-free baseline.
7. Review `README.md`, `SECURITY.md`, `RELEASE.md`, and contract docs for accurate maturity claims.
8. Tag only as an alpha/offline MVP until independent security and operational reviews are complete.

## Release-Day Quick Path

1. Run `PYTHONPATH=src python scripts/validate_all.py --include-rust` (or omit Rust where unavailable).
2. Run `PYTHONPATH=src python scripts/validate_golden_fixtures.py` to detect output contract drift.
3. Run `PYTHONPATH=src python scripts/release_readiness.py --json` and archive the output.
4. Confirm `docs/en/OPEN_SOURCE_RELEASE_PLAN.md` and `docs/en/OPEN_SOURCE_TASKS.md` reflect current status.
5. If any gate fails, do not tag a release; open/attach a release-hardening issue and rerun after fixes.

## Pre-Merge Operator Checklist

1. Run `PYTHONPATH=src python scripts/validate_all.py --include-rust` when Cargo is available.
2. Inspect `PYTHONPATH=src python scripts/release_readiness.py --json`; do not confuse local validation with public release readiness.
3. For contract changes, confirm `source_sha256` was intentionally updated and entrypoints match source functions.
4. Run `git status --short` and ensure no caches, build outputs, logs, DBs, or generated metadata are staged.
5. If docs changed, confirm `docs/TRANSLATION_STATUS.md` still accurately scopes canonical English docs.

## Version And CI Consistency

Repository validation checks that `pyproject.toml` and `arbcore.__version__` agree and that CI includes the expected validation commands. If this fails, fix metadata or CI before reviewing feature behavior.

## Diagnostics

Run `PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics` to inspect non-secret environment details, optional tool availability, resolved policy, validation commands, and built-in safety limits. This output is safe to paste into issues unless your local path itself is sensitive.
