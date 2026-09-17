# Release Checklist

This project is an alpha offline MVP. Do not present it as production trading software.

## Release Positioning

The strongest public story for this repository is:

- deterministic DeFi analysis core
- explicit JSON contracts and validation
- multi-network reusable infrastructure
- strict boundary between analysis and execution

Avoid positioning it as a trading bot, execution engine, or deployable smart-contract system.

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/demo_workflow.py
python -m pip install -r requirements-release.txt
python scripts/build_release_artifacts.py
```

- [ ] Run active-tree secret scan:

```bash
./scripts/secret_scan.sh
```

- [ ] Run optional dev checks where tools are already available:

```bash
pytest
ruff check .
```

- [ ] Run Rust checks if claiming Rust support:

```bash
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
PYTHONPATH=src python scripts/validate_rust_service.py
```

- [ ] Run an independent full-history scanner such as gitleaks outside this dependency-free baseline.
- [ ] Review `contracts/` for unsafe examples, real addresses, RPC URLs, deployment claims, and missing `NOT AUDITED` notices.
- [ ] Review `README.md`, `SECURITY.md`, `docs/en/RUNBOOK.md`, and `docs/en/SECURITY.md` for accurate maturity and limitation claims.
- [ ] Confirm generated files such as `*.egg-info/`, caches, logs, databases, and build outputs are not tracked.
- [ ] Confirm Persian and Chinese docs either mirror current behavior or clearly defer to English docs for latest release-critical details.

## Current Public Snapshot Workflow

1. Finish active-tree and history review tasks
2. Run validation and capture evidence for the current public snapshot
3. Review README, SECURITY, and docs landing pages
4. Confirm translation scope in `docs/TRANSLATION_STATUS.md`
5. Publish the evidence and status update without rewriting `main`

## Current Version Identity

Keep the current package identity `0.1.0a1` unchanged. Any existing `v1.0.0`
tag is historical and must not be moved or deleted. This preparation creates no
new tag and does not rewrite or force-push the public `main` branch.

## No-Dependency Release Gate

Run `PYTHONPATH=src python scripts/release_readiness.py --json` before publishing. The report must be reviewed by a maintainer. Public release remains blocked while any manual release gate is unresolved, even if local validation passes.
