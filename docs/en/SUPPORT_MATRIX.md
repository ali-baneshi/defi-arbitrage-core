# Support Matrix

This matrix is the compact maintainer view of supported, optional, and explicitly unsupported behavior.

## Canonical Components

| Area | Status | Canonical source | Validation evidence |
| --- | --- | --- | --- |
| Python snapshot validation and analysis | Supported offline | `src/arbcore/` | `scripts/validate_all.py` |
| Multi-network snapshot labeling | Supported offline | `src/arbcore/models.py`, `schemas/market_snapshot.schema.json`, `schemas/opportunity.schema.json` | `scripts/validate_schema_consistency.py`, `scripts/validate_output_contracts.py` |
| CLI JSON and text output | Supported offline | `src/arbcore/cli.py`, `src/arbcore/reporters.py` | `scripts/validate_output_contracts.py` |
| Diagnostics/self-check JSON | Supported offline | `src/arbcore/diagnostics.py`, `schemas/diagnostics.schema.json` | `scripts/validate_output_contracts.py` |
| Release readiness JSON | Supported offline status report | `scripts/release_readiness.py`, `schemas/release_readiness.schema.json` | `scripts/release_readiness.py --json` |
| Solidity contract templates | Offline template validation only | `contracts/solidity/`, `contracts/contract-manifest.json` | `scripts/validate_contracts.py --json` |
| Vyper contract templates | Offline template validation only | `contracts/vyper/`, `contracts/contract-manifest.json` | `scripts/validate_contracts.py --json` |
| Rust analyzer | Optional process-boundary analyzer | `rust/arbcore-rs/` | `scripts/validate_rust_service.py`, `cargo test` |

## Explicitly Unsupported

| Area | Status | Reason |
| --- | --- | --- |
| Live trading | Unsupported | No wallet, signing, mempool, or execution layer exists. |
| Mainnet/testnet RPC | Unsupported | Baseline validation must not require network access. |
| Contract compilation | Unsupported in baseline | No Solidity or Vyper compiler is required or downloaded. |
| Contract deployment | Unsupported | Templates are not audited deployable artifacts. |
| Cross-chain bridging or routing | Unsupported | The core analyzes a single local snapshot at a time. |
| Production funds | Unsupported | The project is an alpha offline analysis core. |
| Canonical localized docs | English remains canonical | Localized docs are maintained mirrors, but release-critical interpretation still anchors to `docs/en`. |

## Review Rule

If a change expands any unsupported area, it must add code, validation, documentation, and release-gate updates in the same review. Prose-only expansion is not acceptable.
