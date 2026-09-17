#!/usr/bin/env python3
"""Scan reachable, reflog, and unreachable Git blobs for high-risk patterns."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HIGH_CONFIDENCE = re.compile(
    rb"(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{36,}|"
    rb"github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    rb"-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----)"
)
ASSIGNMENT = re.compile(
    rb"(private[_-]?key|client[_-]?secret|api[_-]?key|access[_-]?token|"
    rb"secret[_-]?key)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=:-]{16,}"
)


def main() -> int:
    if not _inside_git_repo():
        print("not inside a Git repository", file=sys.stderr)
        return 2
    objects = _object_ids()
    findings = [
        object_id
        for object_id, content in _blob_contents(objects)
        if HIGH_CONFIDENCE.search(content) or ASSIGNMENT.search(content)
    ]
    if findings:
        print("potential historical secret patterns found in Git blobs", file=sys.stderr)
        for object_id in sorted(set(findings)):
            print(f"- blob {object_id}", file=sys.stderr)
        return 1
    print(f"Git history scan passed: {len(objects)} blobs inspected")
    return 0


def _inside_git_repo() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def _object_ids() -> set[str]:
    ids: set[str] = set()
    reachable = subprocess.check_output(
        ["git", "rev-list", "--objects", "--all", "--reflog"], cwd=ROOT, text=True
    )
    for line in reachable.splitlines():
        object_id = line.split(maxsplit=1)[0]
        if len(object_id) == 40:
            ids.add(object_id)
    fsck = subprocess.check_output(
        ["git", "fsck", "--full", "--no-reflogs", "--unreachable"],
        cwd=ROOT,
        text=True,
        stderr=subprocess.DEVNULL,
    )
    for line in fsck.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[1] == "blob":
            ids.add(parts[2])
    return ids


def _blob_contents(object_ids: set[str]):
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    try:
        for object_id in sorted(object_ids):
            process.stdin.write(f"{object_id}\n".encode())
        process.stdin.close()
        for object_id in sorted(object_ids):
            header = process.stdout.readline().split()
            if len(header) != 3 or header[1] != b"blob":
                continue
            size = int(header[2])
            content = process.stdout.read(size)
            process.stdout.read(1)
            yield object_id, content
    finally:
        process.stdout.close()
        process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
