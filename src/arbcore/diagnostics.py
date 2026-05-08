from __future__ import annotations

import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from arbcore import __version__
from arbcore.config import Settings
from arbcore.contracts import validate_contract_workspace


def collect_diagnostics() -> dict[str, Any]:
    """Return deterministic, non-secret operational diagnostics."""

    settings = Settings.from_env()
    contract_report = validate_contract_workspace()
    return {
        "arbcore_version": __version__,
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
        },
        "repository": {
            "cwd": str(Path.cwd()),
            "default_snapshot_exists": Path(settings.provider_file).is_file(),
            "default_network": settings.default_network,
            "contract_manifest_exists": Path("contracts/contract-manifest.json").is_file(),
        },
        "capabilities": {
            "offline_snapshot_analysis": True,
            "structured_cli_errors": True,
            "contract_template_validation": contract_report.ok,
            "smart_contract_languages": list(contract_report.languages),
            "multi_network_snapshots": True,
            "live_trading": False,
            "contract_deployment": False,
            "public_release_ready_claimed": False,
        },
        "optional_tools": {
            "cargo": shutil.which("cargo") is not None,
            "pytest": _module_available("pytest"),
            "ruff": shutil.which("ruff") is not None or _module_available("ruff"),
        },
        "resolved_policy": settings.policy.__dict__,
        "validation_commands": [
            "PYTHONPATH=src python scripts/validate_all.py --include-rust",
            "PYTHONPATH=src python scripts/validate_negative_cases.py",
            "PYTHONPATH=src python scripts/release_readiness.py --json",
        ],
        "limits": {
            "max_hops": 8,
            "max_results": 1000,
            "max_snapshot_edges": 10000,
        },
    }


def diagnostics_json() -> str:
    return json.dumps(collect_diagnostics(), indent=2)


def _module_available(name: str) -> bool:
    try:
        __import__(name)
    except ImportError:
        return False
    return True
