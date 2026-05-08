#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arbcore.contracts import report_to_json, validate_contract_workspace  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate repository smart-contract templates.")
    parser.add_argument("manifest", nargs="?", default="contracts/contract-manifest.json")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report JSON")
    args = parser.parse_args(argv)

    report = validate_contract_workspace(args.manifest)
    if args.json:
        print(report_to_json(report))
    else:
        print(
            f"Validated {report.artifacts_checked} contract artifact(s) "
            f"across {', '.join(report.languages) or 'no'} language(s)"
        )
        for finding in report.findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            print(f"{finding.severity.upper()} {finding.code} {location}: {finding.message}")
        if report.ok:
            print("contract validation passed")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
