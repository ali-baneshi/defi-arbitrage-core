# Architecture

## Pipeline

```text
snapshot.json
    |
    v
JsonFileProvider
  size, UTF-8, JSON, shape checks
    |
    v
validate_snapshot_payload + MarketSnapshot.validate
  unknown keys, nulls, timestamps, symbols, rates, fees, liquidity
    |
    v
AnalysisEngine
  graph build, simple-cycle DFS, expansion budget
    |
    v
RiskPolicy
  profit, liquidity, notional, result count
    |
    v
TextReporter / JsonReporter
  stdout only; errors on stderr
```

## Modules

- `arbcore.models`: immutable `Edge`, `MarketSnapshot`, `RiskPolicy`,
  `Opportunity`, and the documented limits.
- `arbcore.validation`: dependency-free JSON shape validation.
- `arbcore.providers`: `JsonFileProvider`, the only input path.
- `arbcore.engine`: graph construction, simple-cycle DFS, deterministic budget,
  cycle canonicalization, capacity conversion, ranking.
- `arbcore.reporters`: text and JSON rendering.
- `arbcore.cli`: argument parsing and exit codes.
- `arbcore.errors`: expected error hierarchy.

There is one implementation. No native binary, second package, or service
boundary exists.

## Determinism

- Assets are normalized to trimmed uppercase symbols.
- Graph nodes are visited in sorted order.
- Cycle keys are rotation-normalized, so each directed cycle appears once.
- Ranking is `profit_bps` descending; equal values keep insertion order.
- JSON uses `dataclasses.asdict` with fixed field order.
- The search budget is a counter over edge expansions, not wall-clock time.

For a fixed snapshot, policy, interpreter, and code version, repeated runs
produce byte-identical JSON for the tested fixtures.

## Bounds

| Limit | Value |
| --- | --- |
| Snapshot bytes | 50 MiB |
| Edges | 10,000 |
| Asset symbol | 32 characters |
| Venue | 80 characters |
| Node out-degree | 500 |
| Hops | 8 |
| Results | 1,000 |
| Edge expansions | 250,000 |

The expansion budget is the real complexity bound. `max_hops` and
`max_results` alone do not bound work: the number of simple cycles grows
quickly with degree. When the budget is exceeded, analysis stops with
`AnalysisLimitError` and exit code `2`; it does not return partial results.

## Trust boundaries

- Snapshot files are untrusted. They are size-checked, decoded as UTF-8,
  parsed as JSON, shape-checked, and domain-checked.
- Asset symbols and venue names are untrusted strings. They are length-limited,
  normalized, and never interpreted as paths, URLs, or code.
- JSON output is data, not a recommendation.
- The process does not open sockets, read environment configuration, spawn a
  second engine, or write files.

## What the engine is not

It is not an execution simulator. Rates are scalar quotes, fees are percentage
deductions, and liquidity is a linear capacity bound in the edge's source
asset. It does not model slippage, gas, latency, MEV, decimals, order books,
bridge risk, or settlement. See `docs/en/PRODUCT.md` for the complete promise.
