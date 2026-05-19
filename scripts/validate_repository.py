#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = (
    "README.md",
    "SECURITY.md",
    "RELEASE.md",
    "CONTRIBUTING.md",
    "docs/TRANSLATION_STATUS.md",
    "docs/en/RUNBOOK.md",
    "docs/en/CONTRACTS.md",
    "docs/en/REVIEWER_GUIDE.md",
    "docs/en/TRUST_BOUNDARIES.md",
    "docs/en/VALIDATION.md",
    "docs/en/ARCHITECTURE.md",
    "docs/en/PROJECT_BOUNDARIES.md",
    "docs/en/RELEASE_EVIDENCE.md",
    "docs/en/SUPPORT_MATRIX.md",
    "docs/en/OPEN_SOURCE_RELEASE_PLAN.md",
    "docs/en/OPEN_SOURCE_TASKS.md",
)
REQUIRED_SCHEMAS = (
    "schemas/diagnostics.schema.json",
    "schemas/error.schema.json",
    "schemas/market_snapshot.schema.json",
    "schemas/opportunity.schema.json",
    "schemas/policy.schema.json",
    "schemas/contract_manifest.schema.json",
    "schemas/contract_validation_report.schema.json",
    "schemas/release_readiness.schema.json",
    "schemas/validation_summary.schema.json",
)
REQUIRED_COMMANDS = (
    "PYTHONPATH=src python scripts/validate_all.py",
    "PYTHONPATH=src python scripts/validate_contracts.py",
    "PYTHONPATH=src python scripts/demo_workflow.py",
    "PYTHONPATH=src python scripts/release_readiness.py",
    "PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics",
    "PYTHONPATH=src python scripts/validate_schema_consistency.py",
    "PYTHONPATH=src python scripts/validate_negative_cases.py",
    "PYTHONPATH=src python -m defi_arbitrage_core.cli examples/market_snapshot.json --validate-only",  # noqa: E501
)
FORBIDDEN_TRACKED_PARTS = ("__pycache__", ".pytest_cache", ".ruff_cache")
FORBIDDEN_TRACKED_SUFFIXES = (".pyc", ".pyo", ".log", ".sqlite", ".db")


def main() -> int:
    errors: list[str] = []
    errors.extend(check_required_files())
    errors.extend(check_schema_files())
    errors.extend(check_readme_commands())
    errors.extend(check_translation_status())
    errors.extend(check_contract_doc_consistency())
    errors.extend(check_boundary_docs())
    errors.extend(check_project_boundary_doc())
    errors.extend(check_release_readiness_model())
    errors.extend(check_release_evidence_doc())
    errors.extend(check_support_matrix_doc())
    errors.extend(check_version_consistency())
    errors.extend(check_ci_coverage())
    errors.extend(check_tracked_generated_files())
    if errors:
        print("repository validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("repository metadata validation passed")
    return 0


def check_required_files() -> list[str]:
    return [
        f"missing required file: {path}" for path in REQUIRED_DOCS if not (ROOT / path).is_file()
    ]


def check_schema_files() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_SCHEMAS:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing schema: {relative}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"schema is invalid JSON: {relative}: {exc}")
            continue
        if not str(payload.get("$schema", "")).startswith("https://json-schema.org"):
            errors.append(f"schema missing json-schema $schema: {relative}")
        if not payload.get("title"):
            errors.append(f"schema missing title: {relative}")
    return errors


def check_readme_commands() -> list[str]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    return [
        f"README missing command: {command}"
        for command in REQUIRED_COMMANDS
        if command not in readme
    ]


def check_translation_status() -> list[str]:
    status = ROOT / "docs" / "TRANSLATION_STATUS.md"
    if not status.is_file():
        return ["missing docs/TRANSLATION_STATUS.md"]
    text = status.read_text(encoding="utf-8")
    required = ("canonical-current", "docs/en")
    errors = [
        f"translation status missing marker: {marker}" for marker in required if marker not in text
    ]
    if "stale-summary" not in text and "localized-current" not in text:
        errors.append("translation status missing supported locale state marker")
    return errors


def check_contract_doc_consistency() -> list[str]:
    errors: list[str] = []
    manifest_path = ROOT / "contracts" / "contract-manifest.json"
    contracts_doc = (ROOT / "docs" / "en" / "CONTRACTS.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"contract manifest is invalid JSON: {exc}"]
    for language in manifest.get("language_metadata", {}):
        if language not in contracts_doc:
            errors.append(f"CONTRACTS.md does not mention manifest language: {language}")
    for artifact in manifest.get("artifacts", []):
        path = artifact.get("path", "")
        if path and path not in contracts_doc and path not in readme:
            errors.append(f"contract artifact path is undocumented: {path}")
        if not artifact.get("source_sha256"):
            errors.append(f"contract artifact missing source_sha256: {artifact.get('name')}")
    return errors


def check_boundary_docs() -> list[str]:
    errors: list[str] = []
    reviewer = (ROOT / "docs" / "en" / "REVIEWER_GUIDE.md").read_text(encoding="utf-8")
    boundaries = (ROOT / "docs" / "en" / "TRUST_BOUNDARIES.md").read_text(encoding="utf-8")
    required_reviewer = (
        "Canonical Sources Of Truth",
        "Normative vs Illustrative",
        "Fast Review Path",
    )
    required_boundaries = ("Untrusted Inputs", "Explicitly Out Of Boundary", "Fail-Closed Rules")
    errors.extend(
        f"REVIEWER_GUIDE.md missing section: {section}"
        for section in required_reviewer
        if section not in reviewer
    )
    errors.extend(
        f"TRUST_BOUNDARIES.md missing section: {section}"
        for section in required_boundaries
        if section not in boundaries
    )
    return errors


def check_project_boundary_doc() -> list[str]:
    path = ROOT / "docs" / "en" / "PROJECT_BOUNDARIES.md"
    if not path.is_file():
        return ["missing docs/en/PROJECT_BOUNDARIES.md"]
    text = path.read_text(encoding="utf-8")
    required = (
        "Canonical Sources",
        "Offline-Only Boundary",
        "Smart-Contract Boundary",
        "Release Boundary",
        "Reviewer Inference Rules",
        "does not compile, audit, deploy",
    )
    return [
        f"PROJECT_BOUNDARIES.md missing marker: {marker}"
        for marker in required
        if marker not in text
    ]


def check_release_readiness_model() -> list[str]:
    text = (ROOT / "scripts" / "release_readiness.py").read_text(encoding="utf-8")
    required = (
        "reviewer_ready",
        "open_source_ready",
        "production_ready",
        "manual_release_gates",
        "public_release_ready",
    )
    return [
        f"release readiness model missing field: {field}" for field in required if field not in text
    ]


def check_support_matrix_doc() -> list[str]:
    path = ROOT / "docs" / "en" / "SUPPORT_MATRIX.md"
    if not path.is_file():
        return ["missing docs/en/SUPPORT_MATRIX.md"]
    text = path.read_text(encoding="utf-8")
    required = (
        "Solidity contract templates",
        "Vyper contract templates",
        "Rust analyzer",
        "Explicitly Unsupported",
        "Live trading",
        "Contract deployment",
        "Prose-only expansion is not acceptable",
    )
    return [
        f"SUPPORT_MATRIX.md missing marker: {marker}" for marker in required if marker not in text
    ]


def check_release_evidence_doc() -> list[str]:
    path = ROOT / "docs" / "en" / "RELEASE_EVIDENCE.md"
    if not path.is_file():
        return ["missing docs/en/RELEASE_EVIDENCE.md"]
    text = path.read_text(encoding="utf-8")
    required = (
        "Readiness State Model",
        "Manual Evidence Requirements",
        "historical_credentials_rotated",
        "independent_history_scan",
        "localized_docs_refreshed_or_scoped",
        "production_ready",
    )
    return [
        f"RELEASE_EVIDENCE.md missing marker: {marker}" for marker in required if marker not in text
    ]


def check_version_consistency() -> list[str]:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]
    init_text = (ROOT / "src" / "arbcore" / "__init__.py").read_text(encoding="utf-8")
    expected = f'__version__ = "{project_version}"'
    if expected not in init_text:
        return [f"package version mismatch: expected {expected}"]
    return []


def check_ci_coverage() -> list[str]:
    workflow = ROOT / ".github" / "workflows" / "ci.yml"
    if not workflow.is_file():
        return ["missing CI workflow"]
    text = workflow.read_text(encoding="utf-8")
    required = (
        "ruff check .",
        "pytest",
        "PYTHONPATH=src python scripts/validate_golden_fixtures.py",
        "PYTHONPATH=src python scripts/validate_all.py --include-rust",
        "PYTHONPATH=src python scripts/release_readiness.py --json",
        "cargo test --manifest-path rust/arbcore-rs/Cargo.toml",
    )
    return [
        f"CI workflow missing command: {command}" for command in required if command not in text
    ]


def check_tracked_generated_files() -> list[str]:
    if not (ROOT / ".git").exists():
        return []
    try:
        output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    except (OSError, subprocess.CalledProcessError):
        return []
    errors: list[str] = []
    for tracked in output.splitlines():
        parts = set(Path(tracked).parts)
        has_forbidden_part = parts.intersection(FORBIDDEN_TRACKED_PARTS)
        has_forbidden_suffix = tracked.endswith(FORBIDDEN_TRACKED_SUFFIXES)
        if has_forbidden_part or has_forbidden_suffix:
            errors.append(f"generated/local file is tracked: {tracked}")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
