#!/usr/bin/env python3
"""Validate that critical JSON outputs conform to golden fixtures and schemas."""

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
    """Run all golden fixture validations."""
    errors: list[str] = []

    # Check that golden fixtures exist
    _check_golden_fixtures_exist(errors)

    # Validate diagnostics output
    _validate_diagnostics_output(errors)

    # Validate CLI error output
    _validate_cli_error_output(errors)

    # Validate contract validation output
    _validate_contract_output(errors)

    # Validate release readiness output
    _validate_release_readiness_output(errors)

    # Validate all outputs against their schemas
    _validate_against_schemas(errors)

    if errors:
        print("golden fixture validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("golden fixture validation passed")
    return 0


def _check_golden_fixtures_exist(errors: list[str]) -> None:
    """Ensure all required golden fixtures are present."""
    required = [
        "fixtures/golden_outputs/diagnostics.json",
        "fixtures/golden_outputs/cli_error.json",
        "fixtures/golden_outputs/contract_validation.json",
        "fixtures/golden_outputs/release_readiness.json",
    ]
    for path in required:
        if not (ROOT / path).exists():
            errors.append(f"missing golden fixture: {path}")


def _validate_diagnostics_output(errors: list[str]) -> None:
    """Validate diagnostics output structure and invariants."""
    actual = collect_diagnostics()
    golden_path = ROOT / "fixtures/golden_outputs/diagnostics.json"

    if not golden_path.exists():
        return

    golden = json.loads(golden_path.read_text(encoding="utf-8"))

    # Check structural invariants
    _check_structure_match(
        errors,
        "diagnostics",
        actual,
        golden,
        [
            "arbcore_version",
            "python",
            "platform",
            "repository",
            "capabilities",
            "optional_tools",
            "resolved_policy",
            "validation_commands",
            "limits",
        ],
    )

    # Check critical capability invariants
    if actual.get("capabilities", {}).get("live_trading") is not False:
        errors.append("diagnostics: live_trading must always be false")

    if actual.get("capabilities", {}).get("contract_deployment") is not False:
        errors.append("diagnostics: contract_deployment must always be false")

    if actual.get("capabilities", {}).get("public_release_ready_claimed") is not False:
        errors.append("diagnostics: public_release_ready_claimed must always be false")

    # Check limits invariants
    limits = actual.get("limits", {})
    if limits.get("max_hops") != 8:
        errors.append(f"diagnostics: max_hops limit must be 8, got {limits.get('max_hops')}")

    if limits.get("max_results") != 1000:
        errors.append(
            f"diagnostics: max_results limit must be 1000, got {limits.get('max_results')}"
        )

    if limits.get("max_snapshot_edges") != 10000:
        errors.append(
            f"diagnostics: max_snapshot_edges must be 10000, got {limits.get('max_snapshot_edges')}"
        )

    actual_cwd = actual.get("repository", {}).get("cwd")
    if actual_cwd is not None:
        from pathlib import Path
        try:
            if Path(actual_cwd).is_absolute():
                errors.append(
                    "diagnostics: repository.cwd must be a relative path, "
                    f"got absolute path {actual_cwd}"
                )
        except (TypeError, OSError):
            errors.append("diagnostics: repository.cwd must be a string path")


def _validate_cli_error_output(errors: list[str]) -> None:
    """Validate CLI structured error output."""
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        code = cli_main(["missing.json", "--error-json"])

    if code != 2:
        errors.append(f"CLI error: exit code must be 2, got {code}")
        return

    try:
        actual = json.loads(stderr.getvalue())
    except json.JSONDecodeError as exc:
        errors.append(f"CLI error: output must be valid JSON: {exc}")
        return

    golden_path = ROOT / "fixtures/golden_outputs/cli_error.json"
    if not golden_path.exists():
        return

    golden = json.loads(golden_path.read_text(encoding="utf-8"))

    _check_structure_match(errors, "CLI error", actual, golden, ["ok", "error"])

    if actual.get("ok") is not False:
        errors.append("CLI error: ok field must be false")

    error_obj = actual.get("error", {})
    if not isinstance(error_obj, dict):
        errors.append("CLI error: error field must be an object")
    else:
        if "type" not in error_obj:
            errors.append("CLI error: error.type is required")
        if "message" not in error_obj:
            errors.append("CLI error: error.message is required")


def _validate_contract_output(errors: list[str]) -> None:
    """Validate contract validation report structure."""
    actual = validate_contract_workspace().to_dict()

    golden_path = ROOT / "fixtures/golden_outputs/contract_validation.json"
    if not golden_path.exists():
        return

    golden = json.loads(golden_path.read_text(encoding="utf-8"))

    _check_structure_match(
        errors,
        "contract validation",
        actual,
        golden,
        [
            "manifest_path",
            "artifacts_checked",
            "languages",
            "manifest_sha256",
            "ok",
            "findings",
        ],
    )

    # For the canonical workspace, ok must be true
    if actual.get("ok") is not True:
        errors.append("contract validation: canonical workspace must pass (ok=true)")

    # Check languages
    expected_languages = {"solidity", "vyper"}
    actual_languages = set(actual.get("languages", []))
    if actual_languages != expected_languages:
        errors.append(
            f"contract validation: languages must be {expected_languages}, got {actual_languages}"
        )


def _validate_release_readiness_output(errors: list[str]) -> None:
    """Validate release readiness report structure and invariants."""
    completed = subprocess.run(
        [sys.executable, "scripts/release_readiness.py", "--json"],
        cwd=ROOT,
        env=ENV,
        text=True,
        capture_output=True,
        check=False,
    )

    if completed.returncode != 0:
        errors.append("release readiness: command failed")
        return

    try:
        actual = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"release readiness: output must be valid JSON: {exc}")
        return

    golden_path = ROOT / "fixtures/golden_outputs/release_readiness.json"
    if not golden_path.exists():
        return

    golden = json.loads(golden_path.read_text(encoding="utf-8"))

    _check_structure_match(
        errors,
        "release readiness",
        actual,
        golden,
        [
            "local_validation_ready",
            "reviewer_ready",
            "open_source_ready",
            "public_release_ready",
            "production_ready",
            "maturity",
            "checks",
            "manual_release_gates",
            "summary",
        ],
    )

    # Check critical invariants
    if actual.get("production_ready") is not False:
        errors.append("release readiness: production_ready must always be false")

    if actual.get("maturity") != "alpha-offline-mvp":
        errors.append(
            f"release readiness: maturity must be 'alpha-offline-mvp', got {actual.get('maturity')}"
        )

    # Check manual gates structure
    gates = actual.get("manual_release_gates", [])
    if not gates:
        errors.append("release readiness: manual_release_gates must not be empty")

    for gate in gates:
        if not isinstance(gate, dict):
            errors.append("release readiness: each manual gate must be an object")
            continue

        required_gate_keys = {"id", "status", "reason", "evidence_required"}
        actual_gate_keys = set(gate.keys())
        if actual_gate_keys != required_gate_keys:
            errors.append(
                f"release readiness: manual gate missing keys: {required_gate_keys - actual_gate_keys}"  # noqa: E501
            )


def _validate_against_schemas(errors: list[str]) -> None:
    """Validate that golden outputs conform to their JSON schemas."""
    validations = [
        ("fixtures/golden_outputs/diagnostics.json", "schemas/diagnostics.schema.json"),
        ("fixtures/golden_outputs/cli_error.json", "schemas/error.schema.json"),
        (
            "fixtures/golden_outputs/contract_validation.json",
            "schemas/contract_validation_report.schema.json",
        ),
        ("fixtures/golden_outputs/release_readiness.json", "schemas/release_readiness.schema.json"),
    ]

    for fixture_path, schema_path in validations:
        fixture = ROOT / fixture_path
        schema = ROOT / schema_path

        if not fixture.exists() or not schema.exists():
            continue

        # Basic schema validation without external dependencies
        try:
            fixture_data = json.loads(fixture.read_text(encoding="utf-8"))
            schema_data = json.loads(schema.read_text(encoding="utf-8"))

            # Check required fields from schema
            if "required" in schema_data:
                for field in schema_data["required"]:
                    if field not in fixture_data:
                        errors.append(
                            f"{fixture_path}: missing required field '{field}' from schema"
                        )
        except Exception as exc:
            errors.append(f"schema validation error for {fixture_path}: {exc}")


def _check_structure_match(
    errors: list[str],
    label: str,
    actual: dict,
    golden: dict,
    required_keys: list[str],
) -> None:
    """Check that actual output has the same structure as golden output."""
    actual_keys = set(actual.keys())
    golden_keys = set(golden.keys())

    # Check for missing keys
    missing = set(required_keys) - actual_keys
    if missing:
        errors.append(f"{label}: missing required keys: {', '.join(sorted(missing))}")

    # Check for unexpected keys (compared to golden)
    extra = actual_keys - golden_keys
    if extra:
        errors.append(f"{label}: unexpected keys not in golden fixture: {', '.join(sorted(extra))}")


if __name__ == "__main__":
    raise SystemExit(main())
