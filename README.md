# defi-arbitrage-core

[![CI](https://github.com/ali-baneshi/defi-arbitrage-core-public-mvp/actions/workflows/ci.yml/badge.svg)](https://github.com/ali-baneshi/defi-arbitrage-core-public-mvp/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange.svg)
![Shell](https://img.shields.io/badge/Shell-Bash-4EAA25.svg)
![Solidity](https://img.shields.io/badge/Solidity-smart--contracts-363636.svg)
![Vyper](https://img.shields.io/badge/Vyper-smart--contracts-7A42F4.svg)
![Dockerfile](https://img.shields.io/badge/Docker-containerized-2496ED.svg)
![Makefile](https://img.shields.io/badge/Build-Make-6D00CC.svg)

A boundary-driven DeFi arbitrage analysis core focused on deterministic validation,
multi-network market modeling, and reproducible off-chain opportunity evaluation.

It is built for researchers, quantitative developers, protocol analysts, and backend teams that need reusable analysis infrastructure rather than a finished trading product or execution bot.

## What This Project Does

- Validates local DeFi market snapshots with fail-closed rules
- Analyzes bounded exchange-rate cycles across multiple EVM-style networks
- Produces stable text and JSON output for downstream systems
- Exposes extension points for providers, reporters, policies, and optional Rust-backed analysis

## What This Project Does Not Do

- It does not collect live RPC data
- It does not manage wallets, keys, signing, or transaction submission
- It does not claim on-chain executability or profit realization
- It does not compile, deploy, or audit smart contracts

## Why It Exists

A lot of DeFi repositories mix experimentation, execution logic, secrets, and incomplete infrastructure. This project keeps a narrower boundary: deterministic offline analysis with explicit contracts, reproducible validation, and a clean path for extension.

## Technology Stack

- Python is the canonical implementation and the default runtime
- Rust is optional and isolated behind a process boundary for acceleration-sensitive workflows
- JSON schemas define the public input, output, diagnostics, and release-readiness contracts

## Current Scope

The current release is an offline alpha MVP for analysis infrastructure. It is suitable for local validation, simulation, route analysis, integration testing, reviewer evaluation, and as a foundation for larger systems that add their own ingestion and execution layers.

## Minimal Example

Input snapshot:

```json
{
  "source": "research-snapshot",
  "network": "base",
  "timestamp": "2026-05-05T00:00:00Z",
  "edges": [
    {"source": "USDC", "target": "ETH", "rate": 0.000255, "venue": "dex-base-a", "fee_bps": 25, "liquidity": 85000},
    {"source": "ETH", "target": "DAI", "rate": 3985, "venue": "dex-base-b", "fee_bps": 30, "liquidity": 90000},
    {"source": "DAI", "target": "USDC", "rate": 1.003, "venue": "dex-base-c", "fee_bps": 5, "liquidity": 100000}
  ]
}
```

Run:

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/base_market_snapshot.json --json
```

Output:

```json
[
  {
    "network": "base",
    "path": ["DAI", "USDC", "ETH", "DAI"],
    "venues": ["dex-base-c", "dex-base-a", "dex-base-b"],
    "gross_return": 1.013118627069043,
    "profit_bps": 131.18627069043097,
    "limiting_liquidity": 85000.0,
    "estimated_capacity": 10000.0
  }
]
```

## Quick Start

Fastest no-install verification:

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json
PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics
PYTHONPATH=src python -m defi_arbitrage_core.cli --self-check
PYTHONPATH=src python scripts/validate_all.py
```

Editable install when dev tools are available:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
defi-arbitrage-core examples/market_snapshot.json --json
pytest
ruff check .
```

Optional Rust validation:

```bash
cargo build --manifest-path rust/arbcore-rs/Cargo.toml
PYTHONPATH=src python scripts/validate_rust_service.py
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --engine auto --rust-binary rust/arbcore-rs/target/debug/defi-arbitrage-core-rs
```

## Docker

Build a reproducible runtime image:

```bash
docker build -t defi-arbitrage-core:local .
```

Run the example snapshot inside the container:

```bash
docker run --rm defi-arbitrage-core:local examples/market_snapshot.json --json
```

Run the full repository validation suite inside Docker:

```bash
docker run --rm --entrypoint python defi-arbitrage-core:local scripts/validate_all.py
```

## Architecture At A Glance

- `providers` load untrusted local snapshots
- `validation` enforces schema and business rules
- `engine` computes bounded cycles deterministically
- `reporters` emit stable human-readable and JSON output
- `service` wraps the optional Rust analyzer behind a safe process boundary
- `contracts` validates Solidity and Vyper templates as repository artifacts

## Production And CI Notes

This repository is intended to run cleanly in local environments, GitHub Actions, and containerized workflows. The baseline validation path is dependency-light and network-independent after installation. Optional layers such as Rust acceleration and pytest/ruff checks are additive, not foundational.

Key commands:

```bash
PYTHONPATH=src python scripts/validate_all.py
PYTHONPATH=src python scripts/validate_all.py --include-rust
PYTHONPATH=src python scripts/release_readiness.py --json
```

## Validation As A First-Class Feature

- JSON schemas document the public contracts
- Runtime validation rejects malformed or unsafe input early
- Negative-case scripts prove that bad inputs fail deterministically
- Output-contract checks keep CLI, diagnostics, and release reports stable

Validation commands:

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --validate-only
PYTHONPATH=src python scripts/validate_contracts.py
PYTHONPATH=src python scripts/demo_workflow.py
PYTHONPATH=src python scripts/validate_negative_cases.py
PYTHONPATH=src python scripts/validate_schema_consistency.py
```

## Who Should Use This Infrastructure

This project is a good fit for:

- researchers validating local market-structure ideas
- quant and market-structure teams comparing route quality across networks
- backend and data-platform engineers building simulation, scoring, or review pipelines
- protocol, analytics, and infrastructure companies that need a reusable analysis kernel

It is a poor fit for anyone looking for a wallet-integrated bot, live execution engine, or turnkey production trading stack.

## Practical Use Cases

### For Individual Researchers
- **Academic Research**: Validate theoretical arbitrage models against curated market snapshots without operational overhead
- **Strategy Prototyping**: Test path-finding algorithms and cycle-detection heuristics in a controlled environment
- **Educational Projects**: Learn DeFi market mechanics through reproducible, deterministic analysis
- **Portfolio Analysis**: Evaluate historical market inefficiencies across multiple networks for research papers

### For Quantitative Trading Teams
- **Route Quality Benchmarking**: Compare arbitrage path efficiency across Base, Ethereum, Arbitrum, Polygon, and other EVM networks
- **Market Structure Analysis**: Identify liquidity topology patterns and venue-specific characteristics
- **Backtesting Foundation**: Use as the deterministic analysis kernel in larger backtesting pipelines
- **Opportunity Scoring**: Generate structured candidate opportunities for downstream risk and execution systems

### For Protocol Development Teams
- **Liquidity Design Validation**: Test how protocol changes affect arbitrage dynamics before mainnet deployment
- **MEV Impact Assessment**: Analyze potential extractable value patterns in protocol designs
- **Cross-Protocol Integration**: Evaluate routing efficiency when integrating with other DeFi protocols
- **Simulation Infrastructure**: Embed as the analysis layer in protocol simulation environments

### For Data Platform & Analytics Companies
- **Market Intelligence Products**: Build dashboards and alerting systems on top of structured opportunity data
- **Research-as-a-Service**: Offer deterministic market analysis to institutional clients
- **Data Pipeline Integration**: Use as a validation and enrichment stage in broader DeFi data workflows
- **Compliance & Reporting**: Generate auditable, reproducible market analysis reports

### For Backend Engineering Teams
- **Internal Tooling**: Provide developers with a clean, testable foundation for DeFi analysis features
- **Microservice Architecture**: Deploy as a stateless analysis service behind API gateways
- **CI/CD Integration**: Use validation scripts as quality gates for market data pipelines
- **Developer Onboarding**: Offer new team members a well-documented, bounded system to learn from

### For Infrastructure & DevOps Teams
- **Containerized Workflows**: Deploy reproducible analysis environments via Docker
- **Batch Processing**: Schedule periodic snapshot analysis jobs in orchestration systems (Airflow, Kubernetes CronJobs)
- **Multi-Region Deployment**: Run identical analysis logic across geographic regions with local snapshots
- **Observability Integration**: Emit structured JSON for ingestion into monitoring and logging platforms

### For Financial Services & Compliance
- **Audit Trail Generation**: Produce deterministic, timestamped analysis records for regulatory review
- **Risk Assessment**: Evaluate market opportunity characteristics before capital allocation decisions
- **Compliance Monitoring**: Validate that analysis workflows meet internal control requirements
- **Third-Party Review**: Provide external auditors with transparent, reproducible analysis artifacts

### What This Infrastructure Does NOT Support
- **Live Trading Execution**: No wallet management, transaction signing, or on-chain execution
- **Real-Time Data Collection**: No RPC polling, WebSocket streams, or mempool monitoring
- **Production Trading Bots**: No position management, capital allocation, or P&L tracking
- **Smart Contract Deployment**: No compilation, gas estimation, or mainnet interaction
- **Custody & Key Management**: No private key storage, HSM integration, or signing infrastructure

### Adoption Anti-Patterns to Avoid
- Treating this as a complete trading system (it is an analysis kernel, not an execution platform)
- Expecting real-time performance without adding your own data ingestion layer
- Assuming contract templates are production-ready without independent audit
- Using this for live trading without building proper risk controls and execution infrastructure
- Deploying to production without understanding the trust boundaries and validation semantics

## Documentation

Start here for deeper review:

- `docs/en/README.md`
- `docs/en/README_DETAILS.md`
- `docs/en/ADVANCED_README.md`
- `docs/en/PUBLIC_RELEASE_GUIDE.md`
- `docs/en/STATUS.md`
- `docs/en/PROJECT_BOUNDARIES.md`

Persian and Chinese documentation are also included under `docs/fa/` and `docs/zh/`.

## GitHub Metadata

Recommended repository topics: `defi`, `arbitrage`, `market-analysis`, `quant-research`, `graph-algorithms`, `json-schema`, `rust`, `python`, `developer-tools`, `infrastructure`.
