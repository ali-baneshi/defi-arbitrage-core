#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arbcore.contracts import validate_contract_workspace  # noqa: E402


def main() -> int:
    checks = [
        check_bad_snapshot_fails,
        check_bad_policy_fails,
        check_bad_metadata_fails,
        check_bad_timestamp_fails,
        check_cli_error_json_fails_cleanly,
        check_contract_entrypoint_mismatch_fails,
        check_contract_hash_mismatch_fails,
        check_contract_network_scope_fails,
        check_contract_role_scope_fails,
        check_contract_required_tags_fails,
    ]
    failures: list[str] = []
    for check in checks:
        try:
            check()
        except AssertionError as exc:
            failures.append(f"{check.__name__}: {exc}")
    if failures:
        print("negative validation checks failed", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("negative validation checks passed")
    return 0


def check_bad_snapshot_fails() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bad.json"
        path.write_text(json.dumps({"edges": [{"source": "A", "target": "A", "rate": 1}]}))
        result = subprocess.run(
            [sys.executable, "-m", "defi_arbitrage_core.cli", str(path), "--validate-only"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(SRC)},
            capture_output=True,
            text=True,
            check=False,
        )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "must differ" in result.stderr, result.stderr


def check_bad_policy_fails() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "defi_arbitrage_core.cli",
            "examples/market_snapshot.json",
            "--max-hops",
            "99",
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "max_hops" in result.stderr, result.stderr


def check_bad_metadata_fails() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bad.json"
        path.write_text(
            json.dumps({"edges": [{"source": "A", "target": "B", "rate": 1, "metadata": []}]})
        )
        result = subprocess.run(
            [sys.executable, "-m", "defi_arbitrage_core.cli", str(path), "--validate-only"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(SRC)},
            capture_output=True,
            text=True,
            check=False,
        )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "metadata" in result.stderr, result.stderr


def check_bad_timestamp_fails() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bad.json"
        path.write_text(
            json.dumps(
                {
                    "timestamp": "2026-05-05 10:00:00",
                    "edges": [{"source": "A", "target": "B", "rate": 1}],
                }
            )
        )
        result = subprocess.run(
            [sys.executable, "-m", "defi_arbitrage_core.cli", str(path), "--validate-only"],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(SRC)},
            capture_output=True,
            text=True,
            check=False,
        )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "timestamp" in result.stderr, result.stderr


def check_cli_error_json_fails_cleanly() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "defi_arbitrage_core.cli", "missing.json", "--error-json"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(SRC)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "SnapshotError"


def check_contract_entrypoint_mismatch_fails() -> None:
    with _contract_workspace() as manifest:
        payload = json.loads(manifest.read_text())
        payload["artifacts"][0]["entrypoints"] = ["missingFunction"]
        manifest.write_text(json.dumps(payload))
        report = validate_contract_workspace(manifest)
    assert not report.ok
    assert any(finding.code == "entrypoint_missing" for finding in report.findings)


def check_contract_hash_mismatch_fails() -> None:
    with _contract_workspace() as manifest:
        payload = json.loads(manifest.read_text())
        payload["artifacts"][0]["source_sha256"] = "0" * 64
        manifest.write_text(json.dumps(payload))
        report = validate_contract_workspace(manifest)
    assert not report.ok
    assert any(finding.code == "source_hash_mismatch" for finding in report.findings)


def check_contract_network_scope_fails() -> None:
    with _contract_workspace() as manifest:
        payload = json.loads(manifest.read_text())
        payload["artifacts"][0]["networks"] = ["local", "mainnet"]
        manifest.write_text(json.dumps(payload))
        report = validate_contract_workspace(manifest)
    assert not report.ok
    assert any(finding.code == "network_scope" for finding in report.findings)


def check_contract_role_scope_fails() -> None:
    with _contract_workspace() as manifest:
        payload = json.loads(manifest.read_text())
        payload["artifacts"][0]["role"] = "deployment"
        manifest.write_text(json.dumps(payload))
        report = validate_contract_workspace(manifest)
    assert not report.ok
    assert any(finding.code == "role_scope" for finding in report.findings)


def check_contract_required_tags_fails() -> None:
    with _contract_workspace() as manifest:
        payload = json.loads(manifest.read_text())
        payload["artifacts"][0]["tags"] = ["template"]
        manifest.write_text(json.dumps(payload))
        report = validate_contract_workspace(manifest)
    assert not report.ok
    assert any(finding.code == "required_tags" for finding in report.findings)


class _contract_workspace:
    def __enter__(self) -> Path:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        contracts = root / "contracts"
        (contracts / "solidity").mkdir(parents=True)
        (contracts / "vyper").mkdir(parents=True)
        for relative in (
            "contracts/solidity/FlashArbExecutor.sol",
            "contracts/vyper/FlashArbExecutor.vy",
        ):
            source = ROOT / relative
            target = root / relative
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        payload = json.loads((ROOT / "contracts/contract-manifest.json").read_text())
        manifest = contracts / "contract-manifest.json"
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        self.old_cwd = Path.cwd()
        os.chdir(root)
        self.manifest = manifest.relative_to(root)
        return self.manifest

    def __exit__(self, exc_type, exc, tb) -> None:
        os.chdir(self.old_cwd)
        self.tmp.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
