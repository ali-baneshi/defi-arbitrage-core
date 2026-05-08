#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def main() -> int:
    steps = [
        [
            sys.executable,
            "-m",
            "defi_arbitrage_core.cli",
            "examples/market_snapshot.json",
            "--json",
        ],
        [
            sys.executable,
            "-m",
            "defi_arbitrage_core.cli",
            "examples/no_opportunity_snapshot.json",
            "--json",
        ],
        [sys.executable, "scripts/validate_contracts.py", "--json"],
        [sys.executable, "-m", "defi_arbitrage_core.cli", "--diagnostics"],
    ]
    report = {"ok": True, "steps": []}
    for command in steps:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=ENV,
            text=True,
            capture_output=True,
            check=False,
        )
        step = {
            "command": " ".join(command),
            "returncode": completed.returncode,
            "stdout_json": _json_or_none(completed.stdout),
            "stderr": completed.stderr.strip(),
        }
        if completed.returncode != 0:
            report["ok"] = False
        report["steps"].append(step)
    first = report["steps"][0]["stdout_json"]
    second = report["steps"][1]["stdout_json"]
    contracts = report["steps"][2]["stdout_json"]
    diagnostics = report["steps"][3]["stdout_json"]
    if not first or first[0]["profit_bps"] <= 0 or not first[0].get("network"):
        report["ok"] = False
    if second != []:
        report["ok"] = False
    if not contracts or contracts.get("ok") is not True:
        report["ok"] = False
    if not diagnostics or "validation_commands" not in diagnostics:
        report["ok"] = False
    if (
        not diagnostics
        or diagnostics.get("capabilities", {}).get("multi_network_snapshots") is not True
    ):
        report["ok"] = False
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


def _json_or_none(value: str) -> object | None:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
