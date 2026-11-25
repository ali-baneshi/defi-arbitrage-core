> **Alpha, offline analysis only.** This project ranks nominal opportunity
> candidates from a local snapshot. It does not trade, sign, fetch prices, or
> claim executable profit. [docs/en/PRODUCT.md](docs/en/PRODUCT.md) defines the
> narrow bar this repository is held to; [docs/en/FINAL_AUDIT.md](docs/en/FINAL_AUDIT.md)
> records the evidence and the limits.

# defi-arbitrage-core

[![CI](https://github.com/ali-baneshi/defi-arbitrage-core/actions/workflows/ci.yml/badge.svg)](https://github.com/ali-baneshi/defi-arbitrage-core/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)

A deterministic, dependency-free analyzer that turns one validated JSON
snapshot of directed exchange quotes into ranked candidate cycles.

## What it does

- Loads a local JSON snapshot.
- Rejects malformed, ambiguous, or out-of-bounds input.
- Enumerates simple cycles up to a hop limit with a deterministic search budget.
- Applies a nominal risk policy: minimum profit, minimum liquidity, maximum
  notional, maximum results.
- Prints a text report or stable JSON.

## What it does not do

- No RPC, price feeds, wallets, private keys, signing, or transaction submission.
- No contract compilation, deployment, or auditing.
- No cross-chain routing. A snapshot names one `network`; the label is copied
  to output and is not verified.
- No slippage, gas, latency, MEV, token decimals, order-book depth, or
  settlement modeling.

## Install and run

From a clean checkout:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
defi-arbitrage-core examples/market_snapshot.json --json
```

Without installing:

```bash
PYTHONPATH=src python -m arbcore.cli examples/market_snapshot.json --json
```

Output:

```json
[
  {
    "network": "polygon",
    "path": ["USDC", "WETH", "DAI", "USDC"],
    "venues": ["dex-a", "dex-b", "dex-c"],
    "gross_return": 1.0079427572346378,
    "profit_bps": 79.42757234637776,
    "limiting_liquidity": 100000.0,
    "estimated_capacity": 10000.0,
    "capacity_known": true,
    "snapshot_source": "example-static-snapshot",
    "snapshot_timestamp": "2026-05-05T00:00:00Z"
  }
]
```

Text output:

```text
[polygon] USDC -> WETH -> DAI -> USDC | 79.43 bps | capacity: 1e+04 | venues: dex-a, dex-b, dex-c
```

## Snapshot format

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

`rate` means units of `target` per one unit of `source` before fees.
`liquidity` is expressed in the edge's source-asset units and is used only as
a linear capacity bound. See [docs/en/USAGE.md](docs/en/USAGE.md) for the full
contract.

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

Exit code `0` means success. Exit code `2` means invalid input, invalid policy,
an unreadable snapshot, or an exceeded analysis budget. Results go to stdout;
errors go to stderr.

## Limits

- Snapshot file: 50 MiB, 10,000 edges.
- Asset symbols: 32 characters, trimmed and uppercased.
- Node out-degree: 500.
- Search budget: 2,000,000 edge expansions. Larger searches fail with
  `AnalysisLimitError` rather than running unbounded. A 12-asset/5-hop complete
  graph fits; a 12-asset/6-hop one does not.
- `max_hops` is capped at 8, but a dense graph can exhaust the budget well
  before that.

The budget makes runtime deterministic and bounded, not fast for every input.
See [docs/en/ARCHITECTURE.md](docs/en/ARCHITECTURE.md).

## Economic model

Rates are scalar and linear. Fees are percentage deductions. Liquidity is a
quote bound, not executable depth. `profit_bps` is nominal. A positive result
means "this cycle passes the stated arithmetic and policy", not "this trade
would make money".

## Validation

```bash
PYTHONPATH=src python scripts/validate_all.py
python -m pytest -q
ruff check .
python scripts/benchmark.py
```

`validate_all.py` compiles the tree and runs the test suite. The benchmark
records representative and worst-case search behavior. See
[docs/en/VALIDATION.md](docs/en/VALIDATION.md).

## Documentation

- [docs/en/PRODUCT.md](docs/en/PRODUCT.md) — promise, contracts, and the
  production-ready definition.
- [docs/en/USAGE.md](docs/en/USAGE.md) — CLI, exit codes, JSON, and library API.
- [docs/en/ARCHITECTURE.md](docs/en/ARCHITECTURE.md) — pipeline, bounds, and
  trust boundaries.
- [docs/en/VALIDATION.md](docs/en/VALIDATION.md) — what each check proves.
- [docs/en/AUDIT.md](docs/en/AUDIT.md) — why the repository was reduced.
- [docs/en/DECISIONS.md](docs/en/DECISIONS.md) — judgment calls and reversal paths.
- [docs/en/RELEASE_CHECKLIST.md](docs/en/RELEASE_CHECKLIST.md) — maintainer
  checklist.
- [docs/en/FINAL_AUDIT.md](docs/en/FINAL_AUDIT.md) — before/after evidence,
  known limitations, and the production-ready verdict.

## License

MIT. See [LICENSE](LICENSE).
