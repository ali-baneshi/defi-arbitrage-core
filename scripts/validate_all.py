#!/usr/bin/env python3
"""Compile the tree and run the test suite.

This is the single local validation entrypoint. It has no network access and
does not install anything; install the dev extras first.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def run(label: str, command: list[str]) -> None:
    print(f"==> {label}", flush=True)
    subprocess.check_call(command, cwd=ROOT, env=ENV)


def main() -> int:
    run(
        "compile Python sources",
        [sys.executable, "-m", "compileall", "-q", "src", "tests", "scripts", "examples"],
    )
    run("test suite", [sys.executable, "-m", "pytest", "-q"])
    print("validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
