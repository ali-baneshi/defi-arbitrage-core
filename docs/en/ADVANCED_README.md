# Advanced Infrastructure Guide

## Design Philosophy

The project is designed as infrastructure first. Its value comes from being small, deterministic, and legible under review. Every major boundary tries to answer a practical question: what can be trusted, what must be validated, and what belongs outside this package.

The result is a system that is easier to audit, extend, and embed than a monolithic arbitrage repository that mixes analysis, execution, wallets, contracts, deployment, and operations.

## System Boundaries

The core accepts local snapshots and emits local reports. That boundary is deliberate.

Inside the boundary, the repository focuses on deterministic contracts, graph analysis, policy filtering, and stable output semantics. Outside the boundary, adopters are free to build collection agents, pricing services, decision engines, transaction systems, or contract deployment workflows under their own controls.

This makes the repository suitable as shared infrastructure inside a company or as a public foundation for other open-source tools.

## Trust Model

Providers and optional accelerators are treated as untrusted boundaries. A provider may read malformed files or inconsistent market data. An accelerator may fail, diverge, or become unavailable. The system therefore validates inputs explicitly and keeps a Python path that can remain authoritative even when optional Rust acceleration is unavailable.

That trust model is useful for organizations that need predictable failure modes instead of optimistic assumptions.

## Extensibility Model

The system is intended to be extended by individuals, startups, internal platform teams, or larger companies.

A typical extension strategy is:

- keep the snapshot contract stable
- add new providers that normalize proprietary or public datasets
- add network-specific examples and negative tests
- add custom reporters or wrappers for internal dashboards, queues, or research notebooks
- keep execution, custody, and production networking in separate services

This pattern allows multiple teams to share one analysis kernel without forcing them into the same operational architecture.

## Suitable Organizational Use Cases

For an individual researcher, the project offers a cleaner foundation than scattered scripts.

For a trading or market-structure team, it can serve as the deterministic analysis stage inside a larger opportunity review pipeline.

For a protocol or infrastructure company, it can act as a reusable validation and route-analysis layer for internal services, simulation environments, or partner tooling.

For an engineering manager or reviewer, it provides clear artifacts, schemas, and boundaries that make technical evaluation faster.

## Quality Bar For Public Use

A public infrastructure repository should be understandable before it is impressive. That means consistent naming, realistic examples, stable machine-readable outputs, explicit maturity language, and honest release blockers.

This repository aims to meet that bar by emphasizing:

- contract-driven interfaces
- deterministic validation
- multi-network reuse
- bounded and testable behavior
- clear release-readiness evidence

## What Adoption Should Look Like

A healthy adoption does not treat this repository as a magic bot. It treats it as a kernel.

Teams should understand the contracts, validate their snapshots, review the failure modes, and then build the surrounding systems they actually need. When used that way, the repository becomes a strong base for research platforms, analytics products, internal developer tooling, and controlled execution pipelines.

## Deep Dive: Infrastructure Boundaries

### Input Boundary

The system accepts local JSON snapshots that conform to the documented schema. This boundary is explicit and validated:

- **Schema Validation**: Every snapshot is checked against `schemas/market_snapshot.schema.json` before processing
- **Business Rule Validation**: Network identity, edge sanity, liquidity bounds, and fee reasonableness are enforced
- **Fail-Closed Semantics**: Invalid input is rejected early with structured error messages, never silently ignored
- **No Network Assumptions**: The system never fetches data, never assumes RPC availability, never requires API keys

This design means you can test the entire analysis pipeline with fixture files, version-controlled snapshots, or synthetically generated market conditions without external dependencies.

### Processing Boundary

Inside the boundary, the system focuses on deterministic graph analysis:

- **Cycle Detection**: Bellman-Ford-based bounded cycle enumeration with configurable depth limits
- **Rate Composition**: Multiplicative rate calculation with explicit fee deduction at each hop
- **Liquidity Constraints**: Capacity estimation based on the limiting liquidity in each path
- **Policy Filtering**: Configurable minimum profit thresholds, maximum path length, and network-specific rules

The engine is designed to produce identical output for identical input, regardless of execution environment, timestamp, or system state. This determinism is critical for reproducible research, regression testing, and multi-environment deployment.

### Output Boundary

The system emits structured, stable output in two formats:

- **Human-Readable Text**: Formatted tables with network, path, venues, profit basis points, and capacity
- **Machine-Readable JSON**: Structured opportunity objects conforming to `schemas/opportunity_report.schema.json`

Output stability is enforced through:

- **Schema Contracts**: JSON output shape is documented and validated in CI
- **Deterministic Ordering**: Opportunities are sorted by profit descending, then by path length
- **Stable Field Names**: Breaking changes to output structure require major version bumps
- **Diagnostics Separation**: Errors, warnings, and metadata are emitted to stderr or separate diagnostic channels

This makes the system safe to embed in automated pipelines, dashboards, and downstream decision systems.

### Extension Boundary

The system is designed for extension without modification:

- **Provider Protocol**: Implement `SnapshotProvider` to normalize proprietary data sources
- **Reporter Protocol**: Implement `OpportunityReporter` to emit custom formats (CSV, Parquet, database writes)
- **Policy Protocol**: Implement `OpportunityPolicy` to add domain-specific filtering logic
- **Service Protocol**: Implement `AnalysisService` to integrate alternative analysis engines (Rust, C++, GPU-accelerated)

Extensions are isolated behind stable interfaces, allowing teams to customize behavior without forking the core engine.

## Deep Dive: Trust Model

### Untrusted Input

All external data is treated as untrusted:

- **File Providers**: May read corrupted JSON, malformed UTF-8, or files with embedded attack payloads
- **Custom Providers**: May return inconsistent data, violate schema contracts, or inject malicious edge definitions
- **Environment Variables**: May contain unexpected values, injection attempts, or misconfigured paths

The validation layer is the trust boundary. Nothing enters the engine without passing schema validation, business rule checks, and sanity bounds.

### Untrusted Accelerators

Optional Rust analysis is treated as an untrusted accelerator:

- **Process Isolation**: Rust binary runs in a separate process with no shared memory
- **Timeout Protection**: Long-running Rust processes are killed after configurable timeout
- **Fallback Semantics**: If Rust fails, diverges, or is unavailable, Python analysis remains authoritative
- **Parity Validation**: Test suite validates that Rust and Python produce identical results on reference snapshots

This design allows teams to benefit from Rust performance without creating a hard dependency or single point of failure.

### Trusted Core

The Python implementation under `src/arbcore/` is the trusted core:

- **Canonical Semantics**: Python defines the authoritative behavior for validation, analysis, and output
- **Minimal Dependencies**: Core analysis requires only Python standard library
- **Auditable Size**: Core engine is under 2000 lines of Python, designed for human review
- **Deterministic Behavior**: No randomness, no timestamps in output, no environment-dependent logic

This trust model makes the system suitable for security-sensitive environments where external dependencies and non-deterministic behavior are unacceptable.

## Deep Dive: Multi-Network Architecture

### Network as First-Class Concept

The `network` field is mandatory and explicit in every snapshot:

```json
{
  "network": "base",
  "timestamp": "2026-05-07T00:00:00Z",
  "edges": [...]
}
```

This design has several benefits:

- **No Implicit Assumptions**: The engine never guesses which network a snapshot represents
- **Multi-Network Pipelines**: A single analysis service can process snapshots from Ethereum, Base, Arbitrum, Polygon, etc.
- **Network-Specific Policies**: Different networks can have different profit thresholds, gas assumptions, or liquidity filters
- **Audit Trail**: Every opportunity report includes the source network, making analysis traceable

### Network-Agnostic Engine

The core engine is deliberately network-agnostic:

- **No Hardcoded Chains**: No special cases for Ethereum vs. Base vs. Arbitrum
- **No RPC Assumptions**: No knowledge of block times, gas prices, or consensus mechanisms
- **No Token Registries**: No hardcoded token addresses or symbol mappings
- **No Venue Catalogs**: No assumptions about which DEXes exist on which networks

This makes the engine reusable across:

- **Public Mainnets**: Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, BNB Chain
- **Public Testnets**: Sepolia, Goerli, Base Sepolia, Arbitrum Sepolia
- **Private Networks**: Internal testnets, forked environments, simulation networks
- **Future Networks**: Any EVM-compatible chain without code changes

### Network-Specific Extensions

Teams can add network-specific logic through extension points:

- **Custom Providers**: Normalize network-specific data sources (Uniswap V3 on Ethereum, Aerodrome on Base)
- **Custom Policies**: Apply network-specific filters (higher profit thresholds on expensive networks)
- **Custom Reporters**: Emit network-specific metadata (gas estimates, block confirmations)

This separation keeps the core clean while allowing practical customization.

## Deep Dive: Validation as Infrastructure

### Why Validation Matters

In production systems, silent failures are more dangerous than loud failures. This repository treats validation as a first-class feature:

- **Early Detection**: Invalid input is rejected before analysis begins, not after partial processing
- **Structured Errors**: Validation failures produce machine-readable error objects with field paths and violation descriptions
- **Fail-Closed**: The system refuses to process ambiguous or unsafe input, never falls back to "best guess" behavior
- **Audit Trail**: Validation results are logged and can be persisted for compliance review

### Schema-Level Validation

JSON schemas under `schemas/` document the public contracts:

- **market_snapshot.schema.json**: Defines the shape of input snapshots
- **opportunity_report.schema.json**: Defines the shape of output opportunities
- **diagnostics.schema.json**: Defines the shape of system diagnostics
- **error_response.schema.json**: Defines the shape of structured errors

These schemas serve multiple purposes:

- **Documentation**: Developers can read the schema to understand expected input/output
- **Validation**: Runtime checks enforce schema compliance
- **Code Generation**: Teams can generate client libraries from schemas
- **Contract Testing**: CI validates that actual output matches schema contracts

### Runtime Validation

Beyond schema validation, the system enforces business rules:

- **Network Identity**: The `network` field must be present and non-empty
- **Edge Sanity**: Rates must be positive, fees must be non-negative, liquidity must be positive
- **Symbol Consistency**: Edges must form valid paths (target of edge N must match source of edge N+1)
- **Bounded Complexity**: Snapshots cannot exceed maximum edge count (prevents DoS via huge graphs)

These checks protect against:

- **Data Quality Issues**: Corrupted snapshots, stale data, inconsistent normalization
- **Attack Vectors**: Malicious snapshots designed to cause crashes, infinite loops, or resource exhaustion
- **Integration Bugs**: Upstream systems that violate contracts due to code changes

### Negative Case Validation

The repository includes explicit negative test cases:

- **Missing Required Fields**: Snapshots without `network` or `edges` must be rejected
- **Invalid Data Types**: String rates, negative liquidity, non-array edges must be rejected
- **Business Rule Violations**: Zero-rate edges, self-loops, disconnected graphs must be rejected

These tests prove that the system fails safely and predictably when given bad input.

## Deep Dive: Extensibility Model

### Protocol-Based Extension

The system uses Python protocols (structural typing) for extension points:

```python
class SnapshotProvider(Protocol):
    def load_snapshot(self, source: str) -> MarketSnapshot:
        ...

class OpportunityReporter(Protocol):
    def report(self, opportunities: List[Opportunity]) -> None:
        ...
```

This design has several advantages:

- **No Inheritance Required**: Extensions don't need to inherit from base classes
- **Duck Typing**: Any object with the right methods satisfies the protocol
- **Testability**: Extensions can be tested in isolation without the full system
- **Composition**: Multiple extensions can be combined without conflicts

### Extension Patterns

Common extension patterns include:

**Custom Data Sources**:
```python
class UniswapV3Provider:
    def load_snapshot(self, pool_addresses: List[str]) -> MarketSnapshot:
        # Fetch pool state from local database
        # Normalize to snapshot format
        # Return validated snapshot
```

**Custom Output Formats**:
```python
class ParquetReporter:
    def report(self, opportunities: List[Opportunity]) -> None:
        # Convert opportunities to DataFrame
        # Write to Parquet file
        # Update metadata catalog
```

**Custom Filtering Logic**:
```python
class GasAwarePolicy:
    def filter(self, opportunity: Opportunity) -> bool:
        # Estimate gas cost for network
        # Compare to profit
        # Return True if profitable after gas
```

### Extension Isolation

Extensions are isolated from the core:

- **No Core Modifications**: Extensions are added via configuration, not code changes
- **Failure Isolation**: Extension failures don't crash the core engine
- **Version Independence**: Extensions can evolve independently of core releases
- **Testing Independence**: Extensions can be tested without running the full system

This makes the system suitable for large organizations where multiple teams need to customize behavior without coordinating releases.

## Deep Dive: Organizational Fit

### For Startups

**Strengths**:
- Small, auditable codebase that a 2-3 person team can understand in a day
- No operational overhead (no databases, no message queues, no service mesh)
- Easy to embed in larger systems without architectural lock-in
- Clear boundaries make it easy to add execution layer when ready

**Considerations**:
- Still need to build data collection, execution, and risk management
- Not a complete product, requires engineering investment
- May need to add network-specific optimizations for production scale

### For Trading Firms

**Strengths**:
- Deterministic analysis suitable for backtesting and compliance
- Multi-network support matches cross-chain trading strategies
- Clean separation between analysis and execution matches risk controls
- Structured output integrates with existing quant infrastructure

**Considerations**:
- Latency-sensitive firms may need to rewrite engine in C++ or Rust
- May need to add proprietary alpha signals and filtering logic
- Requires integration with existing order management and risk systems

### For Protocol Teams

**Strengths**:
- Useful for simulating MEV dynamics in protocol designs
- Can validate liquidity assumptions before mainnet launch
- Helps understand how protocol changes affect arbitrage opportunities
- Clean foundation for building protocol-specific analysis tools

**Considerations**:
- May need to add protocol-specific edge types (concentrated liquidity, dynamic fees)
- Requires integration with protocol simulation environments
- May need to extend for multi-hop cross-protocol routing

### For Data & Analytics Companies

**Strengths**:
- Structured output is easy to ingest into data warehouses
- Deterministic behavior makes it suitable for scheduled batch jobs
- Multi-network support matches market intelligence product needs
- Clean contracts make it easy to build customer-facing APIs on top

**Considerations**:
- May need to add real-time data collection layer
- Requires integration with existing data pipelines and storage
- May need to add customer-specific filtering and enrichment logic

### For Enterprise Infrastructure Teams

**Strengths**:
- Containerized deployment matches modern DevOps practices
- Stateless design makes it easy to scale horizontally
- Structured logging and diagnostics integrate with observability platforms
- Clear trust boundaries match security review requirements

**Considerations**:
- May need to add authentication and authorization for multi-tenant deployment
- Requires integration with existing CI/CD and deployment pipelines
- May need to add rate limiting and resource quotas for shared infrastructure

## Deep Dive: Quality Standards

### Code Quality

The repository maintains high code quality standards:

- **Type Hints**: All public functions have complete type annotations
- **Docstrings**: All modules, classes, and public functions have docstrings
- **Linting**: Code passes `ruff check` with strict settings
- **Formatting**: Code is formatted with `ruff format` for consistency
- **Complexity**: Functions are kept small and focused (typically under 50 lines)

### Test Quality

The test suite is comprehensive:

- **Unit Tests**: Core logic is tested in isolation
- **Integration Tests**: End-to-end workflows are tested with real examples
- **Negative Tests**: Invalid input is tested to ensure proper rejection
- **Parity Tests**: Rust and Python implementations are tested for equivalence
- **Contract Tests**: Output shape is validated against schemas

### Documentation Quality

Documentation is treated as a first-class artifact:

- **Multi-Language**: English, Persian, and Chinese documentation
- **Multiple Levels**: Quick start, detailed guides, and advanced deep dives
- **Honest Maturity**: Clear statements about what is and isn't production-ready
- **Explicit Boundaries**: Clear documentation of what the system does and doesn't do
- **Reviewer-Focused**: Dedicated guides for skeptical reviewers and auditors

### Release Quality

Release readiness is validated programmatically:

- **Automated Checks**: `scripts/release_readiness.py` validates all quality gates
- **Explicit Blockers**: Unresolved blockers are clearly documented
- **Version Semantics**: Semantic versioning with clear breaking change policies
- **Migration Guides**: Documentation for upgrading between versions
- **Changelog**: Detailed changelog with categorized changes

## Conclusion: Infrastructure, Not Product

This repository is infrastructure, not a product. It is a kernel, not a complete system. It is a foundation, not a finished building.

Teams that adopt it successfully understand this distinction. They use it as a clean, auditable, deterministic analysis layer inside a larger system that they control. They add their own data collection, their own risk management, their own execution logic, and their own operational practices.

Teams that struggle with it treat it as a magic bot that should work out of the box. They expect it to collect data, manage wallets, execute trades, and generate profits without additional engineering.

The repository is designed for the first group. If you are in the second group, this is not the right tool for you.

If you are in the first group, welcome. Read the contracts, validate your snapshots, review the failure modes, and build something great on top of this foundation.
