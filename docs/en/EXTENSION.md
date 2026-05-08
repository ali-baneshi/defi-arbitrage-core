# Extension Guide

## Add A Provider

Implement `MarketDataProvider.load_snapshot()` and return a validated `MarketSnapshot`. Providers are untrusted input boundaries; normalize external data and reject unsupported fields. New providers should preserve explicit `network` identity so downstream systems can analyze multiple chains safely.

## Add A Reporter

Implement `Reporter.render(opportunities) -> str`. Reporters must avoid printing secrets or private operational metadata.

## Add Policy Logic

Keep policy explicit. Prefer a wrapper that filters `Opportunity` objects rather than hiding rules in providers. Add tests for boundary and negative cases.

## Add A Contract Template

1. Add Solidity under `contracts/solidity/` or Vyper under `contracts/vyper/`.
2. Include `ARBCORE_CONTRACT_TEMPLATE` and `NOT AUDITED`.
3. Avoid real addresses, RPC URLs, deployment scripts, and dangerous primitives.
4. Add the artifact to `contracts/contract-manifest.json`.
5. Run `PYTHONPATH=src python scripts/validate_contracts.py`.
6. Update tests and docs for user-facing changes.

## Add Another Language

Use JSON snapshots and validation reports as language-neutral contracts. Add a manifest language value, extension rule, validator rules, examples, schemas, docs, and tests before exposing it publicly.

## Add Another Network

The core does not need a new engine implementation for each chain. To support another network professionally:

1. Emit snapshots with a stable `network` label such as `ethereum`, `arbitrum`, `optimism`, `base`, `avalanche`, or `bnb-chain`.
2. Keep asset symbols, venue labels, and fee/liquidity semantics consistent inside that network.
3. Add deterministic examples and negative tests if the new surrounding tooling introduces new failure modes.
4. Keep chain-specific RPC, bridge, gas, sequencer, and execution concerns outside this package.

## Rust Acceleration Boundary

Rust extensions must preserve local JSON input/output contracts and remain optional. Keep failures isolated so Python can continue when Rust is unavailable.
