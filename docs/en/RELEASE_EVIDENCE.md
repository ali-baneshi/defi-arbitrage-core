# Release Evidence

This document maps machine-readable readiness states to the evidence maintainers must collect before any public release.

## Readiness State Model

- `local_validation_ready`: deterministic in-repository checks passed in the active tree.
- `reviewer_ready`: local validation is coherent enough for external review to begin.
- `open_source_ready`: local validation passed and manual release blockers have evidence.
- `public_release_ready`: same as open-source readiness for this alpha repository; it must remain false while manual gates are blocked.
- `production_ready`: always false for this repository because the project does not trade, sign transactions, deploy contracts, or manage funds.

## Manual Evidence Requirements

- `historical_credentials_rotated`: maintainer attestation naming credential classes, rotation date, and owner of rotation verification.
- `old_git_backups_excluded`: maintainer attestation that old repositories, `.git` backups, and local archive paths are excluded from publication artifacts.
- `independent_history_scan`: tool name, scan date, scan scope, and pass/fail result from an independent history scanner outside the dependency-free baseline.
- `localized_docs_refreshed_or_scoped`: release notes either scope `docs/en` as canonical or document that localized files were refreshed for the release.

## Required Machine Evidence

Before asking for public review, attach or reference output from:

```bash
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/validate_output_contracts.py
PYTHONPATH=src python scripts/release_readiness.py --json
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
```

If Cargo is unavailable, say so explicitly and do not claim Rust validation for that environment. If `pytest` or `ruff` are unavailable, say so explicitly and rely on CI or a prepared maintainer environment for those checks.

## What Evidence Does Not Prove

Passing evidence does not prove production safety, contract audit status, live-market correctness, transaction safety, credential history cleanliness, or public-release approval. It only proves that the active tree met the stated offline validation and review-readiness checks.
