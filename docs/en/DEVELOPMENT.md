# Development Guide

## Dependency-Free Baseline

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/demo_workflow.py
```

This is the minimum required validation path and does not require `pytest`, `ruff`, or new packages.

## Optional Dev Tools

```bash
pip install -e .[dev]
pytest
ruff check .
```

Do not install tools when your environment forbids it. CI may run these optional checks.

## Contract Development

```bash
PYTHONPATH=src python scripts/validate_contracts.py
PYTHONPATH=src python scripts/validate_contracts.py --json
```

Keep contract templates offline, not audited, and non-deployable by default.

## Rust Validation

```bash
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
PYTHONPATH=src python scripts/validate_rust_service.py
```

The Rust analyzer is optional. Python fallback must remain tested and working.
