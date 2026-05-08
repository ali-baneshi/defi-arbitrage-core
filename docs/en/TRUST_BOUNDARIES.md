# Trust Boundaries

## Untrusted Inputs

- Snapshot JSON files are untrusted and must pass dependency-free validation before analysis.
- Provider implementations are untrusted adapters until they return validated `MarketSnapshot` objects.
- Contract manifests and source templates are untrusted until `scripts/validate_contracts.py` passes.
- Rust analyzer output is untrusted until parsed into Python `Opportunity` objects.

## Trusted Local Components

- Python source under `src/arbcore/` is the authoritative local implementation.
- Schemas under `schemas/` document public data contracts but do not replace runtime validation.
- Validation scripts under `scripts/` are local guardrails, not external security scanners.

## Explicitly Out Of Boundary

- Private keys, seed phrases, RPC credentials, wallets, signing, transaction broadcast, live trading, and deployment scripts.
- Contract compiler assurance, bytecode verification, gas analysis, formal verification, or audit claims.
- Historical Git secret scanning; this must be performed externally before release.

## Fail-Closed Rules

- Unknown snapshot and manifest keys are rejected.
- Unsupported contract languages are rejected.
- Contract paths must remain under `contracts/`.
- Contract source hashes, entrypoints, language metadata, and local-only network scope are checked.
- Risk policy caps reject unbounded local analysis settings.
