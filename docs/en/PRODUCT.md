# Product definition

Date: 2026-11-25

## Promise

**`defi-arbitrage-core` is a deterministic, dependency-free offline analyzer
that turns one validated local snapshot of directed exchange quotes into a
ranked list of nominal opportunity candidates under documented linear
assumptions, with bounded runtime and stable JSON output.**

It does not execute trades, hold keys, fetch prices, compile or deploy
contracts, verify chain state, or claim realized profit. "Production-ready" in
this repository means the narrow promise below is met and tested. It does not
mean trading-ready.

## User and job

Primary user: a researcher or quantitative developer running local
experiments. Secondary user: a backend engineer embedding `AnalysisEngine` in
a pipeline.

The one job: given a snapshot the user already trusts enough to analyze, show
which cycles pass a stated nominal policy, ranked by `profit_bps`, without
surprising paths, silent truncation, or unbounded work.

## Input contract (version 1)

One UTF-8 JSON object, at most 50 MiB and 10,000 edges:

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

- `source`, `network`, and `timestamp` are optional strings. Missing values
  normalize to `"local"`, `"polygon"`, and `null`. Explicit `null` is rejected.
- `timestamp`, when present, must match `YYYY-MM-DDTHH:MM:SSZ`.
- `edges` is required, non-empty, and at most 10,000 items.
- Each edge requires `source`, `target`, and `rate`. `venue` defaults to
  `"unknown"`; `fee_bps` defaults to `0`; `liquidity` defaults to `null`.
- Asset symbols are trimmed and uppercased, at most 32 characters, and must
  differ. Venues are trimmed, at most 80 characters.
- `rate` is finite and strictly positive. `fee_bps` is finite in `[0, 10000)`.
  `liquidity` is finite and non-negative when present.
- Unknown keys at any level are rejected.
- A self-loop edge is rejected. A snapshot with no cycle is valid and returns
  an empty result.

The published schema is `schemas/market_snapshot.schema.json`.

## Output contract (version 1)

JSON output is an array of objects, ordered by `profit_bps` descending, at most
`max_results` items:

```json
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
```

`path` is a closed cycle with the same asset first and last. `venues` has one
entry per hop. `gross_return` is the product of fee-adjusted linear rates.
`profit_bps = (gross_return - 1) * 10000`. `estimated_capacity` is in starting
asset units, capped by `max_notional` and by supplied liquidity converted to
starting units. `limiting_liquidity` is the raw minimum across hops and is
diagnostic only; raw liquidity values may be in different asset units.
`capacity_known` is false when any hop omits liquidity.

The published schema is `schemas/opportunity.schema.json`.

## CLI contract

```text
defi-arbitrage-core SNAPSHOT [options]

--json                 emit the JSON output contract
--validate-only        validate and exit without analysis
--min-profit-bps N     default 5.0
--max-hops N           default 4, range 2..8
--min-liquidity N      default 0.0
--max-notional N       default 10000.0
--max-results N        default 25, range 1..1000
--version
```

- `SNAPSHOT` is required. Normal absolute, relative, and symlinked paths work.
  There is no path allow-list.
- stdout carries results only: the JSON array, the text report, or the
  validation confirmation.
- stderr carries every error.
- Exit code `0` means success. Exit code `2` means invalid input, invalid
  policy, an unreadable snapshot, or an exceeded analysis budget. Argument
  parser errors also exit `2`.
- There is no environment-variable configuration, no default snapshot, and no
  hidden fallback engine.
- `python -m arbcore` is equivalent to the console script.

## Bounds and determinism

- Search is a simple-cycle DFS with `max_hops` at most 8.
- Node out-degree is at most 500.
- A deterministic budget of 2,000,000 edge expansions aborts the search with
  an actionable error instead of running unbounded. The budget is part of the
  contract and is tested. It admits a 12-asset/5-hop complete graph and aborts
  a 12-asset/6-hop one.
- At most four times `max_results` candidates are retained during the search,
  so a dense profitable graph cannot grow an unbounded result map.
- Output is deterministic for fixed input, policy, interpreter, and code:
  graph iteration is sorted, cycle keys are rotation-normalized, ranking is by
  `profit_bps` with stable input order for ties, and JSON key order is fixed.
- Same results on supported CPython 3.10-3.13 for the tested fixtures.

## Production-ready, defined

The product is production-ready under this document when all of the following
are true, each with a committed check:

1. Runtime validation and both published schemas agree on a parity fixture set,
   including null handling and boundary values.
2. CLI stdout/stderr separation, exit codes, relative paths, absolute paths,
   missing files, directories, and unknown flags are tested.
3. Adversarial snapshots cannot crash the process or exhaust the search budget;
   malformed JSON, unknown keys, non-finite numbers, bad fees, self-loops,
   duplicate edges, disconnected graphs, and oversized inputs have tests.
4. Repeated runs produce byte-identical JSON for the canonical example.
5. A committed benchmark records representative and worst-case behavior and
   the expansion budget holds.
6. A fresh virtual environment can install the package and run the documented
   quick start without `PYTHONPATH`.
7. Every supported flag, script, schema, and document has a user and a test.
8. Unsupported or aspirational surfaces are deleted, not marked "not
   supported".

## Non-goals

Live RPC ingestion, wallets, signing, transaction submission, contract
compilation or deployment, cross-chain routing, order-book simulation,
slippage/gas/MEV modeling, localization, optional native accelerators, and a
release-evidence bureaucracy. These are not planned for this package.

## Known limitations

The numbers are nominal. A positive `profit_bps` does not mean a trade is
profitable or executable. Liquidity is a linear quote bound, not depth.
Parallel edges collapse to the best cycle key. Extreme rate products that
overflow to infinity are skipped. The tool ranks candidates; it does not
prove them.
