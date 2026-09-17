#!/usr/bin/env python3
"""Validate the non-secret release evidence contract without third-party packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXAMPLE = ROOT / "release" / "release-evidence.example.json"
DEFAULT_EVIDENCE = ROOT / "release" / "release-evidence.json"
EXPECTED_URL = "https://github.com/ali-baneshi/defi-arbitrage-core"
EXPECTED_VERSION = "0.1.0-alpha"
GATE_IDS = (
    "historical_credentials_rotated",
    "old_git_backups_excluded",
    "independent_history_scan",
    "localized_docs_refreshed_or_scoped",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=None)
    parser.add_argument(
        "--example",
        action="store_true",
        help="Validate the repository's blocked example instead of the completed attestation",
    )
    args = parser.parse_args(argv)
    path = args.path or (DEFAULT_EXAMPLE if args.example else DEFAULT_EVIDENCE)
    errors = validate(path)
    if errors:
        print("release evidence validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"release evidence structure validated: {path}")
    return 0


def validate(path: Path) -> list[str]:
    if not path.is_file():
        return [f"evidence file does not exist: {path}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"evidence file cannot be read: {exc}"]
    return validate_payload(payload)


def validate_payload(payload: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["evidence file must contain an object"]
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if payload.get("release_version") != EXPECTED_VERSION:
        errors.append(f"release_version must be {EXPECTED_VERSION}")
    repository = payload.get("repository")
    if not isinstance(repository, dict):
        errors.append("repository must be an object")
    else:
        if repository.get("canonical_url") != EXPECTED_URL:
            errors.append(f"repository.canonical_url must be {EXPECTED_URL}")
        release_commit = repository.get("release_commit")
        if not isinstance(release_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", release_commit):
            errors.append("repository.release_commit must be a 40-character lowercase Git SHA")
        if not isinstance(repository.get("publication_scope"), str) or not repository[
            "publication_scope"
        ].strip():
            errors.append("repository.publication_scope must be non-empty")
    gates = payload.get("gates")
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
        return errors
    if set(gates) != set(GATE_IDS):
        errors.append("gates must contain exactly the four release gate IDs")
    for gate_id in GATE_IDS:
        item = gates.get(gate_id)
        if not isinstance(item, dict):
            errors.append(f"{gate_id} must be an object")
            continue
        if item.get("status") not in {"satisfied", "blocked"}:
            errors.append(f"{gate_id}.status must be satisfied or blocked")
        if not isinstance(item.get("notes"), str) or not item["notes"].strip():
            errors.append(f"{gate_id}.notes must be non-empty")
        if gate_id in {"historical_credentials_rotated", "old_git_backups_excluded"}:
            for key in ("attested_by", "attested_on"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    errors.append(f"{gate_id}.{key} must be non-empty")
            _validate_date(errors, gate_id, item.get("attested_on"))
        if gate_id == "independent_history_scan":
            if item.get("result") not in {"pass", "fail", "not-run"}:
                errors.append(f"{gate_id}.result is invalid")
            for key in ("tool", "scanned_on", "scope"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    errors.append(f"{gate_id}.{key} must be non-empty")
            _validate_date(errors, gate_id, item.get("scanned_on"))
            report_sha256 = item.get("report_sha256")
            if report_sha256 is not None and (
                not isinstance(report_sha256, str)
                or not re.fullmatch(r"[a-f0-9]{64}", report_sha256)
            ):
                errors.append(f"{gate_id}.report_sha256 must be a lowercase SHA-256 or null")
            if item.get("status") == "satisfied" and item.get("result") == "pass":
                if not isinstance(report_sha256, str) or not re.fullmatch(
                    r"[a-f0-9]{64}", report_sha256
                ):
                    errors.append(f"{gate_id}.report_sha256 is required for a passing scan")
        if gate_id == "localized_docs_refreshed_or_scoped":
            locales = item.get("locales")
            if set(locales or []) != {"fa", "zh"}:
                errors.append(f"{gate_id}.locales must contain fa and zh")
            for key in ("source_commit", "reviewed_on"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    errors.append(f"{gate_id}.{key} must be non-empty")
            source_commit = item.get("source_commit")
            if not isinstance(source_commit, str) or not re.fullmatch(
                r"[0-9a-f]{40}", source_commit
            ):
                errors.append(f"{gate_id}.source_commit must be a 40-character lowercase Git SHA")
            _validate_date(errors, gate_id, item.get("reviewed_on"))
    return errors


def _validate_date(errors: list[str], gate_id: str, value: object) -> None:
    if not isinstance(value, str):
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        errors.append(f"{gate_id} date must be ISO-8601 YYYY-MM-DD")


if __name__ == "__main__":
    raise SystemExit(main())
