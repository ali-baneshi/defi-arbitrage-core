#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    "README.md",
    "docs/en/RUNBOOK.md",
    "docs/en/VALIDATION.md",
    "docs/en/REVIEWER_GUIDE.md",
    "docs/en/RELEASE_EVIDENCE.md",
]
ALLOWED_PREFIXES = (
    "PYTHONPATH=src python -m defi_arbitrage_core.cli",
    "PYTHONPATH=src python -m arbcore.cli",
    "PYTHONPATH=src python scripts/validate_all.py",
    "PYTHONPATH=src python scripts/validate_repository.py",
    "PYTHONPATH=src python scripts/validate_contracts.py",
    "PYTHONPATH=src python scripts/validate_negative_cases.py",
    "PYTHONPATH=src python scripts/validate_schema_consistency.py",
    "PYTHONPATH=src python scripts/validate_output_contracts.py",
    "PYTHONPATH=src python scripts/run_unit_checks.py",
    "PYTHONPATH=src python scripts/release_readiness.py",
    "PYTHONPATH=src python scripts/demo_workflow.py",
    "PYTHONPATH=src python scripts/validate_rust_service.py",
    "PYTHONPATH=src python scripts/validate_examples.py",
    "PYTHONPATH=src python examples/custom_provider.py",
    "cargo build --manifest-path rust/arbcore-rs/Cargo.toml",
    "cargo test --manifest-path rust/arbcore-rs/Cargo.toml",
    "python -m compileall -q src tests scripts examples",
    "./scripts/secret_scan.sh",
    "pytest",
    "python -m pytest",
    "ruff check .",
    "python -m ruff check .",
    "python -m venv .venv",
    "source .venv/bin/activate",
    "pip install -e .[dev]",
    "pip install -e '.[dev]'",
    "make bootstrap",
    "defi-arbitrage-core ",
    "arbcore ",
)
REQUIRED_COMMANDS = (
    "PYTHONPATH=src python scripts/validate_all.py --include-rust",
    "PYTHONPATH=src python scripts/validate_output_contracts.py",
    "PYTHONPATH=src python scripts/release_readiness.py --json",
    "PYTHONPATH=src python -m defi_arbitrage_core.cli --diagnostics",
    "PYTHONPATH=src python -m defi_arbitrage_core.cli --self-check",
    "cargo test --manifest-path rust/arbcore-rs/Cargo.toml",
)


def main() -> int:
    errors: list[str] = []
    corpus = ""
    for relative in DOCS:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"documented command source missing: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        corpus += "\n" + text
        for command in _commands(text):
            if not command.startswith(ALLOWED_PREFIXES):
                errors.append(f"{relative} contains unsupported documented command: {command}")
            _check_referenced_path(errors, relative, command)
    for required in REQUIRED_COMMANDS:
        if required not in corpus:
            errors.append(f"required reviewer command is undocumented: {required}")
    if errors:
        print("documented command validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("documented command validation passed")
    return 0


def _commands(text: str) -> list[str]:
    commands: list[str] = []
    in_block = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_block = not in_block
            continue
        if not in_block or not stripped or stripped.startswith("#"):
            continue
        if re.match(
            r"^(PYTHONPATH=|cargo |python -m |\./|pytest$|ruff |source |pip |arbcore |defi-arbitrage-core )",  # noqa: E501
            stripped,
        ):
            commands.append(stripped)
    return commands


def _check_referenced_path(errors: list[str], relative: str, command: str) -> None:
    for token in command.split():
        if "target/debug/" in token:
            continue
        if token.startswith(("scripts/", "examples/", "contracts/", "rust/")):
            path = ROOT / token
            if not path.exists():
                errors.append(f"{relative} command references missing path {token}: {command}")


if __name__ == "__main__":
    raise SystemExit(main())
