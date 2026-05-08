# Project Boundaries

This document is the short reviewer-facing contract for what this repository is and is not.

## Canonical Sources

- Python under `src/arbcore/` is canonical for validation, orchestration, CLI behavior, diagnostics, and public API semantics.
- JSON schemas under `schemas/` document public payload shapes; dependency-free runtime checks are the fail-closed enforcement layer.
- Scripts under `scripts/` are the canonical no-install validation and release-readiness gates.
- Rust under `rust/arbcore-rs/` is optional process-boundary analysis support, not the canonical implementation.

## Offline-Only Boundary

The repository may read local files and emit local reports. It must not require private keys, RPC URLs, wallet access, transaction signing, contract deployment, or live trading to validate its core behavior.

## Smart-Contract Boundary

Solidity and Vyper support is manifest-based template support for review workflows. The repository validates source presence, hashes, language declarations, safety markers, and dangerous static patterns. It does not compile, audit, deploy, simulate, or prove contract safety.

## Release Boundary

A passing local validation report means deterministic checks passed in the active tree. It does not mean public release readiness, production readiness, or security clearance. Public release remains blocked until manual history, credential-rotation, localization-scope, and independent security review gates are complete.

## Reviewer Inference Rules

Reviewers should infer that this is an offline alpha core with explicit constraints. Reviewers should not infer that the project can trade, manage funds, safely deploy contracts, or interact with mainnet systems.
