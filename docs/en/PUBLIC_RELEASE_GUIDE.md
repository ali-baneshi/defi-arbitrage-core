# Public Release Guide

## Recommended GitHub About Text

Deterministic multi-network DeFi analysis core for local market snapshots. Validation-first, contract-driven, offline by default.

## Recommended Short Description

A reusable offline DeFi arbitrage analysis kernel with explicit validation, multi-network support, stable JSON contracts, and optional Rust acceleration.

## Recommended Topics

- `defi`
- `arbitrage`
- `market-analysis`
- `quant-research`
- `graph-algorithms`
- `json-schema`
- `python`
- `rust`
- `developer-tools`
- `infrastructure`

## First Public Release Positioning

The first public release should be presented as an alpha offline MVP. The strongest professional story is not that this repository is a trading bot. The strongest story is that it is a deterministic, validation-first DeFi analysis kernel with explicit trust boundaries and clear extension points.

## Suggested Release Notes Structure

### Title

`defi-arbitrage-core v0.1.0-alpha`

### Opening

This first public release introduces `defi-arbitrage-core`, a reusable offline analysis core for local DeFi market snapshots. The project focuses on deterministic validation, bounded cycle analysis, multi-network portability, stable JSON contracts, and clean separation between analysis and execution.

### Highlights

- public `defi-arbitrage-core` branding and CLI entrypoint
- explicit multi-network snapshot support through the `network` field
- fail-closed schema and runtime validation
- structured JSON outputs, diagnostics, and release-readiness reporting
- optional Rust analyzer behind a safe process boundary with Python fallback
- Solidity and Vyper template validation for repository-level contract workflows
- English, Persian, and Chinese documentation for public onboarding

### Scope Statement

This release is an alpha infrastructure release. It does not include wallet handling, signing, live RPC ingestion, trade execution, contract deployment, or production-readiness claims.

### Release Evidence To Preserve

Maintain a copy of:

- `PYTHONPATH=src python scripts/validate_all.py --include-rust`
- `PYTHONPATH=src python scripts/release_readiness.py --json`
- independent history-scan results
- maintainer attestations for credential rotation and old-history exclusion

## Before Marking The Repository Public

Confirm the following in practice, not just in prose:

- historical credentials were rotated
- old `.git` backups cannot be published accidentally
- release evidence is captured and archived
- the repository description and topics match the actual scope
- no document implies live trading or production safety
