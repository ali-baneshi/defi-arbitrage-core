from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Any

from arbcore.errors import PolicyError, SnapshotError

BPS_DENOMINATOR = 10_000.0
MAX_REASONABLE_HOPS = 8
MAX_REASONABLE_RESULTS = 1_000
MAX_ASSET_SYMBOL_LENGTH = 32
MAX_VENUE_LENGTH = 80
MAX_SOURCE_LENGTH = 120
MAX_NETWORK_LENGTH = 64
MAX_METADATA_BYTES = 1_048_576
MAX_METADATA_KEYS = 128
MAX_METADATA_DEPTH = 10
MAX_EDGE_DEGREE = 500
MAX_SNAPSHOT_EDGES = 10_000
MAX_SNAPSHOT_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_TOTAL_METADATA_BYTES = 10 * 1024 * 1024  # 10 MB
RFC3339_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _metadata_depth(value: Any) -> int:
    if isinstance(value, dict):
        if not value:
            return 1
        return 1 + max(_metadata_depth(v) for v in value.values())
    if isinstance(value, list):
        if not value:
            return 1
        return 1 + max(_metadata_depth(v) for v in value)
    return 0


@dataclass(frozen=True)
class Edge:
    """A directed exchange quote from one asset to another.

    `rate` means units of `target` received for one unit of `source` before fees.
    `liquidity` is expressed in source-asset units and is used as a conservative
    route capacity estimate.
    """

    source: str
    target: str
    rate: float
    venue: str = "unknown"
    fee_bps: float = 0.0
    liquidity: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def normalized(self) -> Edge:
        if not isinstance(self.metadata, dict):
            raise SnapshotError("edge metadata must be an object")
        return Edge(
            source=str(self.source).strip().upper(),
            target=str(self.target).strip().upper(),
            rate=float(self.rate),
            venue=str(self.venue).strip() or "unknown",
            fee_bps=float(self.fee_bps),
            liquidity=None if self.liquidity is None else float(self.liquidity),
            metadata=dict(self.metadata),
        )

    def effective_rate(self) -> float:
        fee_multiplier = 1.0 - (self.fee_bps / BPS_DENOMINATOR)
        return self.rate * fee_multiplier

    def validate(self) -> None:
        edge = self.normalized()
        if not edge.source or not edge.target:
            raise SnapshotError("edge source and target are required")
        if len(edge.source) > MAX_ASSET_SYMBOL_LENGTH or len(edge.target) > MAX_ASSET_SYMBOL_LENGTH:
            raise SnapshotError("edge source and target must be 32 characters or fewer")
        if edge.source == edge.target:
            raise SnapshotError("edge source and target must differ")
        if len(edge.venue) > MAX_VENUE_LENGTH:
            raise SnapshotError("edge venue must be 80 characters or fewer")
        if not math.isfinite(edge.rate) or edge.rate <= 0:
            raise SnapshotError("edge rate must be a finite positive number")
        if not math.isfinite(edge.fee_bps) or edge.fee_bps < 0 or edge.fee_bps >= BPS_DENOMINATOR:
            raise SnapshotError("edge fee_bps must be a finite number in [0, 10000)")
        if edge.liquidity is not None and (not math.isfinite(edge.liquidity) or edge.liquidity < 0):
            raise SnapshotError("edge liquidity must be a finite non-negative number")
        if len(edge.metadata) > MAX_METADATA_KEYS:
            raise SnapshotError(
                f"edge metadata must have {MAX_METADATA_KEYS} keys or fewer"
            )
        metadata_bytes = len(json.dumps(edge.metadata, separators=(",", ":"), default=str))
        if metadata_bytes > MAX_METADATA_BYTES:
            raise SnapshotError(
                f"edge metadata must be {MAX_METADATA_BYTES} bytes or fewer"
            )
        if _metadata_depth(edge.metadata) > MAX_METADATA_DEPTH:
            raise SnapshotError(
                f"edge metadata must be nested {MAX_METADATA_DEPTH} levels deep or fewer"
            )


@dataclass(frozen=True)
class MarketSnapshot:
    """A point-in-time collection of exchange edges."""

    edges: tuple[Edge, ...]
    source: str = "local"
    network: str = "polygon"
    timestamp: str | None = None

    def normalized(self) -> MarketSnapshot:
        return MarketSnapshot(
            edges=tuple(edge.normalized() for edge in self.edges),
            source=(self.source or "local").strip(),
            network=(self.network or "polygon").strip().lower(),
            timestamp=self.timestamp,
        )

    def validate(self) -> None:
        if not self.edges:
            raise SnapshotError("market snapshot must contain at least one edge")
        if not isinstance(self.source, str) or not self.source.strip():
            raise SnapshotError("market snapshot source must be a non-empty string")
        if len(self.source.strip()) > MAX_SOURCE_LENGTH:
            raise SnapshotError(
                f"market snapshot source must be {MAX_SOURCE_LENGTH} characters or fewer"
            )
        if not isinstance(self.network, str) or not self.network.strip():
            raise SnapshotError("market snapshot network must be a non-empty string")
        if len(self.network.strip()) > MAX_NETWORK_LENGTH:
            raise SnapshotError(
                f"market snapshot network must be {MAX_NETWORK_LENGTH} characters or fewer"
            )
        if self.timestamp is not None:
            if not isinstance(self.timestamp, str):
                raise SnapshotError("market snapshot timestamp must be a string when provided")
            if not RFC3339_UTC_RE.fullmatch(self.timestamp):
                raise SnapshotError(
                    "market snapshot timestamp must use UTC RFC3339 form YYYY-MM-DDTHH:MM:SSZ"
                )
        # Check aggregate metadata size to prevent memory exhaustion
        total_metadata_bytes = sum(
            len(json.dumps(edge.metadata, separators=(',', ':'), default=str))
            for edge in self.edges
        )
        if total_metadata_bytes > MAX_TOTAL_METADATA_BYTES:
            raise SnapshotError(
                f"total metadata size too large: {total_metadata_bytes} bytes (maximum {MAX_TOTAL_METADATA_BYTES} bytes)"
            )
        for edge in self.edges:
            edge.validate()


@dataclass(frozen=True)
class RiskPolicy:
    """Conservative filters applied before an opportunity is reported.

    `max_notional` is a route capacity ceiling, not a trade recommendation.
    """

    min_profit_bps: float = 5.0
    max_hops: int = 4
    min_liquidity: float = 0.0
    max_notional: float = 10_000.0
    max_results: int = 25

    def validate(self) -> None:
        if not math.isfinite(self.min_profit_bps) or self.min_profit_bps < 0:
            raise PolicyError("min_profit_bps must be a finite non-negative number")
        if self.max_hops < 2:
            raise PolicyError("max_hops must be at least 2")
        if self.max_hops > MAX_REASONABLE_HOPS:
            raise PolicyError(f"max_hops must be at most {MAX_REASONABLE_HOPS}")
        if not math.isfinite(self.min_liquidity) or self.min_liquidity < 0:
            raise PolicyError("min_liquidity must be a finite non-negative number")
        if not math.isfinite(self.max_notional) or self.max_notional <= 0:
            raise PolicyError("max_notional must be a finite positive number")
        if self.max_notional < self.min_liquidity:
            raise PolicyError("max_notional must be at least min_liquidity")
        if self.max_results < 1:
            raise PolicyError("max_results must be at least 1")
        if self.max_results > MAX_REASONABLE_RESULTS:
            raise PolicyError(f"max_results must be at most {MAX_REASONABLE_RESULTS}")


@dataclass(frozen=True)
class Opportunity:
    """A discovered cycle after policy checks."""

    network: str
    path: tuple[str, ...]
    venues: tuple[str, ...]
    gross_return: float
    profit_bps: float
    limiting_liquidity: float | None
    estimated_capacity: float

    @property
    def is_profitable(self) -> bool:
        return self.profit_bps > 0
