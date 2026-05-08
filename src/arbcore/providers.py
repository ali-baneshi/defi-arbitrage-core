from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Protocol

from arbcore.errors import SnapshotError
from arbcore.models import Edge, MarketSnapshot
from arbcore.validation import validate_snapshot_payload


class MarketDataProvider(Protocol):
    """Extension point for loading market snapshots."""

    def load_snapshot(self) -> MarketSnapshot:
        """Return a validated market snapshot."""


class JsonFileProvider:
    """Loads a snapshot from a local JSON file without network access."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load_snapshot(self) -> MarketSnapshot:
        if not self.path.exists():
            raise SnapshotError(f"snapshot file does not exist: {self.path}")
        if not self.path.is_file():
            raise SnapshotError(f"snapshot path is not a file: {self.path}")
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
