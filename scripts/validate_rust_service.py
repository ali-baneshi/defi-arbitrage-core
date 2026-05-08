#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRATE = ROOT / "rust" / "arbcore-rs"
BINARY = CRATE / "target" / "debug" / "defi-arbitrage-core-rs"
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
POLICY_ARGS = ["--min-profit-bps", "1", "--max-hops", "4", "--max-results", "10"]


def main() -> int:
    if not CRATE.exists():
        print("Rust crate is missing", file=sys.stderr)
        return 1
    subprocess.check_call(["cargo", "build"], cwd=CRATE)
    errors: list[str] = []
    errors.extend(_check_valid_parity(ROOT / "examples" / "market_snapshot.json"))
    errors.extend(_check_valid_parity(ROOT / "examples" / "no_opportunity_snapshot.json"))
    errors.extend(_check_fail_closed_cases())
    if errors:
        print("Rust service validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Rust service validation passed")
    return 0


def _check_valid_parity(snapshot: Path) -> list[str]:
    errors: list[str] = []
    rust = _run([str(BINARY), str(snapshot), *POLICY_ARGS])
    python = _run(
        [
            sys.executable,
            "-m",
            "defi_arbitrage_core.cli",
            str(snapshot),
            "--engine",
            "python",
            "--json",
            *POLICY_ARGS,
        ],
        cwd=ROOT,
        env=ENV,
    )
    if rust.returncode != 0:
        return [f"Rust failed for {snapshot.name}: {rust.stderr.strip()}"]
    if python.returncode != 0:
        return [f"Python failed for {snapshot.name}: {python.stderr.strip()}"]
    rust_payload = json.loads(rust.stdout)
    python_payload = json.loads(python.stdout)
    if len(rust_payload) != len(python_payload):
        errors.append(f"Python/Rust opportunity count differs for {snapshot.name}")
        return errors
    for index, (left, right) in enumerate(zip(rust_payload, python_payload, strict=False)):
        for key in ("network", "path", "venues", "limiting_liquidity"):
            if left.get(key) != right.get(key):
                errors.append(f"Python/Rust {key} differs for {snapshot.name} result {index}")
        for key in ("gross_return", "profit_bps", "estimated_capacity"):
            if abs(float(left.get(key)) - float(right.get(key))) > 1e-9:
                errors.append(f"Python/Rust {key} differs for {snapshot.name} result {index}")
    return errors


def _check_fail_closed_cases() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as directory:
        bad_timestamp = Path(directory) / "bad_timestamp.json"
        bad_timestamp.write_text(
            json.dumps(
                {
                    "timestamp": "2026-05-05 00:00:00",
                    "edges": [{"source": "A", "target": "B", "rate": 1.0}],
                }
            ),
            encoding="utf-8",
        )
        bad_metadata = Path(directory) / "bad_metadata.json"
        bad_metadata.write_text(
            json.dumps({"edges": [{"source": "A", "target": "B", "rate": 1.0, "metadata": []}]}),
            encoding="utf-8",
        )
        cases = [
            ("bad timestamp", [str(BINARY), str(bad_timestamp)], "timestamp"),
            ("bad metadata", [str(BINARY), str(bad_metadata)], "metadata"),
            (
                "bad policy",
                [str(BINARY), str(ROOT / "examples" / "market_snapshot.json"), "--max-hops", "99"],
                "max_hops",
            ),
        ]
        for label, command, expected in cases:
            result = _run(command)
            if result.returncode != 2:
                errors.append(f"Rust {label} should exit 2, got {result.returncode}")
            if expected not in result.stderr:
                errors.append(f"Rust {label} stderr should mention {expected!r}")
    return errors


def _run(
    command: list[str], cwd: Path | None = None, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
