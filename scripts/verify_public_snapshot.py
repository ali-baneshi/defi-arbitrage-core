#!/usr/bin/env python3
"""Verify the current public snapshot without creating tags or changing Git state."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "0.1.0a1"


def main() -> int:
    status = _run(["git", "status", "--porcelain", "--untracked-files=all"])
    if status.returncode != 0:
        print("not inside a Git repository", file=sys.stderr)
        return 2
    if status.stdout.strip():
        print("working tree must be clean before verifying the public snapshot", file=sys.stderr)
        return 2

    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if metadata["project"]["version"] != EXPECTED_VERSION:
        print(f"unexpected package version: {metadata['project']['version']}", file=sys.stderr)
        return 1

    validation = _run([sys.executable, "scripts/validate_all.py", "--include-rust"])
    if validation.returncode != 0:
        if validation.stdout.strip():
            print(validation.stdout.strip())
        if validation.stderr.strip():
            print(validation.stderr.strip(), file=sys.stderr)
        return validation.returncode

    readiness = _run([sys.executable, "scripts/release_readiness.py", "--json"])
    if readiness.returncode != 0:
        if readiness.stderr.strip():
            print(readiness.stderr.strip(), file=sys.stderr)
        return readiness.returncode
    try:
        report = json.loads(readiness.stdout)
    except json.JSONDecodeError as exc:
        print(f"readiness output is not valid JSON: {exc}", file=sys.stderr)
        return 1

    print(f"verified public snapshot package version: {EXPECTED_VERSION}")
    print(f"local_validation_ready: {report.get('local_validation_ready')}")
    print(f"public_release_ready: {report.get('public_release_ready')}")
    print(f"production_ready: {report.get('production_ready')}")
    if report.get("public_release_ready") is not True:
        print("public snapshot remains release-gated", file=sys.stderr)
        return 1
    print("public snapshot verification passed; no tag or remote mutation performed")
    return 0


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
