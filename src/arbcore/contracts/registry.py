from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from arbcore.contracts.models import ContractArtifact, ContractLanguageMetadata
from arbcore.errors import ContractValidationError

SUPPORTED_LANGUAGES = {"solidity", "vyper"}
MANIFEST_KEYS = {"schema_version", "description", "language_metadata", "artifacts"}
ARTIFACT_KEYS = {
    "name",
    "language",
    "path",
    "artifact_type",
    "role",
    "description",
    "source_sha256",
    "entrypoints",
    "networks",
    "tags",
}
LANGUAGE_METADATA_KEYS = {
    "file_extension",
    "compiler_family",
    "compiler_required_locally",
    "validation_level",
}


def load_contract_manifest(
    path: str | Path = "contracts/contract-manifest.json",
) -> tuple[list[ContractArtifact], dict[str, ContractLanguageMetadata]]:
    """Load contract artifacts and language metadata from a repository-local manifest."""

    manifest_path = Path(path)
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractValidationError(f"contract manifest does not exist: {manifest_path}") from exc
    except UnicodeDecodeError as exc:
        raise ContractValidationError(
            f"contract manifest must be UTF-8 text: {manifest_path}"
        ) from exc
    except JSONDecodeError as exc:
        raise ContractValidationError(
            f"contract manifest is not valid JSON: {manifest_path}"
        ) from exc
    return parse_contract_manifest(payload)


def parse_contract_manifest(
    payload: object,
) -> tuple[list[ContractArtifact], dict[str, ContractLanguageMetadata]]:
    if not isinstance(payload, dict):
        raise ContractValidationError("contract manifest must be a JSON object")
    unknown = set(payload) - MANIFEST_KEYS
    if unknown:
        raise ContractValidationError(
            f"contract manifest contains unsupported keys: {', '.join(sorted(unknown))}"
        )
    if payload.get("schema_version") != 1:
        raise ContractValidationError("contract manifest schema_version must be 1")
    metadata = _parse_language_metadata(payload.get("language_metadata"))
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ContractValidationError("contract manifest must contain a non-empty artifacts list")
    return [_parse_artifact(item, index) for index, item in enumerate(artifacts)], metadata


def _parse_language_metadata(payload: object) -> dict[str, ContractLanguageMetadata]:
    if not isinstance(payload, dict):
        raise ContractValidationError("contract manifest must contain language_metadata")
    unknown_languages = set(payload) - SUPPORTED_LANGUAGES
    if unknown_languages:
        languages = ", ".join(sorted(unknown_languages))
        raise ContractValidationError(
            f"language_metadata contains unsupported languages: {languages}"
        )
    missing_languages = SUPPORTED_LANGUAGES - set(payload)
    if missing_languages:
        raise ContractValidationError(
            f"language_metadata is missing languages: {', '.join(sorted(missing_languages))}"
        )
    return {
        language: _parse_language_metadata_item(language, item)
        for language, item in payload.items()
    }


def _parse_language_metadata_item(
    language: str,
    item: object,
) -> ContractLanguageMetadata:
    if not isinstance(item, dict):
        raise ContractValidationError(f"language_metadata.{language} must be an object")
    unknown = set(item) - LANGUAGE_METADATA_KEYS
    if unknown:
        raise ContractValidationError(
            f"language_metadata.{language} contains unsupported keys: {', '.join(sorted(unknown))}"
        )
    missing = LANGUAGE_METADATA_KEYS - set(item)
    if missing:
        raise ContractValidationError(
            f"language_metadata.{language} is missing: {', '.join(sorted(missing))}"
        )
    compiler_required = item["compiler_required_locally"]
    if not isinstance(compiler_required, bool):
        raise ContractValidationError(
            f"language_metadata.{language}.compiler_required_locally must be boolean"
        )
    return ContractLanguageMetadata(
        language=language,  # type: ignore[arg-type]
        file_extension=_metadata_string(item, "file_extension", language),
        compiler_family=_metadata_string(item, "compiler_family", language),
        compiler_required_locally=compiler_required,
        validation_level=_metadata_string(item, "validation_level", language),
    )


def _parse_artifact(item: object, index: int) -> ContractArtifact:
    if not isinstance(item, dict):
        raise ContractValidationError(f"artifact at index {index} must be an object")
    unknown = set(item) - ARTIFACT_KEYS
    if unknown:
        raise ContractValidationError(
            f"artifact at index {index} contains unsupported keys: {', '.join(sorted(unknown))}"
        )
    required = {
        "name",
        "language",
        "path",
        "artifact_type",
        "role",
        "description",
        "source_sha256",
    }
    missing = sorted(required - set(item))
    if missing:
        raise ContractValidationError(f"artifact at index {index} is missing: {', '.join(missing)}")
    language = _string(item, "language", index).lower()
    if language not in SUPPORTED_LANGUAGES:
        raise ContractValidationError(
            f"artifact at index {index} has unsupported language: {language}"
        )
    return ContractArtifact(
        name=_string(item, "name", index),
        language=language,  # type: ignore[arg-type]
        path=_string(item, "path", index),
        artifact_type=_string(item, "artifact_type", index),
        role=_string(item, "role", index),
        description=_string(item, "description", index),
        source_sha256=_string(item, "source_sha256", index).lower(),
        entrypoints=_string_tuple(item.get("entrypoints", ()), "entrypoints", index),
        networks=_string_tuple(item.get("networks", ("local",)), "networks", index),
        tags=_string_tuple(item.get("tags", ()), "tags", index),
    )


def _metadata_string(item: dict[str, Any], key: str, language: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"language_metadata.{language}.{key} must be a string")
    return value.strip()


def _string(item: dict[str, Any], key: str, index: int) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"artifact at index {index} field {key} must be a string")
    return value.strip()


def _string_tuple(value: object, key: str, index: int) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise ContractValidationError(f"artifact at index {index} field {key} must be a list")
    result = tuple(str(item).strip() for item in value if str(item).strip())
    if len(result) != len(value):
        raise ContractValidationError(
            f"artifact at index {index} field {key} contains empty values"
        )
    return result
