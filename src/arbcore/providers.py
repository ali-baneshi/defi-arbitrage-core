from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Protocol

from arbcore.errors import SnapshotError
from arbcore.models import Edge, MarketSnapshot, MAX_SNAPSHOT_BYTES
from arbcore.path_utils import _resolve_safe_path
from arbcore.validation import validate_snapshot_payload


class MarketDataProvider(Protocol):
    """Extension point for loading market snapshots."""

    def load_snapshot(self) -> MarketSnapshot:
        """Return a validated market snapshot."""


class JsonFileProvider:
    """Loads a snapshot from a local JSON file without network access."""

    def __init__(self, path: str | Path):
        # Restrict path to be within the current working directory or system temp directory for security
        # In the future, this could be made configurable via an environment variable
        import tempfile
        self.path = _resolve_safe_path(path, allowed_roots=[Path.cwd(), Path(tempfile.gettempdir())])

    def load_snapshot(self) -> MarketSnapshot:
        if not self.path.exists():
            raise SnapshotError(f"snapshot file does not exist: {self.path}")
        if not self.path.is_file():
            raise SnapshotError(f"snapshot path is not a file: {self.path}")
        # Check file size before reading to prevent memory exhaustion
        if self.path.stat().st_size > MAX_SNAPSHOT_BYTES:
            raise SnapshotError(f"snapshot file too large: {self.path.stat().st_size} bytes (maximum {MAX_SNAPSHOT_BYTES} bytes)")
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except UnicodeDecodeError as exc:
            raise SnapshotError(f"snapshot file must be UTF-8 text: {self.path}") from exc
        except JSONDecodeError as exc:
            raise SnapshotError(f"snapshot file is not valid JSON: {self.path}") from exc
        validate_snapshot_payload(payload)
        raw_edges = payload["edges"]

        edges = tuple(self._parse_edge(item, index) for index, item in enumerate(raw_edges))
        snapshot = MarketSnapshot(
            edges=edges,
            source=str(payload.get("source", self.path.name)),
            network=str(payload.get("network", "polygon")),
            timestamp=payload.get("timestamp"),
        ).normalized()
        snapshot.validate()
        return snapshot

    @staticmethod
    def _parse_edge(item: object, index: int) -> Edge:
        if not isinstance(item, dict):
            raise SnapshotError(f"edge at index {index} must be an object")
        required = {"source", "target", "rate"}
        missing = sorted(required - set(item))
        if missing:
            raise SnapshotError(f"edge at index {index} is missing: {', '.join(missing)}")
        try:
            return Edge(
                source=str(item["source"]),
                target=str(item["target"]),
                rate=float(item["rate"]),
                venue=str(item.get("venue", "unknown")),
                fee_bps=float(item.get("fee_bps", 0.0)),
                liquidity=(None if item.get("liquidity") is None else float(item["liquidity"])),
                metadata=dict(item.get("metadata", {})),
            ).normalized()
        except (TypeError, ValueError) as exc:
            raise SnapshotError(f"edge at index {index} contains invalid numeric fields") from exc
