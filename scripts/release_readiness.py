#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
DEFAULT_EVIDENCE_FILE = ROOT / "release" / "release-evidence.json"
EXPECTED_RELEASE_VERSION = "0.1.0-alpha"
EXPECTED_REPOSITORY_URL = "https://github.com/ali-baneshi/defi-arbitrage-core"

MANUAL_GATES = [
    {
        "id": "historical_credentials_rotated",
        "status": "blocked-manual",
        "reason": "Credentials from previous local history must be rotated outside this repo.",
        "evidence_required": "Maintainer attestation naming rotated credential classes and rotation date.",  # noqa: E501
    },
    {
        "id": "old_git_backups_excluded",
        "status": "blocked-manual",
        "reason": "Maintainer must confirm old .git backups are outside publication paths.",
        "evidence_required": "Maintainer attestation that publication artifact excludes old repositories/backups.",  # noqa: E501
    },
    {
        "id": "independent_history_scan",
        "status": "blocked-manual",
        "reason": "Run an independent full-history scanner before public release.",
        "evidence_required": "Tool name, scan date, scope, and pass/fail result from outside this baseline.",  # noqa: E501
    },
    {
        "id": "localized_docs_refreshed_or_scoped",
        "status": "blocked-manual",
        "reason": (
            "English remains canonical for release decisions; localized docs must stay refreshed or be explicitly scoped in release notes."  # noqa: E501
        ),
        "evidence_required": "Release notes confirm docs/en is canonical and localized docs are refreshed or intentionally scoped.",  # noqa: E501
    },
]

CHECKS = [
    [sys.executable, "scripts/validate_repository.py"],
    [sys.executable, "scripts/validate_contracts.py", "--json"],
    [sys.executable, "scripts/validate_negative_cases.py"],
    [sys.executable, "scripts/validate_schema_consistency.py"],
    [sys.executable, "scripts/demo_workflow.py"],
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a no-dependency release readiness report."
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--evidence-file",
        type=Path,
        default=DEFAULT_EVIDENCE_FILE,
        help="Path to the non-secret release evidence attestation",
    )
    args = parser.parse_args(argv)

    checks = [_run(command) for command in CHECKS]
    local_ready = all(check["returncode"] == 0 for check in checks)
    evidence, evidence_error = _load_evidence(args.evidence_file)
    manual_gates = _resolve_manual_gates(evidence, evidence_error)
    release_blockers = [gate for gate in manual_gates if gate["status"].startswith("blocked")]
    reviewer_ready = local_ready
    open_source_ready = local_ready and not release_blockers
    production_ready = False
    report = {
        "local_validation_ready": local_ready,
        "reviewer_ready": reviewer_ready,
        "open_source_ready": open_source_ready,
        "public_release_ready": open_source_ready,
        "production_ready": production_ready,
        "maturity": "alpha-offline-mvp",
        "checks": checks,
        "manual_release_gates": manual_gates,
        "summary": (
            "Local validation and all release attestations passed; public alpha release is ready."
            if local_ready and not release_blockers
            else "Local deterministic validation passed, but public release remains blocked "
            "until manual security/history/documentation gates are completed."
            if local_ready
            else "Local deterministic validation failed; review and public release are blocked."
        ),
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"local_validation_ready: {report['local_validation_ready']}")
        print(f"reviewer_ready: {report['reviewer_ready']}")
        print(f"open_source_ready: {report['open_source_ready']}")
        print(f"public_release_ready: {report['public_release_ready']}")
        print(f"production_ready: {report['production_ready']}")
        print(f"maturity: {report['maturity']}")
        for gate in manual_gates:
            label = "SATISFIED" if gate["status"] == "satisfied-manual" else "BLOCKED"
            print(f"{label} {gate['id']}: {gate['reason']}")
    return 0 if local_ready else 1


def _load_evidence(path: Path) -> tuple[dict[str, object] | None, str | None]:
    if not path.is_file():
        return None, f"release evidence file is missing: {path}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"release evidence file cannot be read: {exc}"
    if not isinstance(payload, dict):
        return None, "release evidence file must contain a JSON object"
    from scripts.validate_release_evidence import validate_payload

    validation_errors = validate_payload(payload)
    if validation_errors:
        return None, "; ".join(validation_errors)
    if payload.get("schema_version") != 1:
        return None, "release evidence schema_version must be 1"
    if payload.get("release_version") != EXPECTED_RELEASE_VERSION:
        return None, f"release evidence release_version must be {EXPECTED_RELEASE_VERSION}"
    repository = payload.get("repository")
    if (
        not isinstance(repository, dict)
        or repository.get("canonical_url") != EXPECTED_REPOSITORY_URL
    ):
        return None, f"release evidence canonical_url must be {EXPECTED_REPOSITORY_URL}"
    gates = payload.get("gates")
    if not isinstance(gates, dict):
        return None, "release evidence must contain a gates object"
    return payload, None


def _resolve_manual_gates(
    evidence: dict[str, object] | None,
    evidence_error: str | None,
) -> list[dict[str, str]]:
    if evidence_error:
        return [
            {
                **gate,
                "status": "blocked-manual",
                "reason": evidence_error,
            }
            for gate in MANUAL_GATES
        ]
    assert evidence is not None
    raw_gates = evidence.get("gates")
    assert isinstance(raw_gates, dict)
    resolved: list[dict[str, str]] = []
    for gate in MANUAL_GATES:
        item = raw_gates.get(gate["id"])
        satisfied = _gate_is_satisfied(gate["id"], item)
        resolved.append(
            {
                **gate,
                "status": "satisfied-manual" if satisfied else "blocked-manual",
                "reason": (
                    "Evidence attestation passed."
                    if satisfied
                    else _gate_failure_reason(gate["id"], item)
                ),
            }
        )
    return resolved


def _gate_is_satisfied(gate_id: str, item: object) -> bool:
    if not isinstance(item, dict) or item.get("status") != "satisfied":
        return False
    if gate_id in {"historical_credentials_rotated", "old_git_backups_excluded"}:
        return all(
            isinstance(item.get(key), str) and item[key].strip()
            for key in ("attested_by", "attested_on")
        )
    if gate_id == "independent_history_scan":
        return (
            item.get("result") == "pass"
            and item.get("tool") not in (None, "not-run")
            and isinstance(item.get("report_sha256"), str)
            and re.fullmatch(r"[a-f0-9]{64}", item["report_sha256"]) is not None
        )
    if gate_id == "localized_docs_refreshed_or_scoped":
        locales = item.get("locales")
        return (
            isinstance(locales, list)
            and {str(value) for value in locales} == {"fa", "zh"}
            and isinstance(item.get("source_commit"), str)
            and re.fullmatch(r"[0-9a-f]{40}", item["source_commit"]) is not None
        )
    return True


def _gate_failure_reason(gate_id: str, item: object) -> str:
    if not isinstance(item, dict):
        return f"Evidence attestation is missing for {gate_id}."
    notes = item.get("notes")
    if isinstance(notes, str) and notes.strip():
        return notes.strip()
    return f"Evidence attestation is not satisfied for {gate_id}."


def _run(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=ENV,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command": " ".join(command),
        "returncode": completed.returncode,
        "stdout_json": _json_or_none(completed.stdout),
        "stdout_tail": completed.stdout.strip().splitlines()[-5:],
        "stderr_tail": completed.stderr.strip().splitlines()[-5:],
    }


def _json_or_none(value: str) -> object | None:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
