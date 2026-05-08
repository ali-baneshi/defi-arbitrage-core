# Project Overview

defi-arbitrage-core is a minimal Python infrastructure for offline market opportunity analysis. It extracts the useful kernel from a larger DeFi arbitrage research system while removing live execution, private keys, deployment workflows, logs, models, and generated state. It now includes offline Solidity and Vyper template validation, but not contract compilation or deployment.

## Best Entry Points

- Start with `README.md` for the repository-level promise and quick commands.
- Read `docs/en/STATUS.md` for current maturity and blockers.
- Read `docs/en/PROJECT_BOUNDARIES.md` before inferring capabilities.
- Read `docs/en/REVIEWER_GUIDE.md` if you are evaluating the repository skeptically.
- Read `docs/en/VALIDATION.md` before changing validation scripts or status claims.

## Purpose

The project helps developers test graph-based market analysis workflows from local data. It is suitable for research, education, simulation, and as a clean foundation for separately reviewed integrations.

## Goals

- Keep the core small enough to audit.
- Make data contracts explicit and stable.
- Provide real extension points through protocols.
- Default to no network, no wallet, and no secrets.
- Document risks honestly.

## Non-Goals

- It is not a live trading bot.
- It does not execute or recommend trades.
- It does not compile, deploy, audit, or interact with smart contracts.
- It does not contain AI models, private RPC endpoints, or wallet code.

## Current Maturity

The working tree is a serious MVP and this repository has been reinitialized with a fresh sanitized Git history. Any credentials from the previous local history must still be treated as compromised and rotated.

## Reading Order

1. `docs/en/STATUS.md`
2. `docs/en/PROJECT_BOUNDARIES.md`
3. `docs/en/ARCHITECTURE.md`
4. `docs/en/VALIDATION.md`
5. `docs/en/RELEASE_EVIDENCE.md`

## Extended Reading

- `docs/en/README_DETAILS.md` explains target users, adoption patterns, and realistic organizational fit.
- `docs/en/ADVANCED_README.md` explains infrastructure boundaries, trust model, and extension posture in more depth.
