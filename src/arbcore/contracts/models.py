from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

ContractLanguage = Literal["solidity", "vyper"]
FindingSeverity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class ContractArtifact:
    """Repository-local smart-contract artifact declared in the manifest."""

    name: str
    language: ContractLanguage
    path: str
    artifact_type: str
    role: str
    description: str
    source_sha256: str
    entrypoints: tuple[str, ...] = ()
    networks: tuple[str, ...] = ("local",)
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContractLanguageMetadata:
    """Language-level expectations used by the dependency-free validator."""

    language: ContractLanguage
    file_extension: str
    compiler_family: str
    compiler_required_locally: bool
    validation_level: str


@dataclass(frozen=True)
class ContractFinding:
    """A deterministic validation finding for a contract artifact or manifest."""

    path: str
    severity: FindingSeverity
    code: str
    message: str
    line: int | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ContractValidationReport:
    """Validation result for the contract manifest and referenced artifacts."""

    manifest_path: str
    artifacts_checked: int
    languages: tuple[str, ...]
    manifest_sha256: str | None
    findings: tuple[ContractFinding, ...]

    @property
    def ok(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)

    def to_dict(self) -> dict[str, object]:
        return {
            "manifest_path": self.manifest_path,
            "artifacts_checked": self.artifacts_checked,
            "languages": list(self.languages),
            "manifest_sha256": self.manifest_sha256,
            "ok": self.ok,
            "findings": [finding.to_dict() for finding in self.findings],
        }
