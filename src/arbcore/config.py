from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from arbcore.errors import ConfigurationError
from arbcore.models import RiskPolicy
from arbcore.path_utils import _resolve_safe_path


def _read_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a number") from exc


def _read_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    provider_file: str = "examples/market_snapshot.json"
    default_network: str = "polygon"
    policy: RiskPolicy = RiskPolicy()

    @classmethod
    def from_env(cls) -> Settings:
        # Resolve provider file path safely, restricting to current working directory and temp directory
        provider_file_path = _resolve_safe_path(
            os.getenv("ARBCORE_PROVIDER_FILE", "examples/market_snapshot.json"),
            allowed_roots=[Path.cwd(), Path(tempfile.gettempdir())]
        )
        settings = cls(
            provider_file=provider_file_path,
            default_network=os.getenv("ARBCORE_DEFAULT_NETWORK", "polygon").strip().lower()
            or "polygon",
            policy=RiskPolicy(
                min_profit_bps=_read_float("ARBCORE_MIN_PROFIT_BPS", 5.0),
                max_hops=_read_int("ARBCORE_MAX_HOPS", 4),
                min_liquidity=_read_float("ARBCORE_MIN_LIQUIDITY", 0.0),
                max_notional=_read_float("ARBCORE_MAX_NOTIONAL", 10_000.0),
                max_results=_read_int("ARBCORE_MAX_RESULTS", 25),
            ),
        )
        if not settings.default_network:
            raise ConfigurationError("ARBCORE_DEFAULT_NETWORK must be a non-empty string")
        settings.policy.validate()
        return settings
