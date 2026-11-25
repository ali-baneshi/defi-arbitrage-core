# Final audit

Date: 2026-11-25
Baseline: commit `162bf8e` (192 tracked files, clean tree)
Result: one offline analyzer with one package, one console script, two
schemas, one validation command, and one benchmark.

## Before and after

| Measure | Before | After |
| --- | --- | --- |
| Tracked files | 192 | 56 |
| Python files | 49 | 20 |
| Source lines under `src/` | 1,901 | 692 |
| Test lines | 652 | 825 |
| Scripts (files / Python lines) | 22 / 2,600 | 2 / 152 |
| Markdown under `docs/` | 79 files / 3,702 lines | 8 files |
| All Markdown | 101 files / 5,001 lines | 18 files |
| Published schemas | 10 | 2 |
| Import packages | 2 | 1 |
| Console scripts | 2 | 1 |
| Optional Rust analyzer | 627 lines + adapter + parity | removed |
| Contract workspace | 54 lines + 573-line validator | removed |
| Release-evidence gate | scripts, schemas, fixtures | removed |
| Localized doc trees | `fa`, `zh` | removed |

The test suite grew because it now protects the surviving contracts instead of
mirroring every optional subsystem.

## What was removed, and why

Each item is authorized and reversible in `docs/en/DECISIONS.md`.

- **Rust analyzer** (D3): a second implementation of a 176-line Python engine,
  with hand-maintained parity, no production user, and no committed benchmark.
- **Solidity/Vyper workspace** (D4): inert templates and a validator for files
  that cannot execute and do not inform an opportunity.
- **Release-evidence gate** (D5): unsatisfiable on a clean checkout and
  exited zero while blocked. Replaced by `RELEASE_CHECKLIST.md`.
- **Persian and Chinese docs** (D2): 56 mirrored pages with no owner and no
  runnable parity test. English under `docs/en/` is canonical.
- **Environment configuration and default snapshot** (D10): duplicated CLI
  flags and made an installed command depend on the checkout directory.
- **Path allow-list** (D6): rejected legitimate absolute paths without a
  threat model.
- **Diagnostics, self-check, show-policy, structured-error, and engine flags**:
  no documented user or test after the optional subsystems were removed.
- **Edge metadata** (D8): no reader, with size/depth validation and schema
  surface.
- **Duplicate package and script names** (D7): the shim had no behavior.
- **Redundant scripts, schemas, fixtures, and release pages**: layered checks
  repeated pytest or protected deleted surfaces.

## What remains

One user, one job: a researcher runs a local snapshot and gets ranked nominal
cycle candidates under a stated policy.

```text
snapshot.json
  -> JsonFileProvider (size, UTF-8, JSON)
  -> validate_snapshot_payload + MarketSnapshot.validate
  -> AnalysisEngine (simple-cycle DFS, 2M-expansion budget, bounded candidates)
  -> RiskPolicy (profit, liquidity, notional, result count)
  -> TextReporter / JsonReporter
```

Surfaces:

- import package `arbcore`, including `AnalysisEngine` and the models;
- console script `defi-arbitrage-core` and `python -m arbcore`;
- `schemas/market_snapshot.schema.json` and
  `schemas/opportunity.schema.json`;
- three example snapshots and one golden JSON output;
- `scripts/validate_all.py` and `scripts/benchmark.py`;
- this documentation set.

## Evidence

Commands run from the repository root on Python 3.12.8, Linux.

| Check | Command | Result |
| --- | --- | --- |
| Validation | `PYTHONPATH=src python scripts/validate_all.py` | passed |
| Tests | `python -m pytest -q` | 77 passed |
| Lint | `ruff check .` | passed |
| Benchmark | `python scripts/benchmark.py` | see below |
| Clean install | `python -m venv .venv-clean && .venv-clean/bin/pip install .` | exit 0 |
| Installed CLI | `.venv-clean/bin/defi-arbitrage-core --version` | `defi-arbitrage-core 0.1.0a1` |
| Installed example | run from `docs/` with `../examples/market_snapshot.json --json` | exit 0, valid JSON |
| Installed module | `.venv-clean/bin/python -m arbcore ../examples/no_opportunity_snapshot.json --json` | exit 0, `[]` |
| Market example | `examples/market_snapshot.json --json` | 79.43 bps, capacity 10000 |
| Base example | `examples/base_market_snapshot.json --json` | 131.19 bps, capacity 10000 |
| No-opportunity example | `examples/no_opportunity_snapshot.json --json` | `[]` |

Final benchmark, complete directed graphs, all rates 1.0, profit floor above
any possible result:

| Assets | Edges | Hops | Seconds | Result |
| --- | --- | --- | --- | --- |
| 8 | 56 | 8 | 0.980 | completed, 0 results |
| 12 | 132 | 3 | 0.058 | completed, 0 results |
| 12 | 132 | 4 | 0.183 | completed, 0 results |
| 12 | 132 | 5 | 1.174 | completed, 0 results |
| 12 | 132 | 6 | 1.913 | `AnalysisLimitError` |
| 12 | 132 | 8 | 2.022 | `AnalysisLimitError` |

The 12-asset/5-hop graph needs about 1.19M expansions; 6 hops would need about
8.5M and 9.6 s without the budget. The budget admits the former and aborts the
latter in under two seconds.

Docker build was attempted but could not pull `python:3.12-slim`: the registry
returned HTTP 403 in this environment. The Dockerfile is minimal, and CI has a
docker-smoke job, but the image was **not** built or run locally. This is an
environment limitation, not a passing check.

## Known limitations, stated plainly

- `profit_bps` is nominal. It is the product of scalar rates after percentage
  fees. It is not expected profit.
- Liquidity is a linear quote bound expressed in each edge's source asset. It
  is not order-book depth, slippage, or executable size.
- Gas, latency, MEV, token decimals, bridge risk, settlement risk, and
  market impact are not modeled.
- A `network` label is copied to output. It is not verified, and no
  cross-network route is considered.
- Parallel edges collapse to one canonical cycle; only the highest-profit copy
  survives.
- Extreme rate products that overflow to infinity are skipped silently.
- Duplicate keys in the input JSON are last-wins; the parser does not reject
  them.
- The timestamp is format-checked but not compared to a current time, so a
  stale snapshot is not flagged.
- The benchmark uses synthetic complete graphs, not representative market
  snapshots.
- Python 3.10-3.13 is asserted in CI; local verification was on 3.12 only.

## Remaining risks

- **Model risk** is the dominant risk. A user can mistake a nominal candidate
  for an executable trade. The documentation says otherwise, but the output
  field names still invite that reading.
- **Resource risk** is bounded by the expansion budget and candidate trim, but
  the budget is a fixed count, not a wall-clock guarantee on a slow machine.
- **Input risk** remains for duplicate JSON keys and for path permissions;
  both are documented or reported, not silently handled.
- **Release risk**: the repository no longer claims production trading
  readiness, and the release checklist is manual.

## Smallest next step that would materially improve the tool

Add an explicit `--as-of TIMESTAMP` and reject snapshots older than a
caller-supplied maximum age. The timestamp is already parsed, the check is
small, and an explicit as-of time keeps determinism. It would stop a stale
snapshot from being presented as a current analysis. It should not be added
without updating the input/output contract, tests, and `PRODUCT.md`.

## Production-ready verdict

**Yes, under the narrow definition in `docs/en/PRODUCT.md`.** All eight
criteria have committed checks: schema parity, CLI contracts, adversarial
inputs, byte-identical output, a bounded benchmark, a clean install, tested
flags/scripts/schemas, and deletion of unsupported surfaces.

**No, for trading, execution, fund management, or contract deployment.** The
economic model is linear and nominal, and the package has no wallet, RPC,
signing, execution, or settlement layer. Nothing in this result changes that.
