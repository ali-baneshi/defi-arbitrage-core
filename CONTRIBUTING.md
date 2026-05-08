# Contributing

Thank you for contributing. The project goal is a small, secure, dependency-light offline analysis core that maintainers can audit quickly.

## Contribution Priorities

High-value contributions usually improve one or more of these areas:

- deterministic analysis quality
- validation and fail-closed behavior
- public data-contract clarity
- extensibility for providers, reporters, and network-specific surrounding tooling
- documentation quality and reviewer experience

## Baseline Validation

```bash
PYTHONPATH=src python scripts/validate_all.py
```

Optional when tools are already available:

```bash
pytest
ruff check .
cargo test --manifest-path rust/arbcore-rs/Cargo.toml
```

## Rules

- Keep live trading, private keys, signing, RPC-specific code, and deployment logic outside this core.
- Add tests for providers, reporters, policies, CLI flags, validation behavior, Rust changes, and contract validation changes.
- Keep contract templates under `contracts/`, marked `ARBCORE_CONTRACT_TEMPLATE` and `NOT AUDITED`.
- Do not commit generated artifacts, logs, databases, model files, `.env` files, credentials, or `*.egg-info/` metadata.
- Prefer explicit data contracts and small interfaces over framework-heavy abstractions.
- Update English docs first; refresh Persian and Chinese docs in the same change when feasible, and update `docs/TRANSLATION_STATUS.md` if they intentionally lag.

## Maintainer Attribution

Maintainer metadata should use Ali Baneshi, baneshi712@gmail.com, https://github.com/ali-baneshi where appropriate.
