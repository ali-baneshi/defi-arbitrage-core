# Project Status

## Current Status

- Maturity: alpha offline MVP.
- Local deterministic validation: expected to pass with `PYTHONPATH=src python scripts/validate_all.py --include-rust` when Cargo is available.
- Public release: blocked until manual gates in `scripts/release_readiness.py` are resolved.
- Production use: not supported.

## Supported Today

- Local JSON snapshot validation and bounded cycle analysis.
- Text and JSON opportunity output.
- Structured CLI diagnostics and expected-error JSON.
- Dependency-free repository, workflow, schema, contract, negative-case, and release-readiness checks.
- Optional Rust analyzer parity validation.
- Offline Solidity and Vyper source-template organization and validation.

## Not Supported Today

- Live RPC, wallets, private keys, signing, mempool monitoring, transaction broadcast, or trade execution.
- Contract compilation, deployment, bytecode verification, gas analysis, audit, or production execution.
- Public release without credential rotation, old-history exclusion confirmation, independent history scanning, and localization scoping/refresh.

## Readiness Interpretation

`local_validation_ready: true` means deterministic local checks passed. It does not mean public release readiness, production readiness, trading safety, or contract safety.
