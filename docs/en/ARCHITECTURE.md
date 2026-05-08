# Architecture

## Core Boundary

The project boundary is local input, deterministic validation, deterministic analysis, and local output. Anything that touches private keys, wallets, signing, RPC services, live trading, contract deployment, or production funds belongs outside this package.

## High-Level Diagram

```text
Local snapshot/provider
        |
        v
schema + runtime validation
        |
        v
 deterministic analysis engine
        |
        +--> text/json reporters
        |
        +--> optional Rust parity path
        |
        +--> downstream research/execution systems
```

## Modules

- `arbcore.models`: immutable market models: `Edge`, `MarketSnapshot`, `RiskPolicy`, and `Opportunity`.
- `arbcore.validation`: dependency-free JSON payload checks and serialization helpers.
- `arbcore.providers`: `MarketDataProvider` protocol and `JsonFileProvider`.
- `arbcore.engine`: bounded DFS cycle search and policy application.
- `arbcore.reporters`: text and JSON output protocols.
- `arbcore.config`: environment-based settings.
- `arbcore.cli`: command-line integration.
- `arbcore.service`: optional Rust process-boundary analyzer adapter.
- `arbcore.contracts`: smart-contract manifest loading and dependency-free Solidity/Vyper template validation.

## Market Data Flow

1. A provider loads a local `MarketSnapshot`.
2. Snapshot payloads and `Edge` objects are normalized and validated, including the explicit `network` label.
3. `AnalysisEngine` builds a directed graph.
4. The engine searches cycles up to `RiskPolicy.max_hops`.
5. Profit is computed after edge fees.
6. Policy gates filter by profit, liquidity, capacity, and result count.
7. Opportunity output preserves the originating `network`.
8. A reporter renders text or JSON.

## Contract Data Flow

1. `contracts/contract-manifest.json` declares Solidity and Vyper artifacts.
2. `arbcore.contracts.registry` parses artifact metadata.
3. `arbcore.contracts.validation` verifies paths, language extensions, safety markers, secret-like values, hard-coded addresses, RPC URLs, and dangerous primitives.
4. `scripts/validate_contracts.py` emits text or JSON validation reports.

This is template support only. The repository does not compile, deploy, audit, or execute smart contracts.

## Public Data Contracts

Schemas live in `schemas/` for snapshots, opportunities, contract manifests, and contract validation reports. Runtime validation remains dependency-free so the core can run in constrained environments.

## Multi-Network Boundary

The core is now network-aware but still intentionally network-agnostic:

- Network identity is a required part of the operational data model.
- The engine does not embed chain-specific execution logic.
- The package does not fetch RPC metadata, chain registries, gas prices, bridge paths, or token lists.
- Larger systems can run the same core independently for Polygon, Ethereum, Arbitrum, Optimism, Base, Avalanche, BNB Chain, or private/local environments by changing the snapshot input, not the engine.

## Python And Rust Boundary

Python is the authoritative orchestration and extension layer. Rust is optional and isolated as a process-boundary analyzer in `rust/arbcore-rs`. Both use the same snapshot and opportunity JSON contracts. Python falls back safely if Rust is missing, times out, or returns invalid output.

## Trust Boundaries

- Providers and snapshots are untrusted input.
- Reporters must not leak private metadata.
- Rust output is untrusted until parsed into `Opportunity` objects.
- Contract sources are untrusted templates until validated; validation is not an audit.
- Network labels are declarative input, not trusted proof of execution environment.

## Canonical Implementation

Python under `src/arbcore/` is authoritative for orchestration, validation, diagnostics, and public API semantics. The Rust binary is optional acceleration behind a process boundary and must preserve JSON contract parity, but it is not the canonical orchestration layer. Schemas in `schemas/` document contracts; runtime validation remains authoritative for fail-closed behavior.

## Normative And Illustrative Areas

Normative components are `src/arbcore/`, `schemas/`, and validation scripts in `scripts/`. Examples and contract templates are deterministic review fixtures, not production integrations. See `docs/en/REVIEWER_GUIDE.md` and `docs/en/TRUST_BOUNDARIES.md` for the reviewer-facing boundary map.


## Python/Rust Parity Contract

Python remains canonical. Rust must preserve the public snapshot and opportunity contracts for the supported process-boundary analyzer path. `scripts/validate_rust_service.py` builds the Rust binary, compares Python and Rust opportunity JSON for canonical positive and no-opportunity fixtures, and verifies fail-closed handling for invalid timestamp, invalid metadata, and unbounded policy cases.

Rust parity validation is evidence for the optional analyzer boundary only; it does not make Rust the canonical orchestration layer and does not prove production trading readiness.
