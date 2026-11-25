# Changelog

All notable changes to `defi-arbitrage-core` are documented here.

## Unreleased

### Added

- Schema-parity, adversarial input, CLI contract, and byte-identical golden
  output tests.

### Changed

- Reduced the product to one deterministic offline analyzer: one import
  package, one console script, two published schemas, one validation command.
- Snapshot paths are normal filesystem paths; the CWD/temp allow-list is gone.
- Explicit `null` for snapshot metadata is rejected instead of silently
  defaulted.
- Cycle search has a deterministic 250,000 edge-expansion budget and fails with
  `AnalysisLimitError` instead of running unbounded.
- Documentation collapsed to English under `docs/en/`; the release-evidence
  gate was replaced by a maintainer checklist.

### Removed

- Optional Rust analyzer, process adapter, parity fixtures, and CI cost.
- Solidity/Vyper template workspace and validators.
- Release-evidence schemas, scripts, and readiness report.
- Diagnostics, self-check, policy-dump, structured-error, and optional engine
  CLI flags.
- Environment-based configuration and the implicit default snapshot.
- Persian and Chinese documentation trees and duplicate release/status pages.
