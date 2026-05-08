#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}

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
    args = parser.parse_args(argv)

    checks = [_run(command) for command in CHECKS]
    local_ready = all(check["returncode"] == 0 for check in checks)
    release_blockers = [gate for gate in MANUAL_GATES if gate["status"].startswith("blocked")]
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
        "manual_release_gates": MANUAL_GATES,
        "summary": (
            "Local deterministic validation passed, but public release remains blocked "
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
        for gate in MANUAL_GATES:
            print(f"BLOCKED {gate['id']}: {gate['reason']}")
    return 0 if local_ready else 1


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
