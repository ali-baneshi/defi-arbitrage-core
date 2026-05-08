from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from arbcore.errors import SnapshotError
from arbcore.models import (
    MAX_NETWORK_LENGTH,
    MAX_SOURCE_LENGTH,
    RFC3339_UTC_RE,
    MarketSnapshot,
    Opportunity,
)

SNAPSHOT_SCHEMA_VERSION = "2020-12"
MAX_SNAPSHOT_EDGES = 10_000


def snapshot_to_dict(snapshot: MarketSnapshot) -> dict[str, Any]:
    normalized = snapshot.normalized()
    return {
        "source": normalized.source,
        "network": normalized.network,
        "timestamp": normalized.timestamp,
        "edges": [asdict(edge) for edge in normalized.edges],
    }


def opportunities_to_dict(opportunities: list[Opportunity]) -> list[dict[str, Any]]:
    return [asdict(item) for item in opportunities]


def validate_snapshot_payload(payload: object) -> None:
    """Validate snapshot shape without optional third-party JSON Schema dependencies."""

    if not isinstance(payload, dict):
        raise SnapshotError("snapshot JSON must be an object")
    unknown = set(payload) - {"source", "network", "timestamp", "edges"}
    if unknown:
        raise SnapshotError(
            f"snapshot JSON contains unsupported keys: {', '.join(sorted(unknown))}"
        )
    source = payload.get("source")
    if source is not None and (not isinstance(source, str) or not source.strip()):
        raise SnapshotError("snapshot JSON source must be a non-empty string when provided")
    if isinstance(source, str) and len(source.strip()) > MAX_SOURCE_LENGTH:
        raise SnapshotError(f"snapshot JSON source must be {MAX_SOURCE_LENGTH} characters or fewer")
    network = payload.get("network")
    if network is not None and (not isinstance(network, str) or not network.strip()):
        raise SnapshotError("snapshot JSON network must be a non-empty string when provided")
    if isinstance(network, str) and len(network.strip()) > MAX_NETWORK_LENGTH:
        raise SnapshotError(
            f"snapshot JSON network must be {MAX_NETWORK_LENGTH} characters or fewer"
        )
    timestamp = payload.get("timestamp")
    if timestamp is not None:
        if not isinstance(timestamp, str):
            raise SnapshotError("snapshot JSON timestamp must be a string when provided")
        if not RFC3339_UTC_RE.fullmatch(timestamp):
            raise SnapshotError(
                "snapshot JSON timestamp must use UTC RFC3339 form YYYY-MM-DDTHH:MM:SSZ"
            )
    edges = payload.get("edges")
    if not isinstance(edges, list):
        raise SnapshotError("snapshot JSON must contain an 'edges' list")
    if not edges:
        raise SnapshotError("snapshot JSON must contain at least one edge")
    if len(edges) > MAX_SNAPSHOT_EDGES:
        raise SnapshotError(f"snapshot JSON must contain at most {MAX_SNAPSHOT_EDGES} edges")
    for index, item in enumerate(edges):
        if not isinstance(item, dict):
            raise SnapshotError(f"edge at index {index} must be an object")
        unknown_edge_keys = set(item) - {
            "source",
            "target",
            "rate",
            "venue",
            "fee_bps",
            "liquidity",
            "metadata",
        }
        if unknown_edge_keys:
            raise SnapshotError(
                f"edge at index {index} contains unsupported keys: "
                f"{', '.join(sorted(unknown_edge_keys))}"
            )
        metadata = item.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise SnapshotError(f"edge at index {index} metadata must be an object")


def load_json_payload(path: str | Path) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SnapshotError(f"snapshot file does not exist: {path}") from exc
    except IsADirectoryError as exc:
        raise SnapshotError(f"snapshot path is not a file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SnapshotError(f"snapshot file is not valid JSON: {path}") from exc
