#!/usr/bin/env python3
"""Clone and scan the refs currently advertised by the public Git remote."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "scripts" / "audit_git_history.py"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--remote",
        default=None,
        help="Remote URL; defaults to the configured origin URL",
    )
    args = parser.parse_args(argv)
    explicit_remote = args.remote is not None
    remote = args.remote or _configured_origin()
    if not remote:
        print("no remote URL supplied and origin is not configured", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="defi-arbitrage-public-audit-") as temp_dir:
        mirror = Path(temp_dir) / "remote.git"
        clone, clone_remote = _clone_mirror(
            remote, mirror, allow_public_https_fallback=not explicit_remote
        )
        if clone.returncode != 0:
            print("public remote mirror clone failed", file=sys.stderr)
            if clone.stderr.strip():
                print(_redact(clone.stderr), file=sys.stderr)
            return clone.returncode
        if clone_remote != remote:
            print(f"Public remote SSH access unavailable; audited HTTPS mirror: {clone_remote}")

        refs = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname) %(objectname)"],
            cwd=mirror,
            text=True,
            capture_output=True,
            check=False,
        )
        if refs.returncode != 0:
            print("could not enumerate mirrored remote refs", file=sys.stderr)
            return refs.returncode

        scan = subprocess.run(
            [sys.executable, str(SCANNER), "--repo", str(mirror)],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            text=True,
            capture_output=True,
            check=False,
        )
        print(f"Public remote refs inspected: {len(refs.stdout.splitlines())}")
        if scan.stdout.strip():
            print(scan.stdout.strip())
        if scan.returncode != 0 and scan.stderr.strip():
            print(_redact(scan.stderr), file=sys.stderr)
        if scan.returncode == 0:
            print(
                "This verifies the advertised public refs only; it does not prove "
                "server-side unreachable objects were removed."
            )
        return scan.returncode


def _configured_origin() -> str | None:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _clone_mirror(
    remote: str, mirror: Path, *, allow_public_https_fallback: bool
) -> tuple[subprocess.CompletedProcess[str], str]:
    candidates = [remote]
    https_remote = _github_https_url(remote)
    if allow_public_https_fallback and https_remote and https_remote != remote:
        candidates.append(https_remote)
    last_result: subprocess.CompletedProcess[str] | None = None
    for candidate in candidates:
        result = subprocess.run(
            ["git", "clone", "--mirror", "--quiet", candidate, str(mirror)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode == 0:
            return result, candidate
        last_result = result
    assert last_result is not None
    return last_result, candidates[-1]


def _github_https_url(remote: str) -> str | None:
    if remote.startswith("git@github.com:"):
        return "https://github.com/" + remote.removeprefix("git@github.com:")
    if remote.startswith("ssh://git@github.com/"):
        return "https://github.com/" + remote.removeprefix("ssh://git@github.com/")
    return None


def _redact(value: str) -> str:
    lines = []
    for line in value.splitlines():
        if "@" in line and "://" in line:
            prefix, suffix = line.split("@", 1)
            scheme = prefix.split("://", 1)[0]
            line = f"{scheme}://[credentials-redacted]@{suffix}"
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
