#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples").glob("*.json"))
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def main() -> int:
    if not EXAMPLES:
        print("No examples found", file=sys.stderr)
        return 1
    for path in EXAMPLES:
        result = subprocess.run(
            [sys.executable, "-m", "defi_arbitrage_core.cli", str(path), "--validate-only"],
            cwd=ROOT,
            env=ENV,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return result.returncode
    output = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "defi_arbitrage_core.cli",
            str(ROOT / "examples" / "market_snapshot.json"),
            "--json",
        ],
        cwd=ROOT,
        env=ENV,
        text=True,
    )
    payload = json.loads(output)
    if not payload or payload[0]["estimated_capacity"] <= 0:
        print("Example analysis did not produce expected opportunity", file=sys.stderr)
        return 1
    print(f"Validated {len(EXAMPLES)} example snapshot(s) and JSON analysis workflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
