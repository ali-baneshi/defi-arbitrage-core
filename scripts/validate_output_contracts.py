#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ENV = {**os.environ, "PYTHONPATH": str(SRC)}
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arbcore.cli import main as cli_main  # noqa: E402
from arbcore.contracts import validate_contract_workspace  # noqa: E402
from arbcore.diagnostics import collect_diagnostics  # noqa: E402


def main() -> int:
    errors: list[str] = []
    _check_diagnostics(errors, collect_diagnostics())
    _check_contract_report(errors, validate_contract_workspace().to_dict())
    _check_cli_error(errors)
    _check_release_readiness(errors)
    _check_schema_files(errors)
    if errors:
        print("output contract validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("output contract validation passed")
    return 0


def _check_diagnostics(errors: list[str], payload: object) -> None:
    if not isinstance(payload, dict):
        errors.append("diagnostics output must be an object")
        return
    required = {
        "arbcore_version",
        "python",
        "platform",
        "repository",
        "capabilities",
        "optional_tools",
        "resolved_policy",
        "validation_commands",
        "limits",
    }
    _expect_keys(errors, "diagnostics", payload, required)
    capabilities = payload.get("capabilities")
    if isinstance(capabilities, dict):
        if capabilities.get("live_trading") is not False:
            errors.append("diagnostics must report live_trading=false")
        if capabilities.get("contract_deployment") is not False:
            errors.append("diagnostics must report contract_deployment=false")
        if capabilities.get("multi_network_snapshots") is not True:
            errors.append("diagnostics must report multi_network_snapshots=true")
        if set(capabilities.get("smart_contract_languages", [])) != {"solidity", "vyper"}:
            errors.append("diagnostics must report solidity and vyper support")
    if payload.get("limits", {}).get("max_snapshot_edges") != 10000:
        errors.append("diagnostics max_snapshot_edges drifted")


def _check_contract_report(errors: list[str], payload: object) -> None:
    if not isinstance(payload, dict):
        errors.append("contract report must be an object")
        return
    required = {
        "manifest_path",
        "artifacts_checked",
        "languages",
        "manifest_sha256",
        "ok",
        "findings",
    }
    _expect_keys(errors, "contract report", payload, required)
    if payload.get("ok") is not True:
        errors.append("canonical contract report must pass")
    if set(payload.get("languages", [])) != {"solidity", "vyper"}:
        errors.append("contract report must include solidity and vyper")
    for finding in payload.get("findings", []):
        if not isinstance(finding, dict):
            errors.append("contract finding must be an object")
            continue
        _expect_keys(
            errors, "contract finding", finding, {"path", "severity", "code", "message", "line"}
        )


def _check_cli_error(errors: list[str]) -> None:
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        code = cli_main(["missing.json", "--error-json"])
    if code != 2:
        errors.append(f"CLI structured error exit code must be 2, got {code}")
        return
    try:
        payload = json.loads(stderr.getvalue())
    except json.JSONDecodeError as exc:
        errors.append(f"CLI structured error must be JSON: {exc}")
        return
    _expect_keys(errors, "CLI error", payload, {"ok", "error"})
    if payload.get("ok") is not False:
        errors.append("CLI error ok must be false")
    error = payload.get("error")
    if not isinstance(error, dict):
        errors.append("CLI error.error must be an object")
    else:
        _expect_keys(errors, "CLI error.error", error, {"type", "message"})


def _check_release_readiness(errors: list[str]) -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/release_readiness.py", "--json"],
        cwd=ROOT,
        env=ENV,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        errors.append("release readiness JSON command failed")
        return
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"release readiness must emit JSON: {exc}")
        return
    required = {
        "local_validation_ready",
        "reviewer_ready",
        "open_source_ready",
        "public_release_ready",
        "production_ready",
        "maturity",
        "checks",
        "manual_release_gates",
        "summary",
    }
    _expect_keys(errors, "release readiness", payload, required)
    if payload.get("production_ready") is not False:
        errors.append("release readiness must not claim production readiness")
    if payload.get("public_release_ready") is not False:
        errors.append(
            "canonical release readiness must remain blocked until manual gates are satisfied"
        )
    for gate in payload.get("manual_release_gates", []):
        if not isinstance(gate, dict):
            errors.append("manual release gate must be an object")
            continue
        _expect_keys(
            errors, "manual release gate", gate, {"id", "status", "reason", "evidence_required"}
        )


def _check_schema_files(errors: list[str]) -> None:
    for relative in (
        "schemas/diagnostics.schema.json",
        "schemas/error.schema.json",
        "schemas/contract_validation_report.schema.json",
        "schemas/release_readiness.schema.json",
        "schemas/validation_summary.schema.json",
    ):
        payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        if not payload.get("title"):
            errors.append(f"schema missing title: {relative}")


def _expect_keys(errors: list[str], label: str, payload: dict, expected: set[str]) -> None:
    actual = set(payload)
    missing = expected - actual
    extra = actual - expected
    if missing:
        errors.append(f"{label} missing keys: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"{label} has unsupported keys: {', '.join(sorted(extra))}")


if __name__ == "__main__":
    raise SystemExit(main())
