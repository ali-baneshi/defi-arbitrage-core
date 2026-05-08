import json
from pathlib import Path

from arbcore.contracts import report_to_json, validate_contract_workspace
from arbcore.contracts.registry import load_contract_manifest, parse_contract_manifest
from arbcore.errors import ContractValidationError


def test_contract_workspace_validates_cleanly():
    report = validate_contract_workspace("contracts/contract-manifest.json")
    assert report.ok, [finding.to_dict() for finding in report.findings]
    assert set(report.languages) == {"solidity", "vyper"}
    assert report.artifacts_checked == 2
    assert report.manifest_sha256 is not None


def test_contract_report_serializes_to_stable_json():
    report = validate_contract_workspace("contracts/contract-manifest.json")
    payload = json.loads(report_to_json(report))
    assert payload["ok"] is True
    assert payload["languages"] == ["solidity", "vyper"]
    assert payload["manifest_sha256"] == report.manifest_sha256
    assert payload["findings"] == []


def test_manifest_rejects_unsupported_language():
    try:
        parse_contract_manifest(
            {
                "schema_version": 1,
                "language_metadata": {
                    "solidity": {
                        "file_extension": ".sol",
                        "compiler_family": "solc",
                        "compiler_required_locally": False,
                        "validation_level": "static-template-checks",
                    },
                    "vyper": {
                        "file_extension": ".vy",
                        "compiler_family": "vyper",
                        "compiler_required_locally": False,
                        "validation_level": "static-template-checks",
                    },
                },
                "artifacts": [
                    {
                        "name": "Bad",
                        "language": "move",
                        "path": "contracts/move/bad.move",
                        "artifact_type": "source-template",
                        "role": "template",
                        "description": "bad",
                        "source_sha256": "0" * 64,
                    }
                ],
            }
        )
    except ContractValidationError as exc:
        assert "unsupported language" in str(exc)
    else:
        raise AssertionError("unsupported language was accepted")


def test_contract_validator_rejects_path_outside_contracts(tmp_path):
    source = tmp_path / "Bad.sol"
    source.write_text(
        "pragma solidity ^0.8.20;\n// ARBCORE_CONTRACT_TEMPLATE\n// NOT AUDITED\ncontract Bad {}\n"
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "language_metadata": _language_metadata(),
                "artifacts": [
                    {
                        "name": "Bad",
                        "language": "solidity",
                        "path": str(source),
                        "artifact_type": "source-template",
                        "role": "template",
                        "description": "bad",
                        "source_sha256": "0" * 64,
                    }
                ],
            }
        )
    )
    report = validate_contract_workspace(manifest)
    assert not report.ok
    assert any(finding.code == "path_scope" for finding in report.findings)


def test_contract_validator_rejects_missing_file(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "language_metadata": _language_metadata(),
                "artifacts": [
                    {
                        "name": "Missing",
                        "language": "vyper",
                        "path": "contracts/vyper/Missing.vy",
                        "artifact_type": "source-template",
                        "role": "template",
                        "description": "missing",
                        "source_sha256": "0" * 64,
                    }
                ],
            }
        )
    )
    report = validate_contract_workspace(manifest)
    assert not report.ok
    assert any(finding.code == "missing_file" for finding in report.findings)


def test_contract_validator_rejects_source_hash_mismatch(tmp_path, monkeypatch):
    workspace = tmp_path / "repo"
    contract_dir = workspace / "contracts" / "solidity"
    contract_dir.mkdir(parents=True)
    source = contract_dir / "Bad.sol"
    source.write_text(
        "pragma solidity ^0.8.20;\n// ARBCORE_CONTRACT_TEMPLATE\n// NOT AUDITED\ncontract Bad {}\n"
    )
    manifest = workspace / "contracts" / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "language_metadata": _language_metadata(),
                "artifacts": [
                    {
                        "name": "Bad",
                        "language": "solidity",
                        "path": "contracts/solidity/Bad.sol",
                        "artifact_type": "source-template",
                        "role": "template",
                        "description": "bad",
                        "source_sha256": "0" * 64,
                    },
                    {
                        "name": "VyperPlaceholder",
                        "language": "vyper",
                        "path": "contracts/vyper/Missing.vy",
                        "artifact_type": "source-template",
                        "role": "template",
                        "description": "missing",
                        "source_sha256": "0" * 64,
                    },
                ],
            }
        )
    )
    monkeypatch.chdir(workspace)
    report = validate_contract_workspace("contracts/manifest.json")
    assert any(finding.code == "source_hash_mismatch" for finding in report.findings)


def test_contract_validator_resolves_paths_from_manifest_location(tmp_path, monkeypatch):
    workspace = tmp_path / "repo"
    contract_dir = workspace / "contracts" / "solidity"
    vyper_dir = workspace / "contracts" / "vyper"
    contract_dir.mkdir(parents=True)
    vyper_dir.mkdir(parents=True)
    solidity_source = Path("contracts/solidity/FlashArbExecutor.sol").read_text(encoding="utf-8")
    vyper_source = Path("contracts/vyper/FlashArbExecutor.vy").read_text(encoding="utf-8")
    (contract_dir / "FlashArbExecutor.sol").write_text(solidity_source, encoding="utf-8")
    (vyper_dir / "FlashArbExecutor.vy").write_text(vyper_source, encoding="utf-8")
    manifest = workspace / "contracts" / "contract-manifest.json"
    manifest.write_text(
        Path("contracts/contract-manifest.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    monkeypatch.chdir(tmp_path)
    report = validate_contract_workspace(manifest)

    assert report.ok, [finding.to_dict() for finding in report.findings]


def test_load_contract_manifest_rejects_non_utf8(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(b"\xff\xfe\x00\x00")
    try:
        load_contract_manifest(manifest)
    except ContractValidationError as exc:
        assert "UTF-8" in str(exc)
    else:
        raise AssertionError("expected non-UTF-8 manifest to fail")


def _language_metadata():
    return {
        "solidity": {
            "file_extension": ".sol",
            "compiler_family": "solc",
            "compiler_required_locally": False,
            "validation_level": "static-template-checks",
        },
        "vyper": {
            "file_extension": ".vy",
            "compiler_family": "vyper",
            "compiler_required_locally": False,
            "validation_level": "static-template-checks",
        },
    }
