from __future__ import annotations

import hashlib
import json
import re
import tempfile
from pathlib import Path

from arbcore.contracts.models import ContractArtifact, ContractFinding, ContractValidationReport
from arbcore.contracts.registry import load_contract_manifest
from arbcore.path_utils import _resolve_safe_path

ADDRESS_RE = re.compile(r"0x[a-fA-F0-9]{40}")
PRIVATE_KEY_RE = re.compile(r"0x[a-fA-F0-9]{64}")
SECRET_RE = re.compile(r"(PRIVATE_KEY|MNEMONIC|RPC_URL|api[_-]?key|sk-[A-Za-z0-9_-]{20,})", re.I)
RPC_RE = re.compile(r"https?://[^\s'\"]*(mainnet|testnet|polygon|alchemy|infura)[^\s'\"]*", re.I)
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

DANGEROUS = {
    "solidity": ("delegatecall", "selfdestruct", "tx.origin", "assembly", ".call{"),
    "vyper": ("raw_call", "selfdestruct", "delegate_call", "tx.origin"),
}
EXTENSIONS = {"solidity": ".sol", "vyper": ".vy"}
ALLOWED_ARTIFACT_TYPES = {"source-template"}
ALLOWED_NETWORKS = {"local"}
ALLOWED_VALIDATION_LEVELS = {"static-template-checks"}
REQUIRED_ARTIFACT_TAGS = {"template", "non-deployable-without-audit"}


def validate_contract_workspace(
    manifest_path: str | Path = "contracts/contract-manifest.json",
) -> ContractValidationReport:
    # Resolve manifest path safely, restricting to current working
    # directory and temp directory
    manifest_path = _resolve_safe_path(
        manifest_path, allowed_roots=[Path.cwd(), Path(tempfile.gettempdir())]
    )
    manifest = Path(manifest_path)
    workspace_root = (
        manifest.resolve().parent.parent if manifest.parent.name == "contracts" else Path.cwd()
    )
    findings: list[ContractFinding] = []
    manifest_hash = _sha256_file(manifest) if manifest.is_file() else None
    try:
        artifacts, metadata = load_contract_manifest(manifest)
    except Exception as exc:  # safe message from parser, converted into report
        findings.append(_finding(str(manifest), "error", "manifest_invalid", str(exc)))
        return ContractValidationReport(str(manifest), 0, (), manifest_hash, tuple(findings))

    for language, expected_extension in EXTENSIONS.items():
        language_metadata = metadata.get(language)
        if language_metadata is None:
            findings.append(_finding(str(manifest), "error", "language_missing", language))
            continue
        if language_metadata.file_extension != expected_extension:
            findings.append(
                _finding(
                    str(manifest),
                    "error",
                    "language_extension_mismatch",
                    f"{language} extension must be {expected_extension}",
                )
            )
        if language_metadata.compiler_required_locally:
            findings.append(
                _finding(
                    str(manifest),
                    "error",
                    "compiler_required",
                    "local compilers must remain optional in this repository",
                )
            )
        if language_metadata.validation_level not in ALLOWED_VALIDATION_LEVELS:
            findings.append(
                _finding(
                    str(manifest),
                    "error",
                    "validation_level",
                    f"unsupported validation level for {language}: {language_metadata.validation_level}",  # noqa: E501
                )
            )

    names: set[str] = set()
    paths: set[str] = set()
    for artifact in artifacts:
        if artifact.name in names:
            findings.append(_finding(artifact.path, "error", "duplicate_name", artifact.name))
        names.add(artifact.name)
        if artifact.path in paths:
            findings.append(_finding(artifact.path, "error", "duplicate_path", artifact.path))
        paths.add(artifact.path)
        findings.extend(_validate_artifact(artifact, workspace_root))

    languages = tuple(sorted({artifact.language for artifact in artifacts}))
    missing_required = set(EXTENSIONS) - set(languages)
    for language in sorted(missing_required):
        findings.append(_finding(str(manifest), "error", "required_language_missing", language))
    return ContractValidationReport(
        str(manifest),
        len(artifacts),
        languages,
        manifest_hash,
        tuple(findings),
    )


def report_to_json(report: ContractValidationReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def _validate_artifact(artifact: ContractArtifact, workspace_root: Path) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    relative_path = Path(artifact.path)
    path_text = str(relative_path)
    if (
        relative_path.is_absolute()
        or ".." in relative_path.parts
        or not relative_path.parts
        or relative_path.parts[0] != "contracts"
    ):
        return [
            _finding(path_text, "error", "path_scope", "artifact path must stay under contracts/")
        ]
    path = workspace_root / relative_path
    if artifact.artifact_type not in ALLOWED_ARTIFACT_TYPES:
        findings.append(_finding(path_text, "error", "artifact_type", "unsupported artifact type"))
    if artifact.role != "template":
        findings.append(
            _finding(path_text, "error", "role_scope", "artifact role must be template")
        )
    missing_tags = REQUIRED_ARTIFACT_TAGS - set(artifact.tags)
    if missing_tags:
        findings.append(
            _finding(
                path_text,
                "error",
                "required_tags",
                f"artifact must carry tags: {', '.join(sorted(missing_tags))}",
            )
        )
    if (
        "audit" not in artifact.description.lower()
        and "template" not in artifact.description.lower()
    ):
        findings.append(
            _finding(
                path_text,
                "warning",
                "description_scope",
                "description should state template/audit scope",
            )
        )
    unsupported_networks = set(artifact.networks) - ALLOWED_NETWORKS
    if unsupported_networks:
        findings.append(
            _finding(
                path_text,
                "error",
                "network_scope",
                f"only local network scope is allowed: {', '.join(sorted(unsupported_networks))}",
            )
        )
    if not SHA256_RE.fullmatch(artifact.source_sha256):
        findings.append(_finding(path_text, "error", "source_hash_format", "invalid sha256"))
    if path.suffix != EXTENSIONS[artifact.language]:
        findings.append(
            _finding(path_text, "error", "extension", "file extension does not match language")
        )
    if not path.exists() or not path.is_file():
        findings.append(
            _finding(path_text, "error", "missing_file", "contract source file is missing")
        )
        return findings
    actual_hash = _sha256_file(path)
    if artifact.source_sha256 != actual_hash:
        findings.append(
            _finding(path_text, "error", "source_hash_mismatch", "source sha256 mismatch")
        )
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        findings.append(_finding(path_text, "error", "encoding", "contract source must be UTF-8"))
        return findings
    findings.extend(_validate_source(artifact, source))
    return findings


def _validate_source(artifact: ContractArtifact, source: str) -> list[ContractFinding]:
    findings: list[ContractFinding] = []
    path = artifact.path
    required_markers = {
        "ARBCORE_CONTRACT_TEMPLATE": "missing_template_marker",
        "NOT AUDITED": "missing_audit_warning",
    }
    for marker, code in required_markers.items():
        if marker not in source:
            findings.append(_finding(path, "error", code, f"source must include {marker}"))
    if PRIVATE_KEY_RE.search(source):
        findings.append(
            _finding(path, "error", "private_key_like_value", "private-key-like value found")
        )
    if ADDRESS_RE.search(source):
        findings.append(
            _finding(path, "error", "hardcoded_address", "hard-coded EVM address found")
        )
    if SECRET_RE.search(source):
        findings.append(_finding(path, "error", "secret_marker", "secret-like marker found"))
    if RPC_RE.search(source):
        findings.append(_finding(path, "error", "rpc_url", "RPC URL found in contract source"))
    lowered = source.lower()
    if "deploy" in lowered and "do not deploy" not in lowered:
        findings.append(
            _finding(path, "warning", "deployment_language", "deployment wording needs review")
        )
    for pattern in DANGEROUS[artifact.language]:
        if pattern.lower() in lowered:
            findings.append(
                _finding(
                    path,
                    "error",
                    "dangerous_primitive",
                    f"dangerous primitive found: {pattern}",
                )
            )
    if artifact.language == "solidity":
        if "pragma solidity" not in source:
            findings.append(
                _finding(path, "error", "solidity_pragma", "Solidity source needs pragma")
            )
        if not re.search(r"\bcontract\s+\w+", source):
            findings.append(
                _finding(
                    path,
                    "error",
                    "solidity_contract",
                    "Solidity source needs contract declaration",
                )
            )
        for entrypoint in artifact.entrypoints:
            pattern = rf"\bfunction\s+{re.escape(entrypoint)}\b"
            if not re.search(pattern, source):
                findings.append(
                    _finding(
                        path,
                        "error",
                        "entrypoint_missing",
                        f"manifest entrypoint is missing from Solidity source: {entrypoint}",
                    )
                )
    if artifact.language == "vyper":
        if "# @version" not in source:
            findings.append(
                _finding(path, "error", "vyper_version", "Vyper source needs # @version")
            )
        if "@external" not in source and "@view" not in source:
            findings.append(
                _finding(
                    path,
                    "error",
                    "vyper_entrypoint",
                    "Vyper source needs @external or @view",
                )
            )
        for entrypoint in artifact.entrypoints:
            pattern = rf"\bdef\s+{re.escape(entrypoint)}\b"
            if not re.search(pattern, source):
                findings.append(
                    _finding(
                        path,
                        "error",
                        "entrypoint_missing",
                        f"manifest entrypoint is missing from Vyper source: {entrypoint}",
                    )
                )
    return findings


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finding(
    path: str,
    severity: str,
    code: str,
    message: str,
    line: int | None = None,
) -> ContractFinding:
    return ContractFinding(
        path=path,
        severity=severity,  # type: ignore[arg-type]
        code=code,
        message=message,
        line=line,
    )
