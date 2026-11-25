#!/usr/bin/env python3
"""Benchmark the cycle search on deterministic complete graphs.

Each case runs in a subprocess so a pathological search cannot hang the parent.
The parent reports a timeout instead of killing the whole benchmark.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DEFAULT_CASES = ((8, 8), (12, 3), (12, 4), (12, 5), (12, 6), (12, 8))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-case timeout in seconds")
    parser.add_argument(
        "--case",
        action="append",
        metavar="ASSETS:HOPS",
        help="Run a custom case; may be repeated",
    )
    parser.add_argument("--worker", nargs=2, metavar=("ASSETS", "HOPS"), help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    if args.worker:
        return _worker(int(args.worker[0]), int(args.worker[1]))

    cases = DEFAULT_CASES
    if args.case:
        cases = tuple(tuple(int(part) for part in value.split(":")) for value in args.case)

    print(f"{'assets':>6} {'edges':>6} {'hops':>5} {'seconds':>9} {'result':>8}")
    for assets, hops in cases:
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "--worker",
            str(assets),
            str(hops),
        ]
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": str(SRC)},
                text=True,
                capture_output=True,
                timeout=args.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            print(f"{assets:>6} {assets * (assets - 1):>6} {hops:>5} {args.timeout:>9.3f} timeout")
            continue
        elapsed = time.perf_counter() - started
        if completed.returncode != 0:
            print(
                f"{assets:>6} {assets * (assets - 1):>6} {hops:>5} {elapsed:>9.3f} "
                f"error: {completed.stderr.strip()}"
            )
            continue
        payload = json.loads(completed.stdout)
        result = payload.get("result", payload.get("error", "unknown"))
        print(f"{assets:>6} {assets * (assets - 1):>6} {hops:>5} {elapsed:>9.3f} {result:>8}")
    return 0


def _worker(assets: int, hops: int) -> int:
    sys.path.insert(0, str(SRC))
    from arbcore import AnalysisEngine, Edge, MarketSnapshot, RiskPolicy

    names = [f"A{index}" for index in range(assets)]
    edges = tuple(
        Edge(source, target, 1.0)
        for source, target in itertools.permutations(names, 2)
    )
    snapshot = MarketSnapshot(edges=edges)
    started = time.perf_counter()
    try:
        opportunities = AnalysisEngine(
            RiskPolicy(min_profit_bps=999_999.0, max_hops=hops, max_results=10)
        ).analyze(snapshot)
    except Exception as exc:  # noqa: BLE001 - report the limit, do not crash the benchmark
        print(
            json.dumps(
                {
                    "error": type(exc).__name__,
                    "message": str(exc),
                    "seconds": round(time.perf_counter() - started, 6),
                }
            )
        )
        return 0
    print(
        json.dumps(
            {
                "result": len(opportunities),
                "seconds": round(time.perf_counter() - started, 6),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
