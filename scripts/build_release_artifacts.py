#!/usr/bin/env python3
"""Build release distributions and emit deterministic SHA-256 checksums."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "dist" / "release")
    args = parser.parse_args(argv)
    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    for child in outdir.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--sdist", "--outdir", str(outdir)],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        return result.returncode
    artifacts = sorted(path for path in outdir.iterdir() if path.is_file())
    if not artifacts:
        print("no release artifacts were produced", file=sys.stderr)
        return 1
    checksum_path = outdir / "SHA256SUMS"
    lines = []
    for artifact in artifacts:
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        lines.append(f"{digest}  {artifact.name}")
    checksum_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"built {len(artifacts)} release artifacts in {outdir}")
    print(f"checksums: {checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
