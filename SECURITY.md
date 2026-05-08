# Security Policy

## Scope

This repository is an offline analysis core. It intentionally excludes private-key handling, transaction signing, smart-contract deployment, live RPC integrations, and trade execution.

## Security Posture

This project aims to be safe by construction in a constrained scope:

- local input only
- deterministic validation
- no required network access
- no wallet or signing layer
- optional Rust isolated behind a fail-closed boundary

## Reporting Vulnerabilities

Please report suspected vulnerabilities privately to Ali Baneshi at baneshi712@gmail.com. Include affected files, reproduction steps, expected impact, and whether any secret exposure is involved.

## Secret Hygiene

Do not commit `.env`, `.env.*`, private keys, API tokens, RPC credentials, wallet data, logs, databases, model checkpoints, generated package metadata, or runtime state. Use `.env.example` only for non-secret placeholders.

## Smart-Contract Template Safety

The `contracts/` workspace contains Solidity and Vyper templates only. They are not audited, compiled, deployed, or production-ready. Validate them with:

```bash
PYTHONPATH=src python scripts/validate_contracts.py
```

The validator rejects obvious secret patterns, hard-coded addresses, RPC URLs, missing safety notices, and dangerous primitives. It does not replace a compiler, formal verification, testnet simulation, or professional audit.

## Git History Warning

This repository has been reinitialized with a fresh sanitized Git history. The previous local history contained sensitive material; rotate all credentials that may have been exposed and do not publish any backup of the old `.git` directory.

## Local Checks

```bash
PYTHONPATH=src python scripts/validate_all.py
./scripts/secret_scan.sh
```

The included secret scan is lightweight active-tree scanning and does not replace independent full-history scanning before publication.

## Translation Note

English security docs are canonical. Localized docs are helpful for readers, but release-critical security interpretation should use `docs/en/SECURITY.md`.

## No-Dependency Release Gate

Run `PYTHONPATH=src python scripts/release_readiness.py --json` before publishing. The report must be reviewed by a maintainer. Public release remains blocked while any manual release gate is unresolved, even if local validation passes.
