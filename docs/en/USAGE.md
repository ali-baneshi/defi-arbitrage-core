# Usage

This page documents local analysis usage only. It does not imply live execution, wallet handling, or deployable smart-contract behavior.

## CLI

```bash
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/base_market_snapshot.json --json
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/no_opportunity_snapshot.json --min-profit-bps 1
PYTHONPATH=src python -m defi_arbitrage_core.cli --show-policy
PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics
PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --validate-only
```

Useful flags: `--min-profit-bps`, `--max-hops`, `--min-liquidity`, `--max-notional`, `--max-results`, `--engine`, and `--rust-binary`. Expected error exit code for known validation/configuration failures is `2`.

If you are wrapping the CLI from another tool, prefer:

- `--json` for opportunities
- `--error-json` for expected failures
- `--diagnostics` for environment and capability inspection
- `--validate-only` when you need input validation without analysis

## Python API

```python
from defi_arbitrage_core import AnalysisEngine, JsonFileProvider, RiskPolicy

snapshot = JsonFileProvider("examples/market_snapshot.json").load_snapshot()
policy = RiskPolicy(min_profit_bps=5, max_hops=4, max_notional=1000)
opportunities = AnalysisEngine(policy).analyze(snapshot)
```

## Snapshot Format

```json
{
  "source": "example",
  "timestamp": "2026-05-05T00:00:00Z",
  "edges": [
    {"source": "USDC", "target": "WETH", "rate": 0.00025, "fee_bps": 30, "liquidity": 100000}
  ]
}
```

`rate` is units of `target` received for one unit of `source` before fees. `liquidity` is optional and expressed in source-asset units.

## Contract Validation

```bash
PYTHONPATH=src python scripts/validate_contracts.py
PYTHONPATH=src python scripts/validate_contracts.py --json
```

This validates Solidity and Vyper templates without compiling or deploying them.

## Full Baseline Validation

```bash
PYTHONPATH=src python scripts/validate_all.py
```

Use `--include-rust` to include optional Rust service validation when Cargo is available.

## Structured Errors

`--error-json` emits expected `ArbCoreError` failures as JSON on stderr with `ok: false`, an error type, and a safe message. Use it for automation that needs deterministic failure handling.

## Multi-Network Usage Pattern

The same CLI and Python API work for multiple networks because network identity lives in the snapshot contract:

```json
{
  "source": "research-snapshot",
  "network": "arbitrum",
  "timestamp": "2026-05-05T00:00:00Z",
  "edges": [
    {"source": "USDC", "target": "WETH", "rate": 0.00025}
  ]
}
```

This repository does not do cross-chain routing, bridging, or chain-specific execution. It provides a reusable single-snapshot analysis core that larger systems can compose per network.
