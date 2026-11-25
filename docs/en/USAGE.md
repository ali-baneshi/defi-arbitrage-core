# Usage

## CLI

```text
defi-arbitrage-core SNAPSHOT [options]

--json                 emit JSON instead of text
--validate-only        validate and exit without analysis
--min-profit-bps N     default 5.0
--max-hops N           default 4, range 2..8
--min-liquidity N      default 0.0
--max-notional N       default 10000.0
--max-results N        default 25, range 1..1000
--version
```

`SNAPSHOT` is required. Absolute, relative, symlinked, and `~` paths are normal
filesystem paths; there is no allow-list.

From a checkout without installing:

```bash
PYTHONPATH=src python -m arbcore.cli examples/market_snapshot.json --json
```

Examples:

```bash
defi-arbitrage-core examples/market_snapshot.json
defi-arbitrage-core examples/base_market_snapshot.json --json
defi-arbitrage-core examples/no_opportunity_snapshot.json --json
defi-arbitrage-core examples/market_snapshot.json --validate-only
defi-arbitrage-core examples/market_snapshot.json --max-hops 2 --min-profit-bps 10
```

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success, including an empty opportunity list |
| 2 | Invalid input, invalid policy, missing/unreadable snapshot, or budget exceeded |

The argument parser also exits `2` for unknown flags and missing values.
Expected errors are printed to stderr; stdout is reserved for results.

## Input

One UTF-8 JSON object, at most 50 MiB:

```json
{
  "source": "example-static-snapshot",
  "network": "polygon",
  "timestamp": "2026-05-05T00:00:00Z",
  "edges": [
    {"source": "USDC", "target": "WETH", "rate": 0.00025,
     "venue": "dex-a", "fee_bps": 30, "liquidity": 100000}
  ]
}
```

Rules:

- `source`, `network`, and `timestamp` are optional. Missing values normalize
  to `"local"`, `"polygon"`, and `null`. Explicit `null` is rejected.
- `timestamp`, when present, is exactly `YYYY-MM-DDTHH:MM:SSZ`.
- `edges` is required, non-empty, and at most 10,000 items.
- `source`, `target`, and `rate` are required per edge.
- `venue` defaults to `"unknown"`; `fee_bps` defaults to `0`; `liquidity`
  defaults to `null`.
- Symbols are trimmed and uppercased, at most 32 characters, and must differ.
- Venues are trimmed and at most 80 characters.
- `rate` is finite and positive.
- `fee_bps` is finite in `[0, 10000)`.
- `liquidity` is finite and non-negative when present.
- Unknown keys are rejected at every level.
- Self-loop edges are rejected. A graph with no cycle returns `[]`.

Published schema: `schemas/market_snapshot.schema.json`.

## Output

JSON is an array ordered by `profit_bps` descending, limited by `max_results`.
Published schema: `schemas/opportunity.schema.json`.

| Field | Meaning |
| --- | --- |
| `network` | Snapshot label, lowercased |
| `path` | Closed cycle; first and last asset match |
| `venues` | One venue per hop |
| `gross_return` | Product of fee-adjusted linear rates |
| `profit_bps` | `(gross_return - 1) * 10000` |
| `limiting_liquidity` | Raw minimum across hops; diagnostic only, units may differ |
| `estimated_capacity` | Starting-asset-unit bound, capped by `max_notional` |
| `capacity_known` | False when any hop omits liquidity |
| `snapshot_source` | Snapshot `source` |
| `snapshot_timestamp` | Snapshot `timestamp` or null |

`--validate-only` prints `Snapshot is valid: PATH`, or with `--json`:

```json
{"ok": true, "snapshot": "examples/market_snapshot.json"}
```

## Policy semantics

- Edges below `min_liquidity` are not added to the graph.
- A cycle is reported when `profit_bps >= min_profit_bps` and
  `estimated_capacity >= min_liquidity`.
- Duplicate rotations of the same cycle collapse to one canonical key; the
  highest-profit copy wins.
- `max_results` truncates after ranking, not before searching.
- `max_hops` counts edges in the cycle.
- The search budget counts every outgoing edge examined. It is a hard safety
  limit, not a performance target.

## Library

```python
from arbcore import AnalysisEngine, Edge, MarketSnapshot, RiskPolicy

snapshot = MarketSnapshot(
    edges=(Edge("USDC", "WETH", 0.00025, fee_bps=30), Edge("WETH", "USDC", 4050.0)),
)
opportunities = AnalysisEngine(RiskPolicy(min_profit_bps=1, max_hops=2)).analyze(snapshot)
```

`AnalysisEngine.analyze` normalizes and validates the snapshot before searching.
It raises `SnapshotError`, `PolicyError`, or `AnalysisLimitError`; all inherit
from `ArbCoreError`.

## Configuration

There is no environment-variable configuration and no default snapshot. Pass a
path and flags explicitly. This keeps runs reproducible and avoids hidden
precedence.
