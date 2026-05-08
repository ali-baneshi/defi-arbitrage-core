#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def run(label: str, command: list[str]) -> None:
    print(f"==> {label}", flush=True)
    subprocess.check_call(command, cwd=ROOT, env=ENV)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run dependency-free repository validation.")
    parser.add_argument(
        "--include-rust",
        action="store_true",
        help="Also build and validate Rust service",
    )
    args = parser.parse_args(argv)

    run(
        "compile Python sources",
        [sys.executable, "-m", "compileall", "-q", "src", "tests", "scripts", "examples"],
    )
    run("dependency-free unit checks", [sys.executable, "scripts/run_unit_checks.py"])
    run("example workflow validation", [sys.executable, "scripts/validate_examples.py"])
    run("custom provider example", [sys.executable, "examples/custom_provider.py"])
    run("contract template validation", [sys.executable, "scripts/validate_contracts.py"])
    run("repository metadata validation", [sys.executable, "scripts/validate_repository.py"])
    run(
        "documented command validation", [sys.executable, "scripts/validate_documented_commands.py"]
    )
    run("schema consistency validation", [sys.executable, "scripts/validate_schema_consistency.py"])
    run("output contract validation", [sys.executable, "scripts/validate_output_contracts.py"])
    run("negative validation scenarios", [sys.executable, "scripts/validate_negative_cases.py"])
    run("deterministic demo workflow", [sys.executable, "scripts/demo_workflow.py"])
    run("release readiness report", [sys.executable, "scripts/release_readiness.py"])
    run("active-tree secret scan", ["./scripts/secret_scan.sh"])
    if args.include_rust:
        if shutil.which("cargo") is None:
            print("cargo is not available; skipping optional Rust validation")
        else:
            run("Rust service validation", [sys.executable, "scripts/validate_rust_service.py"])
    print("all dependency-free validation checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
