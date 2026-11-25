# Validation

## Commands

```bash
PYTHONPATH=src python scripts/validate_all.py
python -m pytest -q
ruff check .
python scripts/benchmark.py
```

`validate_all.py` compiles `src`, `tests`, `scripts`, and `examples`, then runs
the pytest suite. `ruff` is a separate dev check. The benchmark is not part of
the pass/fail gate because it measures, rather than asserts, performance.

## What each check proves

| Check | Proves |
| --- | --- |
| `compileall` | Every Python file parses and imports are syntactically valid |
| `pytest` | Documented behavior, adversarial input, bounds, determinism, and CLI contracts hold |
| `ruff` | Style and common-error rules pass |
| `benchmark.py` | Search behavior is measured on complete graphs and the budget holds |
| Clean-venv install | The documented install command works without `PYTHONPATH` |
| Example CLI runs | The canonical snapshots produce the documented results |

## Covered failure modes

The test suite includes:

- malformed JSON, non-UTF-8 files, missing files, and directories;
- unknown snapshot and edge keys;
- explicit `null` optional fields;
- non-finite and out-of-range rates, fees, and liquidity;
- self-loops and empty edge lists;
- duplicate/parallel edges and disconnected or acyclic graphs;
- oversized symbols and venues;
- invalid policy values;
- search-budget exhaustion;
- CLI missing file, unknown flag, `--json`, `--validate-only`, stdout/stderr
  separation, and exit codes;
- byte-identical repeated JSON output;
- schema/runtime parity for the published contracts.

## Schema parity

`schemas/market_snapshot.schema.json` and `schemas/opportunity.schema.json` are
the published contracts. Tests validate accepted payloads against the schemas
and confirm that boundary constants in the schemas match `arbcore.models`.
When runtime validation and a schema disagree, that is a bug; do not document
around it.

## Benchmark

```bash
python scripts/benchmark.py
python scripts/benchmark.py --timeout 10 --case 12:8
```

Each case runs in a subprocess so a pathological search cannot hang the parent.
The default matrix covers 8 and 12 asset complete graphs at 3-8 hops. The
12-asset, 8-hop case must return `AnalysisLimitError`, not run unbounded.

## Clean install

```bash
python -m venv /tmp/arbcore-venv
/tmp/arbcore-venv/bin/pip install .
/tmp/arbcore-venv/bin/defi-arbitrage-core examples/market_snapshot.json --json
```

Run this from the repository root. It must not require `PYTHONPATH` or any
optional tool.

## Interpreting failure

- Compile failure: fix syntax or imports first.
- Test failure: treat the contract in `PRODUCT.md` and the schema as
  authoritative; fix the code, not the assertion.
- Budget failure: reduce `--max-hops`, raise `--min-liquidity`, or split the
  snapshot. Do not raise the budget without a new benchmark.
- Benchmark timeout: the budget is not being enforced; investigate before
  merging.
