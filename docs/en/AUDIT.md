# Audit: what this repository is, and what it should become

Date: 2026-11-25
Baseline commit: `162bf8e`
Baseline tree: clean, branch `main`

This audit was produced before any deletion. It records verified evidence, not the
repository's own claims. Commands were run from the repository root with Python
3.12.8 on Linux.

## 1. Purpose and philosophy

The real product is a small offline graph analyzer. It reads one local JSON
snapshot of directed exchange quotes, validates it, enumerates simple cycles up
to a hop limit, applies a nominal risk policy, and prints ranked candidate
opportunities as text or JSON.

Its defensible philosophy is **deterministic, inspectable, offline analysis with
no execution surface**. It is a calculator for a deliberately simplified market
model, not a trading system and not an infrastructure platform.

It is **not**:

- a price feed, RPC client, wallet, signer, or execution engine;
- a smart-contract compiler, deployer, auditor, or template library;
- a multi-network router (a snapshot names one network; no cross-network edge
  is ever considered);
- a simulator of slippage, gas, latency, MEV, token decimals, order books, or
  settlement risk;
- a release-readiness system, documentation portal, or polyglot reference
  implementation.

## 2. User and the one job

The primary user is a researcher or quantitative developer running local
experiments against a snapshot they already have. The one job:

> Turn one validated local snapshot into a deterministic, ranked list of
> candidate cycles under documented linear assumptions.

A backend team may embed the same `AnalysisEngine` in a pipeline, but that is a
secondary use of the same small API, not a second product.

## 3. Verified baseline

| Claim | Evidence | Verdict |
| --- | --- | --- |
| ~1,900 Python lines under `src/` | `find src -name '*.py' \| xargs wc -l` = 1,901 | Confirmed |
| 47 tests pass | `PYTHONPATH=src python -m pytest -q` = 47 passed | Confirmed |
| Lint clean | `ruff check .` = All checks passed | Confirmed |
| `validate_all.py` passes | exit 0; ends "all dependency-free validation checks passed" | Confirmed |
| Release readiness blocked | `local_validation_ready: true`, `public_release_ready: false`, `production_ready: false` | Confirmed |
| Rust analyzer ~627 lines | `wc -l rust/arbcore-rs/src/main.rs` = 627 | Confirmed |
| Contracts are tiny and inert | 30-line Solidity, 24-line Vyper, no compiler or deploy step | Confirmed |
| 79 Markdown files under `docs/` | `find docs -name '*.md' \| wc -l` = 79; 3,702 lines | Confirmed |
| 192 tracked files | `git ls-files \| wc -l` = 192 | Confirmed |
| Path sandbox rejects legitimate paths | `path_utils._resolve_safe_path` allows only CWD and the temp directory | Confirmed by inspection; absolute paths under CWD pass, other absolute paths are rejected |
| Search is unbounded in practice | 12-asset complete graph: hops 5 = 1.24 s, hops 6 = 9.04 s, hops 8 > 30 s | Confirmed; see section 8 |
| Snapshot paths are restricted | same path utility is used by `Settings.from_env` and `JsonFileProvider` | Confirmed |
| Two package names | `arbcore` plus `defi_arbitrage_core` shim | Confirmed |
| Two console scripts | `defi-arbitrage-core` and `arbcore` | Confirmed |
| Runtime/schema drift exists | runtime accepts `"source": null` and `"network": null`; schemas require strings | Confirmed by execution |

The baseline test suite is green, but most of it protects surfaces that this
audit recommends deleting. Green tests are not evidence of product usefulness.

## 4. Subsystem inventory

Line counts are Python lines unless stated. "Consumers" means real code paths,
not documentation mentions.

| Path | Purpose | Lines | Entrypoints | Tests | Real consumers | Verdict | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `src/arbcore/models.py` | Edge, snapshot, policy, opportunity | 215 | library | engine/config tests | engine, providers, reporters, CLI | Keep, trim metadata | Metadata has no reader |
| `src/arbcore/engine.py` | Simple-cycle DFS and policy | 129 | library | `test_engine.py` | CLI, service | Keep, add budget | Hops 8 on 12 assets exceeds 30 s |
| `src/arbcore/validation.py` | JSON shape checks | 115 | library | validation tests | provider | Keep, fix null drift | Runtime accepts null source/network |
| `src/arbcore/providers.py` | JSON file loading | 83 | library | provider tests | CLI, service | Keep, remove sandbox | Absolute paths outside CWD/tmp fail |
| `src/arbcore/reporters.py` | Text and JSON output | 38 | library | reporter tests | CLI | Keep | Small and used |
| `src/arbcore/cli.py` | CLI | 145 | `defi-arbitrage-core`, `arbcore` | provider/CLI tests | users | Keep, trim flags | Diagnostics/engine flags have no product user |
| `src/arbcore/config.py` | Env settings and defaults | 62 | env vars | config test | CLI | Delete | Duplicates CLI flags; injects path sandbox |
| `src/arbcore/path_utils.py` | Path allow-list | 92 | internal | indirect | config, providers, service | Delete | Rejects normal use; symlink logic is incomplete |
| `src/arbcore/diagnostics.py` | Environment/capability report | 74 | `--diagnostics` | output checks | CLI, scripts | Delete | Hard-codes `"cwd": "."`; exposes interpreter path; depends on contracts |
| `src/arbcore/service.py` | Rust process adapter | 267 | `--engine auto` | Rust fallback tests | CLI | Delete | Duplicates Python engine; parity maintenance |
| `src/arbcore/contracts/` | Manifest and template validators | 573 | `validate_contracts.py` | contract tests | diagnostics, scripts | Delete | Does not analyze markets; templates cannot execute |
| `src/defi_arbitrage_core/` | Import/CLI shim | 22 | `python -m ...` | CLI test | README | Delete | No unique behavior |
| `rust/arbcore-rs/` | Second engine | 627 (Rust) | binary | Rust unit/parity | service, CI | Delete | No measured production need; parity drift |
| `contracts/` | Solidity/Vyper templates | 54 + manifest | validator | contract tests | diagnostics, release | Delete | Inert; not part of analysis |
| `scripts/` | 22 validation/release scripts | ~2,300 | scripts | some | validate_all, CI | Collapse to 2 | Layers duplicate pytest and each other |
| `schemas/` | 10 JSON schemas | JSON | docs/validation | schema test | scripts | Keep 2 | Only snapshot and opportunity are product contracts |
| `examples/` | 3 snapshots | JSON | CLI | example tests | users | Keep | Canonical demo input |
| `fixtures/parity/` | Rust parity cases | JSON | Rust validator | none direct | Rust | Delete | Rust is removed |
| `fixtures/golden_outputs/` | 4 goldens | JSON | checks | output checks | scripts | Keep 1 | Only opportunity output is a product contract |
| `release/` | Evidence gate | JSON/MD | release scripts | release tests | CI | Delete | Unsatisfiable by design |
| `docs/en/` | 22 pages | ~? | readers | doc validators | users | Collapse to 6-8 | Duplicated status/release narratives |
| `docs/fa/`, `docs/zh/` | 56 mirrored pages | ~? | readers | localization gate | users | Delete | No localization commitment or maintained parity |
| Root `*.md` | 9 files | ~? | readers | doc validators | users | Collapse | Duplicate quick start/release/history |
| `Dockerfile` | Runtime image | 25 | Docker | smoke | users | Simplify | Copies Rust/contracts/docs/tests |
| `.github/workflows/ci.yml` | CI | 70 | CI | - | maintainers | Simplify | Builds Rust; runs release gate |

## 5. Unsupported claims, misleading names, duplicated authority

- **"multi-network market modeling"**: the engine analyzes one snapshot whose
  `network` field is copied into output. There is no cross-network graph, no
  chain verification, and no network-specific logic. Keep the label as
  declarative metadata; drop the capability implication.
- **"optional Rust acceleration"**: no benchmark is committed, no production
  user is named, and parity is maintained by hand in two languages. The Python
  engine is canonical. Rust is an experiment.
- **"validates Solidity and Vyper templates"**: the validator checks file
  presence, hashes, markers, and a few static patterns. It does not compile,
  audit, simulate, or deploy. This is not a market-analysis responsibility.
- **"schema defines the public contract"**: schemas exist, but runtime
  validation is hand-written and already drifts (`null` source/network).
  Schemas must be enforced by tests, not prose.
- **"release readiness"**: `release_readiness.py` exits 0 even when every gate
  is blocked, and the required evidence file is not shipped. It cannot turn
  green from a clean checkout. This is process theater for an offline
  analyzer.
- **"diagnostics"**: `repository.cwd` is hard-coded to `"."`, so it is not a
  diagnostic. It leaks `sys.executable`, depends on the contract subsystem,
  and has no product user.
- **Two authorities**: Python and Rust implement the same engine; the shim and
  `arbcore` expose the same CLI; `validate_all.py`, `run_unit_checks.py`,
  `demo_workflow.py`, and pytest all re-test the same behavior.
- **Unreachable surface**: `--show-policy` is not in the README's quick start;
  `--error-json` is only exercised by its own validation script; custom
  provider example exists only to feed `validate_all.py`.
- **Default snapshot**: the CLI falls back to `examples/market_snapshot.json`,
  which only exists when run from a checkout. An installed command invoked
  elsewhere silently analyzes a path that is not there.

## 6. Failure modes

### Path handling

The provider resolves paths against CWD and the temp directory. A valid
snapshot at `~/data/snapshot.json` is rejected unless the process runs in
`~`. The symlink check inspects the unresolved path components and can be
bypassed or produce false positives. The error is technically descriptive but
the restriction has no threat model: the tool reads a file the user names.

### Resource exhaustion

- `max_hops` up to 8, `max_results` up to 1,000, node degree up to 500, and
  edges up to 10,000, with no search-expansion budget.
- A 12-asset complete graph (132 edges) takes 1.24 s at 5 hops, 9.04 s at 6
  hops, and does not finish within 30 s at 8 hops.
- `max_results` limits output, not work. A hopeless search still explores the
  whole space.
- Metadata limits (1 MiB per edge, 10 MiB total) protect memory but add code
  for data no consumer reads.

### Numeric semantics

- Rates are scalar and linear; fees are percentage deductions only.
- A product that overflows to infinity is skipped silently. A real but extreme
  cycle can disappear.
- Underflow to zero yields a large negative `profit_bps` and is filtered.
- `limiting_liquidity` is the raw minimum across edges denominated in different
  assets. It is explicitly diagnostic, but the name invites misuse.
- Capacity ignores fees when converting liquidity back to starting units; the
  resulting bound is conservative in the tested direction, but it is still a
  linear quote bound, not executable size.
- Duplicate parallel edges collapse into one canonical path; the highest-profit
  edge wins and competing venues disappear.

### Input validation

- Runtime accepts `"source": null` and `"network": null`; schemas reject them.
- Python's `json` parser accepts `NaN`/`Infinity`; domain validation rejects
  non-finite edge values, so this is closed for rated fields.
- Duplicate JSON keys are silently last-wins.
- Self-loops are rejected. Disconnected graphs and acyclic graphs return an
  empty list without error.

### Process and packaging

- The Rust binary is resolved from `rust/` or PATH; a missing binary silently
  falls back unless `--engine` is used. Two behaviors share one flag.
- Docker copies `rust/`, `contracts/`, `docs/`, and `tests/` into a runtime
  image that needs none of them.
- CI builds Rust, validates contracts, and runs a release gate that cannot
  pass. Optional work dominates the pipeline.
- The two console scripts and two import names make installation ambiguous.

## 7. Architecture and economic-model critique

The architecture is a clean four-stage pipeline wrapped in too many
institutional layers. The useful core is roughly 600 lines: models, provider,
validation, engine, reporters, CLI. Everything else is either an alternate
implementation, a release process, a documentation layer, or a template
validator.

The economic model cannot answer a trading question. It can answer a narrower
one: "Given these scalar quotes and percentage fees, which cycles have positive
nominal return, and how do they rank?" It cannot tell a user whether a cycle is
executable, profitable after gas, robust to slippage, or available at the
stated size. The tool must say that plainly and stop implying more.

The current search is also not a trustworthy bound. `max_hops` is not a
complexity budget because the number of simple cycles grows factorially with
node degree. `max_results` truncates after doing all the work.

## 8. Measured performance

Command (committed as `scripts/benchmark.py`):

```bash
python scripts/benchmark.py
```

Baseline, complete directed graph, all rates 1.0, `min_profit_bps=999999` so
every cycle is explored and filtered:

| Assets | Edges | Max hops | Time | Result |
| --- | --- | --- | --- | --- |
| 8 | 56 | 3 | 0.003 s | 0 |
| 8 | 56 | 4 | 0.014 s | 0 |
| 8 | 56 | 5 | 0.067 s | 0 |
| 8 | 56 | 6 | 0.216 s | 0 |
| 8 | 56 | 8 | 0.872 s | 0 |
| 12 | 132 | 3 | 0.013 s | 0 |
| 12 | 132 | 4 | 0.128 s | 0 |
| 12 | 132 | 5 | 1.236 s | 0 |
| 12 | 132 | 6 | 9.035 s | 0 |
| 12 | 132 | 8 | > 30 s (timeout) | did not finish |

The earlier estimate of ~2.6 s at 5 hops is environment-dependent; 1.24 s was
measured here. The conclusion is unchanged: 8 hops is not a safe default or a
safe maximum without an expansion budget.

After the remediation in this work, the engine aborts at 2,000,000 edge
expansions with `AnalysisLimitError` instead of running unbounded. Measured
expansion counts are 767,200 (8 assets, 8 hops), 1,192,224 (12 assets,
5 hops), and 8,510,304 (12 assets, 6 hops); the budget admits the first two
and aborts the third. The baseline table above records the pre-remediation
behavior that justified the budget.

## 9. Minimal target architecture

```text
snapshot.json
    |
    v
JsonFileProvider  (normal filesystem path, size/UTF-8/JSON checks)
    |
    v
validate_snapshot_payload + MarketSnapshot.validate
    |
    v
AnalysisEngine  (simple-cycle DFS, deterministic expansion budget)
    |
    v
RiskPolicy filter and ranking
    |
    v
TextReporter / JsonReporter  (stdout only; errors on stderr)
```

One import package: `arbcore`. One console script: `defi-arbitrage-core`. Two
schemas: snapshot input and opportunity output. One golden output. One
benchmark. One validation command. English docs only.

### Ordered removal list

1. Rust adapter, crate, parity fixtures, Rust scripts, CI steps, claims.
2. Contract package, `contracts/`, contract schemas/scripts/tests/docs.
3. Release evidence directory, schemas, scripts, golden fixture, gate.
4. Persian and Chinese docs, translation status, duplicate release/status docs.
5. `defi_arbitrage_core` shim and the `arbcore` console script.
6. Diagnostics, self-check, show-policy, error-json, custom-provider example.
7. Path sandbox and environment-based settings.
8. Edge metadata from the input contract.
9. Redundant validation/release scripts, schemas, and fixtures.
10. Packaging, CI, Docker, and Makefile surface that only served the above.

### Estimated resulting size

- Python under `src/arbcore/`: about 650-750 lines.
- Tests: about 450-600 lines covering preserved behavior, adversarial input,
  determinism, and schema parity.
- Scripts: about 200 lines (`validate_all.py`, `benchmark.py`).
- Docs: one README plus six to eight short pages under `docs/en/`.
- Schemas: 2. Examples: 3 snapshots. Golden outputs: 1.
- Tracked files: roughly 55-65, down from 192.

## 10. What the audit does not justify

The audit does not justify rewriting the engine, changing the license, moving
the public remote, or adding new analysis capabilities. The graph search,
policy model, and reporters are adequate for the narrow promise. The work is
deletion, contract repair, bounds, tests, and honest documentation.
